# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve plotting with time axis test"""

# guitest: show

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def __create_time_data() -> tuple[np.ndarray, np.ndarray]:
    """Create time data"""
    # Create a temperature monitoring signal with second-resolution timestamps
    base_time = datetime(2025, 10, 7, 10, 0, 0)
    timestamps = [base_time + timedelta(seconds=i * 10) for i in range(100)]

    # Convert timestamps to numpy array of floats (seconds since epoch)
    x = np.array([(ts - datetime(1970, 1, 1)).total_seconds() for ts in timestamps])

    # Simulate temperature data with daily variation and noise
    hours_elapsed = np.arange(100) * 10 / 3600  # Convert to hours
    y = 20 + 5 * np.sin(2 * np.pi * hours_elapsed / 24) + np.random.randn(100) * 0.5

    return x, y


def test_plot_time_axis():
    """Test plot time axis"""
    with qt_app_context(exec_loop=True):
        x, y = __create_time_data()
        items = [make.curve(x, y, color="b")]
        win = ptv.show_items(
            items, plot_type="curve", wintitle=test_plot_time_axis.__doc__
        )
        plot = win.manager.get_plot()
        # Configure x-axis for datetime display
        plot.set_axis_datetime("bottom", format="%H:%M:%S")
        # Set axis limits using datetime objects (zoom to first half of data)
        base_time = datetime(2025, 10, 7, 10, 0, 0)
        plot.set_axis_limits_from_datetime(
            "bottom",
            base_time,
            base_time + timedelta(minutes=10),
        )


if __name__ == "__main__":
    test_plot_time_axis()
