# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Unit tests for the rectangular snapshot tool's "Original size" computation.

This test reproduces the issue reported in PlotPyStack/PlotPy#57:

    The "Original size" option in the rectangular snapshot tool does not behave
    correctly under certain conditions:

    * When the Y axis is not reversed (image-style plot)
    * When the X axis is reversed
    * When using an XYImageItem

    In these cases, the "Original size" preview may display negative values or
    incorrect dimensions. The computation appears to rely on axis scaling
    rather than pixel coordinates, particularly for ``XYImageItem``.

    Additionally, a ``ValueError`` is raised when either axis leads to negative
    values.
"""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC

from plotpy.builder import make
from plotpy.items import (
    compute_image_items_original_size,
    compute_trimageitems_original_size,
)
from plotpy.tests import vistools as ptv

# Image used by the tests (rows = Y, cols = X)
NB_ROWS, NB_COLS = 100, 200


def _canvas_points(plot, x0_plot, y0_plot, x1_plot, y1_plot):
    """Convert plot-coordinate corners into canvas QPointF, the way the
    snapshot tool builds them from a rubber-band rectangle."""
    from plotpy.constants import X_BOTTOM, Y_LEFT

    x0c = plot.transform(X_BOTTOM, x0_plot)
    x1c = plot.transform(X_BOTTOM, x1_plot)
    y0c = plot.transform(Y_LEFT, y0_plot)
    y1c = plot.transform(Y_LEFT, y1_plot)
    # Mimic the tool: p0 is top-left, p1 is bottom-right (in canvas pixels)
    p0 = QC.QPointF(min(x0c, x1c), min(y0c, y1c))
    p1 = QC.QPointF(max(x0c, x1c), max(y0c, y1c))
    return p0, p1


def test_compute_trimageitems_original_size_handles_reversed_axes():
    """Regression: ``compute_trimageitems_original_size`` must return positive
    dimensions even when the source rectangle is given with negative width or
    height (which happens on reversed axes)."""
    # No items: legacy fallback path
    w, h = compute_trimageitems_original_size([], -50.0, -25.0)
    assert w == 50.0 and h == 25.0


def _expected_pixel_size(x0, y0, x1, y1):
    """Original (pixel) size for a selection on a non-transformed image
    spanning [0, NB_COLS] x [0, NB_ROWS] in plot units."""
    return abs(x1 - x0), abs(y1 - y0)


@pytest.mark.parametrize(
    "xreverse,yreverse",
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_snapshot_original_size_with_image_item(xreverse, yreverse):
    """Original size must be positive and equal to the pixel selection size,
    regardless of axis orientation, for a regular ``ImageItem``."""
    data = np.arange(NB_ROWS * NB_COLS, dtype=np.float64).reshape(NB_ROWS, NB_COLS)
    with qt_app_context(exec_loop=False):
        image = make.image(data)
        win = ptv.show_items([image], plot_type="image", auto_tools=False)
        plot = win.manager.get_plot()
        plot.set_axis_direction("bottom", xreverse)
        plot.set_axis_direction("left", yreverse)
        plot.replot()

        # Selection in plot coordinates: a 40x30 pixel rectangle
        x0, y0, x1, y1 = 30.0, 20.0, 70.0, 50.0
        p0, p1 = _canvas_points(plot, x0, y0, x1, y1)

        width, height = compute_image_items_original_size([image], plot, p0, p1)

        exp_w, exp_h = _expected_pixel_size(x0, y0, x1, y1)
        # Allow 1 pixel tolerance for canvas rounding
        assert width > 0 and height > 0
        assert abs(width - exp_w) <= 1.5
        assert abs(height - exp_h) <= 1.5
        win.close()


def test_snapshot_original_size_with_xy_image_item():
    """For an ``XYImageItem``, the original size must be expressed in **pixel**
    coordinates (independent of axis scaling), not in axis units."""
    data = np.arange(NB_ROWS * NB_COLS, dtype=np.float64).reshape(NB_ROWS, NB_COLS)
    # Non-trivial axis scaling: 1 pixel == 5 axis units (X), 2 axis units (Y)
    x = np.linspace(0.0, NB_COLS * 5.0, NB_COLS + 1)
    y = np.linspace(0.0, NB_ROWS * 2.0, NB_ROWS + 1)
    with qt_app_context(exec_loop=False):
        image = make.xyimage(x, y, data)
        win = ptv.show_items([image], plot_type="image", auto_tools=False)
        plot = win.manager.get_plot()
        plot.replot()

        # Selection spanning ~40 columns and ~30 rows in pixel space:
        x0, x1 = 30.0 * 5.0, 70.0 * 5.0  # 40 columns
        y0, y1 = 20.0 * 2.0, 50.0 * 2.0  # 30 rows
        p0, p1 = _canvas_points(plot, x0, y0, x1, y1)

        width, height = compute_image_items_original_size([image], plot, p0, p1)

        # Must be in pixel units, not axis units (axis units would give
        # ~200 x ~60 instead of ~40 x ~30)
        assert width > 0 and height > 0
        assert abs(width - 40) <= 5
        assert abs(height - 30) <= 5
        win.close()


@pytest.mark.parametrize("make_factory", ["image", "xyimage"])
def test_snapshot_original_size_selection_larger_than_image(make_factory):
    """When the selection is larger than the plotted image, the "Original size"
    must correspond to the clipped intersection with the image (i.e. the full
    image when the selection fully covers it), consistently for both
    ``ImageItem`` and ``XYImageItem``.

    Regression for the off-by-one inconsistency reported in issue #57
    (99x99 for XYImageItem vs. oversized for ImageItem on a 100x100 image).
    """
    data = np.arange(NB_ROWS * NB_COLS, dtype=np.float64).reshape(NB_ROWS, NB_COLS)
    with qt_app_context(exec_loop=False):
        if make_factory == "image":
            image = make.image(data)
        else:
            x = np.linspace(0.0, float(NB_COLS), NB_COLS + 1)
            y = np.linspace(0.0, float(NB_ROWS), NB_ROWS + 1)
            image = make.xyimage(x, y, data)
        win = ptv.show_items([image], plot_type="image", auto_tools=False)
        plot = win.manager.get_plot()
        plot.replot()

        # Selection much larger than the image (negative lower bound, upper
        # bound well beyond the image):
        x0, y0, x1, y1 = -50.0, -50.0, NB_COLS + 50.0, NB_ROWS + 50.0
        p0, p1 = _canvas_points(plot, x0, y0, x1, y1)

        width, height = compute_image_items_original_size([image], plot, p0, p1)

        # Must match the full image size exactly (not shape - 1, not oversize)
        assert abs(width - NB_COLS) <= 1
        assert abs(height - NB_ROWS) <= 1
        win.close()
