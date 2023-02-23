# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""2-D Histogram (with function) test"""

# SHOW = True # Show test in GUI-based test launcher
# todo: change this test so that shown data means something...

from numpy import array, concatenate, dot, random

from plotpy.config import _
from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType


def hist2d_func(X, Y, Z):
    win = PlotDialog(
        edit=True,
        toolbar=True,
        wintitle="2-D Histogram X0=(0,1), X1=(-1,-1)",
        options={"type": PlotType.IMAGE},
    )
    hist2d = make.histogram2D(X, Y, 200, 200, Z=Z, computation=2)
    curve = make.curve(X[::50], Y[::50], linestyle="", marker="+", title=_("Markers"))
    plot = win.manager.get_plot()
    plot.set_aspect_ratio(lock=False)
    plot.set_antialiasing(False)
    plot.add_item(hist2d)
    plot.add_item(curve)
    plot.set_item_visible(curve, False)
    win.show()
    win.exec_()


if __name__ == "__main__":
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    N = 150000
    m = array([[1.0, 0.2], [-0.2, 3.0]])
    X1 = random.normal(0, 0.3, size=(N, 2))
    X2 = random.normal(0, 0.3, size=(N, 2))
    X = concatenate((X1 + [0, 1.0], dot(X2, m) + [-1, -1.0]))
    hist2d_func(X[:, 0], X[:, 1], X[:, 0] + X[:, 1])
