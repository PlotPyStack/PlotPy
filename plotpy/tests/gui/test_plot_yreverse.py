# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Reverse y-axis test for curve plotting"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_plot_yreverse():
    """Testing reverse x/y axes"""
    with qt_app_context(exec_loop=True):
        x = np.linspace(-10, 10, 200)
        win = ptv.show_items(
            [make.curve(x, x * np.exp(-x), color="b")],
            plot_type="curve",
            wintitle=test_plot_yreverse.__doc__,
        )
        plot = win.manager.get_plot()
        plot.set_axis_direction("left", True)
        plot.set_axis_direction("bottom", True)


if __name__ == "__main__":
    test_plot_yreverse()
