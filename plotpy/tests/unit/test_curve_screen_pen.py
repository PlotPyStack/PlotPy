# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test the cosmetic pen used to draw thin curves on screen"""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtScaleMap

from plotpy.builder import make
from plotpy.config import CONF
from plotpy.items.curve import base as curve_base
from plotpy.items.curve.base import get_screen_pen

WIDTH, HEIGHT = 100, 60


def _scale_maps() -> tuple[QwtScaleMap, QwtScaleMap]:
    """Return X and Y scale maps from [0, 1] to the image area"""
    xmap, ymap = QwtScaleMap(), QwtScaleMap()
    xmap.setPaintInterval(0, WIDTH)
    xmap.setScaleInterval(0.0, 1.0)
    ymap.setPaintInterval(HEIGHT, 0)
    ymap.setScaleInterval(0.0, 1.0)
    return xmap, ymap


def _hidpi_image(ratio: float = 2.0) -> QG.QImage:
    """Return a white image with the given device pixel ratio"""
    image = QG.QImage(int(WIDTH * ratio), int(HEIGHT * ratio), QG.QImage.Format_ARGB32)
    image.setDevicePixelRatio(ratio)
    image.fill(QC.Qt.white)
    return image


def _painted_rows(image: QG.QImage, column: int) -> int:
    """Return the number of non-white pixels in an image column"""
    white = QG.QColor(QC.Qt.white).rgb()
    return sum(image.pixel(column, row) != white for row in range(image.height()))


def _painted_columns(image: QG.QImage, row: int) -> int:
    """Return the number of non-white pixels in an image row"""
    white = QG.QColor(QC.Qt.white).rgb()
    return sum(image.pixel(col, row) != white for col in range(image.width()))


def _draw_horizontal_curve(image: QG.QImage, width: float) -> None:
    """Draw a horizontal black curve in the middle of the image"""
    x = np.linspace(0.0, 1.0, 50)
    y = np.full_like(x, 0.5)
    curve = make.curve(x, y, color="#000000", linewidth=width)
    xmap, ymap = _scale_maps()
    painter = QG.QPainter(image)
    curve.drawSeries(painter, xmap, ymap, QC.QRectF(0, 0, WIDTH, HEIGHT), 0, -1)
    painter.end()


def _disable_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable the ``curve/cosmetic_hairline`` option"""
    original_get = CONF.get

    def get(section, option, *args, **kwargs):
        if (section, option) == ("plot", "curve/cosmetic_hairline"):
            return False
        return original_get(section, option, *args, **kwargs)

    monkeypatch.setattr(curve_base.CONF, "get", get)


def test_screen_pen_raster() -> None:
    """Thin pens become cosmetic on screen, wide pens are left unchanged"""
    with qt_app_context(exec_loop=False):
        image = _hidpi_image()
        painter = QG.QPainter(image)
        for width in (0.5, 1.0):
            pen = QG.QPen(QG.QColor("red"), width)
            screen_pen = get_screen_pen(painter, pen)
            assert screen_pen.isCosmetic()
            assert screen_pen.widthF() == width
            assert not pen.isCosmetic()  # The original pen is not modified
        pen = QG.QPen(QG.QColor("red"), 2.0)
        assert get_screen_pen(painter, pen) is pen
        painter.end()


def test_screen_pen_print_and_export() -> None:
    """Pens are left unchanged for other paint engines or scaled painters"""
    with qt_app_context(exec_loop=False):
        pen = QG.QPen(QG.QColor("red"), 1.0)
        picture = QG.QPicture()
        painter = QG.QPainter(picture)
        assert get_screen_pen(painter, pen) is pen
        painter.end()
        image = _hidpi_image()
        painter = QG.QPainter(image)
        painter.scale(3.0, 3.0)  # As done by QwtPlotRenderer for printing
        assert get_screen_pen(painter, pen) is pen
        painter.end()


def test_screen_pen_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ``curve/cosmetic_hairline`` option disables cosmetic pens"""
    _disable_option(monkeypatch)
    with qt_app_context(exec_loop=False):
        image = _hidpi_image()
        painter = QG.QPainter(image)
        pen = QG.QPen(QG.QColor("red"), 1.0)
        assert get_screen_pen(painter, pen) is pen
        painter.end()


def test_curve_hidpi_rendering(monkeypatch: pytest.MonkeyPatch) -> None:
    """Curves of width 1 are drawn one device pixel wide on HiDPI screens"""
    with qt_app_context(exec_loop=False):
        image = _hidpi_image()
        _draw_horizontal_curve(image, 1.0)
        assert _painted_rows(image, image.width() // 2) == 1
        image = _hidpi_image()
        _draw_horizontal_curve(image, 2.0)
        assert _painted_rows(image, image.width() // 2) == 4
        _disable_option(monkeypatch)
        image = _hidpi_image()
        _draw_horizontal_curve(image, 1.0)
        assert _painted_rows(image, image.width() // 2) == 2


def test_curve_pen_parameters() -> None:
    """The stored curve pen and its parameters are not modified"""
    with qt_app_context(exec_loop=False):
        curve = make.curve([0.0, 1.0], [0.0, 1.0], color="#000000", linewidth=1.0)
        image = _hidpi_image()
        painter = QG.QPainter(image)
        xmap, ymap = _scale_maps()
        curve.drawSeries(painter, xmap, ymap, QC.QRectF(0, 0, WIDTH, HEIGHT), 0, -1)
        painter.end()
        assert not curve.pen().isCosmetic()
        curve.param.update_param(curve)
        assert curve.param.line.width == 1.0


def test_errorbar_hidpi_rendering() -> None:
    """Error bars of width 1 are drawn one device pixel wide on HiDPI screens"""
    with qt_app_context(exec_loop=False):
        x = np.array([0.5])
        y = np.array([0.5])
        dy = np.array([0.3])
        item = make.error(x, y, None, dy, curvestyle="NoCurve", errorbarcap=0)
        image = _hidpi_image()
        painter = QG.QPainter(image)
        xmap, ymap = _scale_maps()
        item.draw(painter, xmap, ymap, QC.QRectF(0, 0, WIDTH, HEIGHT))
        painter.end()
        assert _painted_columns(image, image.height() // 2) == 1
