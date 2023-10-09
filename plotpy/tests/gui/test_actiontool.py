# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""ActionTool test"""

# guitest: show

from guidata.qthelpers import create_action, qt_app_context
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.items import ImageItem
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests.data import gen_image4
from plotpy.tools import ActionTool


class MyPlotDialog(PlotDialog):
    def __init__(self):
        """Reimplement PlotDialog method"""
        super().__init__(
            title="ActionTool test", toolbar=True, options=PlotOptions(type="image")
        )
        self.info_action = create_action(self, "Show infos", triggered=self.show_info)
        self.manager.add_tool(ActionTool, self.info_action, item_types=(ImageItem,))

    def show_info(self):
        """Show infos on selected item(s)"""
        # This is just a demo of what can be done with ActionTool
        plot = self.get_plot()
        for item in plot.get_selected_items():
            QW.QMessageBox.information(self, "Item infos", str(item))


def test_image_plot_tools():
    """Test"""
    with qt_app_context(exec_loop=True):
        win = MyPlotDialog()
        win.show()
        image = make.image(gen_image4(500, 500), colormap="Spectral")
        plot = win.manager.get_plot()
        plot.add_item(image)


if __name__ == "__main__":
    test_image_plot_tools()
