# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Mandelbrot demo"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC

from plotpy.builder import make
from plotpy.config import _
from plotpy.items import RawImageItem
from plotpy.mandelbrot import mandelbrot
from plotpy.tools import ToggleTool


class FullScale(ToggleTool):
    def __init__(self, parent, image):
        super().__init__(parent, _("MAX resolution"), None)
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
        super().__init__(np.zeros((1, 1), np.uint8))
        self.bounds = QC.QRectF(QC.QPointF(xmin, ymin), QC.QPointF(xmax, ymax))
        self.update_border()
        self.IMAX = 80
        self.set_lut_range([0, self.IMAX])

    # ---- QwtPlotItem API ------------------------------------------------------
    def draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap):
        if self.warn_if_non_linear_scale(painter, canvasRect):
            return
        x1, y1, x2, y2 = canvasRect.toAlignedRect().getCoords()
        i1, j1, i2, j2 = srcRect

        NX = x2 - x1
        NY = y2 - y1
        if self.data.shape != (NX, NY):
            self.data = np.zeros((NY, NX), np.int16)
        mandelbrot(i1, j1, i2, j2, self.data, self.IMAX)

        srcRect = (0, 0, NX, NY)
        x1, y1, x2, y2 = canvasRect.toAlignedRect().getCoords()
        RawImageItem.draw_image(
            self, painter, canvasRect, srcRect, (x1, y1, x2, y2), xMap, yMap
        )


def create_mandelbrot_window():
    """Create a Mandelbrot set window"""
    win = make.window(
        toolbar=True,
        wintitle="Mandelbrot",
        yreverse=False,
        type="image",
    )
    mandel = MandelItem(-1.5, 0.5, -1.0, 1.0)
    fstool = win.manager.add_tool(FullScale, mandel)
    plot = win.get_plot()
    plot.set_aspect_ratio(lock=False)
    plot.add_item(mandel)
    return win, mandel, fstool


def test_mandel():
    """Test Mandelbrot set window"""
    with qt_app_context(exec_loop=True):
        win, _mandel, _fstool = create_mandelbrot_window()
        win.show()


if __name__ == "__main__":
    test_mandel()
