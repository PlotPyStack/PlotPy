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

from guidata.qthelpers import exec_dialog, qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.config import _


def edit_downsampled_curve(
    cdata: tuple[tuple[float, float], ...], dsamp_factor: int
) -> None:
    """
    Plot curves and return selected point(s) coordinates

    Args:
        cdata: tuple of curves to plot
        dsamp_factor: downsampling factor
    """
    win = make.dialog(
        wintitle=_("Right-click on the curve to enable/disable downsampling"),
        edit=True,
        type="curve",
    )
    plot = win.manager.get_plot()
    for cx, cy in cdata[:-1]:
        item = make.mcurve(cx, cy)
        plot.add_item(item)
    item = make.mcurve(*cdata[-1], "r-+", dsamp_factor=dsamp_factor, use_dsamp=True)
    plot.add_item(item)
    plot.set_active_item(item)
    plot.unselect_item(item)
    exec_dialog(win)


def test_edit_curve():
    """Test"""
    with qt_app_context(exec_loop=False):
        nlines = 1000
        x = linspace(-10, 10, num=nlines)
        y = 0.25 * sin(sin(sin(x * 0.5)))
        x2 = linspace(-10, 10, num=nlines)
        y2 = sin(sin(sin(x2)))
        cdata = ((x, y), (x2, y2), (x, sin(2 * y)))
        for dsamp_factor in (10, 50):
            edit_downsampled_curve(cdata, dsamp_factor)


if __name__ == "__main__":
    test_edit_curve()
