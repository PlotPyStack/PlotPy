from __future__ import annotations

from typing import TYPE_CHECKING

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
from plotpy.tools import EditPointTool, SelectPointsTool, SelectPointTool
from plotpy.tools.curve import DownSamplingTool

if TYPE_CHECKING:

    from plotpy.items.curve.base import CurveItem


def test_free_select_point_tool():
    """Test the free select point tool."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(SelectPointTool)
        mouse_event_at_relative_plot_pos(
            win,
            qapp,
            (0.5, 0.5),
            CLICK,
        )
        assert tool.get_coordinates() is not None
        exec_dialog(win)


def test_contrained_select_point_tool():
    """Test the constrained select point tool contrained to a CurveItem."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(SelectPointTool)
        tool.on_active_item = True

        mouse_event_at_relative_plot_pos(
            win,
            qapp,
            (0.5, 0.5),
            CLICK,
        )
        coor = tool.get_coordinates()
        curve_item: CurveItem = win.manager.get_plot().get_active_item()  # type: ignore
        arr_x, arr_y = curve_item.get_data()
        assert coor is not None

        x, y = coor
        assert np.where(arr_x == x)[0] == np.where(arr_y == y)[0]
        exec_dialog(win)


def test_select_points_tool():
    """Test the select points tool constrained to a CurveItem."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(tool_class=SelectPointsTool)
        mod = QC.Qt.KeyboardModifier.ControlModifier

        mouse_event_at_relative_plot_pos(win, qapp, (0.4, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 1

        mouse_event_at_relative_plot_pos(win, qapp, (0.5, 0.5), CLICK, mod)
        mouse_event_at_relative_plot_pos(win, qapp, (0.8, 0.8), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 3

        mouse_event_at_relative_plot_pos(win, qapp, (0.6, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 2

        mouse_event_at_relative_plot_pos(win, qapp, (0.7, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 3

        mouse_event_at_relative_plot_pos(win, qapp, (0.1, 0.1), CLICK)
        assert len(tool.get_coordinates() or ()) == 1

        coor = tool.get_coordinates()
        assert coor is not None
        x, y = coor[0]
        curve_item: CurveItem = win.manager.get_plot().get_active_item()  # type: ignore
        arr_x, arr_y = curve_item.get_data()
        assert np.where(arr_x == x)[0] == np.where(arr_y == y)[0]

        exec_dialog(win)


def test_edit_point_tool():
    """Test the edit point tool for a CurveItem."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(EditPointTool)
        curve_item: CurveItem = win.manager.get_plot().get_active_item()  # type: ignore
        orig_x, orig_y = curve_item.get_data()

        assert orig_x is not None and orig_y is not None
        orig_x, orig_y = orig_x.copy(), orig_y.copy()

        assert tool is not None

        # must activate downsampling because the curve is too dense so the selection
        # distance threshold is too small for the programmed drag to select the first
        # point
        curve_item.param.dsamp_factor = 20
        win.manager.add_tool(DownSamplingTool).activate()
        # The steps must be very small to ensure the mouse passes close
        # enough to the first point of the curve to move it (distance < threshold)
        n = 1000
        min_v, max_v = 0, 1
        x_path = np.full(n, min_v)
        y_path = np.linspace(max_v, min_v, n)
        drag_mouse(win, qapp, x_path, y_path)

        x_path = np.full(n, max_v)

        drag_mouse(win, qapp, x_path, y_path)
        curve_changes = tool.get_changes()[curve_item]

        x_arr, y_arr = curve_item.get_data()
        for i, (x, y) in curve_changes.items():
            assert x == x_arr[i]
            assert y == y_arr[i]

        x_arr, y_arr = tool.get_arrays()
        assert x_arr is not None and y_arr is not None

        x_arr, y_arr = tool.get_initial_arrays()
        assert x_arr is not None and y_arr is not None

        # Reset the arrays and deletes the changes
        keyboard_event(
            win, qapp, QC.Qt.Key.Key_Z, QC.Qt.KeyboardModifier.ControlModifier
        )

        assert len(curve_changes) == 0

        restored_x, restored_y = curve_item.get_data()
        assert restored_x is not None and restored_y is not None
        assert np.allclose(orig_x, restored_x)
        assert np.allclose(orig_y, restored_y)

        mouse_event_at_relative_plot_pos(win, qapp, (0.5, 0.5), CLICK)
        tool.trigger_insert_point_at_selection()

        new_x, new_y = curve_item.get_data()
        assert len(new_x) == len(orig_x) + 1 and len(new_y) == len(orig_y) + 1

        tool.reset_arrays()
        assert tool.get_changes() == {}
        x_arr, y_arr = curve_item.get_data()
        assert np.in1d(x_arr, orig_x).all() and np.in1d(y_arr, orig_y).all()

        exec_dialog(win)


if __name__ == "__main__":
    test_free_select_point_tool()
    test_contrained_select_point_tool()
    test_select_points_tool()
    test_edit_point_tool()
