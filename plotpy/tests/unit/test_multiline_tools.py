from __future__ import annotations

import numpy as np
import qtpy.QtCore as QC
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.tests.unit.utils import (
    CLICK,
    create_window,
    drag_mouse,
    keyboard_event,
    mouse_event_at_relative_plot_pos,
)
from plotpy.tools import MultiLineTool, PolygonTool


def test_free_form_tool():
    """Test the free form tool."""
    corners = np.array(((0.1, 0.1), (0.1, 0.8), (0.8, 0.8), (0.8, 0.1)))
    with qt_app_context(exec_loop=False):
        win, tool = create_window(PolygonTool)

        # drag_mouse(win, x_path, y_path)
        for x, y in corners:
            mouse_event_at_relative_plot_pos(win, (x, y), CLICK)

        assert tool.shape is not None
        assert tool.shape.get_points().shape == corners.shape

        # Delete last point
        keyboard_event(win, QC.Qt.Key.Key_Backspace)

        points_count, _ = tool.shape.get_points().shape

        assert points_count == (len(corners) - 1)

        # add last point by dragging mouse
        drag_mouse(win, corners[-2:, 0], corners[-2:, 1])

        points_count, _ = tool.shape.get_points().shape
        assert points_count == len(corners)

        keyboard_event(win, QC.Qt.Key.Key_Enter)

        assert tool.shape is None

        exec_dialog(win)


def test_multiline_tool():
    """Test the multi line tool."""
    n = 100
    t = np.linspace(0, np.pi * 10, n)

    # Create x and y arrays
    x_arr = t * np.cos(t) / n + 0.5
    y_arr = t * np.sin(t) / n + 0.5

    with qt_app_context(exec_loop=False):
        win, tool = create_window(MultiLineTool)

        # drag_mouse(win, x_path, y_path)
        for x, y in zip(x_arr, y_arr):
            mouse_event_at_relative_plot_pos(win, (x, y), CLICK)

        assert tool.shape is not None
        assert tool.shape.get_points().shape == np.array([x_arr, y_arr]).T.shape

        # Delete last point
        keyboard_event(win, QC.Qt.Key.Key_Backspace)

        points_count, _ = tool.shape.get_points().shape

        assert points_count == (n - 1)

        # add last point by dragging mouse
        drag_mouse(win, x_arr[-2:], y_arr[-2:])

        points_count, _ = tool.shape.get_points().shape
        assert points_count == n

        keyboard_event(win, QC.Qt.Key.Key_Enter)

        assert tool.shape is None

        exec_dialog(win)


if __name__ == "__main__":
    test_free_form_tool()
    test_multiline_tool()
