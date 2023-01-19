# -*- coding: utf-8 -*-
import io
import re
import sys

from guidata.configtools import get_icon
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.misc_from_gui import add_actions, create_action
from plotpy.utils.path import getcwd_or_home
from plotpy.widgets.qthelpers import mimedata2url
from plotpy.widgets.variableexplorer.collectionseditor.editor import CollectionsDelegate
from plotpy.widgets.variableexplorer.collectionseditor.model import (
    CollectionsModel,
    ReadOnlyCollectionsModel,
)
from plotpy.widgets.variableexplorer.importwizard import ImportWizard
from plotpy.widgets.variableexplorer.nsview import (
    DataFrame,
    FakeObject,
    Image,
    MaskedArray,
    Series,
    ndarray,
    np_savetxt,
    try_to_eval,
    unsorted_unique,
)


def fix_reference_name(name, blacklist=None):
    """Return a syntax-valid Python reference name from an arbitrary name"""
    name = "".join(re.split(r"[^0-9a-zA-Z_]", name))
    while name and not re.match(r"([a-zA-Z]+[0-9a-zA-Z_]*)$", name):
        if not re.match(r"[a-zA-Z]", name[0]):
            name = name[1:]
            continue
    name = str(name)
    if not name:
        name = "data"
    if blacklist is not None and name in blacklist:
        get_new_name = lambda index: name + ("%03d" % index)
        index = 0
        while get_new_name(index) in blacklist:
            index += 1
        name = get_new_name(index)
    return name


class BaseTableView(QW.QTableView):
    """Base collection editor table view"""

    sig_option_changed = QC.Signal(str, object)
    sig_files_dropped = QC.Signal(list)
    redirect_stdio = QC.Signal(bool)
    sig_free_memory = QC.Signal()

    def __init__(self, parent):
        QW.QTableView.__init__(self, parent)
        self.array_filename = None
        self.menu = None
        self.empty_ws_menu = None
        self.paste_action = None
        self.copy_action = None
        self.edit_action = None
        self.plot_action = None
        self.hist_action = None
        self.imshow_action = None
        self.save_array_action = None
        self.insert_action = None
        self.remove_action = None
        self.minmax_action = None
        self.rename_action = None
        self.duplicate_action = None
        self.delegate = None
        self.setAcceptDrops(True)

    def setup_table(self):
        """Setup table"""
        self.horizontalHeader().setStretchLastSection(True)
        self.adjust_columns()
        # Sorting columns
        self.setSortingEnabled(True)
        self.sortByColumn(0, QC.Qt.AscendingOrder)

    def setup_menu(self, minmax):
        """Setup context menu"""
        if self.minmax_action is not None:
            self.minmax_action.setChecked(minmax)
            return

        resize_action = create_action(
            self, _("Resize rows to contents"), triggered=self.resizeRowsToContents
        )
        self.paste_action = create_action(
            self, _("Paste"), icon=get_icon("editpaste.png"), triggered=self.paste
        )
        self.copy_action = create_action(
            self, _("Copy"), icon=get_icon("editcopy.png"), triggered=self.copy
        )
        self.edit_action = create_action(
            self, _("Edit"), icon=get_icon("edit.png"), triggered=self.edit_item
        )
        self.plot_action = create_action(
            self,
            _("Plot"),
            icon=get_icon("plot.png"),
            triggered=lambda: self.plot_item("plot"),
        )
        self.plot_action.setVisible(False)
        self.hist_action = create_action(
            self,
            _("Histogram"),
            icon=get_icon("hist.png"),
            triggered=lambda: self.plot_item("hist"),
        )
        self.hist_action.setVisible(False)
        self.imshow_action = create_action(
            self,
            _("Show image"),
            icon=get_icon("imshow.png"),
            triggered=self.imshow_item,
        )
        self.imshow_action.setVisible(False)
        self.save_array_action = create_action(
            self,
            _("Save array"),
            icon=get_icon("filesave.png"),
            triggered=self.save_array,
        )
        self.save_array_action.setVisible(False)
        self.insert_action = create_action(
            self, _("Insert"), icon=get_icon("insert.png"), triggered=self.insert_item
        )
        self.remove_action = create_action(
            self,
            _("Remove"),
            icon=get_icon("editdelete.png"),
            triggered=self.remove_item,
        )
        self.minmax_action = create_action(
            self, _("Show arrays min/max"), toggled=self.toggle_minmax
        )
        self.minmax_action.setChecked(minmax)
        self.toggle_minmax(minmax)
        self.rename_action = create_action(
            self, _("Rename"), icon=get_icon("rename.png"), triggered=self.rename_item
        )
        self.duplicate_action = create_action(
            self,
            _("Duplicate"),
            icon=get_icon("edit_add.png"),
            triggered=self.duplicate_item,
        )
        menu = QW.QMenu(self)
        menu_actions = [
            self.edit_action,
            self.plot_action,
            self.hist_action,
            self.imshow_action,
            self.save_array_action,
            self.insert_action,
            self.remove_action,
            self.copy_action,
            self.paste_action,
            None,
            self.rename_action,
            self.duplicate_action,
            None,
            resize_action,
        ]
        if ndarray is not FakeObject:
            menu_actions.append(self.minmax_action)
        add_actions(menu, menu_actions)
        self.empty_ws_menu = QW.QMenu(self)
        add_actions(
            self.empty_ws_menu,
            [self.insert_action, self.paste_action, None, resize_action],
        )
        return menu

    # ------ Remote/local API ---------------------------------------------------
    def remove_values(self, keys):
        """Remove values from data"""
        raise NotImplementedError

    def copy_value(self, orig_key, new_key):
        """Copy value"""
        raise NotImplementedError

    def new_value(self, key, value):
        """Create new value in data"""
        raise NotImplementedError

    def is_list(self, key):
        """Return True if variable is a list or a tuple"""
        raise NotImplementedError

    def get_len(self, key):
        """Return sequence length"""
        raise NotImplementedError

    def is_array(self, key):
        """Return True if variable is a numpy array"""
        raise NotImplementedError

    def is_image(self, key):
        """Return True if variable is a PIL.Image image"""
        raise NotImplementedError

    def is_dict(self, key):
        """Return True if variable is a dictionary"""
        raise NotImplementedError

    def get_array_shape(self, key):
        """Return array's shape"""
        raise NotImplementedError

    def get_array_ndim(self, key):
        """Return array's ndim"""
        raise NotImplementedError

    def oedit(self, key):
        """Edit item"""
        raise NotImplementedError

    def plot(self, key, funcname):
        """Plot item"""
        raise NotImplementedError

    def imshow(self, key):
        """Show item's image"""
        raise NotImplementedError

    def show_image(self, key):
        """Show image (item is a PIL image)"""
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def refresh_menu(self):
        """Refresh context menu"""
        index = self.currentIndex()
        condition = index.isValid()
        self.edit_action.setEnabled(condition)
        self.remove_action.setEnabled(condition)
        self.refresh_plot_entries(index)

    def refresh_plot_entries(self, index):
        """

        :param index:
        """
        if index.isValid():
            key = self.model.get_key(index)
            is_list = self.is_list(key)
            is_array = self.is_array(key) and self.get_len(key) != 0
            condition_plot = is_array and len(self.get_array_shape(key)) <= 2
            condition_hist = is_array and self.get_array_ndim(key) == 1
            condition_imshow = condition_plot and self.get_array_ndim(key) == 2
            condition_imshow = condition_imshow or self.is_image(key)
        else:
            is_array = (
                condition_plot
            ) = condition_imshow = is_list = condition_hist = False
        self.plot_action.setVisible(condition_plot or is_list)
        self.hist_action.setVisible(condition_hist or is_list)
        self.imshow_action.setVisible(condition_imshow)
        self.save_array_action.setVisible(is_array)

    def adjust_columns(self):
        """Resize two first columns to contents"""
        for col in range(3):
            self.resizeColumnToContents(col)

    def set_data(self, data):
        """Set table data"""
        if data is not None:
            self.model.set_data(data, self.dictfilter)
            self.sortByColumn(0, QC.Qt.AscendingOrder)

    def mousePressEvent(self, event):
        """Reimplement Qt method"""
        if event.button() != QC.Qt.LeftButton:
            QW.QTableView.mousePressEvent(self, event)
            return
        index_clicked = self.indexAt(event.pos())
        if index_clicked.isValid():
            if (
                index_clicked == self.currentIndex()
                and index_clicked in self.selectedIndexes()
            ):
                self.clearSelection()
            else:
                QW.QTableView.mousePressEvent(self, event)
        else:
            self.clearSelection()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Reimplement Qt method"""
        index_clicked = self.indexAt(event.pos())
        if index_clicked.isValid():
            row = index_clicked.row()
            # TODO: Remove hard coded "Value" column number (3 here)
            index_clicked = index_clicked.child(row, 3)
            self.edit(index_clicked)
        else:
            event.accept()

    def keyPressEvent(self, event):
        """Reimplement Qt methods"""
        if event.key() == QC.Qt.Key_Delete:
            self.remove_item()
        elif event.key() == QC.Qt.Key_F2:
            self.rename_item()
        elif event == QG.QKeySequence.Copy:
            self.copy()
        elif event == QG.QKeySequence.Paste:
            self.paste()
        else:
            QW.QTableView.keyPressEvent(self, event)

    def contextMenuEvent(self, event):
        """Reimplement Qt method"""
        if self.model.showndata:
            self.refresh_menu()
            self.menu.popup(event.globalPos())
            event.accept()
        else:
            self.empty_ws_menu.popup(event.globalPos())
            event.accept()

    def dragEnterEvent(self, event):
        """Allow user to drag files"""
        if mimedata2url(event.mimeData()):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Allow user to move files"""
        if mimedata2url(event.mimeData()):
            event.setDropAction(QC.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Allow user to drop supported files"""
        urls = mimedata2url(event.mimeData())
        if urls:
            event.setDropAction(QC.Qt.CopyAction)
            event.accept()
            self.sig_files_dropped.emit(urls)
        else:
            event.ignore()

    @QC.Slot(bool)
    def toggle_minmax(self, state):
        """Toggle min/max display for numpy arrays"""
        self.sig_option_changed.emit("minmax", state)
        self.model.minmax = state

    @QC.Slot(str)
    def set_dataframe_format(self, new_format):
        """
        Set format to use in DataframeEditor.

        Args:
            new_format (string): e.g. "%.3f"
        """
        self.sig_option_changed.emit("dataframe_format", new_format)
        self.model.dataframe_format = new_format

    @QC.Slot()
    def edit_item(self):
        """Edit item"""
        index = self.currentIndex()
        if not index.isValid():
            return
        # TODO: Remove hard coded "Value" column number (3 here)
        self.edit(index.child(index.row(), 3))

    @QC.Slot()
    def remove_item(self):
        """Remove item"""
        indexes = self.selectedIndexes()
        if not indexes:
            return
        for index in indexes:
            if not index.isValid():
                return
        one = _("Do you want to remove the selected item?")
        more = _("Do you want to remove all selected items?")
        answer = QW.QMessageBox.question(
            self,
            _("Remove"),
            one if len(indexes) == 1 else more,
            QW.QMessageBox.Yes | QW.QMessageBox.No,
        )
        if answer == QW.QMessageBox.Yes:
            idx_rows = unsorted_unique([idx.row() for idx in indexes])
            keys = [self.model.keys[idx_row] for idx_row in idx_rows]
            self.remove_values(keys)

    def copy_item(self, erase_original=False):
        """Copy item"""
        indexes = self.selectedIndexes()
        if not indexes:
            return
        idx_rows = unsorted_unique([idx.row() for idx in indexes])
        if len(idx_rows) > 1 or not indexes[0].isValid():
            return
        orig_key = self.model.keys[idx_rows[0]]
        if erase_original:
            title = _("Rename")
            field_text = _("New variable name:")
        else:
            title = _("Duplicate")
            field_text = _("Variable name:")
        data = self.model.get_data()
        if isinstance(data, (list, set)):
            new_key, valid = len(data), True
        else:
            new_key, valid = QW.QInputDialog.getText(
                self, title, field_text, QW.QLineEdit.Normal, orig_key
            )
        if valid and str(new_key):
            new_key = try_to_eval(str(new_key))
            if new_key == orig_key:
                return
            self.copy_value(orig_key, new_key)
            if erase_original:
                self.remove_values([orig_key])

    @QC.Slot()
    def duplicate_item(self):
        """Duplicate item"""
        self.copy_item()

    @QC.Slot()
    def rename_item(self):
        """Rename item"""
        self.copy_item(True)

    @QC.Slot()
    def insert_item(self):
        """Insert item"""
        index = self.currentIndex()
        if not index.isValid():
            row = self.model.rowCount()
        else:
            row = index.row()
        data = self.model.get_data()
        if isinstance(data, list):
            key = row
            data.insert(row, "")
        elif isinstance(data, dict):
            key, valid = QW.QInputDialog.getText(
                self, _("Insert"), _("Key:"), QW.QLineEdit.Normal
            )
            if valid and str(key):
                key = try_to_eval(str(key))
            else:
                return
        else:
            return
        value, valid = QW.QInputDialog.getText(
            self, _("Insert"), _("Value:"), QW.QLineEdit.Normal
        )
        if valid and str(value):
            self.new_value(key, try_to_eval(str(value)))

    def __prepare_plot(self):
        try:
            import plotpy.widgets.plot.interactive  # analysis:ignore

            return True
        except ModuleNotFoundError:
            try:
                if "matplotlib" not in sys.modules:
                    import matplotlib

                    matplotlib.use("Qt4Agg")
                return True
            except ModuleNotFoundError:
                QW.QMessageBox.warning(
                    self,
                    _("Import error"),
                    _("Please install <b>matplotlib</b>" " or <b>plotpy</b>."),
                )

    def plot_item(self, funcname):
        """Plot item"""
        index = self.currentIndex()
        if self.__prepare_plot():
            key = self.model.get_key(index)
            try:
                self.plot(key, funcname)
            except (ValueError, TypeError) as error:
                QW.QMessageBox.critical(
                    self,
                    _("Plot"),
                    _("<b>Unable to plot data.</b>" "<br><br>Error message:<br>%s")
                    % str(error),
                )

    @QC.Slot()
    def imshow_item(self):
        """Imshow item"""
        index = self.currentIndex()
        if self.__prepare_plot():
            key = self.model.get_key(index)
            try:
                if self.is_image(key):
                    self.show_image(key)
                else:
                    self.imshow(key)
            except (ValueError, TypeError) as error:
                QW.QMessageBox.critical(
                    self,
                    _("Plot"),
                    _("<b>Unable to show image.</b>" "<br><br>Error message:<br>%s")
                    % str(error),
                )

    @QC.Slot()
    def save_array(self):
        """Save array"""
        title = _("Save array")
        if self.array_filename is None:
            self.array_filename = getcwd_or_home()
        self.redirect_stdio.emit(False)
        filename, _selfilter = QW.QFileDialog.getSaveFileName(
            self, title, self.array_filename, _("NumPy arrays") + " (*.npy)"
        )
        self.redirect_stdio.emit(True)
        if filename:
            self.array_filename = filename
            data = self.delegate.get_value(self.currentIndex())
            try:
                import numpy as np

                np.save(self.array_filename, data)
            except Exception as error:
                QW.QMessageBox.critical(
                    self,
                    title,
                    _("<b>Unable to save array</b>" "<br><br>Error message:<br>%s")
                    % str(error),
                )

    @QC.Slot()
    def copy(self):
        """Copy text to clipboard"""
        clipboard = QW.QApplication.clipboard()
        clipl = []
        for idx in self.selectedIndexes():
            if not idx.isValid():
                continue
            obj = self.delegate.get_value(idx)
            # Check if we are trying to copy a numpy array, and if so make sure
            # to copy the whole thing in a tab separated format
            if isinstance(obj, (ndarray, MaskedArray)) and ndarray is not FakeObject:
                output = io.BytesIO()
                try:
                    np_savetxt(output, obj, delimiter="\t")
                except:
                    QW.QMessageBox.warning(
                        self,
                        _("Warning"),
                        _("It was not possible to copy " "this array"),
                    )
                    return
                obj = output.getvalue().decode("utf-8")
                output.close()
            elif isinstance(obj, (DataFrame, Series)) and DataFrame is not FakeObject:
                output = io.StringIO()
                try:
                    obj.to_csv(output, sep="\t", index=True, header=True)
                except Exception:
                    QW.QMessageBox.warning(
                        self,
                        _("Warning"),
                        _("It was not possible to copy " "this dataframe"),
                    )
                    return
                obj = output.getvalue()
                output.close()
            elif isinstance(obj, bytes):
                obj = str(obj, "utf8")
            else:
                obj = str(obj)
            clipl.append(obj)
        clipboard.setText("\n".join(clipl))

    def import_from_string(self, text, title=None):
        """Import data from string"""
        data = self.model.get_data()
        # Check if data is a dict
        if not hasattr(data, "keys"):
            return
        editor = ImportWizard(
            self,
            text,
            title=title,
            contents_title=_("Clipboard contents"),
            varname=fix_reference_name("data", blacklist=list(data.keys())),
        )
        if editor.exec_():
            var_name, clip_data = editor.get_data()
            self.new_value(var_name, clip_data)

    @QC.Slot()
    def paste(self):
        """Import text/data/code from clipboard"""
        clipboard = QW.QApplication.clipboard()
        cliptext = ""
        if clipboard.mimeData().hasText():
            cliptext = str(clipboard.text())
        if cliptext.strip():
            self.import_from_string(cliptext, title=_("Import from clipboard"))
        else:
            QW.QMessageBox.warning(
                self, _("Empty clipboard"), _("Nothing to be imported from clipboard.")
            )


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
        return isinstance(data[key], (ndarray, MaskedArray))

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
        data = self.model.get_data()
        from plotpy.widgets.variableexplorer.objecteditor import oedit

        oedit(data[key])

    def plot(self, key, funcname):
        """Plot item"""
        data = self.model.get_data()
        import plotpy.widgets.plot.interactive as plt

        plt.figure()
        getattr(plt, funcname)(data[key])
        plt.show()

    def imshow(self, key):
        """Show item's image"""
        data = self.model.get_data()
        import plotpy.widgets.plot.interactive as plt

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
