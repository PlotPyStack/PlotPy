# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
DownSampleCurveTool test

This plotpy tool provides a toggle to downsample the current curve with a given factor.
"""

# guitest: show

from __future__ import annotations

from typing import Any

from guidata.qthelpers import exec_dialog, qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.config import _
from plotpy.tools import DownSampleCurveTool, EditPointTool


def callback_function(tool: EditPointTool) -> None:
    """Callback that is called by the tool when the user stops clicking. Just prints
    the new arrays and the changes.

    Args:
        tool: tool instance that can be used to retrieve the new arrays and the
        changes
    """
    print("New arrays:", tool.get_arrays())
    print("Indexed changes:", tool.get_changes())


def edit_downsampled_curve(downsampling_factor: int, *args) -> tuple[Any, ...]:
    """
    Plot curves and return selected point(s) coordinates

    Args:
        downsampling_factor: downsampling factor (>=1)
        *args: arguments to be passed to the plotpy builder make.mcurve function

    Returns:
        Modified *args input that can be used in another call to this function to check
        the interaction between edit tool and the donwsampling tool.
    """
    win = make.dialog(
        wintitle=_("Select one point then press OK to accept"),
        edit=True,
        type="curve",
    )
    __ = win.manager.add_tool(
        EditPointTool,
        title="Test",
        end_callback=callback_function,
    )
    # tool accessible via right click menu
    downsample_tool = win.manager.add_tool(
        DownSampleCurveTool,
    )
    downsample_tool.activate()
    plot = win.manager.get_plot()
    for cx, cy in args[:-1]:
        item = make.mcurve(cx, cy)

        plot.add_item(item)
    item = make.mcurve(
        *args[-1], "r-+", downsampling_factor=downsampling_factor, use_downsampling=True
    )
    plot.add_item(item)
    plot.set_active_item(item)
    plot.unselect_item(item)
    exec_dialog(win)
    return args


def test_downsample_curve() -> None:
    """Test the downsample curve tool."""
    with qt_app_context(exec_loop=False):
        nlines = 1000
        x = linspace(-10, 10, num=nlines)
        y = 0.25 * sin(sin(sin(x * 0.5)))
        x2 = linspace(-10, 10, num=nlines)
        y2 = sin(sin(sin(x2)))
        edited_args = edit_downsampled_curve(50, (x, y), (x2, y2), (x, sin(2 * y)))
        edit_downsampled_curve(10, *edited_args)


if __name__ == "__main__":
    test_downsample_curve()
