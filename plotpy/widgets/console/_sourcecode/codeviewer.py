# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Editor widget based on QtGui.QPlainTextEdit
"""

# TODO: Try to separate this module from spyder to create a self
#       consistent editor module (Qt source code and shell widgets library)

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
    QKeySequence,
    QMenu,
    QPainter,
    QPaintEvent,
    QRect,
    QRegExp,
    QSize,
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


class PythonCodeViewer(TextEditBaseWidget):
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
        self.setup_context_menu()

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
        """

        :return:
        """
        copy = config_shortcut(self.copy, context="Editor", name="copy", parent=self)
        select_all = config_shortcut(
            self.selectAll, context="Editor", name="Select All", parent=self
        )

        return [copy, select_all]

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
        highlight_current_line=True,
        highlight_current_cell=True,
        occurrence_highlighting=True,
        scrollflagarea=True,
        edge_line=True,
        edge_line_column=79,
        show_blanks=False,
        tab_stop_width_spaces=4,
        cloned_from=None,
        filename=None,
        occurrence_timeout=1500,
    ):
        """

        :param linenumbers:
        :param language:
        :param markers:
        :param font:
        :param color_scheme:
        :param wrap:
        :param highlight_current_line:
        :param highlight_current_cell:
        :param occurrence_highlighting:
        :param scrollflagarea:
        :param edge_line:
        :param edge_line_column:
        :param show_blanks:
        :param tab_stop_width_spaces:
        :param cloned_from:
        :param filename:
        :param occurrence_timeout:
        """
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
        self.add_remove_breakpoint(line_number, edit_condition=shift)

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

    # ===============================================================================
    #    Qt Event handlers
    # ===============================================================================
    def setup_context_menu(self):
        """Setup context menu"""

        self.copy_action = create_action(
            self,
            _("Copy"),
            icon=get_icon("editcopy.png"),
            shortcut=get_shortcut("editor", "copy"),
            triggered=self.copy,
        )

        selectall_action = create_action(
            self,
            _("Select All"),
            icon=get_icon("selectall.png"),
            shortcut=get_shortcut("editor", "select all"),
            triggered=self.selectAll,
        )

        # Read-only context-menu
        self.readonly_menu = QMenu(self)
        add_actions(self.readonly_menu, (self.copy_action, None, selectall_action))

    def keyReleaseEvent(self, event):
        """Override Qt method."""
        super(PythonCodeViewer, self).keyReleaseEvent(event)
        event.ignore()

    def keyPressEvent(self, event):
        """Reimplement Qt method"""
        key = event.key()
        ctrl = event.modifiers() & Qt.ControlModifier
        shift = event.modifiers() & Qt.ShiftModifier
        text = str(event.text())
        if text:
            self.__clear_occurrences()
        if QToolTip.isVisible():
            self.hide_tooltip_if_necessary(key)

        # Handle the Qt Builtin key sequences
        checks = [("SelectAll", "Select All"), ("Copy", "Copy")]

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

        if key == Qt.Key_Home:
            self.stdkey_home(shift, ctrl)
        elif key == Qt.Key_End:
            # See Issue 495: on MacOS X, it is necessary to redefine this
            # basic action which should have been implemented natively
            self.stdkey_end(shift, ctrl)
        else:
            TextEditBaseWidget.keyPressEvent(self, event)
            if self.is_completion_widget_visible() and text:
                self.completion_text += text

    def mouseMoveEvent(self, event):
        """Underline words when pressing <CONTROL>"""
        if self.has_selected_text():
            TextEditBaseWidget.mouseMoveEvent(self, event)
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

    def contextMenuEvent(self, event):
        """Reimplement Qt method"""
        nonempty_selection = self.has_selected_text()
        self.copy_action.setEnabled(nonempty_selection)

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
