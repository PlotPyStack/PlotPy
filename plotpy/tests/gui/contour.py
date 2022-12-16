# -*- coding: utf-8 -*-
#
# Copyright © 2019 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Contour test"""

SHOW = True  # Show test in GUI-based test launcher

import numpy as np

import plotpy.gui
from plotpy.gui.widgets.builder import make
from plotpy.gui.widgets.contour import contour
from plotpy.gui.widgets.items.shapes import PolygonShape
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.styles import ShapeParam


def test():
    _app = plotpy.gui.qapplication()
    win = PlotDialog(edit=True, toolbar=True, wintitle="Sample contour plotting")
    plot = win.get_plot()
    plot.set_aspect_ratio(lock=True)
    plot.set_antialiasing(False)
    win.get_itemlist_panel().show()

    # compute the image
    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X ** 2 - Y ** 2)
    Z2 = np.exp(-(X - 1) ** 2 - (Y - 1) ** 2)
    Z = (Z1 - Z2) * 2

    # show the image
    item = make.image(Z)
    plot = win.get_plot()
    plot.add_item(item)

    # compute the contour
    values = np.arange(-2, 2, 0.5)
    lines = contour(None, None, Z, values)

    for line in lines:
        param = ShapeParam()
        param.label = f"Line level {line.level}"
        crv = PolygonShape(closed=False, shapeparam=param)
        crv.set_points(line.vertices)
        plot.add_item(crv)

    win.show()
    win.exec_()


if __name__ == "__main__":
    test()
