# guitest: show

from typing import TYPE_CHECKING, TypeVar

import numpy as np
import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW
from guidata.qthelpers import exec_dialog, qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.plot.plotwidget import PlotDialog, PlotWindow
from plotpy.tests import vistools as ptv
from plotpy.tools.base import InteractiveTool
from plotpy.tools.curve import EditPointTool, SelectPointsTool, SelectPointTool

if TYPE_CHECKING:
    from plotpy.items.curve.base import CurveItem

CLICK = (QC.QEvent.Type.MouseButtonPress, QC.QEvent.Type.MouseButtonRelease)
ToolT = TypeVar("ToolT", bound=InteractiveTool)


def mouse_event_at_relative_plot_pos(
    win: PlotDialog,
    qapp: QW.QApplication,
    relative_xy: tuple[float, float],
    click_types: tuple[QC.QEvent.Type, ...] = (QC.QEvent.Type.MouseButtonPress,),
    mod=QC.Qt.KeyboardModifier.NoModifier,
) -> None:
    """Simulates a click on the plot at the given relative position.

    Args:
        win: window containing the plot
        qapp: Main QApplication instance
        relative_xy: Relative position of the click on the plot
        click_types: Different mouse button event types to send.
         Defaults to (QC.QEvent.Type.MouseButtonPress,).
        mod: Keyboard modifier. Defaults to QC.Qt.KeyboardModifier.NoModifier.

    Returns:
        None
    """
    plot = win.manager.get_plot()

    plot = win.manager.get_plot()
    canva: QW.QWidget = plot.canvas()  # type: ignore
    size = canva.size()
    pos_x, pos_y = (
        relative_xy[0] * size.width(),
        size.height() - relative_xy[1] * size.height(),
    )
    # pos_x, pos_y = axes_to_canvas(plot.get_active_item(), x, y)
    canva_pos = QC.QPointF(pos_x, pos_y).toPoint()
    glob_pos = canva.mapToGlobal(canva_pos)
    # QTest.mouseClick(canva, QC.Qt.MouseButton.LeftButton, mod, canva_pos)

    for type_ in click_types:
        mouse_event_press = QG.QMouseEvent(
            type_,
            canva_pos,
            glob_pos,
            QC.Qt.MouseButton.LeftButton,
            QC.Qt.MouseButton.LeftButton,
            mod,
        )
        qapp.sendEvent(canva, mouse_event_press)


def drag_mouse(
    win: PlotDialog,
    qapp: QW.QApplication,
    x_path: np.ndarray,
    y_path: np.ndarray,
    mod=QC.Qt.KeyboardModifier.NoModifier,
) -> None:
    x0, y0 = x_path[0], y_path[0]
    xn, yn = x_path[-1], y_path[-1]
    press = (QC.QEvent.Type.MouseButtonPress,)
    move = (QC.QEvent.Type.MouseMove,)
    release = (QC.QEvent.Type.MouseButtonRelease,)

    mouse_event_at_relative_plot_pos(win, qapp, (x0, y0), press, mod)
    for x, y in zip(x_path, y_path):
        mouse_event_at_relative_plot_pos(win, qapp, (x, y), move, mod)
    mouse_event_at_relative_plot_pos(win, qapp, (xn, yn), release, mod)


def create_window(tool_class: type[ToolT]) -> tuple[PlotWindow, ToolT]:
    n = 100
    x = linspace(
        0,
        n,
    )
    y = (sin(sin(sin(x / (n / 10)))) - 1) * -n
    curve = make.curve(x, y, color="b")
    win = ptv.show_items(
        [curve], wintitle="Unit tests for Point tools", auto_tools=False
    )
    plot = win.manager.get_plot()
    plot.set_active_item(curve)  # type: ignore

    tool = win.manager.add_tool(tool_class)
    tool.activate()
    return win, tool


def test_select_point_tool_1():
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


def test_select_point_tool_2():
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(SelectPointTool)
        tool.on_active_item = True
        mouse_event_at_relative_plot_pos(
            win,
            qapp,
            (0.5, 0.5),
            CLICK,
        )
        assert tool.get_coordinates() is not None
        exec_dialog(win)


def test_select_points_tool():
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(tool_class=SelectPointsTool)
        mod = QC.Qt.KeyboardModifier.ControlModifier

        mouse_event_at_relative_plot_pos(win, qapp, (0.4, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 1

        mouse_event_at_relative_plot_pos(win, qapp, (0.5, 0.5), CLICK, mod)
        mouse_event_at_relative_plot_pos(win, qapp, (0.6, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 3

        mouse_event_at_relative_plot_pos(win, qapp, (0.6, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 2

        mouse_event_at_relative_plot_pos(win, qapp, (0.7, 0.5), CLICK, mod)
        assert len(tool.get_coordinates() or ()) == 3

        mouse_event_at_relative_plot_pos(win, qapp, (0.1, 0.1), CLICK)
        assert len(tool.get_coordinates() or ()) == 1

        exec_dialog(win)


def test_edit_point_tool():
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(EditPointTool)
        assert tool is not None

        n = 100
        min_v, max_v = 0, 1
        x_path = np.full(n, min_v)
        y_path = np.linspace(max_v, min_v, n)
        drag_mouse(win, qapp, x_path, y_path)

        x_path = np.full(n, max_v)

        drag_mouse(win, qapp, x_path, y_path)

        curve_item: CurveItem = win.manager.get_plot().get_active_item()  # type: ignore
        curve_changes = tool.get_changes()[curve_item]
        for i, (x, y) in curve_changes.items():
            x_arr, y_arr = curve_item.get_data()
            assert x == x_arr[i]
            assert y == y_arr[i]
        exec_dialog(win)


if __name__ == "__main__":
    test_select_point_tool_1()
    test_select_point_tool_2()
    test_select_points_tool()
    test_edit_point_tool()
