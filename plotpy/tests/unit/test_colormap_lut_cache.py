# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Image lookup tables are cached by colormap content: a cached table always
matches the colormap, its inversion and the alpha settings."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtGui as QG

from plotpy.builder import make
from plotpy.constants import LUT_MAX, LUT_SIZE, LUTAlpha
from plotpy.mathutils.colormap import FULLRANGE, get_cmap


def _expected_lut(table, alpha: float, alpha_function: int) -> np.ndarray:
    """Lookup table computed directly from the colormap."""
    x = np.arange(LUT_SIZE) / float(LUT_SIZE - 1)
    pix_alpha = {
        LUTAlpha.NONE.value: np.ones(LUT_SIZE),
        LUTAlpha.CONSTANT.value: np.full(LUT_SIZE, alpha),
        LUTAlpha.LINEAR.value: alpha * x,
        LUTAlpha.SIGMOID.value: alpha / (1 + np.exp(-10 * x)),
        LUTAlpha.TANH.value: alpha * np.tanh(5 * x),
        LUTAlpha.STEP.value: np.where(x > 0, alpha, 0.0),
    }[alpha_function]
    alpha_channel = np.clip((255 * pix_alpha + 0.5).astype(np.uint32), 0, 255) << 24
    rgb = np.array(
        [table.rgb(FULLRANGE, i / LUT_MAX) & 0xFFFFFF for i in range(LUT_SIZE)],
        dtype=np.uint32,
    )
    return rgb | alpha_channel.astype(np.uint32)


def _image(colormap: str = "jet", **kwargs):
    return make.image(np.zeros((4, 4)), colormap=colormap, **kwargs)


@pytest.mark.parametrize("alpha_function", list(LUTAlpha))
def test_lut_matches_colormap(alpha_function: LUTAlpha) -> None:
    """Each image gets the lookup table of its colormap, alpha and inversion."""
    with qt_app_context(exec_loop=False):
        for invert in (False, True, False):
            for name in ("jet", "viridis", "gray"):
                item = _image(name, alpha_function=alpha_function, alpha=0.6)
                item.set_color_map(name, invert=invert)
                expected = _expected_lut(get_cmap(name), 0.6, alpha_function.value)
                assert np.array_equal(item.lut[3], expected)
                assert item.cmap == get_cmap(name).colorTable(FULLRANGE)


def test_lut_follows_edited_colormap() -> None:
    """Editing a colormap after a first use gives a new lookup table."""
    with qt_app_context(exec_loop=False):
        table = copy.deepcopy(get_cmap("jet"))
        first = _image()
        first.set_color_map(table)
        before = first.lut[3].copy()

        table.addColorStop(0.5, QG.QColor(255, 255, 255))
        second = _image()
        second.set_color_map(table)
        expected = _expected_lut(table, 1.0, LUTAlpha.NONE.value)
        assert np.array_equal(second.lut[3], expected)
        assert not np.array_equal(second.lut[3], before)


def test_items_do_not_share_lookup_tables() -> None:
    """Changing the lookup table of an item leaves the other items unchanged."""
    with qt_app_context(exec_loop=False):
        first, second = _image(), _image()
        first.lut[3][:] = 0
        third = _image()
        expected = _expected_lut(get_cmap("jet"), 1.0, LUTAlpha.NONE.value)
        assert np.array_equal(second.lut[3], expected)
        assert np.array_equal(third.lut[3], expected)
