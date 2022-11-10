# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Reverse y-axis test for curve plotting"""

SHOW = False  # Do not show test in GUI-based test launcher

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    # --
    import numpy as np

    x = np.linspace(-10, 10, 200)
    y = x * np.exp(-x)
    item = make.curve(x, y, color="b")

    win = PlotDialog(options={"type": PlotType.CURVE})
    plot = win.get_plot()
    plot.add_item(item)
    plot.set_axis_direction("left", True)
    plot.set_axis_direction("bottom", True)
    win.show()
    win.exec_()


if __name__ == "__main__":
    test()
