import numpy as np


def hist_range_threshold(hist, bin_edges, percent):
    """

    :param hist:
    :param bin_edges:
    :param percent:
    :return:
    """
    hist = np.concatenate((hist, [0]))
    hist = hist[1:]
    bin_edges = bin_edges[1:]
    threshold = 0.5 * percent / 100 * hist.sum()

    i_bin_min = np.cumsum(hist).searchsorted(threshold)
    i_bin_max = -1 - np.cumsum(np.flipud(hist)).searchsorted(threshold)

    return bin_edges[i_bin_min], bin_edges[i_bin_max]


def lut_range_threshold(item, bins, percent):
    """

    :param item:
    :param bins:
    :param percent:
    :return:
    """
    hist, bin_edges = item.get_histogram(bins)
    return hist_range_threshold(hist, bin_edges, percent)
