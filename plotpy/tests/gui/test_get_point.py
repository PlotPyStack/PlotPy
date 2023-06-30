# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
SelectPointTool test

This plotpy tool provide a MATLAB-like "ginput" feature.
"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.config import _
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.curve import SelectPointTool


def callback_function(tool):
    print("Current coordinates:", tool.get_coordinates())


def get_point(*args):
    """
    Plot curves and return selected point(s) coordinates
    """
    win = PlotDialog(
        _("Select one point then press OK to accept"),
        edit=True,
        options={"type": PlotType.CURVE},
    )
    default = win.manager.add_tool(
        SelectPointTool,
        title="Test",
        on_active_item=True,
        mode="create",
        end_callback=callback_function,
    )
    default.activate()
    plot = win.manager.get_plot()
    for cx, cy in args:
        item = make.mcurve(cx, cy)
        plot.add_item(item)
    plot.set_active_item(item)
    win.show()
    return win, default.get_coordinates()


def test_get_point():
    """Test"""
    with qt_app_context(exec_loop=True):
        x = linspace(-10, 10, 1000)
        y = sin(sin(sin(x)))
        x2 = linspace(-10, 10, 20)
        y2 = sin(sin(sin(x2)))
        _persist_dialog, coordinates = get_point((x, y), (x2, y2), (x, sin(2 * y)))
        print(coordinates)


if __name__ == "__main__":
    test_get_point()
