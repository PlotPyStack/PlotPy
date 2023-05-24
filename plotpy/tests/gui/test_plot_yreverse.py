# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Reverse y-axis test for curve plotting"""


import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType

SHOW = False  # Do not show test in GUI-based test launcher


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
