# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Horizontal/vertical cursors test"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.tests import vistools as ptv


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
        _win = ptv.show_items(
            wintitle="Plot cursors",
            items=[curve, hcursor, vcursor, vcursor2, xcursor, legend],
            plot_type="curve",
        )


if __name__ == "__main__":
    test_cursor()
