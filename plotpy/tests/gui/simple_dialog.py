# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Simple dialog box based on plotpy"""


import scipy.ndimage
from guidata.dataset.dataitems import ChoiceItem, IntItem, StringItem
from guidata.dataset.datatypes import DataSet
from guidata.dataset.qtwidgets import DataSetEditGroupBox, DataSetShowGroupBox
from guidata.utils import update_dataset

from plotpy.config import _
from plotpy.widgets import io
from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.tools.image import OpenImageTool

SHOW = True  # Show test in GUI-based test launcher


class ImageParam(DataSet):
    title = StringItem(_("Title"))
    width = IntItem(_("Width"), help=_("Image width (pixels)"))
    height = IntItem(_("Height"), help=_("Image height (pixels)"))


class FilterParam(DataSet):
    name = ChoiceItem(
        _("Filter algorithm"),
        (
            ("gaussian_filter", _("gaussian filter")),
            ("uniform_filter", _("uniform filter")),
            ("minimum_filter", _("minimum filter")),
            ("median_filter", _("median filter")),
            ("maximum_filter", _("maximum filter")),
        ),
    )
    size = IntItem(_("Size or sigma"), min=1, default=5)


class ExampleDialog(PlotDialog):
    def __init__(
        self,
        wintitle=_("Example dialog box"),
        icon="guidata.svg",
        options=dict(show_contrast=True, type=PlotType.IMAGE),
        edit=False,
    ):
        self.filter_gbox = None
        self.data = None
        self.item = None
        super(ExampleDialog, self).__init__(
            wintitle=wintitle, icon=icon, toolbar=True, edit=edit, options=options
        )
        self.resize(600, 600)

    def register_tools(self):
        opentool = self.add_tool(OpenImageTool)
        opentool.SIG_OPEN_FILE.connect(self.open_image)
        self.register_all_image_tools()
        self.activate_default_tool()

    def create_plot(self, options):
        self.filter_gbox = DataSetEditGroupBox(_("Filter parameters"), FilterParam)
        self.filter_gbox.setEnabled(False)
        self.filter_gbox.SIG_APPLY_BUTTON_CLICKED.connect(self.apply_filter)
        self.plot_layout.addWidget(self.filter_gbox, 0, 0)
        self.param_gbox = DataSetShowGroupBox(_("Image parameters"), ImageParam)
        self.plot_layout.addWidget(self.param_gbox, 0, 1)

        options = dict(title=_("Image title"), zlabel=_("z-axis scale label"))
        PlotDialog.create_plot(self, options, 1, 0, 1, 0)

    def open_image(self, filename):
        """Opening image *filename*"""
        self.data = io.imread(filename, to_grayscale=True)
        self.show_data(self.data)
        param = ImageParam()
        param.title = filename
        param.height, param.width = self.data.shape
        update_dataset(self.param_gbox.dataset, param)
        self.param_gbox.get()
        self.filter_gbox.setEnabled(True)

    def show_data(self, data):
        plot = self.get_plot()
        if self.item is not None:
            self.item.set_data(data)
        else:
            self.item = make.image(data, colormap="gray")
            plot.add_item(self.item, z=0)
        plot.set_active_item(self.item)
        plot.replot()

    def apply_filter(self):
        param = self.filter_gbox.dataset
        filterfunc = getattr(scipy.ndimage, param.name)
        data = filterfunc(self.data, param.size)
        self.show_data(data)


if __name__ == "__main__":
    import plotpy.config  # Loading icons
    from plotpy.widgets import qapplication

    _app = qapplication()
    dlg = ExampleDialog()
    dlg.exec_()  # No need to call app.exec_: a dialog box has its own event loop
