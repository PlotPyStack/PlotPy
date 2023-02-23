# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Logarithmic scale test for curve plotting"""


from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType

SHOW = False  # Do not show test in GUI-based test launcher


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    import numpy as np

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
    win.exec_()


if __name__ == "__main__":
    test()
