# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Simple dialog box based on plotpy"""

# guitest: show

import scipy.ndimage
from guidata.dataset import ChoiceItem, DataSet, IntItem, StringItem, update_dataset
from guidata.dataset.qtwidgets import DataSetEditGroupBox, DataSetShowGroupBox
from guidata.qthelpers import qt_app_context

from plotpy import io
from plotpy.builder import make
from plotpy.config import _
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tools import OpenImageTool

# guitest: show


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
        title=_("Example dialog box"),
        options=PlotOptions(show_contrast=True, type="image"),
        edit=False,
    ):
        self.filter_gbox = None
        self.data = None
        self.item = None
        options.title = _("Image title")
        options.zlabel = _("z-axis scale label")
        super().__init__(
            title=title,
            toolbar=True,
            edit=edit,
            options=options,
        )
        self.resize(600, 600)
        opentool = self.manager.add_tool(OpenImageTool)
        opentool.SIG_OPEN_FILE.connect(self.open_image)
        self.manager.register_all_image_tools()
        self.manager.activate_default_tool()

    def populate_plot_layout(self):
        """Populate the plot layout"""
        self.filter_gbox = DataSetEditGroupBox(_("Filter parameters"), FilterParam)
        self.filter_gbox.setEnabled(False)
        self.filter_gbox.SIG_APPLY_BUTTON_CLICKED.connect(self.apply_filter)
        self.add_widget(self.filter_gbox, 0, 0)
        self.param_gbox = DataSetShowGroupBox(_("Image parameters"), ImageParam)
        self.add_widget(self.param_gbox, 0, 1)
        self.add_widget(self.plot_widget, 1, 0, 1, 0)

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
        plot = self.manager.get_plot()
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


def test_simple_dialog():
    """Test simple dialog"""
    with qt_app_context(exec_loop=True):
        dlg = ExampleDialog()
        dlg.show()


if __name__ == "__main__":
    test_simple_dialog()
