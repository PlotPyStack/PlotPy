from __future__ import annotations

from typing import Callable

import numpy as np
from guidata.qthelpers import exec_dialog, qt_app_context
from numpy import linspace

from plotpy.interfaces.items import ICurveItemType
from plotpy.tests.unit.utils import create_window, drag_mouse
from plotpy.tools import RectZoomTool


def zoom(
    x_path: np.ndarray, y_path: np.ndarray, compare: Callable[[float, float], bool]
):
    """Zoom in or out on a plot by sumilating a mouse drag along a defined path.

    Args:
        x_path: The x relative plot coordinates of the path to simulate the mouse
         drag along.
        y_path: The y relative plot coordinates of the path to simulate the mouse
         drag along.
        compare: Comparison function to compare the initial and final axis limits to
         check if the zoom worked as expected.
    """
    with qt_app_context(exec_loop=False):
        win, _tool = create_window(RectZoomTool, active_item_type=ICurveItemType)
        plot = win.manager.get_plot()
        initial_axis_limits = [
            plot.get_axis_limits(axis) for axis in plot.get_active_axes()
        ]

        drag_mouse(win, x_path, y_path)

        final_axis_limits = [
            plot.get_axis_limits(axis) for axis in plot.get_active_axes()
        ]

        print(initial_axis_limits)
        print(final_axis_limits)

        assert all(
            map(
                lambda og, final: compare(og[1], final[1]),
                initial_axis_limits,
                final_axis_limits,
            )
        )
        exec_dialog(win)


def test_rect_zoom_tool():
    """Test the rectangular zoom tool."""
    x_path = linspace(0, 0.5, 100)
    y_path = linspace(0, 0.5, 100)
    zoom(x_path, y_path, lambda og, final: final < og)


def test_rect_unzoom_tool():
    """Test the rectangular zoom tool to unzoom."""
    x_path = linspace(-0.5, 1.5, 100)
    y_path = linspace(-0.5, 1.5, 100)
    zoom(x_path, y_path, lambda og, final: abs(final) > abs(og))


if __name__ == "__main__":
    test_rect_zoom_tool()
    test_rect_unzoom_tool()
