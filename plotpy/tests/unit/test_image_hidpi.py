# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test the rendering of images at the resolution of HiDPI screens"""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.builder import make
from plotpy.config import CONF
from plotpy.items import RawImageItem
from plotpy.items.image import base as image_base
from plotpy.items.image.base import get_offscreen_ratio
from plotpy.plot import BasePlot, BasePlotOptions

WIDTH, HEIGHT = 200, 150


def _hidpi_image(ratio: float) -> QG.QImage:
    """Return a white image of the canvas size with the given device pixel ratio"""
    image = QG.QImage(
        round(WIDTH * ratio), round(HEIGHT * ratio), QG.QImage.Format_ARGB32
    )
    image.setDevicePixelRatio(ratio)
    image.fill(QC.Qt.white)
    return image


def _render_item(item, ratio: float) -> QG.QImage:
    """Draw an image item, filling the canvas, into an image with the given device
    pixel ratio, and return it"""
    plot = BasePlot(options=BasePlotOptions(type="image"))
    plot.add_item(item)
    plot.resize(WIDTH, HEIGHT)
    plot.set_aspect_ratio(lock=False)
    xl, yt, xr, yb = item.boundingRect().getCoords()
    plot.set_plot_limits(xl, xr, yt, yb)
    xmap, ymap = _canvas_maps(plot, item)
    image = _hidpi_image(ratio)
    painter = QG.QPainter(image)
    item.draw(painter, xmap, ymap, QC.QRectF(0, 0, WIDTH, HEIGHT))
    painter.end()
    return image


def _canvas_maps(plot: BasePlot, item):
    """Return the scale maps of the item axes, from its bounds to the canvas"""
    xmap = plot.canvasMap(item.xAxis())
    ymap = plot.canvasMap(item.yAxis())
    xmap.setPaintInterval(0, WIDTH)
    ymap.setPaintInterval(0, HEIGHT)
    return xmap, ymap


def _duplicated_columns(image: QG.QImage) -> float:
    """Return the ratio of image columns identical to the previous one, in the
    central part of the image"""
    w, h = image.width(), image.height()
    rows = range(h // 4, 3 * h // 4)
    columns = [
        [image.pixel(col, row) for row in rows] for col in range(w // 4, 3 * w // 4)
    ]
    same = sum(prev == cur for prev, cur in zip(columns[:-1], columns[1:]))
    return same / (len(columns) - 1)


def _noise() -> np.ndarray:
    """Return image data with more pixels than the canvas"""
    return np.random.default_rng(0).random((4 * HEIGHT, 4 * WIDTH))


def _disable_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable the ``image/device_resolution`` option"""
    original_get = CONF.get

    def get(section, option, *args, **kwargs):
        if (section, option) == ("plot", "image/device_resolution"):
            return False
        return original_get(section, option, *args, **kwargs)

    monkeypatch.setattr(image_base.CONF, "get", get)


def test_offscreen_ratio() -> None:
    """Images are rendered at the device resolution on screen only"""
    with qt_app_context(exec_loop=False):
        for ratio in (1.0, 1.25, 2.0):
            image = _hidpi_image(ratio)
            painter = QG.QPainter(image)
            assert get_offscreen_ratio(painter) == ratio
            painter.scale(3.0, 3.0)  # As done by QwtPlotRenderer for printing
            assert get_offscreen_ratio(painter) == 1.0
            painter.end()


def test_offscreen_ratio_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ``image/device_resolution`` option disables the device resolution"""
    _disable_option(monkeypatch)
    with qt_app_context(exec_loop=False):
        image = _hidpi_image(2.0)
        painter = QG.QPainter(image)
        assert get_offscreen_ratio(painter) == 1.0
        painter.end()


@pytest.mark.parametrize("ratio", (1.25, 2.0))
@pytest.mark.parametrize("kind", ("image", "xyimage", "trimage", "maskedimage"))
def test_image_device_resolution(kind: str, ratio: float) -> None:
    """Images are not upscaled from the canvas resolution on HiDPI screens"""
    with qt_app_context(exec_loop=False):
        data = _noise()
        if kind == "image":
            item = make.image(data)
        elif kind == "xyimage":
            ny, nx = data.shape
            item = make.xyimage(np.arange(nx) * 1.0, np.arange(ny) * 1.0, data)
        elif kind == "trimage":
            item = make.trimage(data)
        else:
            mask = np.zeros(data.shape, bool)
            item = make.maskedimage(data, mask, show_mask=True)
        # Upscaling 4 canvas pixels to 5 (125%) or 1 to 2 (200%) device pixels
        # duplicates at least 1 device column out of 5 or 2
        assert _duplicated_columns(_render_item(item, ratio)) < 0.05


def test_image_canvas_resolution_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """With the ``image/device_resolution`` option disabled, images are upscaled
    from the canvas resolution, as before"""
    _disable_option(monkeypatch)
    with qt_app_context(exec_loop=False):
        image = _render_item(make.image(_noise()), 2.0)
        assert _duplicated_columns(image) == pytest.approx(0.5, abs=0.05)


def test_raw_image_item() -> None:
    """Raw image items are drawn (their destination rectangle is converted to
    offscreen image pixels, as expected by the scaling function)"""
    with qt_app_context(exec_loop=False):
        image = _render_item(RawImageItem(_noise()), 1.0)
        white = QG.QColor(QC.Qt.white).rgb()
        assert image.pixel(image.width() // 2, image.height() // 2) != white
