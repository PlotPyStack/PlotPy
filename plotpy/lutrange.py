# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
LUT range
---------

The :mod:`plotpy.lutrange` module provides functions to compute and manipulate
the LUT range of plot items.

.. autofunction:: hist_range_threshold

.. autofunction:: lut_range_threshold
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from plotpy.items import BaseImageItem, Histogram2DItem
    from plotpy.items.histogram import HistDataSource


def hist_range_threshold(
    hist: np.ndarray, bin_edges: np.ndarray, percent: float
) -> tuple[float, float]:
    """Return the range corresponding to the central `percent` of the histogram mass.
    This can be used to eliminate outliers symmetrically, e.g. for contrast adjustment.

    Notes:
        - If the histogram comes from an image with integer values (e.g. 0-255),
          the first bin is assumed to correspond to value 0 and will be ignored.
        - For floating-point images, all bins are considered.

    Args:
        hist: The histogram (length N)
        bin_edges: The bin edges (length N+1)
        percent: Percent of histogram mass to retain (between 0 and 100)

    Returns:
        A tuple containing the minimum and maximum values of the range
        corresponding to the central `percent` of the histogram mass.
    """
    if not (0 <= percent <= 100):
        raise ValueError("percent must be in (0, 100]")

    hist_len = len(hist)
    i_offset = 0

    # 1. Remove the first bin (typically corresponding to 0), only for integer images
    if np.issubdtype(bin_edges.dtype, np.integer):
        hist = hist[1:]
        i_offset = 1

    # 3. Threshold: keep `percent`% of the mass → remove (1 - percent)% symmetrically
    threshold = 0.5 * percent / 100 * hist.sum()

    # 4. Find index where left cumulative sum exceeds threshold
    i_bin_min = max(np.cumsum(hist).searchsorted(threshold) - i_offset, 0)

    # 5. Find index where right cumulative sum exceeds threshold
    i_bin_max = hist_len - np.searchsorted(np.cumsum(np.flipud(hist)), threshold)

    # 6. Return bounds as [bin_edges[i_min], bin_edges[i_max + 1]]
    vmin, vmax = bin_edges[i_bin_min], bin_edges[i_bin_max]

    return vmin, vmax


def lut_range_threshold(
    item: BaseImageItem | Histogram2DItem | HistDataSource, bins: int, percent: float
) -> tuple[float, float]:
    """Return the lut range corresponding to the given percent of the histogram

    Args:
        item (BaseImageItem | Histogram2DItem | HistDataSource): The plot item
        bins (int): The number of bins
        percent (float): The percent of the histogram

    Returns:
        tuple[float, float]: The lut range
    """
    hist, bin_edges = item.get_histogram(bins)
    return hist_range_threshold(hist, bin_edges, percent)
