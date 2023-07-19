# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Horizontal/vertical cursors test"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType


def plot(*items):
    win = PlotDialog(edit=False, toolbar=True, options={"type": PlotType.CURVE})
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    win.show()
    return win


def test_cursor():
    """Test cursor"""
    x = linspace(-10, 10, 1000) + 1
    y = sin(sin(sin(x))) + 3
    with qt_app_context(exec_loop=True):
        curve = make.curve(x, y, "ab", "b")
        hcursor = make.hcursor(3.2, label="y = %.2f")
        vcursor = make.vcursor(7, label="x = %.2f")
        vcursor2 = make.vcursor(-1, label="NOT MOVABLE = %.2f", movable=False)
        xcursor = make.xcursor(-4, 2.5, label="x = %.2f<br>y = %.2f")
        legend = make.legend("TR")
        persist_obj = plot(curve, hcursor, vcursor, vcursor2, xcursor, legend)


if __name__ == "__main__":
    test_cursor()
