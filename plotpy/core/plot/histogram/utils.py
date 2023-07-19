from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from plotpy.core.items import BaseImageItem, Histogram2DItem
    from plotpy.core.items.histogram import HistDataSource


def hist_range_threshold(
    hist: np.ndarray, bin_edges: np.ndarray, percent: float
) -> tuple[float, float]:
    """Return the range corresponding to the given percent of the histogram

    Args:
        hist (numpy.ndarray): The histogram
        bin_edges (numpy.ndarray): The bin edges
        percent (float): The percent of the histogram

    Returns:
        tuple[float, float]: The range
    """
    hist = np.concatenate((hist, [0]))
    hist = hist[1:]
    bin_edges = bin_edges[1:]
    threshold = 0.5 * percent / 100 * hist.sum()

    i_bin_min = np.cumsum(hist).searchsorted(threshold)
    i_bin_max = -1 - np.cumsum(np.flipud(hist)).searchsorted(threshold)

    return bin_edges[i_bin_min], bin_edges[i_bin_max]


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
