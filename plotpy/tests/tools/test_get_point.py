# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
SelectPointTool test

This plotpy tool provide a MATLAB-like "ginput" feature.
"""

# guitest: show

from __future__ import annotations

from guidata.qthelpers import exec_dialog, qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.config import _
from plotpy.tools import SelectPointTool


def callback_function(tool: SelectPointTool) -> None:
    print("Current coordinates:", tool.get_coordinates())


def get_point(cdata: tuple[tuple[float, float], ...]) -> None:
    """
    Plot curves and return selected point(s) coordinates

    Args:
        cdata: A tuple of curves to plot
    """
    win = make.dialog(
        wintitle=_("Select one point then press OK to accept"),
        edit=True,
        type="curve",
        size=(800, 600),
    )
    default = win.manager.add_tool(
        SelectPointTool,
        title="Test",
        on_active_item=True,
        mode="reuse",
        end_callback=callback_function,
    )
    default.activate()
    plot = win.manager.get_plot()
    for cx, cy in cdata[:-1]:
        item = make.mcurve(cx, cy)
        plot.add_item(item)
    item = make.mcurve(*cdata[-1], "r-+")
    plot.add_item(item)
    plot.set_active_item(item)
    plot.unselect_item(item)
    exec_dialog(win)


def test_get_point():
    """Test"""
    with qt_app_context(exec_loop=False):
        x = linspace(-10, 10, 200)
        y = 0.25 * sin(sin(sin(x * 0.5)))
        x2 = linspace(-10, 10, 200)
        y2 = sin(sin(sin(x2)))
        get_point(((x, y), (x2, y2), (x, sin(2 * y))))


if __name__ == "__main__":
    test_get_point()
