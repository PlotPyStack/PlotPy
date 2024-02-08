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
from plotpy.tools import SelectPointsTool


def callback_function(tool: SelectPointsTool) -> None:
    """Callback function to be called by the tool after selection

    Args:
        tool: The tool instance that called the callback
    """
    points = tool.get_coordinates()
    print("Points : ", points)


def get_points(cdata: tuple[tuple[float, float], ...], max_select: int) -> None:
    """
    Plot curves and return selected point(s) coordinates

    Args:
        cdata: A tuple of curves to plot
    """
    win = make.dialog(
        wintitle=_(
            "Select up to %s points then press OK to accept "
            "(hold Ctrl to select multiple points)"
        )
        % max_select,
        edit=True,
        type="curve",
        curve_antialiasing=True,
    )
    default = win.manager.add_tool(
        SelectPointsTool,
        title="Test",
        on_active_item=True,
        mode="reuse",
        end_callback=callback_function,
        max_select=max_select,
    )
    default.activate()
    plot = win.manager.get_plot()
    for cx, cy in cdata[:-1]:
        item = make.mcurve(cx, cy)
        plot.add_item(item)
    # the last curve will be actibe and needs to have a different style for explictness
    item = make.mcurve(*cdata[-1], "r-+")
    plot.add_item(item)
    plot.set_active_item(item)
    plot.unselect_item(item)
    exec_dialog(win)


def test_get_point():
    """Test"""
    with qt_app_context(exec_loop=False):
        x = linspace(-10, 10, num=200)
        y = 0.25 * sin(sin(sin(x * 0.5)))
        x2 = linspace(-10, 10, 200)
        y2 = sin(sin(sin(x2)))
        get_points(((x, y), (x2, y2), (x, sin(2 * y))), max_select=5)


if __name__ == "__main__":
    test_get_point()
