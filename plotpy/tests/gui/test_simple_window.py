# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Simple application based on plotpy"""

# guitest: show

import sys

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset.dataitems import ChoiceItem, FloatArrayItem, IntItem, StringItem
from guidata.dataset.datatypes import DataSet, GetAttrProp, update_dataset
from guidata.dataset.qtwidgets import DataSetEditGroupBox
from guidata.qthelpers import (
    add_actions,
    create_action,
    get_std_icon,
    qt_app_context,
    win32_fix_title_bar_background,
)
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.core import io
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotType, PlotWidget
from plotpy.widgets.about import about

APP_NAME = _("Application example")
VERSION = "1.0.0"


class ImageParam(DataSet):
    _hide_data = False
    _hide_size = True
    title = StringItem(_("Title"), default=_("Untitled"))
    data = FloatArrayItem(_("Data")).set_prop("display", hide=GetAttrProp("_hide_data"))
    width = IntItem(
        _("Width"), help=_("Image width (pixels)"), min=1, default=100
    ).set_prop("display", hide=GetAttrProp("_hide_size"))
    height = IntItem(
        _("Height"), help=_("Image height (pixels)"), min=1, default=100
    ).set_prop("display", hide=GetAttrProp("_hide_size"))


class ImageParamNew(ImageParam):
    _hide_data = True
    _hide_size = False
    type = ChoiceItem(_("Type"), (("rand", _("random")), ("zeros", _("zeros"))))


class ImageListWithProperties(QW.QSplitter):
    def __init__(self, parent):
        QW.QSplitter.__init__(self, parent)
        self.imagelist = QW.QListWidget(self)
        self.addWidget(self.imagelist)
        self.properties = DataSetEditGroupBox(_("Properties"), ImageParam)
        self.properties.setEnabled(False)
        self.addWidget(self.properties)


class CentralWidget(QW.QSplitter):
    def __init__(self, parent, toolbar):
        QW.QSplitter.__init__(self, parent)
        self.setContentsMargins(10, 10, 10, 10)
        self.setOrientation(QC.Qt.Vertical)

        imagelistwithproperties = ImageListWithProperties(self)
        self.addWidget(imagelistwithproperties)
        self.imagelist = imagelistwithproperties.imagelist
        self.imagelist.currentRowChanged.connect(self.current_item_changed)
        self.imagelist.itemSelectionChanged.connect(self.selection_changed)
        self.properties = imagelistwithproperties.properties
        self.properties.SIG_APPLY_BUTTON_CLICKED.connect(self.properties_changed)

        self.plot_widget = PlotWidget(
            self, options={"type": PlotType.IMAGE}, auto_tools=False
        )
        self.plot_widget.plot.SIG_LUT_CHANGED.connect(self.lut_range_changed)
        self.item = None  # image item

        self.plot_widget.manager.add_toolbar(toolbar, "default")
        self.plot_widget.register_tools()

        self.addWidget(self.plot_widget)

        self.images = []  # List of ImageParam instances
        self.lut_ranges = []  # List of LUT ranges

        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setHandleWidth(10)
        self.setSizes([1, 2])

    def refresh_list(self):
        """Refresh image list"""
        self.imagelist.clear()
        self.imagelist.addItems([image.title for image in self.images])

    def selection_changed(self):
        """Image list: selection changed"""
        row = self.imagelist.currentRow()
        self.properties.setDisabled(row == -1)

    def current_item_changed(self, row):
        """Image list: current image changed"""
        image, lut_range = self.images[row], self.lut_ranges[row]
        self.show_data(image.data, lut_range)
        update_dataset(self.properties.dataset, image)
        self.properties.get()

    def lut_range_changed(self):
        """LUT range changed"""
        row = self.imagelist.currentRow()
        self.lut_ranges[row] = self.item.get_lut_range()

    def show_data(self, data, lut_range=None):
        """Show image data"""
        plot = self.plot_widget.plot
        if self.item is not None:
            self.item.set_data(data)
            if lut_range is None:
                lut_range = self.item.get_lut_range()
            self.plot_widget.manager.set_contrast_range(*lut_range)
            self.plot_widget.manager.update_cross_sections()
        else:
            self.item = make.image(data)
            plot.add_item(self.item, z=0)
        plot.replot()

    def properties_changed(self):
        """The properties 'Apply' button was clicked: updating image"""
        row = self.imagelist.currentRow()
        image = self.images[row]
        update_dataset(image, self.properties.dataset)
        self.refresh_list()
        self.show_data(image.data)

    def add_image(self, image):
        """Add image"""
        self.images.append(image)
        self.lut_ranges.append(None)
        self.refresh_list()
        self.imagelist.setCurrentRow(len(self.images) - 1)
        plot = self.plot_widget.plot
        plot.do_autoscale()

    def add_image_from_file(self, filename):
        """Add image from file"""
        image = ImageParam()
        image.title = str(filename)
        image.data = io.imread(filename, to_grayscale=True)
        image.height, image.width = image.data.shape
        self.add_image(image)


class MainWindow(QW.QMainWindow):
    """Main Window"""

    def __init__(self):
        super().__init__()
        win32_fix_title_bar_background(self)
        self.setup()

    def setup(self):
        """Setup window parameters"""
        self.setWindowIcon(get_icon("python.png"))
        self.setWindowTitle(APP_NAME)
        self.resize(QC.QSize(600, 800))

        # Welcome message in statusbar:
        status = self.statusBar()
        status.showMessage(_("Welcome to plotpy application example!"), 5000)

        # File menu
        file_menu = self.menuBar().addMenu(_("File"))
        new_action = create_action(
            self,
            _("New..."),
            shortcut="Ctrl+N",
            icon=get_icon("filenew.png"),
            tip=_("Create a new image"),
            triggered=self.new_image,
        )
        open_action = create_action(
            self,
            _("Open..."),
            shortcut="Ctrl+O",
            icon=get_icon("fileopen.png"),
            tip=_("Open an image"),
            triggered=self.open_image,
        )
        quit_action = create_action(
            self,
            _("Quit"),
            shortcut="Ctrl+Q",
            icon=get_std_icon("DialogCloseButton"),
            tip=_("Quit application"),
            triggered=self.close,
        )
        add_actions(file_menu, (new_action, open_action, None, quit_action))

        # Help menu
        help_menu = self.menuBar().addMenu("?")
        about_action = create_action(
            self,
            _("About..."),
            icon=get_std_icon("MessageBoxInformation"),
            triggered=self.about,
        )
        add_actions(help_menu, (about_action,))

        main_toolbar = self.addToolBar("Main")
        add_actions(main_toolbar, (new_action, open_action))

        # Set central widget:
        toolbar = self.addToolBar("Image")
        self.mainwidget = CentralWidget(self, toolbar)
        self.setCentralWidget(self.mainwidget)

    # ------?
    def about(self):
        """About box"""
        QW.QMessageBox.about(
            self,
            _("About ") + APP_NAME,
            "<b>{}</b> v{}"
            "<p>{} Pierre Raybaut<br><br>{}".format(
                APP_NAME,
                VERSION,
                _("Developped by"),
                about(html=True, copyright_only=True),
            ),
        )

    # ------I/O
    def new_image(self):
        """Create a new image"""
        imagenew = ImageParamNew(title=_("Create a new image"))
        if not imagenew.edit(self):
            return
        image = ImageParam()
        image.title = imagenew.title
        if imagenew.type == "zeros":
            image.data = np.zeros((imagenew.width, imagenew.height))
        elif imagenew.type == "rand":
            image.data = np.random.randn(imagenew.width, imagenew.height)
        self.mainwidget.add_image(image)

    def open_image(self):
        """Open image file"""
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        filename, _filter = QW.QFileDialog.getOpenFileName(
            self,
            _("Open"),
            "",
            io.iohandler.get_filters("load"),
            "",
            options=QW.QFileDialog.ShowDirsOnly,
        )
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        if filename:
            self.mainwidget.add_image_from_file(filename)


def test_simple_window():
    """Test simple window"""
    with qt_app_context(exec_loop=True):
        window = MainWindow()
        window.show()


if __name__ == "__main__":
    test_simple_window()
