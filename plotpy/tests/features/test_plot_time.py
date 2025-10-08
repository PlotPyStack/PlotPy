# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve plotting with time axis test"""

# guitest: show

from __future__ import annotations

import csv
from datetime import datetime, timedelta

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.plot import PlotWidget
from plotpy.tests import get_path, vistools
from plotpy.tools import VCursorTool


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


def test_plot_time_axis1():
    """Test plot time axis"""
    with qt_app_context(exec_loop=True):
        x, y = __create_time_data()
        items = [make.curve(x, y, color="b")]
        win = vistools.show_items(
            items, plot_type="curve", wintitle=test_plot_time_axis1.__doc__
        )
        win.manager.add_tool(VCursorTool)
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


def test_plot_time_axis2():
    """Test plot time axis with data from file"""
    datafile = get_path("datetime.txt")

    # Read data from file without Pandas dependency
    timestamps = []
    temperatures = []

    with open(datafile, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row

        for row in reader:
            if len(row) >= 3:  # Ensure we have at least timestamp and temperature
                try:
                    # Parse timestamp (column 1) and temperature (column 2)
                    timestamp_str = row[1]
                    temperature = float(row[2])

                    # Parse datetime and convert to seconds since epoch
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    timestamp_epoch = (dt - datetime(1970, 1, 1)).total_seconds()

                    timestamps.append(timestamp_epoch)
                    temperatures.append(temperature)
                except (ValueError, IndexError):
                    # Skip malformed rows
                    continue

    # Convert to numpy arrays
    x = np.array(timestamps)
    y = np.array(temperatures)

    with qt_app_context(exec_loop=True):
        items = [make.curve(x, y, color="r")]
        win = vistools.show_items(
            items, plot_type="curve", wintitle=test_plot_time_axis2.__doc__
        )
        plot = win.manager.get_plot()
        # Configure x-axis for datetime display
        plot.set_axis_datetime("bottom", format="%Y-%m-%d %H:%M")

        # Set axis limits using datetime objects
        if len(timestamps) > 0:
            dt1 = datetime(2025, 6, 19, 10, 0)
            dt2 = datetime(2025, 6, 19, 12, 0)
            plot.set_axis_limits_from_datetime("bottom", dt1, dt2)


def test_datetime_scale_type():
    """Test the new 'datetime' scale type API"""
    with qt_app_context():
        from plotpy.plot import PlotWidget

        plot_widget = PlotWidget()
        plot = plot_widget.plot

        # Test setting datetime scale type
        plot.set_axis_scale("bottom", "datetime")
        assert plot.get_axis_scale("bottom") == "datetime"

        # Test scale switching
        plot.set_axis_scale("bottom", "lin")
        assert plot.get_axis_scale("bottom") == "lin"

        plot.set_axis_scale("bottom", "log")
        assert plot.get_axis_scale("bottom") == "log"

        plot.set_axis_scale("bottom", "datetime")
        assert plot.get_axis_scale("bottom") == "datetime"

        # Verify the scale engine type
        from qwt import QwtDateTimeScaleEngine

        axis_id = plot.get_axis_id("bottom")
        engine = plot.axisScaleEngine(axis_id)
        assert isinstance(engine, QwtDateTimeScaleEngine)

        print("✓ Datetime scale type tests passed")


def test_datetime_coordinate_formatting():
    """Test that coordinates are formatted as datetime when axis is in datetime mode"""
    with qt_app_context():
        plot_widget = PlotWidget()
        plot = plot_widget.plot

        # Create datetime data
        start_time = datetime(2024, 1, 15, 10, 0, 0)
        times = [start_time + timedelta(hours=x) for x in range(24)]
        timestamps = [t.timestamp() for t in times]
        values = np.random.random(len(times))

        # Add curve and set datetime scale
        curve = make.curve(timestamps, values, title="Test curve")
        plot.add_item(curve)
        plot.set_axis_limits("bottom", timestamps[0], timestamps[-1])
        plot.set_axis_scale("bottom", "datetime")

        # Test coordinate formatting
        test_time = timestamps[12]  # Noon
        test_value = values[12]

        # Test plot-level coordinate display
        grid_coords = plot.get_coordinates_str(test_time, test_value)
        assert "2024-01-15" in grid_coords, (
            f"Grid coordinates should contain datetime: {grid_coords}"
        )

        # Test curve-level coordinate display
        curve_coords = curve.get_coordinates_label(test_time, test_value)
        assert "2024-01-15" in curve_coords, (
            f"Curve coordinates should contain datetime: {curve_coords}"
        )

        # Test with custom format
        plot.set_axis_datetime("bottom", format="%H:%M")
        custom_coords = plot.get_coordinates_str(test_time, test_value)
        expected_time = datetime.fromtimestamp(test_time).strftime("%H:%M")
        assert expected_time in custom_coords, (
            f"Custom format coordinates should contain {expected_time}: {custom_coords}"
        )

        # Test switch back to linear
        plot.set_axis_scale("bottom", "lin")
        linear_coords = plot.get_coordinates_str(test_time, test_value)
        assert (
            str(int(test_time)) in linear_coords or f"{test_time:g}" in linear_coords
        ), f"Linear coordinates should contain numeric timestamp: {linear_coords}"

        print("✓ Datetime coordinate formatting tests passed")


if __name__ == "__main__":
    test_plot_time_axis1()
    test_plot_time_axis2()
    test_datetime_scale_type()
    test_datetime_coordinate_formatting()
