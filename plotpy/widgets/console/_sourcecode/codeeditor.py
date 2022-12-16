# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Editor widget based on QtGui.QPlainTextEdit
"""

# %% This line is for cell execution testing
# pylint: disable=C0103
# pylint: disable=R0903
# pylint: disable=R0911
# pylint: disable=R0201

import keyword
import os.path as osp
import re
import sre_constants
import sys

import plotpy.console.syntaxhighlighters as sh
from plotpy.console.dochelpers import getobj
from plotpy.console.widgets.editortools import PythonCFM
from plotpy.console.widgets.sourcecode.base import TextEditBaseWidget
from plotpy.gui.config.misc import get_icon
from plotpy.gui.utils import encoding
from plotpy.gui.utils.misc import (
    add_actions,
    config_shortcut,
    create_action,
    get_shortcut,
)
from plotpy.gui.widgets.config import CONF, _
from plotpy.gui.widgets.ext_gui_lib import (
    QApplication,
    QBrush,
    QColor,
    QCursor,
    QKeySequence,
    QMenu,
    QMessageBox,
    QPainter,
    QPaintEvent,
    QRect,
    QRegExp,
    QSize,
    QStyle,
    Qt,
    QTextBlockUserData,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextEdit,
    QTextFormat,
    QTextOption,
    QTimer,
    QToolTip,
    QWidget,
    Signal,
    Slot,
)

# %% This line is for cell execution testing


nbformat = None  # analysis:ignore

ALL_LANGUAGES = {"Python": ("py", "pyw", "python", "ipy")}

PYTHON_LIKE_LANGUAGES = ("Python", "Cython", "Enaml")

CELL_LANGUAGES = {"Python": ("#%%", "# %%", "# <codecell>", "# In[")}


# ===============================================================================
# Viewport widgets
# ===============================================================================
class LineNumberArea(QWidget):
    """Line number area (on the left side of the text editor widget)"""

    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.code_editor = editor
        self.setMouseTracking(True)

    def sizeHint(self):
        """Override Qt method"""
        return QSize(self.code_editor.compute_linenumberarea_width(), 0)

    def paintEvent(self, event):
        """Override Qt method"""
        self.code_editor.linenumberarea_paint_event(event)

    def mouseMoveEvent(self, event):
        """Override Qt method"""
        self.code_editor.linenumberarea_mousemove_event(event)

    def mouseDoubleClickEvent(self, event):
        """Override Qt method"""
        self.code_editor.linenumberarea_mousedoubleclick_event(event)

    def mousePressEvent(self, event):
        """Override Qt method"""
        self.code_editor.linenumberarea_mousepress_event(event)

    def mouseReleaseEvent(self, event):
        """Override Qt method"""
        self.code_editor.linenumberarea_mouserelease_event(event)

    def wheelEvent(self, event):
        """Override Qt method"""
        self.code_editor.wheelEvent(event)


class ScrollFlagArea(QWidget):
    """Source code editor's scroll flag area"""

    WIDTH = 12
    FLAGS_DX = 4
    FLAGS_DY = 2

    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.code_editor = editor
        editor.verticalScrollBar().valueChanged.connect(lambda value: self.repaint())

    def sizeHint(self):
        """Override Qt method"""
        return QSize(self.WIDTH, 0)

    def paintEvent(self, event):
        """Override Qt method"""
        self.code_editor.scrollflagarea_paint_event(event)

    def mousePressEvent(self, event):
        """Override Qt method"""
        vsb = self.code_editor.verticalScrollBar()
        value = self.position_to_value(event.pos().y() - 1)
        vsb.setValue(value - 0.5 * vsb.pageStep())

    def get_scale_factor(self, slider=False):
        """Return scrollbar's scale factor:
        ratio between pixel span height and value span height"""
        delta = 0 if slider else 2
        vsb = self.code_editor.verticalScrollBar()
        position_height = vsb.height() - delta - 1
        value_height = vsb.maximum() - vsb.minimum() + vsb.pageStep()
        return float(position_height) / value_height

    def value_to_position(self, y, slider=False):
        """Convert value to position"""
        offset = 0 if slider else 1
        vsb = self.code_editor.verticalScrollBar()
        return (y - vsb.minimum()) * self.get_scale_factor(slider) + offset

    def position_to_value(self, y, slider=False):
        """Convert position to value"""
        offset = 0 if slider else 1
        vsb = self.code_editor.verticalScrollBar()
        return vsb.minimum() + max([0, (y - offset) / self.get_scale_factor(slider)])

    def make_flag_qrect(self, position):
        """Make flag QRect"""
        return QRect(
            self.FLAGS_DX / 2,
            position - self.FLAGS_DY / 2,
            self.WIDTH - self.FLAGS_DX,
            self.FLAGS_DY,
        )

    def make_slider_range(self, value):
        """Make slider range QRect"""
        vsb = self.code_editor.verticalScrollBar()
        pos1 = self.value_to_position(value, slider=True)
        pos2 = self.value_to_position(value + vsb.pageStep(), slider=True)
        return QRect(1, pos1, self.WIDTH - 2, pos2 - pos1 + 1)

    def wheelEvent(self, event):
        """Override Qt method"""
        self.code_editor.wheelEvent(event)


class EdgeLine(QWidget):
    """Source code editor's edge line (default: 79 columns, PEP8)"""

    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.code_editor = editor
        self.column = 79
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        """Override Qt method"""
        painter = QPainter(self)
        color = QColor(Qt.darkGray)
        color.setAlphaF(0.5)
        painter.fillRect(event.rect(), color)


# ===============================================================================
# CodeEditor widget
# ===============================================================================
class BlockUserData(QTextBlockUserData):
    """

    """

    def __init__(self, editor):
        QTextBlockUserData.__init__(self)
        self.editor = editor
        self.breakpoint = False
        self.breakpoint_condition = None
        self.code_analysis = []
        self.todo = ""
        self.editor.blockuserdata_list.append(self)

    def is_empty(self):
        """

        :return:
        """
        return not self.breakpoint and not self.code_analysis and not self.todo

    def __del__(self):
        bud_list = self.editor.blockuserdata_list
        bud_list.pop(bud_list.index(self))


def set_scrollflagarea_painter(painter, light_color):
    """Set scroll flag area painter pen and brush colors"""
    painter.setPen(QColor(light_color).darker(120))
    painter.setBrush(QBrush(QColor(light_color)))


def get_file_language(filename, text=None):
    """Get file language from filename"""
    ext = osp.splitext(filename)[1]
    if ext.startswith("."):
        ext = ext[1:]  # file extension with leading dot
    language = ext
    if not ext:
        if text is None:
            text, _enc = encoding.read(filename)
        for line in text.splitlines():
            if not line.strip():
                continue
            if line.startswith("#!"):
                shebang = line[2:]
                if "python" in shebang:
                    language = "python"
            else:
                break
    return language


class PythonCodeEditor(TextEditBaseWidget):
    """Source Code Viewer Widget based exclusively on Qt

    It's a read only widget that highlights Python code.
    """

    LANGUAGES = {"Python": (sh.PythonSH, "#", PythonCFM)}

    TAB_ALWAYS_INDENTS = ("py", "pyw", "python", "c", "cpp", "cl", "h")

    # Custom signal to be emitted upon completion of the editor's paintEvent
    painted = Signal(QPaintEvent)

    # To have these attrs when early viewportEvent's are triggered
    edge_line = None
    linenumberarea = None

    get_completions = Signal(bool)
    go_to_definition = Signal(int)
    sig_show_object_info = Signal(int)
    go_to_definition_regex = Signal(int)
    sig_cursor_position_changed = Signal(int, int)
    focus_changed = Signal()
    sig_new_file = Signal(str)

    def __init__(self, parent=None):
        TextEditBaseWidget.__init__(self, parent)

        self.setFocusPolicy(Qt.StrongFocus)

        # We use these object names to set the right background
        # color when changing color schemes or creating new
        # Editor windows. This seems to be a Qt bug.
        # Fixes Issue 2028
        if sys.platform == "darwin":
            plugin_name = repr(parent)
            if "editor" in plugin_name.lower():
                self.setObjectName("editor")
            elif "help" in plugin_name.lower():
                self.setObjectName("help")
            elif "historylog" in plugin_name.lower():
                self.setObjectName("historylog")
            elif "configdialog" in plugin_name.lower():
                self.setObjectName("configdialog")

        # Caret (text cursor)
        self.setCursorWidth(CONF.get("main", "cursor/width"))

        # 79-col edge line
        self.edge_line_enabled = True
        self.edge_line = EdgeLine(self)

        # Blanks enabled
        self.blanks_enabled = False

        # Markers
        self.markers_margin = True
        self.markers_margin_width = 15

        # Line number area management
        self.linenumbers_margin = True
        self.linenumberarea_enabled = None
        self.linenumberarea = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_linenumberarea_width)
        self.updateRequest.connect(self.update_linenumberarea)
        self.linenumberarea_pressed = -1
        self.linenumberarea_released = -1

        # Colors to be defined in _apply_highlighter_color_scheme()
        # Currentcell color and current line color are defined in base.py
        self.occurrence_color = None
        self.ctrl_click_color = None
        self.sideareas_color = None
        self.matched_p_color = None
        self.unmatched_p_color = None
        self.normal_color = None
        self.comment_color = None

        self.linenumbers_color = QColor(Qt.darkGray)

        self.error_pixmap = (
            self.style()
            .standardIcon(QStyle.SP_MessageBoxCritical)
            .pixmap(QSize(14, 14))
        )
        self.warning_pixmap = (
            self.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(QSize(14, 14))
        )
        self.todo_pixmap = get_icon("todo").pixmap(QSize(14, 14))

        # --- Syntax highlight entrypoint ---
        #
        # - if set, self.highlighter is responsible for
        #   - coloring raw text data inside editor on load
        #   - coloring text data when editor is cloned
        #   - updating document highlight on line edits
        #   - providing color palette (scheme) for the editor
        #   - providing data for Outliner
        # - self.highlighter is not responsible for
        #   - background highlight for current line
        #   - background highlight for search / current line occurrences

        self.highlighter_class = sh.TextSH
        self.highlighter = None
        ccs = "Spyder"
        if ccs not in sh.COLOR_SCHEME_NAMES:
            ccs = sh.COLOR_SCHEME_NAMES[0]
        self.color_scheme = ccs

        self.highlight_current_line_enabled = False

        # Scrollbar flag area
        self.scrollflagarea_enabled = None
        self.scrollflagarea = ScrollFlagArea(self)
        self.scrollflagarea.hide()
        self.warning_color = "#FFAD07"
        self.error_color = "#EA2B0E"
        self.todo_color = "#B4D4F3"
        self.breakpoint_color = "#30E62E"

        self.update_linenumberarea_width()

        self.document_id = id(self)

        # Indicate occurrences of the selected word
        self.cursorPositionChanged.connect(self.__cursor_position_changed)
        self.__find_first_pos = None
        self.__find_flags = None

        self.supported_language = False
        self.supported_cell_language = False
        self.classfunc_match = None
        self.comment_string = None

        # Block user data
        self.blockuserdata_list = []

        # Mark occurrences timer
        self.occurrence_highlighting = None
        self.occurrence_timer = QTimer(self)
        self.occurrence_timer.setSingleShot(True)
        self.occurrence_timer.setInterval(1500)
        self.occurrence_timer.timeout.connect(self.__mark_occurrences)
        self.occurrences = []
        self.occurrence_color = QColor(Qt.yellow).lighter(160)

        # Mark found results
        self.textChanged.connect(self.__text_has_changed)
        self.found_results = []
        self.found_results_color = QColor(Qt.magenta).lighter(180)

        # Context menu
        self.gotodef_action = None
        self.setup_context_menu()

        # Tab key behavior
        self.tab_indents = None
        self.tab_mode = True  # see CodeEditor.set_tab_mode

        # Intelligent backspace mode
        self.intelligent_backspace = True

        self.go_to_definition_enabled = False
        self.close_parentheses_enabled = True
        self.close_quotes_enabled = False
        self.add_colons_enabled = True
        self.auto_unindent_enabled = True

        # Mouse tracking
        self.setMouseTracking(True)
        self.__cursor_changed = False
        self.ctrl_click_color = QColor(Qt.blue)

        # Keyboard shortcuts
        self.shortcuts = self.create_shortcuts()

        # Code editor
        self.__visible_blocks = []  # Visible blocks, update with repaint
        self.painted.connect(self._draw_editor_cell_divider)

        self.verticalScrollBar().valueChanged.connect(
            lambda value: self.rehighlight_cells()
        )

    def create_shortcuts(self):
        codecomp = config_shortcut(
            self.do_completion, context="Editor", name="Code Completion", parent=self
        )
        duplicate_line = config_shortcut(
            self.duplicate_line, context="Editor", name="Duplicate line", parent=self
        )
        copyline = config_shortcut(
            self.copy_line, context="Editor", name="Copy line", parent=self
        )
        deleteline = config_shortcut(
            self.delete_line, context="Editor", name="Delete line", parent=self
        )
        movelineup = config_shortcut(
            self.move_line_up, context="Editor", name="Move line up", parent=self
        )
        movelinedown = config_shortcut(
            self.move_line_down, context="Editor", name="Move line down", parent=self
        )
        gotonewline = config_shortcut(
            self.go_to_new_line, context="Editor", name="Go to new line", parent=self
        )
        gotodef = config_shortcut(
            self.do_go_to_definition,
            context="Editor",
            name="Go to definition",
            parent=self,
        )
        toggle_comment = config_shortcut(
            self.toggle_comment, context="Editor", name="Toggle comment", parent=self
        )
        blockcomment = config_shortcut(
            self.blockcomment, context="Editor", name="Blockcomment", parent=self
        )
        unblockcomment = config_shortcut(
            self.unblockcomment, context="Editor", name="Unblockcomment", parent=self
        )
        transform_uppercase = config_shortcut(
            self.transform_to_uppercase,
            context="Editor",
            name="Transform to uppercase",
            parent=self,
        )
        transform_lowercase = config_shortcut(
            self.transform_to_lowercase,
            context="Editor",
            name="Transform to lowercase",
            parent=self,
        )

        indent = config_shortcut(
            lambda: self.indent(force=True),
            context="Editor",
            name="Indent",
            parent=self,
        )
        unindent = config_shortcut(
            lambda: self.unindent(force=True),
            context="Editor",
            name="Unindent",
            parent=self,
        )

        def cb_maker(attr):
            """Make a callback for cursor move event type, (e.g. "Start")
            """

            def cursor_move_event():
                cursor = self.textCursor()
                move_type = getattr(QTextCursor, attr)
                cursor.movePosition(move_type)
                self.setTextCursor(cursor)

            return cursor_move_event

        line_start = config_shortcut(
            cb_maker("StartOfLine"), context="Editor", name="Start of line", parent=self
        )
        line_end = config_shortcut(
            cb_maker("EndOfLine"), context="Editor", name="End of line", parent=self
        )

        prev_line = config_shortcut(
            cb_maker("Up"), context="Editor", name="Previous line", parent=self
        )
        next_line = config_shortcut(
            cb_maker("Down"), context="Editor", name="Next line", parent=self
        )

        prev_char = config_shortcut(
            cb_maker("Left"), context="Editor", name="Previous char", parent=self
        )
        next_char = config_shortcut(
            cb_maker("Right"), context="Editor", name="Next char", parent=self
        )

        prev_word = config_shortcut(
            cb_maker("PreviousWord"),
            context="Editor",
            name="Previous word",
            parent=self,
        )
        next_word = config_shortcut(
            cb_maker("NextWord"), context="Editor", name="Next word", parent=self
        )

        start_doc = config_shortcut(
            cb_maker("Start"), context="Editor", name="Start of Document", parent=self
        )

        end_doc = config_shortcut(
            cb_maker("End"), context="Editor", name="End of document", parent=self
        )

        undo = config_shortcut(self.undo, context="Editor", name="undo", parent=self)
        redo = config_shortcut(self.redo, context="Editor", name="redo", parent=self)
        cut = config_shortcut(self.cut, context="Editor", name="cut", parent=self)
        copy = config_shortcut(self.copy, context="Editor", name="copy", parent=self)
        paste = config_shortcut(self.paste, context="Editor", name="paste", parent=self)
        delete = config_shortcut(
            self.delete, context="Editor", name="delete", parent=self
        )
        select_all = config_shortcut(
            self.selectAll, context="Editor", name="Select All", parent=self
        )
        array_inline = config_shortcut(
            lambda: self.enter_array_inline(),
            context="array_builder",
            name="enter array inline",
            parent=self,
        )
        array_table = config_shortcut(
            lambda: self.enter_array_table(),
            context="array_builder",
            name="enter array table",
            parent=self,
        )

        return [
            codecomp,
            duplicate_line,
            copyline,
            deleteline,
            movelineup,
            movelinedown,
            gotonewline,
            gotodef,
            toggle_comment,
            blockcomment,
            unblockcomment,
            transform_uppercase,
            transform_lowercase,
            line_start,
            line_end,
            prev_line,
            next_line,
            prev_char,
            next_char,
            prev_word,
            next_word,
            start_doc,
            end_doc,
            undo,
            redo,
            cut,
            copy,
            paste,
            delete,
            select_all,
            array_inline,
            array_table,
            indent,
            unindent,
        ]

    def get_shortcut_data(self):
        """
        Returns shortcut data, a list of tuples (shortcut, text, default)
        shortcut (QShortcut or QAction instance)
        text (string): action/shortcut description
        default (string): default key sequence
        """
        return [sc.data for sc in self.shortcuts]

    def closeEvent(self, event):
        """

        :param event:
        """
        TextEditBaseWidget.closeEvent(self, event)

    def get_document_id(self):
        """

        :return:
        """
        return self.document_id

    def set_as_clone(self, editor):
        """Set as clone editor"""
        self.setDocument(editor.document())
        self.document_id = editor.get_document_id()
        self.highlighter = editor.highlighter
        self.eol_chars = editor.eol_chars
        self._apply_highlighter_color_scheme()

    # -----Widget setup and options
    def toggle_wrap_mode(self, enable):
        """Enable/disable wrap mode"""
        self.set_wrap_mode("word" if enable else None)

    def setup_editor(
        self,
        linenumbers=True,
        language=None,
        markers=False,
        font=None,
        color_scheme=None,
        wrap=False,
        tab_mode=True,
        intelligent_backspace=True,
        highlight_current_line=True,
        highlight_current_cell=True,
        occurrence_highlighting=True,
        scrollflagarea=True,
        edge_line=True,
        edge_line_column=79,
        codecompletion_auto=False,
        codecompletion_case=True,
        codecompletion_enter=False,
        show_blanks=False,
        calltips=None,
        go_to_definition=False,
        close_parentheses=True,
        close_quotes=False,
        add_colons=True,
        auto_unindent=True,
        indent_chars=" " * 4,
        tab_stop_width_spaces=4,
        cloned_from=None,
        filename=None,
        occurrence_timeout=1500,
    ):

        # Code completion and calltips
        self.set_codecompletion_auto(codecompletion_auto)
        self.set_codecompletion_case(codecompletion_case)
        self.set_codecompletion_enter(codecompletion_enter)
        self.set_calltips(calltips)
        self.set_go_to_definition_enabled(go_to_definition)
        self.set_close_parentheses_enabled(close_parentheses)
        self.set_close_quotes_enabled(close_quotes)
        self.set_add_colons_enabled(add_colons)
        self.set_auto_unindent_enabled(auto_unindent)
        self.set_indent_chars(indent_chars)
        # Scrollbar flag area
        self.set_scrollflagarea_enabled(scrollflagarea)

        # Edge line
        self.set_edge_line_enabled(edge_line)
        self.set_edge_line_column(edge_line_column)

        # Blanks
        self.set_blanks_enabled(show_blanks)

        # Line number area
        if cloned_from:
            self.setFont(font)  # this is required for line numbers area
        self.setup_margins(linenumbers, markers)

        # Lexer
        self.set_language(language, filename)

        # Highlight current cell
        self.set_highlight_current_cell(highlight_current_cell)

        # Highlight current line
        self.set_highlight_current_line(highlight_current_line)

        # Occurrence highlighting
        self.set_occurrence_highlighting(occurrence_highlighting)
        self.set_occurrence_timeout(occurrence_timeout)

        # Tab always indents (even when cursor is not at the begin of line)
        self.set_tab_mode(tab_mode)

        # Intelligent backspace
        self.toggle_intelligent_backspace(intelligent_backspace)

        if cloned_from is not None:
            self.set_as_clone(cloned_from)
            self.update_linenumberarea_width()
        elif font is not None:
            self.set_font(font, color_scheme)
        elif color_scheme is not None:
            self.set_color_scheme(color_scheme)

        # Set tab spacing after font is set
        self.set_tab_stop_width_spaces(tab_stop_width_spaces)

        self.toggle_wrap_mode(wrap)

    def set_tab_mode(self, enable):
        """
        enabled = tab always indent
        (otherwise tab indents only when cursor is at the beginning of a line)
        """
        self.tab_mode = enable

    def toggle_intelligent_backspace(self, state):
        self.intelligent_backspace = state

    def set_go_to_definition_enabled(self, enable):
        """Enable/Disable go-to-definition feature, which is implemented in
        child class -> Editor widget"""
        self.go_to_definition_enabled = enable

    def set_close_parentheses_enabled(self, enable):
        """Enable/disable automatic parentheses insertion feature"""
        self.close_parentheses_enabled = enable

    def set_close_quotes_enabled(self, enable):
        """Enable/disable automatic quote insertion feature"""
        self.close_quotes_enabled = enable

    def set_add_colons_enabled(self, enable):
        """Enable/disable automatic colons insertion feature"""
        self.add_colons_enabled = enable

    def set_auto_unindent_enabled(self, enable):
        """Enable/disable automatic unindent after else/elif/finally/except"""
        self.auto_unindent_enabled = enable

    def set_occurrence_highlighting(self, enable):
        """Enable/disable occurrence highlighting"""
        self.occurrence_highlighting = enable
        if not enable:
            self.__clear_occurrences()

    def set_occurrence_timeout(self, timeout):
        """Set occurrence highlighting timeout (ms)"""
        self.occurrence_timer.setInterval(timeout)

    def set_highlight_current_line(self, enable):
        """Enable/disable current line highlighting"""
        self.highlight_current_line_enabled = enable
        if self.highlight_current_line_enabled:
            self.highlight_current_line()
        else:
            self.unhighlight_current_line()

    def set_highlight_current_cell(self, enable):
        """Enable/disable current line highlighting"""
        hl_cell_enable = enable and self.supported_cell_language
        self.highlight_current_cell_enabled = hl_cell_enable
        if self.highlight_current_cell_enabled:
            self.highlight_current_cell()
        else:
            self.unhighlight_current_cell()

    def set_language(self, language, filename=None):
        """

        :param language:
        :param filename:
        """
        self.tab_indents = language in self.TAB_ALWAYS_INDENTS
        self.comment_string = ""
        sh_class = sh.TextSH
        if language is not None:
            for (key, value) in ALL_LANGUAGES.items():
                if language.lower() in value:
                    self.supported_language = True
                    sh_class, comment_string, CFMatch = self.LANGUAGES[key]
                    self.comment_string = comment_string
                    if key in CELL_LANGUAGES:
                        self.supported_cell_language = True
                        self.cell_separators = CELL_LANGUAGES[key]
                    if CFMatch is None:
                        self.classfunc_match = None
                    else:
                        self.classfunc_match = CFMatch()
                    break
        self._set_highlighter(sh_class)

    def _set_highlighter(self, sh_class):
        self.highlighter_class = sh_class
        if self.highlighter is not None:
            # Removing old highlighter
            # TODO: test if leaving parent/document as is eats memory
            self.highlighter.setParent(None)
            self.highlighter.setDocument(None)
        self.highlighter = self.highlighter_class(
            self.document(), self.font(), self.color_scheme
        )
        self._apply_highlighter_color_scheme()

    def is_json(self):
        return (
            isinstance(self.highlighter, sh.PygmentsSH)
            and self.highlighter._lexer.name == "JSON"
        )

    def is_python(self):
        return self.highlighter_class is sh.PythonSH

    def is_cython(self):
        return self.highlighter_class is sh.CythonSH

    def is_enaml(self):
        return self.highlighter_class is sh.EnamlSH

    def is_python_like(self):
        return self.is_python() or self.is_cython() or self.is_enaml()

    def intelligent_tab(self):
        """Provide intelligent behavoir for Tab key press"""
        leading_text = self.get_text("sol", "cursor")
        if not leading_text.strip() or leading_text.endswith("#"):
            # blank line or start of comment
            self.indent_or_replace()
        elif self.in_comment_or_string() and not leading_text.endswith(" "):
            # in a word in a comment
            self.do_completion()
        elif leading_text.endswith("import ") or leading_text[-1] == ".":
            # blank import or dot completion
            self.do_completion()
        elif leading_text.split()[0] in ["from", "import"] and not ";" in leading_text:
            # import line with a single statement
            #  (prevents lines like: `import pdb; pdb.set_trace()`)
            self.do_completion()
        elif leading_text[-1] in "(," or leading_text.endswith(", "):
            self.indent_or_replace()
        elif leading_text.endswith(" "):
            # if the line ends with a space, indent
            self.indent_or_replace()
        elif re.search(r"[^\d\W]\w*\Z", leading_text, re.UNICODE):
            # if the line ends with a non-whitespace character
            self.do_completion()
        else:
            self.indent_or_replace()

    def intelligent_backtab(self):
        """Provide intelligent behavoir for Shift+Tab key press"""
        leading_text = self.get_text("sol", "cursor")
        if not leading_text.strip():
            # blank line
            self.unindent()
        elif self.in_comment_or_string():
            self.unindent()
        elif leading_text[-1] in "(," or leading_text.endswith(", "):
            position = self.get_position("cursor")
            self.show_object_info(position)
        else:
            # if the line ends with any other character but comma
            self.unindent()

    def rehighlight(self):
        """
        Rehighlight the whole document to rebuild outline explorer data
        and import statements data from scratch
        """
        if self.highlighter is not None:
            self.highlighter.rehighlight()
        if self.highlight_current_cell_enabled:
            self.highlight_current_cell()
        else:
            self.unhighlight_current_cell()
        if self.highlight_current_line_enabled:
            self.highlight_current_line()
        else:
            self.unhighlight_current_line()

    def rehighlight_cells(self):
        """Rehighlight cells when moving the scrollbar"""
        if self.highlight_current_cell_enabled:
            self.highlight_current_cell()

    def setup_margins(self, linenumbers=True, markers=True):
        """
        Setup margin settings
        (except font, now set in self.set_font)
        """
        self.linenumbers_margin = linenumbers
        self.markers_margin = markers
        self.set_linenumberarea_enabled(linenumbers or markers)

    def remove_trailing_spaces(self):
        """Remove trailing spaces"""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.Start)
        while True:
            cursor.movePosition(QTextCursor.EndOfBlock)
            text = str(cursor.block().text())
            length = len(text) - len(text.rstrip())
            if length > 0:
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, length)
                cursor.removeSelectedText()
            if cursor.atEnd():
                break
            cursor.movePosition(QTextCursor.NextBlock)
        cursor.endEditBlock()

    @Slot()
    def delete(self):
        """Remove selected text or next character."""
        if not self.has_selected_text():
            cursor = self.textCursor()
            position = cursor.position()
            if not cursor.atEnd():
                cursor.setPosition(position + 1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        self.remove_selected_text()

    # ------Find occurrences
    def __find_first(self, text):
        """Find first occurrence: scan whole document"""
        flags = QTextDocument.FindCaseSensitively | QTextDocument.FindWholeWords
        cursor = self.textCursor()
        # Scanning whole document
        cursor.movePosition(QTextCursor.Start)
        regexp = QRegExp(r"\b%s\b" % QRegExp.escape(text), Qt.CaseSensitive)
        cursor = self.document().find(regexp, cursor, flags)
        self.__find_first_pos = cursor.position()
        return cursor

    def __find_next(self, text, cursor):
        """Find next occurrence"""
        flags = QTextDocument.FindCaseSensitively | QTextDocument.FindWholeWords
        regexp = QRegExp(r"\b%s\b" % QRegExp.escape(text), Qt.CaseSensitive)
        cursor = self.document().find(regexp, cursor, flags)
        if cursor.position() != self.__find_first_pos:
            return cursor

    def __cursor_position_changed(self):
        """Cursor position has changed"""
        line, column = self.get_cursor_line_column()
        self.sig_cursor_position_changed.emit(line, column)
        if self.highlight_current_cell_enabled:
            self.highlight_current_cell()
        else:
            self.unhighlight_current_cell()
        if self.highlight_current_line_enabled:
            self.highlight_current_line()
        else:
            self.unhighlight_current_line()
        if self.occurrence_highlighting:
            self.occurrence_timer.stop()
            self.occurrence_timer.start()

    def __clear_occurrences(self):
        """Clear occurrence markers"""
        self.occurrences = []
        self.clear_extra_selections("occurrences")
        self.scrollflagarea.update()

    def __highlight_selection(
        self,
        key,
        cursor,
        foreground_color=None,
        background_color=None,
        underline_color=None,
        underline_style=QTextCharFormat.SpellCheckUnderline,
        update=False,
    ):
        extra_selections = self.get_extra_selections(key)
        selection = QTextEdit.ExtraSelection()
        if foreground_color is not None:
            selection.format.setForeground(foreground_color)
        if background_color is not None:
            selection.format.setBackground(background_color)
        if underline_color is not None:
            selection.format.setProperty(
                QTextFormat.TextUnderlineStyle, underline_style
            )
            selection.format.setProperty(
                QTextFormat.TextUnderlineColor, underline_color
            )
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = cursor
        extra_selections.append(selection)
        self.set_extra_selections(key, extra_selections)
        if update:
            self.update_extra_selections()

    def __mark_occurrences(self):
        """Marking occurrences of the currently selected word"""
        self.__clear_occurrences()

        if not self.supported_language:
            return

        text = self.get_current_word()
        if text is None:
            return
        if self.has_selected_text() and self.get_selected_text() != text:
            return

        if keyword.iskeyword(str(text)) or str(text) == "self":
            return

        # Highlighting all occurrences of word *text*
        cursor = self.__find_first(text)
        self.occurrences = []
        while cursor:
            self.occurrences.append(cursor.blockNumber())
            self.__highlight_selection(
                "occurrences", cursor, background_color=self.occurrence_color
            )
            cursor = self.__find_next(text, cursor)
        self.update_extra_selections()
        if len(self.occurrences) > 1 and self.occurrences[-1] == 0:
            # XXX: this is never happening with PySide but it's necessary
            # for PyQt4... this must be related to a different behavior for
            # the QTextDocument.find function between those two libraries
            self.occurrences.pop(-1)
        self.scrollflagarea.update()

    # -----highlight found results (find/replace widget)
    def highlight_found_results(self, pattern, words=False, regexp=False):
        """Highlight all found patterns"""
        pattern = str(pattern)
        if not pattern:
            return
        if not regexp:
            pattern = re.escape(str(pattern))
        pattern = r"\b%s\b" % pattern if words else pattern
        text = str(self.toPlainText())
        try:
            regobj = re.compile(pattern)
        except sre_constants.error:
            return
        extra_selections = []
        self.found_results = []
        for match in regobj.finditer(text):
            pos1, pos2 = match.span()
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(self.found_results_color)
            selection.cursor = self.textCursor()
            selection.cursor.setPosition(pos1)
            self.found_results.append(selection.cursor.blockNumber())
            selection.cursor.setPosition(pos2, QTextCursor.KeepAnchor)
            extra_selections.append(selection)
        self.set_extra_selections("find", extra_selections)
        self.update_extra_selections()

    def clear_found_results(self):
        """Clear found results highlighting"""
        self.found_results = []
        self.clear_extra_selections("find")
        self.scrollflagarea.update()

    def __text_has_changed(self):
        """Text has changed, eventually clear found results highlighting"""
        if self.found_results:
            self.clear_found_results()

    # -----markers
    def get_markers_margin(self):
        """

        :return:
        """
        if self.markers_margin:
            return self.markers_margin_width
        else:
            return 0

    # -----linenumberarea
    def set_linenumberarea_enabled(self, state):
        """

        :param state:
        """
        self.linenumberarea_enabled = state
        self.linenumberarea.setVisible(state)
        self.update_linenumberarea_width()

    def get_linenumberarea_width(self):
        """Return current line number area width"""
        return self.linenumberarea.contentsRect().width()

    def compute_linenumberarea_width(self):
        """Compute and return line number area width"""
        if not self.linenumberarea_enabled:
            return 0
        digits = 1
        maxb = max(1, self.blockCount())
        while maxb >= 10:
            maxb /= 10
            digits += 1
        if self.linenumbers_margin:
            linenumbers_margin = 3 + self.fontMetrics().width("9" * digits)
        else:
            linenumbers_margin = 0
        return linenumbers_margin + self.get_markers_margin()

    def update_linenumberarea_width(self, new_block_count=None):
        """
        Update line number area width.

        new_block_count is needed to handle blockCountChanged(int) signal
        """
        self.setViewportMargins(
            self.compute_linenumberarea_width(), 0, self.get_scrollflagarea_width(), 0
        )

    def update_linenumberarea(self, qrect, dy):
        """Update line number area"""
        if dy:
            self.linenumberarea.scroll(0, dy)
        else:
            self.linenumberarea.update(
                0, qrect.y(), self.linenumberarea.width(), qrect.height()
            )
        if qrect.contains(self.viewport().rect()):
            self.update_linenumberarea_width()

    def linenumberarea_paint_event(self, event):
        """Painting line number area"""
        painter = QPainter(self.linenumberarea)
        painter.fillRect(event.rect(), self.sideareas_color)
        # This is needed to make that the font size of line numbers
        # be the same as the text one when zooming
        # See Issues 2296 and 4811
        font = self.font()
        font_height = self.fontMetrics().height()

        active_block = self.textCursor().block()
        active_line_number = active_block.blockNumber() + 1

        def draw_pixmap(ytop, pixmap):
            """

            :param ytop:
            :param pixmap:
            """
            pixmap_height = pixmap.height() / pixmap.devicePixelRatio()
            painter.drawPixmap(0, ytop + (font_height - pixmap_height) / 2, pixmap)

        for top, line_number, block in self.visible_blocks:
            if self.linenumbers_margin:
                if line_number == active_line_number:
                    font.setWeight(font.Bold)
                    painter.setFont(font)
                    painter.setPen(self.normal_color)
                else:
                    font.setWeight(font.Normal)
                    painter.setFont(font)
                    painter.setPen(self.linenumbers_color)

                painter.drawText(
                    0,
                    top,
                    self.linenumberarea.width(),
                    font_height,
                    Qt.AlignRight | Qt.AlignBottom,
                    str(line_number),
                )

            data = block.userData()
            if self.markers_margin and data:
                if data.code_analysis:
                    for _message, error in data.code_analysis:
                        if error:
                            break
                    if error:
                        draw_pixmap(top, self.error_pixmap)
                    else:
                        draw_pixmap(top, self.warning_pixmap)
                if data.todo:
                    draw_pixmap(top, self.todo_pixmap)
                if data.breakpoint:
                    if data.breakpoint_condition is None:
                        draw_pixmap(top, self.bp_pixmap)
                    else:
                        draw_pixmap(top, self.bpc_pixmap)

    def __get_linenumber_from_mouse_event(self, event):
        """Return line number from mouse event"""
        block = self.firstVisibleBlock()
        line_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top < event.pos().y():
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            line_number += 1

        return line_number

    def linenumberarea_mousemove_event(self, event):
        """Handling line number area mouse move event"""
        line_number = self.__get_linenumber_from_mouse_event(event)
        block = self.document().findBlockByNumber(line_number - 1)
        data = block.userData()

        # this disables pyflakes messages if there is an active drag/selection
        # operation
        check = self.linenumberarea_released == -1
        if data and data.code_analysis and check:
            self.__show_code_analysis_results(line_number, data.code_analysis)

        if event.buttons() == Qt.LeftButton:
            self.linenumberarea_released = line_number
            self.linenumberarea_select_lines(
                self.linenumberarea_pressed, self.linenumberarea_released
            )

    def linenumberarea_mousedoubleclick_event(self, event):
        """Handling line number area mouse double-click event"""
        line_number = self.__get_linenumber_from_mouse_event(event)
        shift = event.modifiers() & Qt.ShiftModifier

    def linenumberarea_mousepress_event(self, event):
        """Handling line number area mouse double press event"""
        line_number = self.__get_linenumber_from_mouse_event(event)
        self.linenumberarea_pressed = line_number
        self.linenumberarea_released = line_number
        self.linenumberarea_select_lines(
            self.linenumberarea_pressed, self.linenumberarea_released
        )

    def linenumberarea_mouserelease_event(self, event):
        """Handling line number area mouse release event"""
        self.linenumberarea_released = -1
        self.linenumberarea_pressed = -1

    def linenumberarea_select_lines(self, linenumber_pressed, linenumber_released):
        """Select line(s) after a mouse press/mouse press drag event"""
        find_block_by_line_number = self.document().findBlockByLineNumber
        move_n_blocks = linenumber_released - linenumber_pressed
        start_line = linenumber_pressed
        start_block = find_block_by_line_number(start_line - 1)

        cursor = self.textCursor()
        cursor.setPosition(start_block.position())

        # Select/drag downwards
        if move_n_blocks > 0:
            for n in range(abs(move_n_blocks) + 1):
                cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor)
        # Select/drag upwards or select single line
        else:
            cursor.movePosition(cursor.NextBlock)
            for n in range(abs(move_n_blocks) + 1):
                cursor.movePosition(cursor.PreviousBlock, cursor.KeepAnchor)

        # Account for last line case
        if linenumber_released == self.blockCount():
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
        else:
            cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)

        self.setTextCursor(cursor)

    # -----Code introspection
    def do_completion(self, automatic=False):
        """Trigger completion"""
        if not self.is_completion_widget_visible():
            self.get_completions.emit(automatic)

    def do_go_to_definition(self):
        """Trigger go-to-definition"""
        if not self.in_comment_or_string():
            self.go_to_definition.emit(self.textCursor().position())

    def show_object_info(self, position):
        """Trigger a calltip"""
        self.sig_show_object_info.emit(position)

    # -----edge line
    def set_edge_line_enabled(self, state):
        """Toggle edge line visibility"""
        self.edge_line_enabled = state
        self.edge_line.setVisible(state)

    def set_edge_line_column(self, column):
        """Set edge line column value"""
        self.edge_line.column = column
        self.edge_line.update()

    # -----blank spaces
    def set_blanks_enabled(self, state):
        """Toggle blanks visibility"""
        self.blanks_enabled = state
        option = self.document().defaultTextOption()
        option.setFlags(
            option.flags() | QTextOption.AddSpaceForLineAndParagraphSeparators
        )
        if self.blanks_enabled:
            option.setFlags(option.flags() | QTextOption.ShowTabsAndSpaces)
        else:
            option.setFlags(option.flags() & ~QTextOption.ShowTabsAndSpaces)
        self.document().setDefaultTextOption(option)
        # Rehighlight to make the spaces less apparent.
        self.rehighlight()

    # -----scrollflagarea
    def set_scrollflagarea_enabled(self, state):
        """Toggle scroll flag area visibility"""
        self.scrollflagarea_enabled = state
        self.scrollflagarea.setVisible(state)
        self.update_linenumberarea_width()

    def get_scrollflagarea_width(self):
        """Return scroll flag area width"""
        if self.scrollflagarea_enabled:
            return ScrollFlagArea.WIDTH
        else:
            return 0

    def scrollflagarea_paint_event(self, event):
        """Painting the scroll flag area"""
        make_flag = self.scrollflagarea.make_flag_qrect
        make_slider = self.scrollflagarea.make_slider_range

        # Filling the whole painting area
        painter = QPainter(self.scrollflagarea)
        painter.fillRect(event.rect(), self.sideareas_color)
        block = self.document().firstBlock()

        # Painting warnings and todos
        for line_number in range(1, self.document().blockCount() + 1):
            data = block.userData()
            if data:
                position = self.scrollflagarea.value_to_position(line_number)
                if data.code_analysis:
                    # Warnings
                    color = self.warning_color
                    for _message, error in data.code_analysis:
                        if error:
                            color = self.error_color
                            break
                    set_scrollflagarea_painter(painter, color)
                    painter.drawRect(make_flag(position))
                if data.todo:
                    # TODOs
                    set_scrollflagarea_painter(painter, self.todo_color)
                    painter.drawRect(make_flag(position))
            block = block.next()

        # Occurrences
        if self.occurrences:
            set_scrollflagarea_painter(painter, self.occurrence_color)
            for line_number in self.occurrences:
                position = self.scrollflagarea.value_to_position(line_number)
                painter.drawRect(make_flag(position))

        # Found results
        if self.found_results:
            set_scrollflagarea_painter(painter, self.found_results_color)
            for line_number in self.found_results:
                position = self.scrollflagarea.value_to_position(line_number)
                painter.drawRect(make_flag(position))

        # Painting the slider range
        pen_color = QColor(Qt.white)
        pen_color.setAlphaF(0.8)
        painter.setPen(pen_color)
        brush_color = QColor(Qt.white)
        brush_color.setAlphaF(0.5)
        painter.setBrush(QBrush(brush_color))
        painter.drawRect(make_slider(self.firstVisibleBlock().blockNumber()))

    def resizeEvent(self, event):
        """Reimplemented Qt method to handle line number area resizing"""
        TextEditBaseWidget.resizeEvent(self, event)
        cr = self.contentsRect()
        self.linenumberarea.setGeometry(
            QRect(cr.left(), cr.top(), self.compute_linenumberarea_width(), cr.height())
        )
        self.__set_scrollflagarea_geometry(cr)

    def __set_scrollflagarea_geometry(self, contentrect):
        """Set scroll flag area geometry"""
        cr = contentrect
        if self.verticalScrollBar().isVisible():
            vsbw = self.verticalScrollBar().contentsRect().width()
        else:
            vsbw = 0
        _left, _top, right, _bottom = self.getContentsMargins()
        if right > vsbw:
            # Depending on the platform (e.g. on Ubuntu), the scrollbar sizes
            # may be taken into account in the contents margins whereas it is
            # not on Windows for example
            vsbw = 0
        self.scrollflagarea.setGeometry(
            QRect(
                cr.right() - ScrollFlagArea.WIDTH - vsbw,
                cr.top(),
                self.scrollflagarea.WIDTH,
                cr.height(),
            )
        )

    # -----edgeline
    def viewportEvent(self, event):
        """Override Qt method"""
        # 79-column edge line
        offset = self.contentOffset()
        x = (
            self.blockBoundingGeometry(self.firstVisibleBlock())
            .translated(offset.x(), offset.y())
            .left()
            + self.get_linenumberarea_width()
            + self.fontMetrics().width("9" * self.edge_line.column)
            + 5
        )
        cr = self.contentsRect()
        self.edge_line.setGeometry(QRect(x, cr.top(), 1, cr.bottom()))
        self.__set_scrollflagarea_geometry(cr)
        return TextEditBaseWidget.viewportEvent(self, event)

    # -----Misc.
    def _apply_highlighter_color_scheme(self):
        """Apply color scheme from syntax highlighter to the editor"""
        hl = self.highlighter
        if hl is not None:
            self.set_palette(
                background=hl.get_background_color(),
                foreground=hl.get_foreground_color(),
            )
            self.currentline_color = hl.get_currentline_color()
            self.currentcell_color = hl.get_currentcell_color()
            self.occurrence_color = hl.get_occurrence_color()
            self.ctrl_click_color = hl.get_ctrlclick_color()
            self.sideareas_color = hl.get_sideareas_color()
            self.comment_color = hl.get_comment_color()
            self.normal_color = hl.get_foreground_color()
            self.matched_p_color = hl.get_matched_p_color()
            self.unmatched_p_color = hl.get_unmatched_p_color()

    def apply_highlighter_settings(self, color_scheme=None):
        """Apply syntax highlighter settings"""
        if self.highlighter is not None:
            # Updating highlighter settings (font and color scheme)
            self.highlighter.setup_formats(self.font())
            if color_scheme is not None:
                self.set_color_scheme(color_scheme)
            else:
                self.highlighter.rehighlight()

    def get_outlineexplorer_data(self):
        """Get data provided by the Outline Explorer"""
        return self.highlighter.get_outlineexplorer_data()

    def set_font(self, font, color_scheme=None):
        """Set font"""
        # Note: why using this method to set color scheme instead of
        #       'set_color_scheme'? To avoid rehighlighting the document twice
        #       at startup.
        if color_scheme is not None:
            self.color_scheme = color_scheme
        self.setFont(font)
        self.update_linenumberarea_width()
        self.apply_highlighter_settings(color_scheme)

    def set_color_scheme(self, color_scheme):
        """Set color scheme for syntax highlighting"""
        self.color_scheme = color_scheme
        if self.highlighter is not None:
            # this calls self.highlighter.rehighlight()
            self.highlighter.set_color_scheme(color_scheme)
            self._apply_highlighter_color_scheme()
        if self.highlight_current_cell_enabled:
            self.highlight_current_cell()
        else:
            self.unhighlight_current_cell()
        if self.highlight_current_line_enabled:
            self.highlight_current_line()
        else:
            self.unhighlight_current_line()

    def set_text(self, text):
        """Set the text of the editor"""
        self.setPlainText(text)
        self.set_eol_chars(text)

    def set_text_from_file(self, filename, language=None):
        """Set the text of the editor from file *fname*"""
        text, _enc = encoding.read(filename)
        if language is None:
            language = get_file_language(filename, text)
        self.set_language(language, filename)
        self.set_text(text)

    def append(self, text):
        """Append text to the end of the text widget"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)

    @Slot()
    def paste(self):
        """
        Reimplement QPlainTextEdit's method to fix the following issue:
        on Windows, pasted text has only 'LF' EOL chars even if the original
        text has 'CRLF' EOL chars
        """
        clipboard = QApplication.clipboard()
        text = str(clipboard.text())
        if len(text.splitlines()) > 1:
            eol_chars = self.get_line_separator()
            clipboard.setText(eol_chars.join((text + eol_chars).splitlines()))
        # Standard paste
        TextEditBaseWidget.paste(self)

    def get_block_data(self, block):
        """Return block data (from syntax highlighter)"""
        return self.highlighter.block_data.get(block)

    def get_fold_level(self, block_nb):
        """Is it a fold header line?
        If so, return fold level
        If not, return None"""
        block = self.document().findBlockByNumber(block_nb)
        return self.get_block_data(block).fold_level

    # ===============================================================================
    #    High-level editor features
    # ===============================================================================
    @Slot()
    def center_cursor_on_next_focus(self):
        """QPlainTextEdit's "centerCursor" requires the widget to be visible"""
        self.centerCursor()
        self.focus_in.disconnect(self.center_cursor_on_next_focus)

    def go_to_line(self, line, word=""):
        """Go to line number *line* and eventually highlight it"""
        line = min(line, self.get_line_count())
        block = self.document().findBlockByNumber(line - 1)
        self.setTextCursor(QTextCursor(block))
        if self.isVisible():
            self.centerCursor()
        else:
            self.focus_in.connect(self.center_cursor_on_next_focus)
        self.horizontalScrollBar().setValue(0)
        if word and str(word) in str(block.text()):
            self.find(word, QTextDocument.FindCaseSensitively)

    def cleanup_code_analysis(self):
        """Remove all code analysis markers"""
        self.setUpdatesEnabled(False)
        self.clear_extra_selections("code_analysis")
        for data in self.blockuserdata_list[:]:
            data.code_analysis = []
            if data.is_empty():
                del data
        self.setUpdatesEnabled(True)
        # When the new code analysis results are empty, it is necessary
        # to update manually the scrollflag and linenumber areas (otherwise,
        # the old flags will still be displayed):
        self.scrollflagarea.update()
        self.linenumberarea.update()

    def process_code_analysis(self, check_results):
        """Analyze filename code with pyflakes"""
        self.cleanup_code_analysis()
        if check_results is None:
            # Not able to compile module
            return
        self.setUpdatesEnabled(False)
        cursor = self.textCursor()
        document = self.document()
        flags = QTextDocument.FindCaseSensitively | QTextDocument.FindWholeWords
        for message, line_number in check_results:
            error = "syntax" in message
            # Note: line_number start from 1 (not 0)
            block = self.document().findBlockByNumber(line_number - 1)
            data = block.userData()
            if not data:
                data = BlockUserData(self)
            data.code_analysis.append((message, error))
            block.setUserData(data)
            refs = re.findall(r"\'[a-zA-Z0-9_]*\'", message)
            for ref in refs:
                # Highlighting found references
                text = ref[1:-1]

                # Scanning line number *line* and following lines if continued
                def is_line_splitted(line_no):
                    text = str(document.findBlockByNumber(line_no).text())
                    stripped = text.strip()
                    return (
                        stripped.endswith("\\")
                        or stripped.endswith(",")
                        or len(stripped) == 0
                    )

                line2 = line_number - 1
                while line2 < self.blockCount() - 1 and is_line_splitted(line2):
                    line2 += 1
                cursor.setPosition(block.position())
                cursor.movePosition(QTextCursor.StartOfBlock)
                regexp = QRegExp(r"\b%s\b" % QRegExp.escape(text), Qt.CaseSensitive)
                color = self.error_color if error else self.warning_color
                # Highlighting all occurrences (this is a compromise as pyflakes
                # do not provide the column number -- see Issue 709 on Spyder's
                # GoogleCode project website)
                cursor = document.find(regexp, cursor, flags)
                if cursor:
                    while (
                        cursor
                        and cursor.blockNumber() <= line2
                        and cursor.blockNumber() >= line_number - 1
                        and cursor.position() > 0
                    ):
                        self.__highlight_selection(
                            "code_analysis", cursor, underline_color=QColor(color)
                        )
                        cursor = document.find(text, cursor, flags)
        self.update_extra_selections()
        self.setUpdatesEnabled(True)
        self.linenumberarea.update()

    def __show_code_analysis_results(self, line_number, code_analysis):
        """Show warning/error messages"""
        msglist = [msg for msg, _error in code_analysis]
        self.show_calltip(
            _("Code analysis"), msglist, color="#129625", at_line=line_number
        )

    def go_to_next_warning(self):
        """Go to next code analysis warning message
        and return new cursor position"""
        block = self.textCursor().block()
        line_count = self.document().blockCount()
        while True:
            if block.blockNumber() + 1 < line_count:
                block = block.next()
            else:
                block = self.document().firstBlock()
            data = block.userData()
            if data and data.code_analysis:
                break
        line_number = block.blockNumber() + 1
        self.go_to_line(line_number)
        self.__show_code_analysis_results(line_number, data.code_analysis)
        return self.get_position("cursor")

    def go_to_previous_warning(self):
        """Go to previous code analysis warning message
        and return new cursor position"""
        block = self.textCursor().block()
        while True:
            if block.blockNumber() > 0:
                block = block.previous()
            else:
                block = self.document().lastBlock()
            data = block.userData()
            if data and data.code_analysis:
                break
        line_number = block.blockNumber() + 1
        self.go_to_line(line_number)
        self.__show_code_analysis_results(line_number, data.code_analysis)
        return self.get_position("cursor")

    # ------Tasks management
    def go_to_next_todo(self):
        """Go to next todo and return new cursor position"""
        block = self.textCursor().block()
        line_count = self.document().blockCount()
        while True:
            if block.blockNumber() + 1 < line_count:
                block = block.next()
            else:
                block = self.document().firstBlock()
            data = block.userData()
            if data and data.todo:
                break
        line_number = block.blockNumber() + 1
        self.go_to_line(line_number)
        self.show_calltip(_("To do"), data.todo, color="#3096FC", at_line=line_number)
        return self.get_position("cursor")

    def process_todo(self, todo_results):
        """Process todo finder results"""
        for data in self.blockuserdata_list[:]:
            data.todo = ""
            if data.is_empty():
                del data
        for message, line_number in todo_results:
            block = self.document().findBlockByNumber(line_number - 1)
            data = block.userData()
            if not data:
                data = BlockUserData(self)
            data.todo = message
            block.setUserData(data)
        self.scrollflagarea.update()

    # ------Comments/Indentation
    def add_prefix(self, prefix):
        """Add prefix to current line or selected line(s)"""
        cursor = self.textCursor()
        if self.has_selected_text():
            # Add prefix to selected line(s)
            start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()

            # Let's see if selection begins at a block start
            first_pos = min([start_pos, end_pos])
            first_cursor = self.textCursor()
            first_cursor.setPosition(first_pos)
            begins_at_block_start = first_cursor.atBlockStart()

            cursor.beginEditBlock()
            cursor.setPosition(end_pos)
            # Check if end_pos is at the start of a block: if so, starting
            # changes from the previous block
            if cursor.atBlockStart():
                cursor.movePosition(QTextCursor.PreviousBlock)
                if cursor.position() < start_pos:
                    cursor.setPosition(start_pos)

            while cursor.position() >= start_pos:
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.insertText(prefix)
                if start_pos == 0 and cursor.blockNumber() == 0:
                    # Avoid infinite loop when indenting the very first line
                    break
                cursor.movePosition(QTextCursor.PreviousBlock)
                cursor.movePosition(QTextCursor.EndOfBlock)
            cursor.endEditBlock()
            if begins_at_block_start:
                # Extending selection to prefix:
                cursor = self.textCursor()
                start_pos = cursor.selectionStart()
                end_pos = cursor.selectionEnd()
                if start_pos < end_pos:
                    start_pos -= len(prefix)
                else:
                    end_pos -= len(prefix)
                cursor.setPosition(start_pos, QTextCursor.MoveAnchor)
                cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
        else:
            # Add prefix to current line
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.insertText(prefix)
            cursor.endEditBlock()

    def __is_cursor_at_start_of_block(self, cursor):
        cursor.movePosition(QTextCursor.StartOfBlock)

    def remove_suffix(self, suffix):
        """
        Remove suffix from current line (there should not be any selection)
        """
        cursor = self.textCursor()
        cursor.setPosition(cursor.position() - len(suffix), QTextCursor.KeepAnchor)
        if str(cursor.selectedText()) == suffix:
            cursor.removeSelectedText()

    def remove_prefix(self, prefix):
        """Remove prefix from current line or selected line(s)"""
        cursor = self.textCursor()
        if self.has_selected_text():
            # Remove prefix from selected line(s)
            start_pos, end_pos = sorted(
                [cursor.selectionStart(), cursor.selectionEnd()]
            )
            cursor.setPosition(start_pos)
            if not cursor.atBlockStart():
                cursor.movePosition(QTextCursor.StartOfBlock)
                start_pos = cursor.position()
            cursor.beginEditBlock()
            cursor.setPosition(end_pos)
            # Check if end_pos is at the start of a block: if so, starting
            # changes from the previous block
            if cursor.atBlockStart():
                cursor.movePosition(QTextCursor.PreviousBlock)
                if cursor.position() < start_pos:
                    cursor.setPosition(start_pos)

            cursor.movePosition(QTextCursor.StartOfBlock)
            old_pos = None
            while cursor.position() >= start_pos:
                new_pos = cursor.position()
                if old_pos == new_pos:
                    break
                else:
                    old_pos = new_pos
                line_text = str(cursor.block().text())
                if (
                    prefix.strip()
                    and line_text.lstrip().startswith(prefix)
                    or line_text.startswith(prefix)
                ):
                    cursor.movePosition(
                        QTextCursor.Right,
                        QTextCursor.MoveAnchor,
                        line_text.find(prefix),
                    )
                    cursor.movePosition(
                        QTextCursor.Right, QTextCursor.KeepAnchor, len(prefix)
                    )
                    cursor.removeSelectedText()
                cursor.movePosition(QTextCursor.PreviousBlock)
            cursor.endEditBlock()
        else:
            # Remove prefix from current line
            cursor.movePosition(QTextCursor.StartOfBlock)
            line_text = str(cursor.block().text())
            if (
                prefix.strip()
                and line_text.lstrip().startswith(prefix)
                or line_text.startswith(prefix)
            ):
                cursor.movePosition(
                    QTextCursor.Right, QTextCursor.MoveAnchor, line_text.find(prefix)
                )
                cursor.movePosition(
                    QTextCursor.Right, QTextCursor.KeepAnchor, len(prefix)
                )
                cursor.removeSelectedText()

    def fix_indent(self, *args, **kwargs):
        """Indent line according to the preferences"""
        if self.is_python_like():
            return self.fix_indent_smart(*args, **kwargs)
        else:
            return self.simple_indentation(*args, **kwargs)

    def simple_indentation(self, forward=True, **kwargs):
        """
        Simply preserve the indentation-level of the previous line.
        """
        cursor = self.textCursor()
        block_nb = cursor.blockNumber()
        prev_block = self.document().findBlockByLineNumber(block_nb - 1)
        prevline = str(prev_block.text())

        indentation = re.match(r"\s*", prevline).group()
        # Unident
        if not forward:
            indentation = indentation[len(self.indent_chars) :]

        cursor.insertText(indentation)
        return False  # simple indentation don't fix indentation

    def fix_indent_smart(self, forward=True, comment_or_string=False):
        """
        Fix indentation (Python only, no text selection)
        forward=True: fix indent only if text is not enough indented
                      (otherwise force indent)
        forward=False: fix indent only if text is too much indented
                       (otherwise force unindent)

        Returns True if indent needed to be fixed
        """
        cursor = self.textCursor()
        block_nb = cursor.blockNumber()
        # find the line that contains our scope
        diff_paren = 0
        diff_brack = 0
        diff_curly = 0
        add_indent = False
        prevline = None
        prevtext = ""
        for prevline in range(block_nb - 1, -1, -1):
            cursor.movePosition(QTextCursor.PreviousBlock)
            prevtext = str(cursor.block().text()).rstrip()

            # Remove inline comment
            inline_comment = prevtext.find("#")
            if inline_comment != -1:
                prevtext = prevtext[:inline_comment]

            if (
                self.is_python_like()
                and not prevtext.strip().startswith("#")
                and prevtext
            ) or prevtext:

                if not "return" in prevtext.strip().split()[:1] and (
                    prevtext.strip().endswith(")")
                    or prevtext.strip().endswith("]")
                    or prevtext.strip().endswith("}")
                ):

                    comment_or_string = True  # prevent further parsing

                elif prevtext.strip().endswith(":") and self.is_python_like():
                    add_indent = True
                    comment_or_string = True
                if prevtext.count(")") > prevtext.count("("):
                    diff_paren = prevtext.count(")") - prevtext.count("(")
                elif prevtext.count("]") > prevtext.count("["):
                    diff_brack = prevtext.count("]") - prevtext.count("[")
                elif prevtext.count("}") > prevtext.count("{"):
                    diff_curly = prevtext.count("}") - prevtext.count("{")
                elif diff_paren or diff_brack or diff_curly:
                    diff_paren += prevtext.count(")") - prevtext.count("(")
                    diff_brack += prevtext.count("]") - prevtext.count("[")
                    diff_curly += prevtext.count("}") - prevtext.count("{")
                    if not (diff_paren or diff_brack or diff_curly):
                        break
                else:
                    break

        if prevline:
            correct_indent = self.get_block_indentation(prevline)
        else:
            correct_indent = 0

        indent = self.get_block_indentation(block_nb)

        if add_indent:
            if self.indent_chars == "\t":
                correct_indent += self.tab_stop_width_spaces
            else:
                correct_indent += len(self.indent_chars)

        if not comment_or_string:
            if prevtext.endswith(":") and self.is_python_like():
                # Indent
                if self.indent_chars == "\t":
                    correct_indent += self.tab_stop_width_spaces
                else:
                    correct_indent += len(self.indent_chars)
            elif self.is_python_like() and (
                prevtext.endswith("continue")
                or prevtext.endswith("break")
                or prevtext.endswith("pass")
                or (
                    "return" in prevtext.strip().split()[:1]
                    and len(re.split(r"\(|\{|\[", prevtext))
                    == len(re.split(r"\)|\}|\]", prevtext))
                )
            ):
                # Unindent
                if self.indent_chars == "\t":
                    correct_indent -= self.tab_stop_width_spaces
                else:
                    correct_indent -= len(self.indent_chars)
            elif len(re.split(r"\(|\{|\[", prevtext)) > 1:

                # Check if all braces are matching using a stack
                stack = ["dummy"]  # Dummy elemet to avoid index errors
                deactivate = None
                for c in prevtext:
                    if deactivate is not None:
                        if c == deactivate:
                            deactivate = None
                    elif c in ["'", '"']:
                        deactivate = c
                    elif c in ["(", "[", "{"]:
                        stack.append(c)
                    elif c == ")" and stack[-1] == "(":
                        stack.pop()
                    elif c == "]" and stack[-1] == "[":
                        stack.pop()
                    elif c == "}" and stack[-1] == "{":
                        stack.pop()

                if len(stack) == 1:  # all braces matching
                    pass

                # Hanging indent
                # find out if the last one is (, {, or []})
                # only if prevtext is long that the hanging indentation
                elif re.search(r"[\(|\{|\[]\s*$", prevtext) is not None and (
                    (
                        self.indent_chars == "\t"
                        and self.tab_stop_width_spaces * 2 < len(prevtext)
                    )
                    or (
                        self.indent_chars.startswith(" ")
                        and len(self.indent_chars) * 2 < len(prevtext)
                    )
                ):
                    if self.indent_chars == "\t":
                        correct_indent += self.tab_stop_width_spaces * 2
                    else:
                        correct_indent += len(self.indent_chars) * 2
                else:
                    rlmap = {")": "(", "]": "[", "}": "{"}
                    for par in rlmap:
                        i_right = prevtext.rfind(par)
                        if i_right != -1:
                            prevtext = prevtext[:i_right]
                            for _i in range(len(prevtext.split(par))):
                                i_left = prevtext.rfind(rlmap[par])
                                if i_left != -1:
                                    prevtext = prevtext[:i_left]
                                else:
                                    break
                    else:
                        if prevtext.strip():
                            if len(re.split(r"\(|\{|\[", prevtext)) > 1:
                                # correct indent only if there are still opening brackets
                                prevexpr = re.split(r"\(|\{|\[", prevtext)[-1]
                                correct_indent = len(prevtext) - len(prevexpr)
                            else:
                                correct_indent = len(prevtext)

        if (
            not (diff_paren or diff_brack or diff_curly)
            and not prevtext.endswith(":")
            and prevline
        ):
            cur_indent = self.get_block_indentation(block_nb - 1)
            is_blank = not self.get_text_line(block_nb - 1).strip()
            prevline_indent = self.get_block_indentation(prevline)
            trailing_text = self.get_text_line(block_nb).strip()

            if cur_indent < prevline_indent and (trailing_text or is_blank):
                if cur_indent % len(self.indent_chars) == 0:
                    correct_indent = cur_indent
                else:
                    correct_indent = cur_indent + (
                        len(self.indent_chars) - cur_indent % len(self.indent_chars)
                    )

        if (forward and indent >= correct_indent) or (
            not forward and indent <= correct_indent
        ):
            # No indentation fix is necessary
            return False

        if correct_indent >= 0:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfBlock)
            if self.indent_chars == "\t":
                indent = indent // self.tab_stop_width_spaces
            cursor.setPosition(cursor.position() + indent, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            if self.indent_chars == "\t":
                indent_text = "\t" * (
                    correct_indent // self.tab_stop_width_spaces
                ) + " " * (correct_indent % self.tab_stop_width_spaces)
            else:
                indent_text = " " * correct_indent
            cursor.insertText(indent_text)
            return True

    @Slot()
    def clear_all_output(self):
        """Removes all ouput in the ipynb format (Json only)"""
        try:
            nb = nbformat.reads(self.toPlainText(), as_version=4)
            if nb.cells:
                for cell in nb.cells:
                    if "outputs" in cell:
                        cell["outputs"] = []
                    if "prompt_number" in cell:
                        cell["prompt_number"] = None
            # We do the following rather than using self.setPlainText
            # to benefit from QTextEdit's undo/redo feature.
            self.selectAll()
            self.insertPlainText(nbformat.writes(nb))
        except Exception as e:
            QMessageBox.critical(
                self,
                _("Removal error"),
                _(
                    "It was not possible to remove outputs from "
                    "this notebook. The error is:\n\n"
                )
                + str(e),
            )
            return

    def indent(self, force=False):
        """
        Indent current line or selection

        force=True: indent even if cursor is not a the beginning of the line
        """
        leading_text = self.get_text("sol", "cursor")
        if self.has_selected_text():
            self.add_prefix(self.indent_chars)
        elif force or not leading_text.strip() or (self.tab_indents and self.tab_mode):
            if self.is_python_like():
                if not self.fix_indent(forward=True):
                    self.add_prefix(self.indent_chars)
            else:
                self.add_prefix(self.indent_chars)
        else:
            if len(self.indent_chars) > 1:
                length = len(self.indent_chars)
                self.insert_text(" " * (length - (len(leading_text) % length)))
            else:
                self.insert_text(self.indent_chars)

    def indent_or_replace(self):
        """Indent or replace by 4 spaces depending on selection and tab mode"""
        if (self.tab_indents and self.tab_mode) or not self.has_selected_text():
            self.indent()
        else:
            cursor = self.textCursor()
            if self.get_selected_text() == str(cursor.block().text()):
                self.indent()
            else:
                cursor1 = self.textCursor()
                cursor1.setPosition(cursor.selectionStart())
                cursor2 = self.textCursor()
                cursor2.setPosition(cursor.selectionEnd())
                if cursor1.blockNumber() != cursor2.blockNumber():
                    self.indent()
                else:
                    self.replace(self.indent_chars)

    def unindent(self, force=False):
        """
        Unindent current line or selection

        force=True: unindent even if cursor is not a the beginning of the line
        """
        if self.has_selected_text():
            self.remove_prefix(self.indent_chars)
        else:
            leading_text = self.get_text("sol", "cursor")
            if (
                force
                or not leading_text.strip()
                or (self.tab_indents and self.tab_mode)
            ):
                if self.is_python_like():
                    if not self.fix_indent(forward=False):
                        self.remove_prefix(self.indent_chars)
                elif leading_text.endswith("\t"):
                    self.remove_prefix("\t")
                else:
                    self.remove_prefix(self.indent_chars)

    @Slot()
    def toggle_comment(self):
        """Toggle comment on current line or selection"""
        cursor = self.textCursor()
        start_pos, end_pos = sorted([cursor.selectionStart(), cursor.selectionEnd()])
        cursor.setPosition(end_pos)
        last_line = cursor.block().blockNumber()
        if cursor.atBlockStart() and start_pos != end_pos:
            last_line -= 1
        cursor.setPosition(start_pos)
        first_line = cursor.block().blockNumber()
        # If the selection contains only commented lines and surrounding
        # whitespace, uncomment. Otherwise, comment.
        is_comment_or_whitespace = True
        at_least_one_comment = False
        for _line_nb in range(first_line, last_line + 1):
            text = str(cursor.block().text()).lstrip()
            is_comment = text.startswith(self.comment_string)
            is_whitespace = text == ""
            is_comment_or_whitespace *= is_comment or is_whitespace
            if is_comment:
                at_least_one_comment = True
            cursor.movePosition(QTextCursor.NextBlock)
        if is_comment_or_whitespace and at_least_one_comment:
            self.uncomment()
        else:
            self.comment()

    def comment(self):
        """Comment current line or selection."""
        self.add_prefix(self.comment_string)

    def uncomment(self):
        """Uncomment current line or selection."""
        self.remove_prefix(self.comment_string)

    def __blockcomment_bar(self):
        return self.comment_string + " " + "=" * (78 - len(self.comment_string))

    def transform_to_uppercase(self):
        """Change to uppercase current line or selection."""
        cursor = self.textCursor()
        prev_pos = cursor.position()
        selected_text = str(cursor.selectedText())

        if len(selected_text) == 0:
            prev_pos = cursor.position()
            cursor.select(QTextCursor.WordUnderCursor)
            selected_text = str(cursor.selectedText())

        s = selected_text.upper()
        cursor.insertText(s)
        self.set_cursor_position(prev_pos)

    def transform_to_lowercase(self):
        """Change to lowercase current line or selection."""
        cursor = self.textCursor()
        prev_pos = cursor.position()
        selected_text = str(cursor.selectedText())

        if len(selected_text) == 0:
            prev_pos = cursor.position()
            cursor.select(QTextCursor.WordUnderCursor)
            selected_text = str(cursor.selectedText())

        s = selected_text.lower()
        cursor.insertText(s)
        self.set_cursor_position(prev_pos)

    def blockcomment(self):
        """Block comment current line or selection."""
        comline = self.__blockcomment_bar() + self.get_line_separator()
        cursor = self.textCursor()
        if self.has_selected_text():
            self.extend_selection_to_complete_lines()
            start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()
        else:
            start_pos = end_pos = cursor.position()
        cursor.beginEditBlock()
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.StartOfBlock)
        while cursor.position() <= end_pos:
            cursor.insertText(self.comment_string + " ")
            cursor.movePosition(QTextCursor.EndOfBlock)
            if cursor.atEnd():
                break
            cursor.movePosition(QTextCursor.NextBlock)
            end_pos += len(self.comment_string + " ")
        cursor.setPosition(end_pos)
        cursor.movePosition(QTextCursor.EndOfBlock)
        if cursor.atEnd():
            cursor.insertText(self.get_line_separator())
        else:
            cursor.movePosition(QTextCursor.NextBlock)
        cursor.insertText(comline)
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.insertText(comline)
        cursor.endEditBlock()

    def unblockcomment(self):
        """Un-block comment current line or selection"""

        def __is_comment_bar(cursor):
            return str(cursor.block().text()).startswith(self.__blockcomment_bar())

        # Finding first comment bar
        cursor1 = self.textCursor()
        if __is_comment_bar(cursor1):
            return
        while not __is_comment_bar(cursor1):
            cursor1.movePosition(QTextCursor.PreviousBlock)
            if cursor1.atStart():
                break
        if not __is_comment_bar(cursor1):
            return

        def __in_block_comment(cursor):
            cs = self.comment_string
            return str(cursor.block().text()).startswith(cs)

        # Finding second comment bar
        cursor2 = QTextCursor(cursor1)
        cursor2.movePosition(QTextCursor.NextBlock)
        while not __is_comment_bar(cursor2) and __in_block_comment(cursor2):
            cursor2.movePosition(QTextCursor.NextBlock)
            if cursor2.block() == self.document().lastBlock():
                break
        if not __is_comment_bar(cursor2):
            return
        # Removing block comment
        cursor3 = self.textCursor()
        cursor3.beginEditBlock()
        cursor3.setPosition(cursor1.position())
        cursor3.movePosition(QTextCursor.NextBlock)
        while cursor3.position() < cursor2.position():
            cursor3.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            if not cursor3.atBlockEnd():
                # standard commenting inserts '# ' but a trailing space on an
                # empty line might be stripped.
                cursor3.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            cursor3.removeSelectedText()
            cursor3.movePosition(QTextCursor.NextBlock)
        for cursor in (cursor2, cursor1):
            cursor3.setPosition(cursor.position())
            cursor3.select(QTextCursor.BlockUnderCursor)
            cursor3.removeSelectedText()
        cursor3.endEditBlock()

    # ------Autoinsertion of quotes/colons
    def __get_current_color(self, cursor=None):
        """Get the syntax highlighting color for the current cursor position"""
        if cursor is None:
            cursor = self.textCursor()

        block = cursor.block()
        pos = cursor.position() - block.position()  # relative pos within block
        layout = block.layout()
        block_formats = layout.additionalFormats()

        if block_formats:
            # To easily grab current format for autoinsert_colons
            if cursor.atBlockEnd():
                current_format = block_formats[-1].format
            else:
                current_format = None
                for fmt in block_formats:
                    if (pos >= fmt.start) and (pos < fmt.start + fmt.length):
                        current_format = fmt.format
                if current_format is None:
                    return None
            color = current_format.foreground().color().name()
            return color
        else:
            return None

    def in_comment_or_string(self, cursor=None):
        """Is the cursor inside or next to a comment or string?"""
        if self.highlighter:
            if cursor is None:
                current_color = self.__get_current_color()
            else:
                current_color = self.__get_current_color(cursor=cursor)

            comment_color = self.highlighter.get_color_name("comment")
            string_color = self.highlighter.get_color_name("string")
            if (current_color == comment_color) or (current_color == string_color):
                return True
            else:
                return False
        else:
            return False

    def __colon_keyword(self, text):
        stmt_kws = ["def", "for", "if", "while", "with", "class", "elif", "except"]
        whole_kws = ["else", "try", "except", "finally"]
        text = text.lstrip()
        words = text.split()
        if any([text == wk for wk in whole_kws]):
            return True
        elif len(words) < 2:
            return False
        elif any([words[0] == sk for sk in stmt_kws]):
            return True
        else:
            return False

    def __forbidden_colon_end_char(self, text):
        end_chars = [":", "\\", "[", "{", "(", ","]
        text = text.rstrip()
        if any([text.endswith(c) for c in end_chars]):
            return True
        else:
            return False

    def __unmatched_braces_in_line(self, text, closing_braces_type=None):
        """
        Checks if there is an unmatched brace in the 'text'.
        The brace type can be general or specified by closing_braces_type
        (')', ']', or '}')
        """
        if closing_braces_type is None:
            opening_braces = ["(", "[", "{"]
            closing_braces = [")", "]", "}"]
        else:
            closing_braces = [closing_braces_type]
            opening_braces = [{")": "(", "}": "{", "]": "["}[closing_braces_type]]
        block = self.textCursor().block()
        line_pos = block.position()
        for pos, char in enumerate(text):
            if char in opening_braces:
                match = self.find_brace_match(line_pos + pos, char, forward=True)
                if (match is None) or (match > line_pos + len(text)):
                    return True
            if char in closing_braces:
                match = self.find_brace_match(line_pos + pos, char, forward=False)
                if (match is None) or (match < line_pos):
                    return True
        return False

    def __has_colon_not_in_brackets(self, text):
        """
        Return whether a string has a colon which is not between brackets.
        This function returns True if the given string has a colon which is
        not between a pair of (round, square or curly) brackets. It assumes
        that the brackets in the string are balanced.
        """
        for pos, char in enumerate(text):
            if char == ":" and not self.__unmatched_braces_in_line(text[:pos]):
                return True
        return False

    def autoinsert_colons(self):
        """Decide if we want to autoinsert colons"""
        line_text = self.get_text("sol", "cursor")
        if not self.textCursor().atBlockEnd():
            return False
        elif self.in_comment_or_string():
            return False
        elif not self.__colon_keyword(line_text):
            return False
        elif self.__forbidden_colon_end_char(line_text):
            return False
        elif self.__unmatched_braces_in_line(line_text):
            return False
        elif self.__has_colon_not_in_brackets(line_text):
            return False
        else:
            return True

    def __unmatched_quotes_in_line(self, text):
        """Return whether a string has open quotes.
        This simply counts whether the number of quote characters of either
        type in the string is odd.

        Take from the IPython project (in IPython/core/completer.py in v0.13)
        Spyder team: Add some changes to deal with escaped quotes

        - Copyright (C) 2008-2011 IPython Development Team
        - Copyright (C) 2001-2007 Fernando Perez. <fperez@colorado.edu>
        - Copyright (C) 2001 Python Software Foundation, www.python.org

        Distributed under the terms of the BSD License.
        """
        # We check " first, then ', so complex cases with nested quotes will
        # get the " to take precedence.
        text = text.replace("\\'", "")
        text = text.replace('\\"', "")
        if text.count('"') % 2:
            return '"'
        elif text.count("'") % 2:
            return "'"
        else:
            return ""

    def __next_char(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        next_char = str(cursor.selectedText())
        return next_char

    def __in_comment(self):
        if self.highlighter:
            current_color = self.__get_current_color()
            comment_color = self.highlighter.get_color_name("comment")
            if current_color == comment_color:
                return True
            else:
                return False
        else:
            return False

    def autoinsert_quotes(self, key):
        """Control how to automatically insert quotes in various situations"""
        char = {Qt.Key_QuoteDbl: '"', Qt.Key_Apostrophe: "'"}[key]

        line_text = self.get_text("sol", "eol")
        line_to_cursor = self.get_text("sol", "cursor")
        cursor = self.textCursor()
        last_three = self.get_text("sol", "cursor")[-3:]
        last_two = self.get_text("sol", "cursor")[-2:]
        trailing_text = self.get_text("cursor", "eol").strip()

        if self.has_selected_text():
            text = "".join([char, self.get_selected_text(), char])
            self.insert_text(text)
        elif self.__in_comment():
            self.insert_text(char)
        elif (
            len(trailing_text) > 0
            and not self.__unmatched_quotes_in_line(line_to_cursor) == char
        ):
            self.insert_text(char)
        elif self.__unmatched_quotes_in_line(line_text) and (
            not last_three == 3 * char
        ):
            self.insert_text(char)
        # Move to the right if we are before a quote
        elif self.__next_char() == char:
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 1)
            cursor.clearSelection()
            self.setTextCursor(cursor)
        # Automatic insertion of triple double quotes (for docstrings)
        elif last_three == 3 * char:
            self.insert_text(3 * char)
            cursor = self.textCursor()
            cursor.movePosition(
                QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor, 3
            )
            cursor.clearSelection()
            self.setTextCursor(cursor)
        # If last two chars are quotes, just insert one more because most
        # probably the user wants to write a docstring
        elif last_two == 2 * char:
            self.insert_text(char)
        # Automatic insertion of quotes
        else:
            self.insert_text(2 * char)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.PreviousCharacter)
            self.setTextCursor(cursor)

    # ===============================================================================
    #    Qt Event handlers
    # ===============================================================================
    def setup_context_menu(self):
        """Setup context menu"""
        self.undo_action = create_action(
            self,
            _("Undo"),
            icon=get_icon("undo"),
            shortcut=get_shortcut("editor", "undo"),
            triggered=self.undo,
        )
        self.redo_action = create_action(
            self,
            _("Redo"),
            icon=get_icon("redo"),
            shortcut=get_shortcut("editor", "redo"),
            triggered=self.redo,
        )
        self.cut_action = create_action(
            self,
            _("Cut"),
            icon=get_icon("editcut"),
            shortcut=get_shortcut("editor", "cut"),
            triggered=self.cut,
        )
        self.copy_action = create_action(
            self,
            _("Copy"),
            icon=get_icon("editcopy.png"),
            shortcut=get_shortcut("editor", "copy"),
            triggered=self.copy,
        )
        self.paste_action = create_action(
            self,
            _("Paste"),
            icon=get_icon("paste"),
            shortcut=get_shortcut("editor", "paste"),
            triggered=self.paste,
        )
        selectall_action = create_action(
            self,
            _("Select All"),
            icon=get_icon("selectall"),
            shortcut=get_shortcut("editor", "select all"),
            triggered=self.selectAll,
        )
        toggle_comment_action = create_action(
            self,
            _("Comment") + "/" + _("Uncomment"),
            icon=get_icon("comment"),
            shortcut=get_shortcut("editor", "toggle comment"),
            triggered=self.toggle_comment,
        )
        self.clear_all_output_action = create_action(
            self,
            _("Clear all ouput"),
            icon=get_icon("ipython_console"),
            triggered=self.clear_all_output,
        )
        self.gotodef_action = create_action(
            self,
            _("Go to definition"),
            shortcut=get_shortcut("editor", "go to definition"),
            triggered=self.go_to_definition_from_cursor,
        )

        # Zoom actions
        zoom_in_action = create_action(
            self,
            _("Zoom in"),
            icon=get_icon("zoom_in"),
            shortcut=QKeySequence(QKeySequence.ZoomIn),
            triggered=self.zoom_in.emit,
        )
        zoom_out_action = create_action(
            self,
            _("Zoom out"),
            icon=get_icon("zoom_out"),
            shortcut=QKeySequence(QKeySequence.ZoomOut),
            triggered=self.zoom_out.emit,
        )
        zoom_reset_action = create_action(
            self,
            _("Zoom reset"),
            shortcut=QKeySequence("Ctrl+0"),
            triggered=self.zoom_reset.emit,
        )

        # Build menu
        self.menu = QMenu(self)
        actions_1 = [
            self.gotodef_action,
            None,
            self.undo_action,
            self.redo_action,
            None,
            self.cut_action,
            self.copy_action,
            self.paste_action,
            selectall_action,
        ]
        actions_2 = [
            None,
            zoom_in_action,
            zoom_out_action,
            zoom_reset_action,
            None,
            toggle_comment_action,
        ]
        if nbformat is not None:
            nb_actions = [self.clear_all_output_action, self.ipynb_convert_action, None]
            actions = actions_1 + nb_actions + actions_2
            add_actions(self.menu, actions)
        else:
            actions = actions_1 + actions_2
            add_actions(self.menu, actions)

        # Read-only context-menu
        self.readonly_menu = QMenu(self)
        add_actions(
            self.readonly_menu,
            (self.copy_action, None, selectall_action, self.gotodef_action),
        )

    def keyReleaseEvent(self, event):
        """Override Qt method."""
        super(PythonCodeEditor, self).keyReleaseEvent(event)
        event.ignore()

    def keyPressEvent(self, event):
        """Reimplement Qt method"""
        key = event.key()
        ctrl = event.modifiers() & Qt.ControlModifier
        shift = event.modifiers() & Qt.ShiftModifier
        text = str(event.text())
        has_selection = self.has_selected_text()
        if text:
            self.__clear_occurrences()
        if QToolTip.isVisible():
            self.hide_tooltip_if_necessary(key)

        # Handle the Qt Builtin key sequences
        checks = [
            ("SelectAll", "Select All"),
            ("Copy", "Copy"),
            ("Cut", "Cut"),
            ("Paste", "Paste"),
        ]

        for qname, name in checks:
            seq = getattr(QKeySequence, qname)
            sc = get_shortcut("editor", name)
            default = QKeySequence(seq).toString()
            # XXX - Using debug_print, it can be seen that event and seq
            # will never be equal, so this code is never executed.
            # Need to find out the intended purpose and if it should be
            # retained.
            if event == seq and sc != default:
                # if we have overridden it, call our action
                for shortcut in self.shortcuts:
                    qsc, name, keystr = shortcut.data
                    if keystr == default:
                        qsc.activated.emit()
                        event.ignore()
                        return

                # otherwise, pass it on to parent
                event.ignore()
                return

        if key in (Qt.Key_Enter, Qt.Key_Return):
            if not shift and not ctrl:
                if (
                    self.add_colons_enabled
                    and self.is_python_like()
                    and self.autoinsert_colons()
                ):
                    self.textCursor().beginEditBlock()
                    self.insert_text(":" + self.get_line_separator())
                    self.fix_indent()
                    self.textCursor().endEditBlock()
                elif self.is_completion_widget_visible() and self.codecompletion_enter:
                    self.select_completion_list()
                else:
                    # Check if we're in a comment or a string at the
                    # current position
                    cmt_or_str_cursor = self.in_comment_or_string()

                    # Check if the line start with a comment or string
                    cursor = self.textCursor()
                    cursor.setPosition(
                        cursor.block().position(), QTextCursor.KeepAnchor
                    )
                    cmt_or_str_line_begin = self.in_comment_or_string(cursor=cursor)

                    # Check if we are in a comment or a string
                    cmt_or_str = cmt_or_str_cursor and cmt_or_str_line_begin

                    self.textCursor().beginEditBlock()
                    TextEditBaseWidget.keyPressEvent(self, event)
                    self.fix_indent(comment_or_string=cmt_or_str)
                    self.textCursor().endEditBlock()
            elif shift:
                self.run_cell_and_advance.emit()
            elif ctrl:
                self.run_cell.emit()
        elif shift and key == Qt.Key_Delete:
            # Shift + Del is a Key sequence reserved by most OSes
            # https://github.com/spyder-ide/spyder/issues/3405
            # For now, add back reserved sequence for cut (issue 5973).
            # Since Ctrl+X is configurable, this should also use preferences.
            # https://doc.qt.io/qt-5/qkeysequence.html
            if has_selection:
                self.cut()
            else:
                self.delete_line()
        elif shift and key == Qt.Key_Insert:
            # For now, add back reserved sequence for paste (issue 5973).
            # Since Ctrl+V is configurable, this should also use preferences.
            # https://doc.qt.io/qt-5/qkeysequence.html
            self.paste()
        elif key == Qt.Key_Insert and not shift and not ctrl:
            self.setOverwriteMode(not self.overwriteMode())
        elif key == Qt.Key_Backspace and not shift and not ctrl:
            leading_text = self.get_text("sol", "cursor")
            leading_length = len(leading_text)
            trailing_spaces = leading_length - len(leading_text.rstrip())
            if has_selection or not self.intelligent_backspace:
                TextEditBaseWidget.keyPressEvent(self, event)
            else:
                trailing_text = self.get_text("cursor", "eol")
                if not leading_text.strip() and leading_length > len(self.indent_chars):
                    if leading_length % len(self.indent_chars) == 0:
                        self.unindent()
                    else:
                        TextEditBaseWidget.keyPressEvent(self, event)
                elif trailing_spaces and not trailing_text.strip():
                    self.remove_suffix(leading_text[-trailing_spaces:])
                elif (
                    leading_text
                    and trailing_text
                    and leading_text[-1] + trailing_text[0]
                    in ("()", "[]", "{}", "''", '""')
                ):
                    cursor = self.textCursor()
                    cursor.movePosition(QTextCursor.PreviousCharacter)
                    cursor.movePosition(
                        QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 2
                    )
                    cursor.removeSelectedText()
                else:
                    TextEditBaseWidget.keyPressEvent(self, event)
                    if self.is_completion_widget_visible():
                        self.completion_text = self.completion_text[:-1]
        elif key == Qt.Key_Period:
            self.insert_text(text)
            if (
                (self.is_python_like())
                and not self.in_comment_or_string()
                and self.codecompletion_auto
            ):
                # Enable auto-completion only if last token isn't a float
                last_obj = getobj(self.get_text("sol", "cursor"))
                if last_obj and not last_obj.isdigit():
                    self.do_completion(automatic=True)
        elif key == Qt.Key_Home:
            self.stdkey_home(shift, ctrl)
        elif key == Qt.Key_End:
            # See Issue 495: on MacOS X, it is necessary to redefine this
            # basic action which should have been implemented natively
            self.stdkey_end(shift, ctrl)
        elif text == "(" and not has_selection:
            self.hide_completion_widget()
            self.handle_parentheses(text)
        elif (
            text in ("[", "{") and not has_selection and self.close_parentheses_enabled
        ):
            s_trailing_text = self.get_text("cursor", "eol").strip()
            if len(s_trailing_text) == 0 or s_trailing_text[0] in (",", ")", "]", "}"):
                self.insert_text({"{": "{}", "[": "[]"}[text])
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.PreviousCharacter)
                self.setTextCursor(cursor)
            else:
                TextEditBaseWidget.keyPressEvent(self, event)
        elif key in (Qt.Key_QuoteDbl, Qt.Key_Apostrophe) and self.close_quotes_enabled:
            self.autoinsert_quotes(key)
        elif (
            key in (Qt.Key_ParenRight, Qt.Key_BraceRight, Qt.Key_BracketRight)
            and not has_selection
            and self.close_parentheses_enabled
            and not self.textCursor().atBlockEnd()
        ):
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            text = str(cursor.selectedText())
            key_matches_next_char = (
                text
                == {
                    Qt.Key_ParenRight: ")",
                    Qt.Key_BraceRight: "}",
                    Qt.Key_BracketRight: "]",
                }[key]
            )
            if key_matches_next_char and not self.__unmatched_braces_in_line(
                cursor.block().text(), text
            ):
                # overwrite an existing brace if all braces in line are matched
                cursor.clearSelection()
                self.setTextCursor(cursor)
            else:
                TextEditBaseWidget.keyPressEvent(self, event)
        elif key == Qt.Key_Colon and not has_selection and self.auto_unindent_enabled:
            leading_text = self.get_text("sol", "cursor")
            if leading_text.lstrip() in ("else", "finally"):
                ind = lambda txt: len(txt) - len(txt.lstrip())
                prevtxt = str(self.textCursor().block().previous().text())
                if ind(leading_text) == ind(prevtxt):
                    self.unindent(force=True)
            TextEditBaseWidget.keyPressEvent(self, event)
        elif (
            key == Qt.Key_Space
            and not shift
            and not ctrl
            and not has_selection
            and self.auto_unindent_enabled
        ):
            leading_text = self.get_text("sol", "cursor")
            if leading_text.lstrip() in ("elif", "except"):
                ind = lambda txt: len(txt) - len(txt.lstrip())
                prevtxt = str(self.textCursor().block().previous().text())
                if ind(leading_text) == ind(prevtxt):
                    self.unindent(force=True)
            TextEditBaseWidget.keyPressEvent(self, event)
        elif key == Qt.Key_Tab:
            # Important note: <TAB> can't be called with a QShortcut because
            # of its singular role with respect to widget focus management
            if not has_selection and not self.tab_mode:
                self.intelligent_tab()
            else:
                # indent the selected text
                self.indent_or_replace()
        elif key == Qt.Key_Backtab:
            # Backtab, i.e. Shift+<TAB>, could be treated as a QShortcut but
            # there is no point since <TAB> can't (see above)
            if not has_selection and not self.tab_mode:
                self.intelligent_backtab()
            else:
                # indent the selected text
                self.unindent()
        else:
            TextEditBaseWidget.keyPressEvent(self, event)
            if self.is_completion_widget_visible() and text:
                self.completion_text += text

    def handle_parentheses(self, text):
        """Handle left and right parenthesis depending on editor config."""
        position = self.get_position("cursor")
        rest = self.get_text("cursor", "eol").rstrip()
        valid = not rest or rest[0] in (",", ")", "]", "}")
        if self.close_parentheses_enabled and valid:
            self.insert_text("()")
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.PreviousCharacter)
            self.setTextCursor(cursor)
        else:
            self.insert_text(text)
        if self.is_python_like() and self.get_text("sol", "cursor") and self.calltips:
            self.sig_show_object_info.emit(position)

    def mouseMoveEvent(self, event):
        """Underline words when pressing <CONTROL>"""
        if self.has_selected_text():
            TextEditBaseWidget.mouseMoveEvent(self, event)
            return
        if self.go_to_definition_enabled and event.modifiers() & Qt.ControlModifier:
            text = self.get_word_at(event.pos())
            if text and (self.is_python_like()) and not keyword.iskeyword(str(text)):
                if not self.__cursor_changed:
                    QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))
                    self.__cursor_changed = True
                cursor = self.cursorForPosition(event.pos())
                cursor.select(QTextCursor.WordUnderCursor)
                self.clear_extra_selections("ctrl_click")
                self.__highlight_selection(
                    "ctrl_click",
                    cursor,
                    update=True,
                    foreground_color=self.ctrl_click_color,
                    underline_color=self.ctrl_click_color,
                    underline_style=QTextCharFormat.SingleUnderline,
                )
                event.accept()
                return
        if self.__cursor_changed:
            QApplication.restoreOverrideCursor()
            self.__cursor_changed = False
            self.clear_extra_selections("ctrl_click")
        TextEditBaseWidget.mouseMoveEvent(self, event)

    def leaveEvent(self, event):
        """If cursor has not been restored yet, do it now"""
        if self.__cursor_changed:
            QApplication.restoreOverrideCursor()
            self.__cursor_changed = False
            self.clear_extra_selections("ctrl_click")
        TextEditBaseWidget.leaveEvent(self, event)

    @Slot()
    def go_to_definition_from_cursor(self, cursor=None):
        """Go to definition from cursor instance (QTextCursor)"""
        if not self.go_to_definition_enabled:
            return
        if cursor is None:
            cursor = self.textCursor()
        if self.in_comment_or_string():
            return
        position = cursor.position()
        text = str(cursor.selectedText())
        if len(text) == 0:
            cursor.select(QTextCursor.WordUnderCursor)
            text = str(cursor.selectedText())
        if not text is None:
            self.go_to_definition.emit(position)

    def mousePressEvent(self, event):
        """Reimplement Qt method"""
        if event.button() == Qt.LeftButton and (event.modifiers() & Qt.ControlModifier):
            TextEditBaseWidget.mousePressEvent(self, event)
            cursor = self.cursorForPosition(event.pos())
            self.go_to_definition_from_cursor(cursor)
        else:
            TextEditBaseWidget.mousePressEvent(self, event)

    def contextMenuEvent(self, event):
        """Reimplement Qt method"""
        nonempty_selection = self.has_selected_text()
        self.copy_action.setEnabled(nonempty_selection)
        self.cut_action.setEnabled(nonempty_selection)
        self.clear_all_output_action.setVisible(self.is_json() and nbformat is not None)
        self.ipynb_convert_action.setVisible(self.is_json() and nbformat is not None)
        self.run_cell_action.setVisible(self.is_python())
        self.run_cell_and_advance_action.setVisible(self.is_python())
        self.run_selection_action.setVisible(self.is_python())
        self.re_run_last_cell_action.setVisible(self.is_python())
        self.gotodef_action.setVisible(
            self.go_to_definition_enabled and self.is_python_like()
        )

        # Code duplication go_to_definition_from_cursor and mouse_move_event
        cursor = self.textCursor()
        text = str(cursor.selectedText())
        if len(text) == 0:
            cursor.select(QTextCursor.WordUnderCursor)
            text = str(cursor.selectedText())

        self.undo_action.setEnabled(self.document().isUndoAvailable())
        self.redo_action.setEnabled(self.document().isRedoAvailable())
        menu = self.menu
        if self.isReadOnly():
            menu = self.readonly_menu
        menu.popup(event.globalPos())
        event.accept()

    # ------ Paint event
    def paintEvent(self, event):
        """Overrides paint event to update the list of visible blocks"""
        self.update_visible_blocks(event)
        TextEditBaseWidget.paintEvent(self, event)
        self.painted.emit(event)

    def update_visible_blocks(self, event):
        """Update the list of visible blocks/lines position"""
        self.__visible_blocks[:] = []
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())
        ebottom_bottom = self.height()

        while block.isValid():
            visible = bottom <= ebottom_bottom
            if not visible:
                break
            if block.isVisible():
                self.__visible_blocks.append((top, blockNumber + 1, block))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber = block.blockNumber()

    def _draw_editor_cell_divider(self):
        """Draw a line on top of a define cell"""
        if self.supported_cell_language:
            cell_line_color = self.comment_color
            painter = QPainter(self.viewport())
            pen = painter.pen()
            pen.setStyle(Qt.SolidLine)
            pen.setBrush(cell_line_color)
            painter.setPen(pen)

            for top, line_number, block in self.visible_blocks:
                if self.is_cell_separator(block):
                    painter.drawLine(4, top, self.width(), top)

    @property
    def visible_blocks(self):
        """
        Returns the list of visible blocks.

        Each element in the list is a tuple made up of the line top position,
        the line number (already 1 based), and the QTextBlock itself.

        :return: A list of tuple(top position, line number, block)
        :rtype: List of tuple(int, int, QtGui.QTextBlock)
        """
        return self.__visible_blocks

    def is_editor(self):
        """

        :return:
        """
        return True
