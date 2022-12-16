# -*- coding: utf-8 -*-
import builtins
import keyword
import os
import re
import time

from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.config.getters import get_icon
from plotpy.utils.misc_from_gui import (
    add_actions,
    config_shortcut,
    create_action,
    get_shortcut,
    restore_keyevent,
)
from plotpy.widgets.console.mixins import GetHelpMixin, TracebackLinksMixin
from plotpy.widgets.console.shell.base import ShellBaseWidget


class PythonShellWidget(TracebackLinksMixin, ShellBaseWidget, GetHelpMixin):
    """Python shell widget"""

    QT_CLASS = ShellBaseWidget
    INITHISTORY = [
        "# -*- coding: utf-8 -*-",
        "# *** Spyder Python Console History Log ***",
    ]
    SEPARATOR = "%s##---(%s)---" % (os.linesep * 2, time.ctime())
    go_to_error = QC.Signal(str)

    def __init__(self, parent, history_filename, profile=False, initial_message=None):
        ShellBaseWidget.__init__(
            self, parent, history_filename, profile, initial_message
        )
        TracebackLinksMixin.__init__(self)
        GetHelpMixin.__init__(self)

        # Local shortcuts
        self.shortcuts = self.create_shortcuts()

    def create_shortcuts(self):
        """

        :return:
        """
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
        inspectsc = config_shortcut(
            self.inspect_current_object,
            context="Console",
            name="Inspect current object",
            parent=self,
        )
        return [inspectsc, array_inline, array_table]

    def get_shortcut_data(self):
        """
        Returns shortcut data, a list of tuples (shortcut, text, default)
        shortcut (QShortcut or QAction instance)
        text (string): action/shortcut description
        default (string): default key sequence
        """
        return [sc.data for sc in self.shortcuts]

    # ------ Context menu
    def setup_context_menu(self):
        """Reimplements ShellBaseWidget method"""
        ShellBaseWidget.setup_context_menu(self)
        self.copy_without_prompts_action = create_action(
            self,
            _("Copy without prompts"),
            icon=get_icon("copywop.png"),
            triggered=self.copy_without_prompts,
        )
        clear_line_action = create_action(
            self,
            _("Clear line"),
            shortcut=QG.QKeySequence(get_shortcut("console", "Clear line")),
            icon=get_icon("editdelete.png"),
            tip=_("Clear line"),
            triggered=self.clear_line,
        )
        clear_action = create_action(
            self,
            _("Clear shell"),
            shortcut=QG.QKeySequence(get_shortcut("console", "Clear shell")),
            icon=get_icon("editclear.png"),
            tip=_("Clear shell contents " "('cls' command)"),
            triggered=self.clear_terminal,
        )
        add_actions(
            self.menu,
            (self.copy_without_prompts_action, clear_line_action, clear_action),
        )

    def contextMenuEvent(self, event):
        """Reimplements ShellBaseWidget method"""
        state = self.has_selected_text()
        self.copy_without_prompts_action.setEnabled(state)
        ShellBaseWidget.contextMenuEvent(self, event)

    @QC.Slot()
    def copy_without_prompts(self):
        """Copy text to clipboard without prompts"""
        text = self.get_selected_text()
        lines = text.split(os.linesep)
        for index, line in enumerate(lines):
            if line.startswith(">>> ") or line.startswith("... "):
                lines[index] = line[4:]
        text = os.linesep.join(lines)
        QW.QApplication.clipboard().setText(text)

    # ------ Key handlers
    def postprocess_keyevent(self, event):
        """Process keypress event"""
        ShellBaseWidget.postprocess_keyevent(self, event)
        if QW.QToolTip.isVisible():
            _event, _text, key, _ctrl, _shift = restore_keyevent(event)
            self.hide_tooltip_if_necessary(key)

    def _key_other(self, text):
        """1 character key"""
        if self.is_completion_widget_visible():
            self.completion_text += text

    def _key_backspace(self, cursor_position):
        """Action for Backspace key"""
        if self.has_selected_text():
            self.check_selection()
            self.remove_selected_text()
        elif self.current_prompt_pos == cursor_position:
            # Avoid deleting prompt
            return
        elif self.is_cursor_on_last_line():
            self.stdkey_backspace()
            if self.is_completion_widget_visible():
                # Removing only last character because if there was a selection
                # the completion widget would have been canceled
                self.completion_text = self.completion_text[:-1]

    def _key_tab(self):
        """Action for TAB key"""
        if self.is_cursor_on_last_line():
            empty_line = not self.get_current_line_to_cursor().strip()
            if empty_line:
                self.stdkey_tab()
            else:
                self.show_code_completion(automatic=False)

    def _key_ctrl_space(self):
        """Action for Ctrl+Space"""
        if not self.is_completion_widget_visible():
            self.show_code_completion(automatic=False)

    def _key_pageup(self):
        """Action for PageUp key"""
        pass

    def _key_pagedown(self):
        """Action for PageDown key"""
        pass

    def _key_escape(self):
        """Action for ESCAPE key"""
        if self.is_completion_widget_visible():
            self.hide_completion_widget()

    def _key_question(self, text):
        """Action for '?'"""
        if self.get_current_line_to_cursor():
            last_obj = self.get_last_obj()
            if last_obj and not last_obj.isdigit():
                self.show_object_info(last_obj)
        self.insert_text(text)
        # In case calltip and completion are shown at the same time:
        if self.is_completion_widget_visible():
            self.completion_text += "?"

    def _key_parenleft(self, text):
        """Action for '('"""
        self.hide_completion_widget()
        if self.get_current_line_to_cursor():
            last_obj = self.get_last_obj()
            if last_obj and not last_obj.isdigit():
                self.insert_text(text)
                self.show_object_info(last_obj, call=True)
                return
        self.insert_text(text)

    def _key_period(self, text):
        """Action for '.'"""
        self.insert_text(text)
        if self.codecompletion_auto:
            # Enable auto-completion only if last token isn't a float
            last_obj = self.get_last_obj()
            if last_obj and not last_obj.isdigit():
                self.show_code_completion(automatic=True)

    # ------ Paste
    def paste(self):
        """Reimplemented slot to handle multiline paste action"""
        text = str(QW.QApplication.clipboard().text())
        if len(text.splitlines()) > 1:
            # Multiline paste
            if self.new_input_line:
                self.on_new_line()
            self.remove_selected_text()  # Remove selection, eventually
            end = self.get_current_line_from_cursor()
            lines = self.get_current_line_to_cursor() + text + end
            self.clear_line()
            self.execute_lines(lines)
            self.move_cursor(-len(end))
        else:
            # Standard paste
            ShellBaseWidget.paste(self)

    # ------ Code Completion / Calltips
    # Methods implemented in child class:
    # (e.g. InternalShell)
    def get_dir(self, objtxt):
        """Return dir(object)"""
        raise NotImplementedError

    def get_module_completion(self, objtxt):
        """Return module completion list associated to object name"""
        pass

    def get_globals_keys(self):
        """Return shell globals() keys"""
        raise NotImplementedError

    def get_cdlistdir(self):
        """Return shell current directory list dir"""
        raise NotImplementedError

    def iscallable(self, objtxt):
        """Is object callable?"""
        raise NotImplementedError

    def get_arglist(self, objtxt):
        """Get func/method argument list"""
        raise NotImplementedError

    def get__doc__(self, objtxt):
        """Get object __doc__"""
        raise NotImplementedError

    def get_doc(self, objtxt):
        """Get object documentation dictionary"""
        raise NotImplementedError

    def get_source(self, objtxt):
        """Get object source"""
        raise NotImplementedError

    def is_defined(self, objtxt, force_import=False):
        """Return True if object is defined"""
        raise NotImplementedError

    def show_code_completion(self, automatic):
        """Display a completion list based on the current line"""
        # Note: unicode conversion is needed only for ExternalShellBase
        text = str(self.get_current_line_to_cursor())
        last_obj = self.get_last_obj()

        if not text:
            return

        if text.startswith("import "):
            obj_list = self.get_module_completion(text)
            words = text.split(" ")
            if "," in words[-1]:
                words = words[-1].split(",")
            self.show_completion_list(
                obj_list, completion_text=words[-1], automatic=automatic
            )
            return

        elif text.startswith("from "):
            obj_list = self.get_module_completion(text)
            if obj_list is None:
                return
            words = text.split(" ")
            if "(" in words[-1]:
                words = words[:-2] + words[-1].split("(")
            if "," in words[-1]:
                words = words[:-2] + words[-1].split(",")
            self.show_completion_list(
                obj_list, completion_text=words[-1], automatic=automatic
            )
            return

        obj_dir = self.get_dir(last_obj)
        if last_obj and obj_dir and text.endswith("."):
            self.show_completion_list(obj_dir, automatic=automatic)
            return

        # Builtins and globals
        if (
            not text.endswith(".")
            and last_obj
            and re.match(r"[a-zA-Z_0-9]*$", last_obj)
        ):
            b_k_g = dir(builtins) + self.get_globals_keys() + keyword.kwlist
            for objname in b_k_g:
                if objname.startswith(last_obj) and objname != last_obj:
                    self.show_completion_list(
                        b_k_g, completion_text=last_obj, automatic=automatic
                    )
                    return
            else:
                return

        # Looking for an incomplete completion
        if last_obj is None:
            last_obj = text
        dot_pos = last_obj.rfind(".")
        if dot_pos != -1:
            if dot_pos == len(last_obj) - 1:
                completion_text = ""
            else:
                completion_text = last_obj[dot_pos + 1 :]
                last_obj = last_obj[:dot_pos]
            completions = self.get_dir(last_obj)
            if completions is not None:
                self.show_completion_list(
                    completions, completion_text=completion_text, automatic=automatic
                )
                return

        # Looking for ' or ": filename completion
        q_pos = max([text.rfind("'"), text.rfind('"')])
        if q_pos != -1:
            completions = self.get_cdlistdir()
            if completions:
                self.show_completion_list(
                    completions, completion_text=text[q_pos + 1 :], automatic=automatic
                )
            return

    # ------ Drag'n Drop
    def drop_pathlist(self, pathlist):
        """Drop path list"""
        if pathlist:
            files = ["r'%s'" % path for path in pathlist]
            if len(files) == 1:
                text = files[0]
            else:
                text = "[" + ", ".join(files) + "]"
            if self.new_input_line:
                self.on_new_line()
            self.insert_text(text)
            self.setFocus()
