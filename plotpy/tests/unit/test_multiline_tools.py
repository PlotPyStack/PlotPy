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


def __generic_polyline_tool_test(
    toolklass: type[MultiLineTool] | type[PolygonTool], points: np.ndarray
) -> None:
    """Generic polyline tool test."""
    with qt_app_context(exec_loop=False):
        win, tool = create_window(toolklass)

        x0, y0 = None, None
        for x, y in points:
            if x0 is not None:
                x_path = np.linspace(x0, x, 10)
                y_path = np.linspace(y0, y, 10)
                drag_mouse(win, x_path, y_path)
            else:
                mouse_event_at_relative_plot_pos(win, (x, y), CLICK)
            x0, y0 = x, y

        assert tool.handler.shape is not None
        assert tool.handler.shape.get_points().shape == points.shape

        keyboard_event(win, QC.Qt.Key.Key_Backspace)

        points_count, _ = tool.handler.shape.get_points().shape

        assert points_count == (len(points) - 1)

        # add last point by dragging mouse
        drag_mouse(win, points[-2:, 0], points[-2:, 1])

        points_count, _ = tool.handler.shape.get_points().shape
        assert points_count == len(points)

        keyboard_event(win, QC.Qt.Key.Key_Space)

        exec_dialog(win)


def test_polygon_tool():
    """Test the polygon tool."""
    corners = np.array(((0.1, 0.1), (0.1, 0.8), (0.8, 0.8), (0.8, 0.1)))
    __generic_polyline_tool_test(PolygonTool, corners)


def test_multiline_tool():
    """Test the multi line tool."""
    n = 100
    # Start from 2*pi to skip the degenerate center of the spiral where adjacent
    # points are too close and may map to the same pixel on small canvases (this
    # caused the test to fail with PyQt6 due to a smaller default canvas size).
    t = np.linspace(2 * np.pi, np.pi * 10, n)
    x_arr = t * np.cos(t) / n + 0.5
    y_arr = t * np.sin(t) / n + 0.5
    __generic_polyline_tool_test(MultiLineTool, np.array([x_arr, y_arr]).T)


if __name__ == "__main__":
    test_polygon_tool()
    test_multiline_tool()
