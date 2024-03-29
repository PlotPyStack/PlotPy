# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing BasePlot API"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.tests import vistools as ptv
from plotpy.tests.features.test_auto_curve_image import make_curve_image_legend
from plotpy.tools.curve import EditPointTool, SelectPointsTool


def test_baseplot_api():
    """Testing BasePlot API"""
    with qt_app_context(exec_loop=True):
        items = make_curve_image_legend()
        win = ptv.show_items(items, wintitle=test_baseplot_api.__doc__)
        plot = win.get_plot()
        plot.manager.add_tool(SelectPointsTool)
        plot.manager.add_tool(EditPointTool)
        plot.get_default_item()
        title = "Test title"
        plot.set_title(title)
        assert plot.get_title() == title
        unit = "Test unit"
        plot.set_axis_unit("left", unit)
        assert plot.get_axis_unit("left") == unit
        plot.set_axis_ticks("left", 10, 10)
        plot.set_scales("lin", "lin")
        plot.enable_used_axes()
        plot.disable_unused_axes()
        plot.copy_to_clipboard()
        QW.QApplication.processEvents()
        fname = f"{test_baseplot_api.__name__}.pdf"
        plot.save_widget(fname)
        os.remove(fname)
        plot.hide_items(items)
        plot.show_items(items)
        plot.select_all()
        plot.move_up([items[0]])
        plot.move_down([items[0]])
        plot.unselect_item(items[0])
        plot.select_some_items(items)
        plot.unselect_all()
        plot.get_nearest_object(QC.QPointF(0, 0))
        plot.get_nearest_object_in_z(QC.QPointF(0, 0))
        plot.get_context_menu()
        plot.select_all()
        plot.edit_plot_parameters("item")
        plot.edit_axis_parameters(plot.yLeft)
        plot.set_titles(
            "Test title", "Test x title", "Test y title", "Test x unit", "Test y unit"
        )
        plot.notify_colormap_changed()


if __name__ == "__main__":
    test_baseplot_api()
