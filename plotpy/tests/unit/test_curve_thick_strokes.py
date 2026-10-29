# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test the fast drawing of thick curves as several one-pixel strokes"""

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
from plotpy.items.curve.base import (
    THICK_LINE_MAX_STROKES_WIDTH,
    get_thick_line_strokes,
)

WIDTH, HEIGHT = 200, 120


def _image(ratio: float = 1.0) -> QG.QImage:
    """Return a white image with the given device pixel ratio"""
    image = QG.QImage(int(WIDTH * ratio), int(HEIGHT * ratio), QG.QImage.Format_ARGB32)
    image.setDevicePixelRatio(ratio)
    image.fill(QC.Qt.white)
    return image


def _set_option(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """Set the ``curve/fast_thick_lines`` option"""
    original_get = CONF.get

    def get(section, option, *args, **kwargs):
        if (section, option) == ("plot", "curve/fast_thick_lines"):
            return enabled
        return original_get(section, option, *args, **kwargs)

    monkeypatch.setattr(curve_base.CONF, "get", get)


def _strokes(image: QG.QImage, pen: QG.QPen, scale: float = 1.0):
    """Return the strokes of a pen for a painter on an image"""
    painter = QG.QPainter(image)
    if scale != 1.0:
        painter.scale(scale, scale)
    strokes = get_thick_line_strokes(painter, pen)
    painter.end()
    return strokes


def _render(
    width: float, color: str = "#000000", style: str = "-", ratio: float = 1.0
) -> np.ndarray:
    """Render a noisy sine curve and return the image darkness (0 to 1)"""
    rng = np.random.default_rng(0)
    x = np.linspace(0.0, 1.0, 400)
    y = 0.5 + 0.3 * np.sin(12 * x) + 0.03 * rng.standard_normal(x.size)
    curve = make.curve(x, y, color=color, linewidth=width, linestyle=style)
    xmap, ymap = QwtScaleMap(), QwtScaleMap()
    xmap.setPaintInterval(0, WIDTH)
    xmap.setScaleInterval(0.0, 1.0)
    ymap.setPaintInterval(HEIGHT, 0)
    ymap.setScaleInterval(0.0, 1.0)
    image = _image(ratio)
    painter = QG.QPainter(image)
    painter.setRenderHint(QG.QPainter.Antialiasing, True)
    curve.drawSeries(painter, xmap, ymap, QC.QRectF(0, 0, WIDTH, HEIGHT), 0, -1)
    painter.end()
    gray = image.convertToFormat(QG.QImage.Format_Grayscale8)
    data = np.array(
        [
            [gray.pixelColor(col, row).value() for col in range(gray.width())]
            for row in range(gray.height())
        ],
        dtype=float,
    )
    return 1.0 - data / 255.0


def test_thick_line_strokes_offsets() -> None:
    """Strokes cover the line width, horizontally and vertically"""
    with qt_app_context(exec_loop=False):
        pen = QG.QPen(QG.QColor("#000000"), 2.0)
        stroke_pen, offsets = _strokes(_image(), pen)
        assert stroke_pen.isCosmetic() and stroke_pen.widthF() == 1.0
        assert sorted(offsets) == [(-0.5, 0.0), (0.0, -0.5), (0.0, 0.5), (0.5, 0.0)]
        # Width of 3 device pixels with a device pixel ratio of 1.5:
        _stroke_pen, offsets = _strokes(_image(1.5), pen)
        assert len(offsets) == 5
        shifts = sorted(dx * 1.5 for dx, _dy in offsets if _dy == 0.0)
        assert shifts == pytest.approx([-1.0, 0.0, 1.0])
        assert not pen.isCosmetic()  # The original pen is not modified


def test_thick_line_strokes_dash_pattern() -> None:
    """Dash patterns of strokes are scaled by the line width"""
    with qt_app_context(exec_loop=False):
        pen = QG.QPen(QG.QColor("#000000"), 2.0, QC.Qt.DashLine)
        stroke_pen, _offsets = _strokes(_image(), pen)
        assert list(stroke_pen.dashPattern()) == [
            2.0 * length for length in pen.dashPattern()
        ]


@pytest.mark.parametrize(
    "pen_args, scale",
    [
        (("#000000", 1.0), 1.0),  # Thin line
        (("#80000000", 2.0), 1.0),  # Translucent color
        (("#000000", THICK_LINE_MAX_STROKES_WIDTH + 1.0), 1.0),  # Very wide line
        (("#000000", 2.0), 3.0),  # Scaled painter (printing, exporting)
    ],
)
def test_thick_line_pen_kept(pen_args: tuple[str, float], scale: float) -> None:
    """Lines are drawn with their pen when strokes do not apply"""
    with qt_app_context(exec_loop=False):
        color, width = pen_args
        pen = QG.QPen(QG.QColor(color), width)
        assert _strokes(_image(), pen, scale) is None


def test_thick_line_other_engine() -> None:
    """Lines are drawn with their pen on other paint devices"""
    with qt_app_context(exec_loop=False):
        picture = QG.QPicture()
        painter = QG.QPainter(picture)
        assert get_thick_line_strokes(painter, QG.QPen(QG.QColor("red"), 2.0)) is None
        painter.end()


def test_thick_line_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ``curve/fast_thick_lines`` option disables strokes"""
    _set_option(monkeypatch, False)
    with qt_app_context(exec_loop=False):
        assert _strokes(_image(), QG.QPen(QG.QColor("red"), 2.0)) is None


@pytest.mark.parametrize("ratio", [1.0, 1.5])
@pytest.mark.parametrize("width", [1.5, 2.0, 3.0])
def test_thick_line_rendering(
    monkeypatch: pytest.MonkeyPatch, width: float, ratio: float
) -> None:
    """Strokes look like the line drawn with its pen"""
    with qt_app_context(exec_loop=False):
        _set_option(monkeypatch, True)
        strokes = _render(width, ratio=ratio)
        _set_option(monkeypatch, False)
        reference = _render(width, ratio=ratio)
        # Same amount of ink, at the same place:
        assert strokes.sum() == pytest.approx(reference.sum(), rel=0.1)
        assert np.abs(strokes - reference).sum() < 0.2 * reference.sum()
        assert not np.array_equal(strokes, reference)  # Strokes were used


def test_translucent_thick_line_rendering(monkeypatch: pytest.MonkeyPatch) -> None:
    """Translucent thick lines are drawn with their pen"""
    with qt_app_context(exec_loop=False):
        _set_option(monkeypatch, True)
        image = _render(2.0, color="#80ff0000")
        _set_option(monkeypatch, False)
        np.testing.assert_array_equal(image, _render(2.0, color="#80ff0000"))
