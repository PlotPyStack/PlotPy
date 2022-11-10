# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
plotpy.gui.dataset.qtwidgets
============================

Dialog boxes used to edit data sets:
    DataSetEditDialog
    DataSetGroupEditDialog
    DataSetShowDialog

...and layouts:
    GroupItem
    DataSetEditLayout
    DataSetShowLayout
"""

try:
    # PyQt4 4.3.3 on Windows (static DLLs) with py2exe installed:
    # -> pythoncom must be imported first, otherwise py2exe's boot_com_servers
    #    will raise an exception ("Unable to load DLL [...]") when calling any
    #    of the QFileDialog static methods (getOpenFileName, ...)
    import pythoncom
except ImportError:
    pass

from gettext import gettext as _

from plotpy.core.dataset.dataitems import (
    BoolItem,
    ButtonItem,
    ChoiceItem,
    ColorItem,
    DateItem,
    DateTimeItem,
    DirectoryItem,
    FileOpenItem,
    FileSaveItem,
    FilesOpenItem,
    FloatArrayItem,
    FloatItem,
    ImageChoiceItem,
    IntItem,
    MultipleChoiceItem,
    StringItem,
    TextItem,
)
from plotpy.core.dataset.datatypes import (
    BeginGroup,
    DataSetGroup,
    EndGroup,
    GroupItem,
    TabGroupItem,
)
from plotpy.gui.config.misc import get_icon
from plotpy.gui.dataset.dataitems import DictItem

# Enregistrement des correspondances avec les widgets
from plotpy.gui.dataset.qtitemwidgets import (
    AbstractDataSetWidget,
    ButtonWidget,
    CheckBoxWidget,
    ChoiceWidget,
    ColorWidget,
    DateTimeWidget,
    DateWidget,
    DirectoryWidget,
    FileWidget,
    FloatArrayWidget,
    FloatSliderWidget,
    GroupWidget,
    LineEditWidget,
    MultipleChoiceWidget,
    SliderWidget,
    TabGroupWidget,
    TextEditWidget,
)
from plotpy.gui.widgets.dialog import (
    get_open_filename,
    get_open_filenames,
    get_save_filename,
)
from plotpy.gui.widgets.ext_gui_lib import (
    QApplication,
    QBrush,
    QColor,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QIcon,
    QLabel,
    QMessageBox,
    QPainter,
    QPicture,
    QPushButton,
    QRect,
    QSize,
    QSpacerItem,
    Qt,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    Signal,
)


class DataSetEditDialog(QDialog):
    """
    Dialog box for DataSet editing
    """

    def __init__(
        self, instance, icon="", parent=None, apply=None, wordwrap=True, size=None
    ):
        QDialog.__init__(self, parent)
        self.wordwrap = wordwrap
        self.apply_func = apply
        self.layout = QVBoxLayout()
        if instance.get_comment():
            label = QLabel(instance.get_comment())
            label.setWordWrap(wordwrap)
            self.layout.addWidget(label)
        self.instance = instance
        self.edit_layout = []

        self.setup_instance(instance)

        if apply is not None:
            apply_button = QDialogButtonBox.Apply
        else:
            apply_button = QDialogButtonBox.NoButton
        bbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | apply_button
        )
        self.bbox = bbox
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        bbox.clicked.connect(self.button_clicked)
        self.layout.addWidget(bbox)

        self.setLayout(self.layout)

        if not isinstance(icon, QIcon):
            icon = get_icon(icon, default="guidata.svg")
        self.setWindowIcon(icon)

        self.setModal(True)
        self.setWindowTitle(instance.get_title())

        if size is not None:
            if isinstance(size, QSize):
                self.resize(size)
            else:
                self.resize(*size)

    def button_clicked(self, button):
        """

        :param button:
        """
        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole and self.apply_func is not None:
            if self.check():
                for edl in self.edit_layout:
                    edl.accept_changes()
                self.apply_func(self.instance)

    def setup_instance(self, instance):
        """Construct main layout"""
        grid = QGridLayout()
        grid.setAlignment(Qt.AlignTop)
        self.layout.addLayout(grid)
        self.edit_layout.append(self.layout_factory(instance, grid))

    def layout_factory(self, instance, grid):
        """A factory method that produces instances of DataSetEditLayout

        or derived classes (see DataSetShowDialog)
        """
        return DataSetEditLayout(self, instance, grid)

    def child_title(self, item):
        """Return data item title combined with QApplication title"""
        app_name = QApplication.applicationName()
        if not app_name:
            app_name = self.instance.get_title()
        return "{} - {}".format(app_name, item.label())

    def check(self):
        """

        :return:
        """
        is_ok = True
        for edl in self.edit_layout:
            if not edl.check_all_values():
                is_ok = False
        if not is_ok:
            QMessageBox.warning(
                self,
                self.instance.get_title(),
                _("Some required entries are incorrect")
                + "\n"
                + _("Please check highlighted fields."),
            )
            return False
        return True

    def accept(self):
        """Validate inputs"""
        if self.check():
            for edl in self.edit_layout:
                edl.accept_changes()
            QDialog.accept(self)


class DataSetGroupEditDialog(DataSetEditDialog):
    """
    Tabbed dialog box for DataSet editing
    """

    def setup_instance(self, instance):
        """Override DataSetEditDialog method"""
        assert isinstance(instance, DataSetGroup)
        tabs = QTabWidget()
        #        tabs.setUsesScrollButtons(False)
        self.layout.addWidget(tabs)
        for dataset in instance.datasets:
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)
            if dataset.get_comment():
                label = QLabel(dataset.get_comment())
                label.setWordWrap(self.wordwrap)
                layout.addWidget(label)
            grid = QGridLayout()
            self.edit_layout.append(self.layout_factory(dataset, grid))
            layout.addLayout(grid)
            page = QWidget()
            page.setLayout(layout)
            if dataset.get_icon():
                tabs.addTab(page, get_icon(dataset.get_icon()), dataset.get_title())
            else:
                tabs.addTab(page, dataset.get_title())


class DataSetEditLayout(object):
    """
    Layout in which data item widgets are placed
    """

    _widget_factory = {}

    @classmethod
    def register(cls, item_type, factory):
        """Register a factory for a new item_type"""
        cls._widget_factory[item_type] = factory

    def __init__(self, parent, instance, layout, items=None, first_line=0):
        self.parent = parent
        self.instance = instance
        self.layout = layout
        self.first_line = first_line
        self.widgets = []
        self.linenos = {}  # prochaine ligne à remplir par colonne
        self.items_pos = {}
        if not items:
            items = self.instance._items
        items = self.transform_items(items)
        self.setup_layout(items)

    def transform_items(self, items):
        """
        Handle group of items: transform items into a GroupItem instance
        if they are located between BeginGroup and EndGroup
        """
        item_lists = [[]]
        for item in items:
            if isinstance(item, BeginGroup):
                item = item.get_group()
                item_lists[-1].append(item)
                item_lists.append(item.group)
            elif isinstance(item, EndGroup):
                item_lists.pop()
            else:
                item_lists[-1].append(item)
        assert len(item_lists) == 1
        return item_lists[-1]

    def check_all_values(self):
        """Check input of all widgets"""
        for widget in self.widgets:
            if widget.is_active() and not widget.check():
                return False
        return True

    def accept_changes(self):
        """Accept changes made to widget inputs"""
        self.update_dataitems()

    def setup_layout(self, items):
        """Place items on layout"""

        def last_col(col, span):
            """Return last column (which depends on column span)"""
            if not span:
                return col
            else:
                return col + span - 1

        colmax = max(
            [
                last_col(
                    item.get_prop("display", "col"), item.get_prop("display", "colspan")
                )
                for item in items
            ]
        )
        self.items_pos = {}
        line = self.first_line - 1
        last_item = [-1, 0, colmax]
        for item in items:
            beg = item.get_prop("display", "col")
            span = item.get_prop("display", "colspan")
            if span is None:
                span = colmax - beg + 1
            if beg <= last_item[1]:
                # on passe à la ligne si la colonne de debut de cet item
                #  est avant la colonne de debut de l'item précédent
                line += 1
            else:
                last_item[2] = beg - last_item[1]
            last_item = [line, beg, span]
            self.items_pos[item] = last_item

        for item in items:
            hide = item.get_prop_value("display", self.instance, "hide", False)
            if hide:
                continue
            widget = self.build_widget(item)
            self.add_row(widget)

        self.refresh_widgets()

    def build_widget(self, item):
        """

        :param item:
        :return:
        """
        factory = self._widget_factory[type(item)]
        widget = factory(item.bind(self.instance), self)
        self.widgets.append(widget)
        return widget

    def add_row(self, widget):
        """Add widget to row"""
        item = widget.item
        line, col, span = self.items_pos[item.item]
        if col > 0:
            self.layout.addItem(QSpacerItem(20, 1), line, col * 3 - 1)

        widget.place_on_grid(self.layout, line, col * 3, col * 3 + 1, 1, 3 * span - 2)
        try:
            widget.get()
        except Exception:
            print("Error building item :", item.item._name)
            raise

    def refresh_widgets(self):
        """Refresh the status of all widgets"""
        for widget in self.widgets:
            widget.set_state()

    def update_dataitems(self):
        """Refresh the content of all data items"""
        for widget in self.widgets:
            if widget.is_active():
                widget.set()

    def update_widgets(self, except_this_one=None):
        """Refresh the content of all widgets"""
        for widget in self.widgets:
            if widget is not except_this_one:
                widget.get()


DataSetEditLayout.register(GroupItem, GroupWidget)
DataSetEditLayout.register(TabGroupItem, TabGroupWidget)
DataSetEditLayout.register(FloatItem, LineEditWidget)
DataSetEditLayout.register(StringItem, LineEditWidget)
DataSetEditLayout.register(TextItem, TextEditWidget)
DataSetEditLayout.register(IntItem, SliderWidget)
DataSetEditLayout.register(FloatItem, FloatSliderWidget)
DataSetEditLayout.register(BoolItem, CheckBoxWidget)
DataSetEditLayout.register(DateItem, DateWidget)
DataSetEditLayout.register(DateTimeItem, DateTimeWidget)
DataSetEditLayout.register(ColorItem, ColorWidget)
DataSetEditLayout.register(
    FileOpenItem, lambda item, parent: FileWidget(item, parent, get_open_filename)
)
DataSetEditLayout.register(
    FilesOpenItem, lambda item, parent: FileWidget(item, parent, get_open_filenames)
)
DataSetEditLayout.register(
    FileSaveItem, lambda item, parent: FileWidget(item, parent, get_save_filename)
)
DataSetEditLayout.register(DirectoryItem, DirectoryWidget)
DataSetEditLayout.register(ChoiceItem, ChoiceWidget)
DataSetEditLayout.register(ImageChoiceItem, ChoiceWidget)
DataSetEditLayout.register(MultipleChoiceItem, MultipleChoiceWidget)
DataSetEditLayout.register(FloatArrayItem, FloatArrayWidget)
DataSetEditLayout.register(ButtonItem, ButtonWidget)
DataSetEditLayout.register(DictItem, ButtonWidget)


LABEL_CSS = """
QLabel { font-weight: bold; color: blue }
QLabel:disabled { font-weight: bold; color: grey }
"""


class DataSetShowWidget(AbstractDataSetWidget):
    """Read-only base widget"""

    READ_ONLY = True

    def __init__(self, item, parent_layout):
        AbstractDataSetWidget.__init__(self, item, parent_layout)
        self.group = QLabel()
        wordwrap = item.get_prop_value("display", "wordwrap", False)
        self.group.setWordWrap(wordwrap)
        self.group.setToolTip(item.get_help())
        self.group.setStyleSheet(LABEL_CSS)
        self.group.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # self.group.setEnabled(False)

    def get(self):
        """Override AbstractDataSetWidget method"""
        self.set_state()
        text = self.item.get_string_value()
        self.group.setText(text)

    def set(self):
        """Read only..."""
        pass


class ShowColorWidget(DataSetShowWidget):
    """Read-only color item widget"""

    def __init__(self, item, parent_layout):
        DataSetShowWidget.__init__(self, item, parent_layout)
        self.picture = None

    def get(self):
        """Override AbstractDataSetWidget method"""
        value = self.item.get()
        if value is not None:
            color = QColor(value)
            self.picture = QPicture()
            painter = QPainter()
            painter.begin(self.picture)
            painter.fillRect(QRect(0, 0, 60, 20), QBrush(color))
            painter.end()
            self.group.setPicture(self.picture)


class ShowBooleanWidget(DataSetShowWidget):
    """Read-only bool item widget"""

    def place_on_grid(
        self, layout, row, label_column, widget_column, row_span=1, column_span=1
    ):
        """Override AbstractDataSetWidget method"""
        if not self.item.get_prop_value("display", "label"):
            widget_column = label_column
            column_span += 1
        else:
            self.place_label(layout, row, label_column)
        layout.addWidget(self.group, row, widget_column, row_span, column_span)

    def get(self):
        """Override AbstractDataSetWidget method"""
        # DataSetShowWidget.get(self)
        text = self.item.get_prop_value("display", "text")
        self.group.setText(text)
        font = self.group.font()
        value = self.item.get()
        state = bool(value)
        font.setStrikeOut(not state)
        self.group.setFont(font)
        self.group.setEnabled(state)


class DataSetShowLayout(DataSetEditLayout):
    """Read-only layout"""

    _widget_factory = {}


class DataSetShowDialog(DataSetEditDialog):
    """Read-only dialog box"""

    def layout_factory(self, instance, grid):
        """Override DataSetEditDialog method"""
        return DataSetShowLayout(self, instance, grid)


DataSetShowLayout.register(GroupItem, GroupWidget)
DataSetShowLayout.register(TabGroupItem, TabGroupWidget)
DataSetShowLayout.register(FloatItem, DataSetShowWidget)
DataSetShowLayout.register(StringItem, DataSetShowWidget)
DataSetShowLayout.register(TextItem, DataSetShowWidget)
DataSetShowLayout.register(IntItem, DataSetShowWidget)
DataSetShowLayout.register(BoolItem, ShowBooleanWidget)
DataSetShowLayout.register(DateItem, DataSetShowWidget)
DataSetShowLayout.register(DateTimeItem, DataSetShowWidget)
DataSetShowLayout.register(ColorItem, ShowColorWidget)
DataSetShowLayout.register(FileOpenItem, DataSetShowWidget)
DataSetShowLayout.register(FilesOpenItem, DataSetShowWidget)
DataSetShowLayout.register(FileSaveItem, DataSetShowWidget)
DataSetShowLayout.register(DirectoryItem, DataSetShowWidget)
DataSetShowLayout.register(ChoiceItem, DataSetShowWidget)
DataSetShowLayout.register(ImageChoiceItem, DataSetShowWidget)
DataSetShowLayout.register(MultipleChoiceItem, DataSetShowWidget)
DataSetShowLayout.register(FloatArrayItem, DataSetShowWidget)


class DataSetShowWidget(QWidget):
    """widget showing a read-only DataSet"""

    def __init__(self, klass, wordwrap=False, **kwargs):
        QWidget.__init__(self)
        self.klass = klass
        self.dataset = klass(**kwargs)
        self.layout = QVBoxLayout()
        if self.dataset.get_comment():
            label = QLabel(self.dataset.get_comment())
            label.setWordWrap(wordwrap)
            self.layout.addWidget(label)
        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)
        self.setLayout(self.layout)
        self.edit = self.get_edit_layout()

    def get_edit_layout(self):
        """Return edit layout"""
        return DataSetShowLayout(self, self.dataset, self.grid_layout)

    def get(self):
        """Update group box contents from data item values"""
        for widget in self.edit.widgets:
            widget.build_mode = True
            widget.get()
            widget.build_mode = False


class DataSetEditWidget(DataSetShowWidget):
    """
    Widget including a DataSet

    klass: guidata.DataSet class
    button_text: action button text (default: "Apply")
    button_icon: QIcon object or string (default "apply.png")
    """

    #: Signal emitted when Apply button is clicked
    SIG_APPLY_BUTTON_CLICKED = Signal()

    def __init__(self, klass, button_text=None, button_icon=None,
                 show_button=True, wordwrap=False, **kwargs):
        DataSetShowWidget.__init__(self, klass, wordwrap=wordwrap,
                                   **kwargs)
        if show_button:
            if button_text is None:
                button_text = _("Apply")
            if button_icon is None:
                button_icon = get_icon("apply.png")
            elif isinstance(button_icon, str):
                button_icon = get_icon(button_icon)
            apply_btn = QPushButton(button_icon, button_text, self)
            apply_btn.clicked.connect(self.set)
            layout = self.edit.layout
            layout.addWidget(apply_btn, layout.rowCount(),
                             0, 1, -1, Qt.AlignRight)

    def get_edit_layout(self):
        """Return edit layout"""
        return DataSetEditLayout(self, self.dataset, self.grid_layout)

    def set(self, check=True):
        """Update data item values from layout contents"""
        for widget in self.edit.widgets:
            if widget.is_active():
                if not check or widget.check():
                    widget.set()
        self.SIG_APPLY_BUTTON_CLICKED.emit()

    def child_title(self, item):
        """Return data item title combined with QApplication title"""
        app_name = QApplication.applicationName()
        if not app_name:
            app_name = str(self.title())
        return "%s - %s" % (app_name, item.label())


class DataSetShowGroupBox(QGroupBox):
    """Group box widget showing a read-only DataSet"""

    def __init__(self, label, klass, wordwrap=False, **kwargs):
        QGroupBox.__init__(self, label)
        self.klass = klass
        self.dataset = klass(**kwargs)
        self.layout = QVBoxLayout()
        if self.dataset.get_comment():
            label = QLabel(self.dataset.get_comment())
            label.setWordWrap(wordwrap)
            self.layout.addWidget(label)
        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)
        self.setLayout(self.layout)
        self.edit = self.get_edit_layout()

    def get_edit_layout(self):
        """Return edit layout"""
        return DataSetShowLayout(self, self.dataset, self.grid_layout)

    def get(self):
        """Update group box contents from data item values"""
        for widget in self.edit.widgets:
            widget.build_mode = True
            widget.get()
            widget.build_mode = False


class DataSetEditGroupBox(DataSetShowGroupBox):
    """
    Group box widget including a DataSet

    label: group box label (string)
    klass: plotpy.core.dataset.DataSet class
    button_text: action button text (default: "Apply")
    button_icon: QIcon object or string (default "apply.png")
    """

    #: Signal emitted when Apply button is clicked
    SIG_APPLY_BUTTON_CLICKED = Signal()

    def __init__(
        self,
        label,
        klass,
        button_text=None,
        button_icon=None,
        show_button=True,
        wordwrap=False,
        **kwargs
    ):
        DataSetShowGroupBox.__init__(self, label, klass, wordwrap=wordwrap, **kwargs)
        if show_button:
            if button_text is None:
                button_text = _("Apply")
            if button_icon is None:
                button_icon = get_icon("apply.png")
            elif isinstance(button_icon, str):
                button_icon = get_icon(button_icon)
            apply_btn = QPushButton(button_icon, button_text, self)
            apply_btn.clicked.connect(self.set)
            layout = self.edit.layout
            layout.addWidget(apply_btn, layout.rowCount(), 0, 1, -1, Qt.AlignRight)

    def get_edit_layout(self):
        """Return edit layout"""
        return DataSetEditLayout(self, self.dataset, self.grid_layout)

    def set(self, check=True):
        """Update data item values from layout contents"""
        for widget in self.edit.widgets:
            if widget.is_active():
                if not check or widget.check():
                    widget.set()
        self.SIG_APPLY_BUTTON_CLICKED.emit()


    def child_title(self, item):
        """Return data item title combined with QApplication title"""
        app_name = QApplication.applicationName()
        if not app_name:
            app_name = str(self.title())
        return "{} - {}".format(app_name, item.label())
