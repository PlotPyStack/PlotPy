# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test PlotBuilder image factory methods"""

import numpy as np
import pytest

from plotpy.builder import make
from plotpy.styles import LUTAlpha
from plotpy.tests.unit.test_builder_curve import show_items_qtbot


def _make_image(
    alpha_function=None,
    xdata=[None, None],
    ydata=[None, None],
    pixel_size=None,
    center_on=None,
    interpolation="linear",
    background_color=None,
    eliminate_outliers=None,
    lut_range=None,
    lock_position=None,
):
    """Make image"""
    data = np.ones((50, 50), dtype=np.uint16)
    return make.image(
        data,
        title="Title",
        alpha_function=alpha_function,
        alpha=0.5,
        xdata=xdata,
        ydata=ydata,
        pixel_size=pixel_size,
        center_on=center_on,
        interpolation=interpolation,
        background_color=background_color,
        colormap="jet",
        eliminate_outliers=eliminate_outliers,
        xformat="%.1f",
        yformat="%.1f",
        zformat="%.1f",
        lut_range=lut_range,
        lock_position=lock_position,
    )


@pytest.mark.parametrize(
    "alpha_function",
    [
        None,
        LUTAlpha.NONE,
        LUTAlpha.CONSTANT,
        LUTAlpha.LINEAR,
        LUTAlpha.SIGMOID,
        LUTAlpha.TANH,
    ],
)
def test_builder_image_alpha_function(qtbot, alpha_function):
    item = _make_image(alpha_function=alpha_function)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize(
    "xdata,ydata", [[[None, None], [None, None]], [[-10, 10], [-10, 10]]]
)
def test_builder_image_xdata_ydata(qtbot, xdata, ydata):
    item = _make_image(xdata=xdata, ydata=ydata)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("pixel_size", [None, 1.0, (1.0, 2.0)])
def test_builder_image_pixel_size(qtbot, pixel_size):
    item = _make_image(pixel_size=pixel_size)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("center_on", [None, [1.0, 3.0]])
def test_builder_image_center_on(qtbot, center_on):
    item = _make_image(center_on=center_on, pixel_size=(1.0, 1.0))
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("interpolation", ["nearest", "linear", "antialiasing"])
def test_builder_image_interpolation(qtbot, interpolation):
    item = _make_image(interpolation=interpolation)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("background_color", [None, "red"])
def test_builder_image_background_color(qtbot, background_color):
    item = _make_image(background_color=background_color)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("eliminate_outliers", [None, 3.0])
def test_builder_image_eliminate_outliers(qtbot, eliminate_outliers):
    item = _make_image(eliminate_outliers=eliminate_outliers)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("lut_range", [None, [0.0, 100.0]])
def test_builder_image_lut_range(qtbot, lut_range):
    item = _make_image(lut_range=lut_range)
    show_items_qtbot(qtbot, [item])


@pytest.mark.parametrize("lock_position", [None, True, False])
def test_builder_image_lock_position(qtbot, lock_position):
    item = _make_image(lock_position=lock_position)
    show_items_qtbot(qtbot, [item])
