# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Logarithmic scale test for curve plotting"""


import numpy as np

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.qthelpers_guidata import qt_app_context

SHOW = False  # Do not show test in GUI-based test launcher


def test_plot_log():
    """Test plot log"""
    with qt_app_context(exec_loop=True):
        x = np.linspace(1, 10, 200)
        y = np.exp(-x)
        y[0] = 0
        item = make.curve(x, y, color="b")
        item = make.error(x, y, None, y * 0.23)

        win = PlotDialog(options={"type": PlotType.CURVE})
        plot = win.manager.get_plot()
        plot.set_axis_scale("left", "log")
        plot.set_axis_scale("bottom", "log")
        #    plot.set_axis_limits("left", 4.53999297625e-05, 22026.4657948)
        plot.add_item(item)
        win.show()


if __name__ == "__main__":
    test_plot_log()
