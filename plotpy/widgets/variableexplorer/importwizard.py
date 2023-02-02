# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Text data Importing Wizard based on Qt
"""


# ----date and datetime objects support
import datetime
import io
from functools import partial as ft_partial
from itertools import zip_longest

import pandas as pd
from guidata.configtools import get_icon
from numpy import array, nan, ndarray
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.misc_from_gui import add_actions, create_action
from plotpy.widgets import qapplication

try:
    from dateutil.parser import parse as dateparse
except ImportError:

    def dateparse(datestr, dayfirst=True):  # analysis:ignore
        """Just for 'day/month/year' strings"""
        _a, _b, _c = list(map(int, datestr.split("/")))
        if dayfirst:
            return datetime.datetime(_c, _b, _a)
        return datetime.datetime(_c, _a, _b)


def try_to_parse(value):
    """

    :param value:
    :return:
    """
    _types = ("int", "float")
    for _t in _types:
        try:
            _val = eval("%s('%s')" % (_t, value))
            return _val
        except (ValueError, SyntaxError):
            pass
    return value


def try_to_eval(value):
    """

    :param value:
    :return:
    """
    try:
        return eval(value)
    except (NameError, SyntaxError, ImportError):
        return value


def datestr_to_datetime(value, dayfirst=True):
    """

    :param value:
    :param dayfirst:
    :return:
    """
    return dateparse(value, dayfirst=dayfirst)


# ----Background colors for supported types
COLORS = {
    bool: QC.Qt.magenta,
    (float, int): QC.Qt.blue,
    list: QC.Qt.yellow,
    dict: QC.Qt.cyan,
    tuple: QC.Qt.lightGray,
    (str,): QC.Qt.darkRed,
    ndarray: QC.Qt.green,
    datetime.date: QC.Qt.darkYellow,
}


def get_color(value, alpha):
    """Return color depending on value type"""
    color = QG.QColor()
    for typ in COLORS:
        if isinstance(value, typ):
            color = QG.QColor(COLORS[typ])
    color.setAlphaF(alpha)
    return color


class ContentsWidget(QW.QWidget):
    """Import wizard contents widget"""

    asDataChanged = QC.Signal(bool)

    def __init__(self, parent, text):
        QW.QWidget.__init__(self, parent)

        self.text_editor = QW.QTextEdit(self)
        self.text_editor.setText(text)
        self.text_editor.setReadOnly(True)

        # Type frame
        type_layout = QW.QHBoxLayout()
        type_label = QW.QLabel(_("Import as"))
        type_layout.addWidget(type_label)
        data_btn = QW.QRadioButton(_("data"))
        data_btn.setChecked(True)
        self._as_data = True
        type_layout.addWidget(data_btn)
        code_btn = QW.QRadioButton(_("code"))
        self._as_code = False
        type_layout.addWidget(code_btn)
        txt_btn = QW.QRadioButton(_("text"))
        type_layout.addWidget(txt_btn)

        h_spacer = QW.QSpacerItem(
            40, 20, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
        )
        type_layout.addItem(h_spacer)
        type_frame = QW.QFrame()
        type_frame.setLayout(type_layout)

        # Opts frame
        grid_layout = QW.QGridLayout()
        grid_layout.setSpacing(0)

        col_label = QW.QLabel(_("Column separator:"))
        grid_layout.addWidget(col_label, 0, 0)
        col_w = QW.QWidget()
        col_btn_layout = QW.QHBoxLayout()
        self.tab_btn = QW.QRadioButton(_("Tab"))
        self.tab_btn.setChecked(False)
        col_btn_layout.addWidget(self.tab_btn)
        self.ws_btn = QW.QRadioButton(_("Whitespace"))
        self.ws_btn.setChecked(False)
        col_btn_layout.addWidget(self.ws_btn)
        other_btn_col = QW.QRadioButton(_("other"))
        other_btn_col.setChecked(True)
        col_btn_layout.addWidget(other_btn_col)
        col_w.setLayout(col_btn_layout)
        grid_layout.addWidget(col_w, 0, 1)
        self.line_edt = QW.QLineEdit(",")
        self.line_edt.setMaximumWidth(30)
        self.line_edt.setEnabled(True)
        other_btn_col.toggled.connect(self.line_edt.setEnabled)
        grid_layout.addWidget(self.line_edt, 0, 2)

        row_label = QW.QLabel(_("Row separator:"))
        grid_layout.addWidget(row_label, 1, 0)
        row_w = QW.QWidget()
        row_btn_layout = QW.QHBoxLayout()
        self.eol_btn = QW.QRadioButton(_("EOL"))
        self.eol_btn.setChecked(True)
        row_btn_layout.addWidget(self.eol_btn)
        other_btn_row = QW.QRadioButton(_("other"))
        row_btn_layout.addWidget(other_btn_row)
        row_w.setLayout(row_btn_layout)
        grid_layout.addWidget(row_w, 1, 1)
        self.line_edt_row = QW.QLineEdit(";")
        self.line_edt_row.setMaximumWidth(30)
        self.line_edt_row.setEnabled(False)
        other_btn_row.toggled.connect(self.line_edt_row.setEnabled)
        grid_layout.addWidget(self.line_edt_row, 1, 2)

        grid_layout.setRowMinimumHeight(2, 15)

        other_group = QW.QGroupBox(_("Additional options"))
        other_layout = QW.QGridLayout()
        other_group.setLayout(other_layout)

        skiprows_label = QW.QLabel(_("Skip rows:"))
        other_layout.addWidget(skiprows_label, 0, 0)
        self.skiprows_edt = QW.QLineEdit("0")
        self.skiprows_edt.setMaximumWidth(30)
        intvalid = QG.QIntValidator(0, len(str(text).splitlines()), self.skiprows_edt)
        self.skiprows_edt.setValidator(intvalid)
        other_layout.addWidget(self.skiprows_edt, 0, 1)

        other_layout.setColumnMinimumWidth(2, 5)

        comments_label = QW.QLabel(_("Comments:"))
        other_layout.addWidget(comments_label, 0, 3)
        self.comments_edt = QW.QLineEdit("#")
        self.comments_edt.setMaximumWidth(30)
        other_layout.addWidget(self.comments_edt, 0, 4)

        self.trnsp_box = QW.QCheckBox(_("Transpose"))
        # self.trnsp_box.setEnabled(False)
        other_layout.addWidget(self.trnsp_box, 1, 0, 2, 0)

        grid_layout.addWidget(other_group, 3, 0, 2, 0)

        opts_frame = QW.QFrame()
        opts_frame.setLayout(grid_layout)

        data_btn.toggled.connect(opts_frame.setEnabled)
        data_btn.toggled.connect(self.set_as_data)
        code_btn.toggled.connect(self.set_as_code)
        #        self.connect(txt_btn, SIGNAL("toggled(bool)"),
        #                     self, SLOT("is_text(bool)"))

        # Final layout
        layout = QW.QVBoxLayout()
        layout.addWidget(type_frame)
        layout.addWidget(self.text_editor)
        layout.addWidget(opts_frame)
        self.setLayout(layout)

    def get_as_data(self):
        """Return if data type conversion"""
        return self._as_data

    def get_as_code(self):
        """Return if code type conversion"""
        return self._as_code

    def get_as_num(self):
        """Return if numeric type conversion"""
        return self._as_num

    def get_col_sep(self):
        """Return the column separator"""
        if self.tab_btn.isChecked():
            return "\t"
        elif self.ws_btn.isChecked():
            return None
        return str(self.line_edt.text())

    def get_row_sep(self):
        """Return the row separator"""
        if self.eol_btn.isChecked():
            return "\n"
        return str(self.line_edt_row.text())

    def get_skiprows(self):
        """Return number of lines to be skipped"""
        return int(str(self.skiprows_edt.text()))

    def get_comments(self):
        """Return comment string"""
        return str(self.comments_edt.text())

    @QC.Slot(bool)
    def set_as_data(self, as_data):
        """Set if data type conversion"""
        self._as_data = as_data
        self.asDataChanged.emit(as_data)

    @QC.Slot(bool)
    def set_as_code(self, as_code):
        """Set if code type conversion"""
        self._as_code = as_code


class PreviewTableModel(QC.QAbstractTableModel):
    """Import wizard preview table model"""

    def __init__(self, data=[], parent=None):
        QC.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, _parent=QC.QModelIndex()):
        """Return row count"""
        return len(self._data)

    def columnCount(self, _parent=QC.QModelIndex()):
        """Return column count"""
        return len(self._data[0])

    def _display_data(self, index):
        """Return a data element"""
        return self._data[index.row()][index.column()]

    def data(self, index, role=QC.Qt.DisplayRole):
        """Return a model data element"""
        if not index.isValid():
            return None
        if role == QC.Qt.DisplayRole:
            return self._display_data(index)
        elif role == QC.Qt.BackgroundColorRole:
            return get_color(self._data[index.row()][index.column()], 0.2)
        elif role == QC.Qt.TextAlignmentRole:
            return int(QC.Qt.AlignRight | QC.Qt.AlignVCenter)
        return None

    def setData(self, _index, _value, _role=QC.Qt.EditRole):
        """Set model data"""
        return False

    def get_data(self):
        """Return a copy of model data"""
        return self._data[:][:]

    def parse_data_type(self, index, **kwargs):
        """Parse a type to an other type"""
        if not index.isValid():
            return False
        try:
            if kwargs["atype"] == "date":
                self._data[index.row()][index.column()] = datestr_to_datetime(
                    self._data[index.row()][index.column()], kwargs["dayfirst"]
                ).date()
            elif kwargs["atype"] == "perc":
                _tmp = self._data[index.row()][index.column()].replace("%", "")
                self._data[index.row()][index.column()] = eval(_tmp) / 100.0
            elif kwargs["atype"] == "account":
                _tmp = self._data[index.row()][index.column()].replace(",", "")
                self._data[index.row()][index.column()] = eval(_tmp)
            elif kwargs["atype"] == "unicode":
                self._data[index.row()][index.column()] = str(
                    self._data[index.row()][index.column()]
                )
            elif kwargs["atype"] == "int":
                self._data[index.row()][index.column()] = int(
                    self._data[index.row()][index.column()]
                )
            elif kwargs["atype"] == "float":
                self._data[index.row()][index.column()] = float(
                    self._data[index.row()][index.column()]
                )
            self.dataChanged.emit(index, index)
        except Exception as instance:
            print(instance)  # spyder: test-skip

    def reset(self):
        """ """
        self.beginResetModel()
        self.endResetModel()


class PreviewTable(QW.QTableView):
    """Import wizard preview widget"""

    def __init__(self, parent):
        QW.QTableView.__init__(self, parent)
        self._model = None

        # Setting up actions
        self.date_dayfirst_action = create_action(
            self,
            "dayfirst",
            triggered=ft_partial(self.parse_to_type, atype="date", dayfirst=True),
        )
        self.date_monthfirst_action = create_action(
            self,
            "monthfirst",
            triggered=ft_partial(self.parse_to_type, atype="date", dayfirst=False),
        )
        self.perc_action = create_action(
            self, "perc", triggered=ft_partial(self.parse_to_type, atype="perc")
        )
        self.acc_action = create_action(
            self, "account", triggered=ft_partial(self.parse_to_type, atype="account")
        )
        self.str_action = create_action(
            self, "unicode", triggered=ft_partial(self.parse_to_type, atype="unicode")
        )
        self.int_action = create_action(
            self, "int", triggered=ft_partial(self.parse_to_type, atype="int")
        )
        self.float_action = create_action(
            self, "float", triggered=ft_partial(self.parse_to_type, atype="float")
        )

        # Setting up menus
        self.date_menu = QW.QMenu()
        self.date_menu.setTitle("Date")
        add_actions(
            self.date_menu, (self.date_dayfirst_action, self.date_monthfirst_action)
        )
        self.parse_menu = QW.QMenu(self)
        self.parse_menu.addMenu(self.date_menu)
        add_actions(self.parse_menu, (self.perc_action, self.acc_action))
        self.parse_menu.setTitle("String to")
        self.opt_menu = QW.QMenu(self)
        self.opt_menu.addMenu(self.parse_menu)
        add_actions(
            self.opt_menu, (self.str_action, self.int_action, self.float_action)
        )

    def _shape_text(
        self,
        text,
        colsep="\t",
        rowsep="\n",
        transpose=False,
        skiprows=0,
        comments="#",
    ):
        """Decode the shape of the given text"""
        assert colsep != rowsep
        out = []
        text_rows = text.split(rowsep)[skiprows:]
        for row in text_rows:
            stripped = str(row).strip()
            if len(stripped) == 0 or stripped.startswith(comments):
                continue
            line = str(row).split(colsep)
            line = [try_to_parse(str(x)) for x in line]
            out.append(line)
        # Replace missing elements with np.nan's or None's

        out = list(zip_longest(*out, fillvalue=nan))

        # Tranpose the last result to get the expected one
        out = [[r[col] for r in out] for col in range(len(out[0]))]
        if transpose:
            return [[r[col] for r in out] for col in range(len(out[0]))]
        return out

    def get_data(self):
        """Return model data"""
        if self._model is None:
            return None
        return self._model.get_data()

    def process_data(
        self,
        text,
        colsep="\t",
        rowsep="\n",
        transpose=False,
        skiprows=0,
        comments="#",
    ):
        """Put data into table model"""
        data = self._shape_text(text, colsep, rowsep, transpose, skiprows, comments)
        self._model = PreviewTableModel(data)
        self.setModel(self._model)

    @QC.Slot()
    def parse_to_type(self, **kwargs):
        """Parse to a given type"""
        indexes = self.selectedIndexes()
        if not indexes:
            return
        for index in indexes:
            self.model().parse_data_type(index, **kwargs)

    def contextMenuEvent(self, event):
        """Reimplement Qt method"""
        self.opt_menu.popup(event.globalPos())
        event.accept()


class PreviewWidget(QW.QWidget):
    """Import wizard preview widget"""

    def __init__(self, parent):
        QW.QWidget.__init__(self, parent)

        vert_layout = QW.QVBoxLayout()

        # Type frame
        type_layout = QW.QHBoxLayout()
        type_label = QW.QLabel(_("Import as"))
        type_layout.addWidget(type_label)

        self.array_btn = array_btn = QW.QRadioButton(_("array"))
        type_layout.addWidget(array_btn)

        list_btn = QW.QRadioButton(_("list"))
        list_btn.setChecked(not array_btn.isChecked())
        type_layout.addWidget(list_btn)

        if pd:
            self.df_btn = df_btn = QW.QRadioButton(_("DataFrame"))
            df_btn.setChecked(False)
            type_layout.addWidget(df_btn)

        h_spacer = QW.QSpacerItem(
            40, 20, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
        )
        type_layout.addItem(h_spacer)
        type_frame = QW.QFrame()
        type_frame.setLayout(type_layout)

        self._table_view = PreviewTable(self)
        vert_layout.addWidget(type_frame)
        vert_layout.addWidget(self._table_view)
        self.setLayout(vert_layout)

    def open_data(
        self,
        text,
        colsep="\t",
        rowsep="\n",
        transpose=False,
        skiprows=0,
        comments="#",
    ):
        """Open clipboard text as table"""
        if pd:
            self.pd_text = text
            self.pd_info = dict(
                sep=colsep, lineterminator=rowsep, skiprows=skiprows, comment=comments
            )
            if colsep is None:
                self.pd_info = dict(
                    lineterminator=rowsep,
                    skiprows=skiprows,
                    comment=comments,
                    delim_whitespace=True,
                )
        self._table_view.process_data(
            text, colsep, rowsep, transpose, skiprows, comments
        )

    def get_data(self):
        """Return table data"""
        return self._table_view.get_data()


class ImportWizard(QW.QDialog):
    """Text data import wizard"""

    def __init__(
        self, parent, text, title=None, icon=None, contents_title=None, varname=None
    ):
        QW.QDialog.__init__(self, parent)

        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        self.setAttribute(QC.Qt.WA_DeleteOnClose)

        if title is None:
            title = _("Import wizard")
        self.setWindowTitle(title)
        if icon is None:
            self.setWindowIcon(get_icon("fileimport.png"))
        if contents_title is None:
            contents_title = _("Raw text")

        if varname is None:
            varname = _("variable_name")

        self.var_name, self.clip_data = None, None

        # Setting GUI
        self.tab_widget = QW.QTabWidget(self)
        self.text_widget = ContentsWidget(self, text)
        self.table_widget = PreviewWidget(self)

        self.tab_widget.addTab(self.text_widget, _("text"))
        self.tab_widget.setTabText(0, contents_title)
        self.tab_widget.addTab(self.table_widget, _("table"))
        self.tab_widget.setTabText(1, _("Preview"))
        self.tab_widget.setTabEnabled(1, False)

        name_layout = QW.QHBoxLayout()
        name_label = QW.QLabel(_("Variable Name"))
        name_layout.addWidget(name_label)

        self.name_edt = QW.QLineEdit()
        self.name_edt.setText(varname)
        name_layout.addWidget(self.name_edt)

        btns_layout = QW.QHBoxLayout()
        cancel_btn = QW.QPushButton(_("Cancel"))
        btns_layout.addWidget(cancel_btn)
        cancel_btn.clicked.connect(self.reject)
        h_spacer = QW.QSpacerItem(
            40, 20, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
        )
        btns_layout.addItem(h_spacer)
        self.back_btn = QW.QPushButton(_("Previous"))
        self.back_btn.setEnabled(False)
        btns_layout.addWidget(self.back_btn)
        self.back_btn.clicked.connect(ft_partial(self._set_step, step=-1))
        self.fwd_btn = QW.QPushButton(_("Next"))
        if not text:
            self.fwd_btn.setEnabled(False)
        btns_layout.addWidget(self.fwd_btn)
        self.fwd_btn.clicked.connect(ft_partial(self._set_step, step=1))
        self.done_btn = QW.QPushButton(_("Done"))
        self.done_btn.setEnabled(False)
        btns_layout.addWidget(self.done_btn)
        self.done_btn.clicked.connect(self.process)

        self.text_widget.asDataChanged.connect(self.fwd_btn.setEnabled)
        self.text_widget.asDataChanged.connect(self.done_btn.setDisabled)
        layout = QW.QVBoxLayout()
        layout.addLayout(name_layout)
        layout.addWidget(self.tab_widget)
        layout.addLayout(btns_layout)
        self.setLayout(layout)

    def _focus_tab(self, tab_idx):
        """Change tab focus"""
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, False)
        self.tab_widget.setTabEnabled(tab_idx, True)
        self.tab_widget.setCurrentIndex(tab_idx)

    def _set_step(self, step):
        """Proceed to a given step"""
        new_tab = self.tab_widget.currentIndex() + step
        assert new_tab < self.tab_widget.count() and new_tab >= 0
        if new_tab == self.tab_widget.count() - 1:
            try:
                self.table_widget.open_data(
                    self._get_plain_text(),
                    self.text_widget.get_col_sep(),
                    self.text_widget.get_row_sep(),
                    self.text_widget.trnsp_box.isChecked(),
                    self.text_widget.get_skiprows(),
                    self.text_widget.get_comments(),
                )
                self.done_btn.setEnabled(True)
                self.done_btn.setDefault(True)
                self.fwd_btn.setEnabled(False)
                self.back_btn.setEnabled(True)
            except (SyntaxError, AssertionError) as error:
                QW.QMessageBox.critical(
                    self,
                    _("Import wizard"),
                    _(
                        "<b>Unable to proceed to next step</b>"
                        "<br><br>Please check your entries."
                        "<br><br>Error message:<br>%s"
                    )
                    % str(error),
                )
                return
        elif new_tab == 0:
            self.done_btn.setEnabled(False)
            self.fwd_btn.setEnabled(True)
            self.back_btn.setEnabled(False)
        self._focus_tab(new_tab)

    def get_data(self):
        """Return processed data"""
        # It is import to avoid accessing Qt C++ object as it has probably
        # already been destroyed, due to the Qt.WA_DeleteOnClose attribute
        return self.var_name, self.clip_data

    def _simplify_shape(self, alist, rec=0):
        """Reduce the alist dimension if needed"""
        if rec != 0:
            if len(alist) == 1:
                return alist[-1]
            return alist
        if len(alist) == 1:
            return self._simplify_shape(alist[-1], 1)
        return [self._simplify_shape(al, 1) for al in alist]

    def _get_table_data(self):
        """Return clipboard processed as data"""
        data = self._simplify_shape(self.table_widget.get_data())
        if self.table_widget.array_btn.isChecked():
            return array(data)
        elif pd and self.table_widget.df_btn.isChecked():
            info = self.table_widget.pd_info
            buf = io.StringIO(self.table_widget.pd_text)
            return pd.read_csv(buf, **info)
        return data

    def _get_plain_text(self):
        """Return clipboard as text"""
        return self.text_widget.text_editor.toPlainText()

    @QC.Slot()
    def process(self):
        """Process the data from clipboard"""
        var_name = self.name_edt.text()
        try:
            self.var_name = str(var_name)
        except UnicodeEncodeError:
            self.var_name = str(var_name)
        if self.text_widget.get_as_data():
            self.clip_data = self._get_table_data()
        elif self.text_widget.get_as_code():
            self.clip_data = try_to_eval(str(self._get_plain_text()))
        else:
            self.clip_data = str(self._get_plain_text())
        self.accept()


def test(text):
    """Test"""

    _app = qapplication()  # analysis:ignore
    dialog = ImportWizard(None, text)
    if dialog.exec_():
        print(dialog.get_data())  # spyder: test-skip


if __name__ == "__main__":
    test("17/11/1976\t1.34\n14/05/09\t3.14")
