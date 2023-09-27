# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Contour test"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.plot import PlotDialog


def test_contour():
    with qt_app_context(exec_loop=True):
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

        # add the contours
        values = np.arange(-2, 2, 0.5)
        for item in make.contours(Z, values):
            plot.add_item(item)

        win.show()


if __name__ == "__main__":
    test_contour()
