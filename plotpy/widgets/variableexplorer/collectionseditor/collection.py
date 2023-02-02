# -*- coding: utf-8 -*-
import copy
import datetime
import warnings

import numpy as np
import pandas as pd
import PIL
from guidata.configtools import get_font, get_icon
from numpy.ma import MaskedArray
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QMessageBox

import plotpy.widgets.plot.interactive as plt
from plotpy.config import CONF, _
from plotpy.widgets import qapplication
from plotpy.widgets.variableexplorer.arrayeditor import ArrayEditor
from plotpy.widgets.variableexplorer.collectionseditor.base import BaseTableView
from plotpy.widgets.variableexplorer.collectionseditor.model import (
    CollectionsModel,
    ReadOnlyCollectionsModel,
)
from plotpy.widgets.variableexplorer.dataframeeditor import DataFrameEditor
from plotpy.widgets.variableexplorer.nsview import (
    DataFrame,
    DatetimeIndex,
    Image,
    Series,
    display_to_value,
    get_object_attrs,
    is_editable_type,
    is_known_type,
)

# from plotpy.widgets.variableexplorer.objecteditor.editor import oedit
from plotpy.widgets.variableexplorer.texteditor import TextEditor


class CollectionsEditor(QW.QDialog):
    """Collections Editor Dialog"""

    def __init__(self, parent=None):
        QW.QDialog.__init__(self, parent)

        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        self.setAttribute(QC.Qt.WA_DeleteOnClose)

        self.data_copy = None
        self.widget = None
        self.btn_save_and_close = None
        self.btn_close = None

    def setup(self, data, title="", readonly=False, width=650, icon=None, parent=None):
        """Setup editor."""
        if isinstance(data, dict):
            # dictionnary
            self.data_copy = data.copy()
            datalen = len(data)
        elif isinstance(data, (tuple, list)):
            # list, tuple
            self.data_copy = data[:]
            datalen = len(data)
        else:
            # unknown object
            try:
                self.data_copy = copy.deepcopy(data)
            except NotImplementedError:
                self.data_copy = copy.copy(data)
            except (TypeError, AttributeError):
                readonly = True
                self.data_copy = data
            datalen = len(get_object_attrs(data))

        # If the copy has a different type, then do not allow editing, because
        # this would change the type after saving; cf. issue #6936
        if type(self.data_copy) != type(data):
            readonly = True

        self.widget = CollectionsEditorWidget(
            self, self.data_copy, title=title, readonly=readonly
        )
        self.widget.editor.model.sig_setting_data.connect(self.save_and_close_enable)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

        # Buttons configuration
        btn_layout = QW.QHBoxLayout()
        btn_layout.addStretch()

        if not readonly:
            self.btn_save_and_close = QW.QPushButton(_("Save and Close"))
            self.btn_save_and_close.setDisabled(True)
            self.btn_save_and_close.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_save_and_close)

        self.btn_close = QW.QPushButton(_("Close"))
        self.btn_close.setAutoDefault(True)
        self.btn_close.setDefault(True)
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        constant = 121
        row_height = 30
        error_margin = 10
        height = constant + row_height * min([10, datalen]) + error_margin
        self.resize(width, height)

        self.setWindowTitle(self.widget.get_title())
        if icon is None:
            self.setWindowIcon(get_icon("dictedit.png"))
        # Make the dialog act as a window
        self.setWindowFlags(QC.Qt.Window)

    @QC.Slot()
    def save_and_close_enable(self):
        """Handle the data change event to enable the save and close button."""
        if self.btn_save_and_close:
            self.btn_save_and_close.setEnabled(True)
            self.btn_save_and_close.setAutoDefault(True)
            self.btn_save_and_close.setDefault(True)

    def get_value(self):
        """Return modified copy of dictionary or list"""
        # It is import to avoid accessing Qt C++ object as it has probably
        # already been destroyed, due to the Qt.WA_DeleteOnClose attribute
        return self.data_copy


class DictEditor(CollectionsEditor):
    """ """

    def __init__(self, parent=None):
        warnings.warn(
            "`DictEditor` has been renamed to `CollectionsEditor` in "
            "Spyder 3. Please use `CollectionsEditor` instead",
            RuntimeWarning,
        )
        CollectionsEditor.__init__(self, parent)


class CollectionsEditorWidget(QW.QWidget):
    """Dictionary Editor Widget"""

    def __init__(self, parent, data, readonly=False, title=""):
        QW.QWidget.__init__(self, parent)
        self.editor = CollectionsEditorTableView(self, data, readonly, title)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def set_data(self, data):
        """Set DictEditor data"""
        self.editor.set_data(data)

    def get_title(self):
        """Get model title"""
        return self.editor.model.title


class CollectionsEditorTableView(BaseTableView):
    """CollectionsEditor table view"""

    def __init__(
        self, parent, data, readonly=False, title="", names=False, minmax=False
    ):
        BaseTableView.__init__(self, parent)
        self.dictfilter = None
        self.readonly = readonly or isinstance(data, tuple)
        CollectionsModelClass = (
            ReadOnlyCollectionsModel if self.readonly else CollectionsModel
        )
        self.model = CollectionsModelClass(
            self, data, title, names=names, minmax=minmax
        )
        self.setModel(self.model)
        self.delegate = CollectionsDelegate(self)
        self.setItemDelegate(self.delegate)

        self.setup_table()
        self.menu = self.setup_menu(minmax)

    # ------ Remote/local API ---------------------------------------------------
    def remove_values(self, keys):
        """Remove values from data"""
        data = self.model.get_data()
        for key in sorted(keys, reverse=True):
            data.pop(key)
            self.set_data(data)

    def copy_value(self, orig_key, new_key):
        """Copy value"""
        data = self.model.get_data()
        if isinstance(data, list):
            data.append(data[orig_key])
        if isinstance(data, set):
            data.add(data[orig_key])
        else:
            data[new_key] = data[orig_key]
        self.set_data(data)

    def new_value(self, key, value):
        """Create new value in data"""
        data = self.model.get_data()
        data[key] = value
        self.set_data(data)

    def is_list(self, key):
        """Return True if variable is a list or a tuple"""
        data = self.model.get_data()
        return isinstance(data[key], (tuple, list))

    def get_len(self, key):
        """Return sequence length"""
        data = self.model.get_data()
        return len(data[key])

    def is_array(self, key):
        """Return True if variable is a numpy array"""
        data = self.model.get_data()
        return isinstance(data[key], (np.ndarray, np.ma.MaskedArray))

    def is_image(self, key):
        """Return True if variable is a PIL.Image image"""
        data = self.model.get_data()
        return isinstance(data[key], Image)

    def is_dict(self, key):
        """Return True if variable is a dictionary"""
        data = self.model.get_data()
        return isinstance(data[key], dict)

    def get_array_shape(self, key):
        """Return array's shape"""
        data = self.model.get_data()
        return data[key].shape

    def get_array_ndim(self, key):
        """Return array's ndim"""
        data = self.model.get_data()
        return data[key].ndim

    def oedit(self, key):
        """Edit item"""
        from plotpy.widgets.variableexplorer.objecteditor.editor import oedit

        data = self.model.get_data()

        oedit(data[key])

    def plot(self, key, funcname):
        """Plot item"""
        data = self.model.get_data()

        plt.figure()
        getattr(plt, funcname)(data[key])
        plt.show()

    def imshow(self, key):
        """Show item's image"""
        data = self.model.get_data()

        plt.figure()
        plt.imshow(data[key])
        plt.show()

    def show_image(self, key):
        """Show image (item is a PIL image)"""
        data = self.model.get_data()
        data[key].show()

    # ---------------------------------------------------------------------------

    def refresh_menu(self):
        """Refresh context menu"""
        data = self.model.get_data()
        index = self.currentIndex()
        condition = (
            (not isinstance(data, tuple)) and index.isValid() and not self.readonly
        )
        self.edit_action.setEnabled(condition)
        self.remove_action.setEnabled(condition)
        self.insert_action.setEnabled(not self.readonly)
        self.duplicate_action.setEnabled(condition)
        condition_rename = not isinstance(data, (tuple, list, set))
        self.rename_action.setEnabled(condition_rename)
        self.refresh_plot_entries(index)

    def set_filter(self, dictfilter=None):
        """Set table dict filter"""
        self.dictfilter = dictfilter


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
        except Exception:
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
        elif isinstance(value, (np.ndarray, MaskedArray)):
            editor = ArrayEditor(parent=parent)
            if not editor.setup_and_check(value, title=key, readonly=readonly):
                return
            self.create_dialog(
                editor,
                dict(model=index.model(), editor=editor, key=key, readonly=readonly),
            )
            return None
        # ArrayEditor for an images
        elif isinstance(value, Image):
            arr = np.array(value)
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
        elif isinstance(value, (DataFrame, DatetimeIndex, Series)):
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
                # FIXME
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
                except Exception:
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
                QMessageBox.critical(
                    editor,
                    _("Edit item"),
                    _(
                        "<b>Unable to assign data to item.</b>"
                        "<br><br>Error message:<br>%s"
                    )
                    % str(msg),
                )
                raise
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


# =============================================================================
# Tests
# =============================================================================
def get_test_data():
    """Create test data."""
    image = PIL.Image.Image.fromarray(np.random.randint(256, size=(100, 100)), mode="P")
    testdict = {"d": 1, "a": np.random.rand(10, 10), "b": [1, 2]}
    testdate = datetime.date(1945, 5, 8)
    test_timedelta = datetime.timedelta(days=-1, minutes=42, seconds=13)

    test_timestamp = pd.Timestamp("1945-05-08T23:01:00.12345")
    test_pd_td = pd.Timedelta(days=2193, hours=12)
    test_dtindex = pd.DatetimeIndex(start="1939-09-01T", end="1939-10-06", freq="12H")
    test_series = pd.Series({"series_name": [0, 1, 2, 3, 4, 5]})
    test_df = pd.DataFrame(
        {
            "string_col": ["a", "b", "c", "d"],
            "int_col": [0, 1, 2, 3],
            "float_col": [1.1, 2.2, 3.3, 4.4],
            "bool_col": [True, False, False, True],
        }
    )

    class Foobar(object):
        """ """

        def __init__(self):
            self.text = "toto"
            self.testdict = testdict
            self.testdate = testdate

    foobar = Foobar()
    return {
        "object": foobar,
        "module": np,
        "str": "kjkj kj k j j kj k jkj",
        "unicode": "éù",
        "list": [1, 3, [sorted, 5, 6], "kjkj", None],
        "tuple": ([1, testdate, testdict, test_timedelta], "kjkj", None),
        "dict": testdict,
        "float": 1.2233,
        "int": 223,
        "bool": True,
        "array": np.random.rand(10, 10).astype(np.int64),
        "masked_array": np.ma.array(
            [[1, 0], [1, 0]], mask=[[True, False], [False, False]]
        ),
        "1D-array": np.linspace(-10, 10).astype(np.float16),
        "3D-array": np.random.randint(2, size=(5, 5, 5)).astype(np.bool_),
        "empty_array": np.array([]),
        "image": image,
        "date": testdate,
        "datetime": datetime.datetime(1945, 5, 8, 23, 1, 0, int(1.5e5)),
        "timedelta": test_timedelta,
        "complex": 2 + 1j,
        "complex64": np.complex64(2 + 1j),
        "complex128": np.complex128(9j),
        "int8_scalar": np.int8(8),
        "int16_scalar": np.int16(16),
        "int32_scalar": np.int32(32),
        "int64_scalar": np.int64(64),
        "float16_scalar": np.float16(16),
        "float32_scalar": np.float32(32),
        "float64_scalar": np.float64(64),
        "bool_scalar": np.bool_(8),
        "bool__scalar": np.bool_(8),
        "timestamp": test_timestamp,
        "timedelta_pd": test_pd_td,
        "datetimeindex": test_dtindex,
        "series": test_series,
        "ddataframe": test_df,
        "None": None,
        "unsupported1": np.arccos,
        "unsupported2": np.cast,
        # Test for Issue #3518
        "big_struct_array": np.zeros(
            1000, dtype=[("ID", "f8"), ("param1", "f8", 5000)]
        ),
    }


def editor_test():
    """Test Collections editor."""

    app = qapplication()  # analysis:ignore
    dialog = CollectionsEditor()
    dialog.setup(get_test_data())
    dialog.show()
    app.exec_()


if __name__ == "__main__":
    editor_test()
