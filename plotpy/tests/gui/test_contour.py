# -*- coding: utf-8 -*-
#
# Copyright © 2019 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Contour test"""


import numpy as np

import plotpy.widgets
from plotpy.widgets.builder import make
from plotpy.widgets.contour import contour
from plotpy.widgets.items.shapes.polygon import PolygonShape
from plotpy.widgets.plot.plotwidget import PlotDialog
from plotpy.widgets.styles.shape import ShapeParam

SHOW = True  # Show test in GUI-based test launcher


def test_contour():
    _app = plotpy.widgets.qapplication()
    win = PlotDialog(edit=True, toolbar=True, wintitle="Sample contour plotting")
    plot = win.manager.get_plot()
    plot.set_aspect_ratio(lock=True)
    plot.set_antialiasing(False)
    win.manager.get_itemlist_panel().show()

    # compute the image
    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-(X**2) - Y**2)
    Z2 = np.exp(-((X - 1) ** 2) - (Y - 1) ** 2)
    Z = (Z1 - Z2) * 2

    # show the image
    item = make.image(Z)
    plot = win.manager.get_plot()
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
    test_contour()
