# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing plot with synchronized axes"""

from __future__ import annotations

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtGui as QG

from plotpy.builder import make
from plotpy.config import _
from plotpy.plot import BasePlot, PlotOptions
from plotpy.plot.plotwidget import SyncPlotWindow
from plotpy.tests.data import gen_2d_gaussian


def plot(plot_type, *itemlists):
    """Plot items in SyncPlotDialog"""
    win = SyncPlotWindow(
        title="Window for showing plots, optionally synchronized",
        options=PlotOptions(type=plot_type),
    )
    row, col = 0, 0
    for items in itemlists:
        plot = BasePlot()
        for item in items:
            plot.add_item(item)
        plot.set_axis_font("left", QG.QFont("Courier"))
        plot.set_items_readonly(False)
        win.add_plot(row, col, plot, sync=True)
        col += 1
        if col == 2:
            row += 1
            col = 0
    win.finalize_configuration()
    if plot_type == "image":
        win.manager.get_contrast_panel().show()
    win.resize(800, 600)
    win.show()


def test_syncplot_curves():
    """Test plot synchronization: curves"""
    x = np.linspace(-10, 10, 200)
    dy = x / 100.0
    y = np.sin(np.sin(np.sin(x)))
    x2 = np.linspace(-10, 10, 20)
    y2 = np.sin(np.sin(np.sin(x2)))
    with qt_app_context(exec_loop=True):
        plot(
            "curve",
            [
                make.curve(x, y, color="b"),
                make.label(
                    "Relative position <b>outside</b>", (x[0], y[0]), (-10, -10), "BR"
                ),
            ],
            [make.curve(x2, y2, color="g")],
            [
                make.curve(x, np.sin(2 * y), color="r"),
                make.label(
                    "Relative position <i>inside</i>", (x[0], y[0]), (10, 10), "TL"
                ),
            ],
            [
                make.merror(x, y / 2, dy),
                make.label("Absolute position", "R", (0, 0), "R"),
                make.legend("TR"),
            ],
        )


def test_syncplot_images():
    """Test plot synchronization: images"""
    img1 = gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=7, sigma=10.0)
    img2 = gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=5, sigma=8.0)
    img3 = gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=3, sigma=6.0)
    with qt_app_context(exec_loop=True):

        def makeim(data):
            """Make image item"""
            return make.image(data, interpolation="nearest")

        plot("image", [makeim(img1)], [makeim(img2)], [makeim(img3)])


if __name__ == "__main__":
    test_syncplot_curves()
    test_syncplot_images()
