# -*- coding: utf-8 -*-
import datetime

import PIL
from guidata.configtools import get_font
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import CONF, _
from plotpy.widgets.variableexplorer.collectionseditor.editor import CollectionsEditor
from plotpy.widgets.variableexplorer.nsview import (
    DataFrame,
    DatetimeIndex,
    FakeObject,
    Image,
    MaskedArray,
    Series,
    array,
    display_to_value,
    is_editable_type,
    is_known_type,
    ndarray,
)
from plotpy.widgets.variableexplorer.texteditor import TextEditor

if ndarray is not FakeObject:
    from plotpy.widgets.variableexplorer.arrayeditor import ArrayEditor

if DataFrame is not FakeObject:
    from plotpy.widgets.variableexplorer.dataframeeditor import DataFrameEditor


class CollectionsDelegate(QW.QItemDelegate):
    """CollectionsEditor Item Delegate"""

    sig_free_memory = QC.Signal()

    def __init__(self, parent=None):
        QW.QItemDelegate.__init__(self, parent)
        self._editors = {}  # keep references on opened editors

    def get_value(self, index):
        """

        :param index:
        :return:
        """
        if index.isValid():
            return index.model().get_value(index)

    def set_value(self, index, value):
        """

        :param index:
        :param value:
        """
        if index.isValid():
            index.model().set_value(index, value)

    def show_warning(self, index):
        """
        Decide if showing a warning when the user is trying to view
        a big variable associated to a Tablemodel index

        This avoids getting the variables' value to know its
        size and type, using instead those already computed by
        the TableModel.

        The problem is when a variable is too big, it can take a
        lot of time just to get its value
        """
        try:
            val_size = index.model().sizes[index.row()]
            val_type = index.model().types[index.row()]
        except:
            return False
        if val_type in ["list", "tuple", "dict"] and int(val_size) > 1e5:
            return True
        else:
            return False

    def createEditor(self, parent, option, index):
        """Overriding method createEditor"""
        if index.column() < 3:
            return None
        if self.show_warning(index):
            answer = QW.QMessageBox.warning(
                self.parent(),
                _("Warning"),
                _(
                    "Opening this variable can be slow\n\n"
                    "Do you want to continue anyway?"
                ),
                QW.QMessageBox.Yes | QW.QMessageBox.No,
            )
            if answer == QW.QMessageBox.No:
                return None
        try:
            value = self.get_value(index)
            if value is None:
                return None
        except Exception as msg:
            QW.QMessageBox.critical(
                self.parent(),
                _("Error"),
                _(
                    "Spyder was unable to retrieve the value of "
                    "this variable from the console.<br><br>"
                    "The error mesage was:<br>"
                    "<i>%s</i>"
                )
                % str(msg),
            )
            return
        key = index.model().get_key(index)
        readonly = (
            isinstance(value, tuple)
            or self.parent().readonly
            or not is_known_type(value)
        )
        # CollectionsEditor for a list, tuple, dict, etc.
        if isinstance(value, (list, tuple, dict)):
            editor = CollectionsEditor(parent=parent)
            editor.setup(value, key, icon=self.parent().windowIcon(), readonly=readonly)
            self.create_dialog(
                editor,
                dict(model=index.model(), editor=editor, key=key, readonly=readonly),
            )
            return None
        # ArrayEditor for a Numpy array
        elif isinstance(value, (ndarray, MaskedArray)) and ndarray is not FakeObject:
            editor = ArrayEditor(parent=parent)
            if not editor.setup_and_check(value, title=key, readonly=readonly):
                return
            self.create_dialog(
                editor,
                dict(model=index.model(), editor=editor, key=key, readonly=readonly),
            )
            return None
        # ArrayEditor for an images
        elif (
            isinstance(value, Image)
            and ndarray is not FakeObject
            and Image is not FakeObject
        ):
            arr = array(value)
            editor = ArrayEditor(parent=parent)
            if not editor.setup_and_check(arr, title=key, readonly=readonly):
                return
            conv_func = lambda arr: PIL.Image.fromarray(arr, mode=value.mode)
            self.create_dialog(
                editor,
                dict(
                    model=index.model(),
                    editor=editor,
                    key=key,
                    readonly=readonly,
                    conv=conv_func,
                ),
            )
            return None
        # DataFrameEditor for a pandas dataframe, series or index
        elif (
            isinstance(value, (DataFrame, DatetimeIndex, Series))
            and DataFrame is not FakeObject
        ):
            editor = DataFrameEditor(parent=parent)
            if not editor.setup_and_check(value, title=key):
                return
            editor.dataModel.set_format(index.model().dataframe_format)
            editor.sig_option_changed.connect(self.change_option)
            self.create_dialog(
                editor,
                dict(model=index.model(), editor=editor, key=key, readonly=readonly),
            )
            return None
        # QDateEdit and QDateTimeEdit for a dates or datetime respectively
        elif isinstance(value, datetime.date):
            if readonly:
                return None
            else:
                if isinstance(value, datetime.datetime):
                    editor = QW.QDateTimeEdit(value, parent=parent)
                else:
                    editor = QW.QDateEdit(value, parent=parent)
                editor.setCalendarPopup(True)
                editor.setFont(get_font(CONF, "dicteditor", "font"))
                return editor
        # TextEditor for a long string
        elif isinstance(value, str) and len(value) > 40:
            te = TextEditor(None, parent=parent)
            if te.setup_and_check(value):
                editor = TextEditor(value, key, readonly=readonly, parent=parent)
                self.create_dialog(
                    editor,
                    dict(
                        model=index.model(), editor=editor, key=key, readonly=readonly
                    ),
                )
            return None
        # QLineEdit for an individual value (int, float, short string, etc)
        elif is_editable_type(value):
            if readonly:
                return None
            else:
                editor = QW.QLineEdit(parent=parent)
                editor.setFont(get_font(CONF, "dicteditor", "font"))
                editor.setAlignment(QC.Qt.AlignLeft)
                # This is making Spyder crash because the QLineEdit that it's
                # been modified is removed and a new one is created after
                # evaluation. So the object on which this method is trying to
                # act doesn't exist anymore.
                # editor.returnPressed.connect(self.commitAndCloseEditor)
                return editor
        # CollectionsEditor for an arbitrary Python object
        else:
            editor = CollectionsEditor(parent=parent)
            editor.setup(value, key, icon=self.parent().windowIcon(), readonly=readonly)
            self.create_dialog(
                editor,
                dict(model=index.model(), editor=editor, key=key, readonly=readonly),
            )
            return None

    def create_dialog(self, editor, data):
        """

        :param editor:
        :param data:
        """
        self._editors[id(editor)] = data
        editor.accepted.connect(lambda eid=id(editor): self.editor_accepted(eid))
        editor.rejected.connect(lambda eid=id(editor): self.editor_rejected(eid))
        editor.show()

    @QC.Slot(str, object)
    def change_option(self, option_name, new_value):
        """
        Change configuration option.

        This function is called when a `sig_option_changed` signal is received.
        At the moment, this signal can only come from a DataFrameEditor.
        """
        if option_name == "dataframe_format":
            self.parent().set_dataframe_format(new_value)

    def editor_accepted(self, editor_id):
        """

        :param editor_id:
        """
        data = self._editors[editor_id]
        if not data["readonly"]:
            index = data["model"].get_index_from_key(data["key"])
            value = data["editor"].get_value()
            conv_func = data.get("conv", lambda v: v)
            self.set_value(index, conv_func(value))
        self._editors.pop(editor_id)
        self.free_memory()

    def editor_rejected(self, editor_id):
        """

        :param editor_id:
        """
        self._editors.pop(editor_id)
        self.free_memory()

    def free_memory(self):
        """Free memory after closing an editor."""
        try:
            self.sig_free_memory.emit()
        except RuntimeError:
            pass

    def commitAndCloseEditor(self):
        """Overriding method commitAndCloseEditor"""
        editor = self.sender()
        # Avoid a segfault with PyQt5. Variable value won't be changed
        # but at least Spyder won't crash. It seems generated by a bug in sip.
        try:
            self.commitData.emit(editor)
        except AttributeError:
            pass
        self.closeEditor.emit(editor, QW.QAbstractItemDelegate.NoHint)

    def setEditorData(self, editor, index):
        """
        Overriding method setEditorData
        Model --> Editor
        """
        value = self.get_value(index)
        if isinstance(editor, QW.QLineEdit):
            if isinstance(value, bytes):
                try:
                    value = str(value, "utf8")
                except:
                    pass
            if not isinstance(value, str):
                value = repr(value)
            editor.setText(value)
        elif isinstance(editor, QW.QDateEdit):
            editor.setDate(value)
        elif isinstance(editor, QW.QDateTimeEdit):
            editor.setDateTime(QC.QDateTime(value.date(), value.time()))

    def setModelData(self, editor, model, index):
        """
        Overriding method setModelData
        Editor --> Model
        """
        if not hasattr(model, "set_value"):
            # Read-only mode
            return

        if isinstance(editor, QW.QLineEdit):
            value = editor.text()
            try:
                value = display_to_value(
                    value, self.get_value(index), ignore_errors=False
                )
            except Exception as msg:
                raise
                QMessageBox.critical(
                    editor,
                    _("Edit item"),
                    _(
                        "<b>Unable to assign data to item.</b>"
                        "<br><br>Error message:<br>%s"
                    )
                    % str(msg),
                )
                return
        elif isinstance(editor, QW.QDateEdit):
            qdate = editor.date()
            value = datetime.date(qdate.year(), qdate.month(), qdate.day())
        elif isinstance(editor, QW.QDateTimeEdit):
            qdatetime = editor.dateTime()
            qdate = qdatetime.date()
            qtime = qdatetime.time()
            value = datetime.datetime(
                qdate.year(),
                qdate.month(),
                qdate.day(),
                qtime.hour(),
                qtime.minute(),
                qtime.second(),
            )
        else:
            # Should not happen...
            raise RuntimeError("Unsupported editor widget")
        self.set_value(index, value)
