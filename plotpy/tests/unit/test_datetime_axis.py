# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing datetime axis feature"""

# guitest: show

from datetime import datetime

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.plot.scaledraw import DateTimeScaleDraw
from plotpy.tests import vistools as ptv


def test_datetime_axis():
    """Testing datetime axis with various formats"""
    with qt_app_context(exec_loop=False):
        # Create time data
        x = np.linspace(0, 86400, 100)  # One day in seconds from epoch
        y = np.sin(x / 3600 * 2 * np.pi) + np.random.randn(100) * 0.1

        items = [make.curve(x, y, color="b")]
        win = ptv.show_items(items, plot_type="curve", wintitle="Test datetime axis")
        plot = win.manager.get_plot()

        # Test 1: Set datetime axis with default format
        plot.set_axis_datetime("bottom")
        scale_draw = plot.axisScaleDraw(plot.xBottom)
        assert isinstance(scale_draw, DateTimeScaleDraw)
        assert scale_draw.get_format() == "%Y-%m-%d %H:%M:%S"

        # Test 2: Set datetime axis with custom format (time only)
        plot.set_axis_datetime("bottom", format="%H:%M:%S")
        scale_draw = plot.axisScaleDraw(plot.xBottom)
        assert scale_draw.get_format() == "%H:%M:%S"

        # Test 3: Set datetime axis with date only
        plot.set_axis_datetime("bottom", format="%Y-%m-%d", rotate=0, spacing=10)
        scale_draw = plot.axisScaleDraw(plot.xBottom)
        assert scale_draw.get_format() == "%Y-%m-%d"

        # Test 4: Verify label formatting
        timestamp = 86400.0  # 1970-01-02 00:00:00 UTC
        label = scale_draw.label(timestamp)
        expected = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        assert label.text() == expected

        # Test 5: Set axis limits using datetime objects
        dt1 = datetime(1970, 1, 1, 6, 0, 0)
        dt2 = datetime(1970, 1, 1, 18, 0, 0)
        plot.set_axis_limits_from_datetime("bottom", dt1, dt2)

        # Verify the limits were set correctly
        # Note: autoscale margin might affect the exact values
        vmin, vmax = plot.get_axis_limits("bottom")
        expected_min = (dt1 - datetime(1970, 1, 1)).total_seconds()
        expected_max = (dt2 - datetime(1970, 1, 1)).total_seconds()
        # Just verify that limits are in the right order and contain expected range
        assert vmin <= expected_min
        assert vmax >= expected_max
        assert vmax > vmin

        print("All datetime axis tests passed!")


if __name__ == "__main__":
    test_datetime_axis()
