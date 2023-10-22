# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Logarithmic scale test for curve plotting"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_plot_log():
    """Test plot log"""
    with qt_app_context(exec_loop=True):
        x = np.linspace(1, 10, 200)
        y = np.exp(-x)
        y[0] = 0
        items = [make.curve(x, y, color="b"), make.error(x, y, None, y * 0.23)]
        win = ptv.show_items(items, plot_type="curve")
        plot = win.manager.get_plot()
        plot.set_axis_scale("left", "log")
        plot.set_axis_scale("bottom", "log")
        #    plot.set_axis_limits("left", 4.53999297625e-05, 22026.4657948)


if __name__ == "__main__":
    test_plot_log()
