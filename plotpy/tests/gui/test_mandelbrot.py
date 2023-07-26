# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Mandelbrot demo"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC

import plotpy.widgets
from plotpy.config import _
from plotpy.core.items.image.base import RawImageItem
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.base import ToggleTool
from plotpy.mandelbrot import mandelbrot


class FullScale(ToggleTool):
    def __init__(self, parent, image):
        super(FullScale, self).__init__(parent, _("MAX resolution"), None)
        self.image = image
        self.minprec = image.IMAX
        self.maxprec = 5 * image.IMAX

    def activate_command(self, plot, checked):
        if self.image.IMAX == self.minprec:
            self.image.IMAX = self.maxprec
        else:
            self.image.IMAX = self.minprec
        self.image.set_lut_range([0, self.image.IMAX])
        plot.replot()

    def update_status(self, plot):
        self.action.setChecked(self.image.IMAX == self.maxprec)


class MandelItem(RawImageItem):
    def __init__(self, xmin, xmax, ymin, ymax):
        super(MandelItem, self).__init__(np.zeros((1, 1), np.uint8))
        self.bounds = QC.QRectF(QC.QPointF(xmin, ymin), QC.QPointF(xmax, ymax))
        self.update_border()
        self.IMAX = 80
        self.set_lut_range([0, self.IMAX])

    # ---- QwtPlotItem API ------------------------------------------------------
    def draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap):
        x1, y1 = canvasRect.left(), canvasRect.top()
        x2, y2 = canvasRect.right(), canvasRect.bottom()
        i1, j1, i2, j2 = srcRect

        NX = x2 - x1
        NY = y2 - y1
        if self.data.shape != (NX, NY):
            self.data = np.zeros((NY, NX), np.uint8)
        mandelbrot(i1, j1, i2, j2, self.data, self.IMAX)

        srcRect = (0, 0, NX, NY)
        x1, y1, x2, y2 = canvasRect.getCoords()
        RawImageItem.draw_image(
            self, painter, canvasRect, srcRect, (x1, y1, x2, y2), xMap, yMap
        )


def test_mandel():
    with qt_app_context(exec_loop=True):
        win = PlotDialog(
            edit=True,
            toolbar=True,
            wintitle="Mandelbrot",
            options=dict(yreverse=False, type=PlotType.IMAGE),
        )
        mandel = MandelItem(-1.5, 0.5, -1.0, 1.0)
        win.manager.add_tool(FullScale, mandel)
        plot = win.manager.get_plot()
        plot.set_aspect_ratio(lock=False)
        plot.add_item(mandel)
        win.show()


if __name__ == "__main__":
    test_mandel()
