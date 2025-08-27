# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing plot with synchronized axes"""

from __future__ import annotations

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import exec_dialog, qt_app_context
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.plot import BasePlot, PlotOptions
from plotpy.plot.plotwidget import SyncPlotDialog, SyncPlotWindow
from plotpy.tests.data import gen_2d_gaussian


def show_with(cls: type[SyncPlotDialog] | type[SyncPlotWindow], plot_type, *itemlists):
    """Show plot items in SyncPlotWindow or SyncPlotDialog"""
    widget = cls(
        title=f"{cls.__name__}: showing plots, optionally synchronized ({plot_type})",
        options=PlotOptions(type=plot_type),
    )
    row, col = 0, 0
    for items in itemlists:
        plot = BasePlot()
        for item in items:
            plot.add_item(item)
        plot.set_axis_font("left", QG.QFont("Courier"))
        plot.set_items_readonly(False)
        widget.add_plot(row, col, plot, sync=True)
        col += 1
        if col == 2:
            row += 1
            col = 0
    widget.finalize_configuration()
    if plot_type == "image":
        widget.get_manager().get_contrast_panel().show()
    widget.resize(800, 600)
    if cls is SyncPlotWindow:
        widget.show()
        if not execenv.unattended:
            app = QW.QApplication.instance()
            app.exec()
    else:
        exec_dialog(widget)


def test_syncplot_curves():
    """Test plot synchronization: curves"""
    x = np.linspace(-10, 10, 200)
    dy = x / 100.0
    y = np.sin(np.sin(np.sin(x)))
    x2 = np.linspace(-10, 10, 20)
    y2 = np.sin(np.sin(np.sin(x2)))
    with qt_app_context():
        itemlists = [
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
        ]
        for cls in (SyncPlotWindow, SyncPlotDialog):
            show_with(cls, "curve", *itemlists)


def test_syncplot_images():
    """Test plot synchronization: images"""
    img1 = gen_2d_gaussian(20, np.uint8, x0=-10.0, y0=-10.0, mu=7.0, sigma=10.0)
    img2 = gen_2d_gaussian(20, np.uint8, x0=-10.0, y0=-10.0, mu=5.0, sigma=8.0)
    img3 = gen_2d_gaussian(20, np.uint8, x0=-10.0, y0=-10.0, mu=3.0, sigma=6.0)
    with qt_app_context():

        def makeim(data):
            """Make image item"""
            return make.image(data, interpolation="nearest")

        itemlists = [[makeim(img1)], [makeim(img2)], [makeim(img3)]]

        for cls in (SyncPlotWindow, SyncPlotDialog):
            show_with(cls, "image", *itemlists)


if __name__ == "__main__":
    test_syncplot_curves()
    test_syncplot_images()
