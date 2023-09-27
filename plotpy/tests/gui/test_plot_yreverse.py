# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Reverse y-axis test for curve plotting"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.constants import PlotType
from plotpy.plot import PlotDialog


def test_plot_yreverse():
    """Test plot reverse"""
    with qt_app_context(exec_loop=True):
        x = np.linspace(-10, 10, 200)
        y = x * np.exp(-x)
        item = make.curve(x, y, color="b")

        win = PlotDialog(options={"type": PlotType.CURVE})
        plot = win.manager.get_plot()
        plot.add_item(item)
        plot.set_axis_direction("left", True)
        plot.set_axis_direction("bottom", True)
        win.show()


if __name__ == "__main__":
    test_plot_yreverse()
