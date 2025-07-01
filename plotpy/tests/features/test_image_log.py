# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Logarithmic scale test for image plotting"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv

LOG_MIN, LOG_MAX = 1, 10**8
WAVELENGTHS = (371, 382, 393, 404, 415)


def create_data() -> np.ndarray:
    """Create a sample data set, representing a spectrum"""
    num_bins = 1024
    log_bins = np.logspace(np.log10(LOG_MIN), np.log10(LOG_MAX), num_bins)
    sample_data = np.zeros((num_bins - 1, len(WAVELENGTHS)))
    for i_lambda in range(len(WAVELENGTHS)):
        num_samples = 100000
        mean1, std1 = 10 ** (2 + i_lambda * 0.7), 10 ** (2 + i_lambda * 0.7) * 0.3
        mean2, std2 = 10 ** (4 + i_lambda * 0.5), 10 ** (4 + i_lambda * 0.5) * 0.2
        raw_data = np.abs(
            np.concatenate(
                [
                    np.random.normal(mean1, std1, num_samples // 2),
                    np.random.normal(mean2, std2, num_samples // 2),
                ]
            )
        )
        hist_values, _ = np.histogram(raw_data, bins=log_bins)
        sample_data[:, i_lambda] = hist_values
    return sample_data


def test_image_log() -> None:
    """Image with logarithmic scale"""
    with qt_app_context(exec_loop=True):
        data = create_data()
        xdata = min(WAVELENGTHS), max(WAVELENGTHS)
        ydata = LOG_MIN, LOG_MAX
        x = np.linspace(xdata[0], xdata[1], data.shape[1] + 1)
        y = np.linspace(ydata[0], ydata[1], data.shape[0] + 1)
        y = np.log10(np.clip(y, LOG_MIN, LOG_MAX))
        items = [make.xyimage(x, y, data, interpolation="nearest")]
        _win = ptv.show_items(
            items,
            plot_type="curve",
            wintitle=test_image_log.__doc__,
            xlabel="Wavelength",
            ylabel="log10(Intensity)",
        )


if __name__ == "__main__":
    test_image_log()
