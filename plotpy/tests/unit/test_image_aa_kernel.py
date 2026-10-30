# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Anti-aliasing interpolation kernel of image items (Issue #89).

The scaling functions require the anti-aliasing kernel to have the data type of
the data they scale: exporting and drawing an image must work whatever the Z-axis
scale and the data type of the image data.
"""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qwt import QwtScaleMap

from plotpy.builder import make
from plotpy.items import assemble_imageitems

KINDS = ("image", "xyimage", "trimage", "maskedimage", "maskedxyimage")
DTYPES = (np.uint8, np.uint16, np.int32, np.float32)
NY, NX = 6, 8


def _data(dtype: type) -> np.ndarray:
    """Return image data of the given data type"""
    return np.arange(1, NY * NX + 1).reshape(NY, NX).astype(dtype)


def _make_item(kind: str, data: np.ndarray):
    """Return an image item of the given kind, with the anti-aliasing
    interpolation"""
    x, y = np.arange(NX, dtype=float), np.arange(NY, dtype=float)
    mask = np.zeros(data.shape, dtype=bool)
    interpolation = "antialiasing"
    builders = {
        "image": lambda: make.image(data, interpolation=interpolation),
        "xyimage": lambda: make.xyimage(x, y, data, interpolation=interpolation),
        "trimage": lambda: make.trimage(data, interpolation=interpolation),
        "maskedimage": lambda: make.maskedimage(
            data, mask, interpolation=interpolation
        ),
        "maskedxyimage": lambda: make.maskedxyimage(
            x, y, data, mask, interpolation=interpolation
        ),
    }
    return builders[kind]()


def _export(item, apply_lut: bool) -> np.ndarray:
    """Export the image with its interpolation"""
    rect = QC.QRectF(0, 0, NX, NY)
    return assemble_imageitems(
        [item], rect, NX, NY, apply_lut=apply_lut, apply_interpolation=True
    )


def _draw(item) -> None:
    """Draw the image item on an image, raising the exceptions which would be
    raised in the plot's paint event"""
    width, height = 4 * NX, 4 * NY
    xmap, ymap = QwtScaleMap(), QwtScaleMap()
    xmap.setPaintInterval(0, width)
    xmap.setScaleInterval(0, NX)
    ymap.setPaintInterval(0, height)
    ymap.setScaleInterval(0, NY)
    image = QG.QImage(width, height, QG.QImage.Format_ARGB32)
    painter = QG.QPainter(image)
    try:
        item.draw(painter, xmap, ymap, QC.QRectF(0, 0, width, height))
    finally:
        painter.end()


def _plot_with_item(item):
    """Return a plot window showing the image item"""
    # In unattended mode, leaving a `qt_app_context` schedules the closing of all
    # top-level widgets: process it now, so that it does not close this window
    QW.QApplication.processEvents()
    win = make.dialog(type="image")
    win.manager.get_plot().add_item(item)
    return win


@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("kind", KINDS)
def test_export_with_anti_aliasing(kind: str, dtype: type) -> None:
    """Exporting an image area with the anti-aliasing interpolation works with or
    without the LUT, with or without the Z-axis log scale"""
    with qt_app_context(exec_loop=False):
        item = _make_item(kind, _data(dtype))
        for log_state in (False, True):
            item.set_zaxis_log_state(log_state)
            for apply_lut in (False, True):
                assert _export(item, apply_lut).shape == (NY, NX)


@pytest.mark.parametrize("kind", KINDS)
def test_set_data_of_another_data_type(kind: str) -> None:
    """After replacing the data by data of another type, the kernel has the data
    type of the data drawn, and the image can be drawn and exported"""
    with qt_app_context(exec_loop=False):
        item = _make_item(kind, _data(np.uint16))
        win = _plot_with_item(item)
        for log_state in (False, True):
            item.set_zaxis_log_state(log_state)
            for dtype in (np.float32, np.uint8):
                item.set_data(_data(dtype))
                # With the log scale, the data drawn is the float64 logarithm
                expected_dtype = np.float64 if log_state else dtype
                assert item.interpolate[1].dtype == expected_dtype
                _draw(item)
                for apply_lut in (False, True):
                    assert _export(item, apply_lut).shape == (NY, NX)
        win.close()


if __name__ == "__main__":
    for _kind in KINDS:
        for _dtype in DTYPES:
            test_export_with_anti_aliasing(_kind, _dtype)
        test_set_data_of_another_data_type(_kind)
