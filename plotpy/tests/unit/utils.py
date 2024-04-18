from __future__ import annotations

import time
from typing import TYPE_CHECKING, TypeVar, Union

import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW
from qwt import QwtPlotItem

from plotpy.interfaces.items import ICurveItemType, IItemType
from plotpy.plot.base import BasePlot
from plotpy.tests import vistools as ptv
from plotpy.tests.features.test_auto_curve_image import make_curve_image_legend
from plotpy.tools import CommandTool, InteractiveTool

if TYPE_CHECKING:
    import numpy as np

    from plotpy.items.curve.base import CurveItem
    from plotpy.items.image.base import BaseImageItem
    from plotpy.panels.base import PanelWidget
    from plotpy.plot.plotwidget import PlotDialog, PlotWindow


CLICK = (QC.QEvent.Type.MouseButtonPress, QC.QEvent.Type.MouseButtonRelease)
ToolT = TypeVar("ToolT", bound=Union[InteractiveTool, CommandTool])


def rel_pos_to_canvas_pos(
    canvas: BasePlot, relative_xy: tuple[float, float]
) -> tuple[QC.QPointF, QC.QPointF]:
    """Computes and return the relative position on the canvas and the corresponding
    abolute position in the window.

    Args:
        canvas: Plot canvas
        relative_xy: Relative position on the canvas (0 < xy <1)

    Returns:
        Tuple of the relative position on the canvas and the corresponding absolute
         position in the window.
    """
    size = canvas.size()
    pos_x, pos_y = (
        relative_xy[0] * size.width(),
        relative_xy[1] * size.height(),
    )
    canvas_pos = QC.QPointF(pos_x, pos_y)
    return canvas_pos, QC.QPointF(canvas.mapToGlobal(canvas_pos.toPoint()))


def keyboard_event(
    win: PlotDialog | PlotWindow,
    qapp: QW.QApplication,
    key: QC.Qt.Key,
    mod=QC.Qt.KeyboardModifier.NoModifier,
):
    """Simulates a keyboard event on the plot.

    Args:
        win: window containing the plot
        qapp: Main QApplication instance
        key: Key to simulate
        mod: Keyboard modifier. Defaults to QC.Qt.KeyboardModifier.NoModifier.

    Returns:
        None
    """
    plot = win.manager.get_plot()
    canva: QW.QWidget = plot.canvas()  # type: ignore
    key_event = QG.QKeyEvent(QC.QEvent.Type.KeyPress, key, mod)
    qapp.sendEvent(canva, key_event)


def undo(qapp: QW.QApplication, win: PlotWindow):
    keyboard_event(
        win, qapp, QC.Qt.Key.Key_Z, mod=QC.Qt.KeyboardModifier.ControlModifier
    )


def redo(qapp: QW.QApplication, win: PlotWindow):
    keyboard_event(
        win, qapp, QC.Qt.Key.Key_Y, mod=QC.Qt.KeyboardModifier.ControlModifier
    )


def undo_redo(qapp: QW.QApplication, win: PlotWindow):
    undo(qapp, win)
    time.sleep(0.1)
    redo(qapp, win)


def new_wheel_event(
    canvas: BasePlot,
    pos_xy: tuple[float, float],
    angle_delta: int,
    pix_delta: int,
    btns: QC.Qt.MouseButton = QC.Qt.MouseButton.NoButton,
    mods=QC.Qt.KeyboardModifier.NoModifier,
) -> QG.QWheelEvent:
    canva_pos, glob_pos = rel_pos_to_canvas_pos(canvas, pos_xy)
    angle_delta = QC.QPoint(0, angle_delta)  # Scroll distance in eighths of a degree
    pix_delta = QC.QPoint(0, pix_delta)  # Scroll distance in pixels
    qt4_delta = 0  # You may need to adjust this value
    orientation = QC.Qt.Orientation.Vertical  # You may need to adjust this value

    # Create QWheelEvent
    return QG.QWheelEvent(
        canva_pos, glob_pos, pix_delta, angle_delta, qt4_delta, orientation, btns, mods
    )


def scroll_wheel(
    win: PlotDialog | PlotWindow,
    qapp: QW.QApplication,
    relative_xy: tuple[float, float],
    angle_delta: int,
    pix_delta: int = 0,
    btns: QC.Qt.MouseButton = QC.Qt.MouseButton.NoButton,
    mods=QC.Qt.KeyboardModifier.NoModifier,
) -> None:
    """Simulates a scroll wheel event on the plot at the given relative position.

    Args:
        win: window containing the plot
        qapp: Main QApplication instance
        relative_xy: Relative position of the click on the plot
        angle_delta: Scroll distance in eighths of a degree
        pix_delta: Scroll distance in pixels. Defaults to 0.
        btns: Mouse buttons. Defaults to QC.Qt.MouseButton.NoButton.
        mod: Keyboard modifier. Defaults to QC.Qt.KeyboardModifier.NoModifier.

    Returns:
        None
    """
    plot = win.manager.get_plot()
    canvas: BasePlot = plot.canvas()  # type: ignore
    wheel_event = new_wheel_event(
        canvas, relative_xy, angle_delta, pix_delta, btns, mods
    )
    qapp.sendEvent(canvas, wheel_event)


def mouse_event_at_relative_plot_pos(
    win: PlotDialog | PlotWindow,
    qapp: QW.QApplication,
    relative_xy: tuple[float, float],
    click_types: tuple[QC.QEvent.Type, ...] = (QC.QEvent.Type.MouseButtonPress,),
    mod=QC.Qt.KeyboardModifier.NoModifier,
    btn=QC.Qt.MouseButton.LeftButton,
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
    canvas = plot.canvas()
    canvas_pos, _ = rel_pos_to_canvas_pos(canvas, relative_xy)

    for type_ in click_types:
        mouse_event = QG.QMouseEvent(
            type_,
            canvas_pos,
            btn,
            btn,
            mod,
        )
        qapp.sendEvent(canvas, mouse_event)


# def mouse_wheel_event_at_relative_pos(
#     win: PlotDialog | PlotWindow,
#     qapp: QW.QApplication,
#     relative_xy: tuple[float, float],
#     click_types: tuple[QC.QEvent.Type, ...] = (QC.QEvent.Type.MouseButtonPress,),
#     mod=QC.Qt.KeyboardModifier.NoModifier,
# ) -> None:


def drag_mouse(
    win: PlotWindow,
    qapp: QW.QApplication,
    x_path: np.ndarray,
    y_path: np.ndarray,
    mod=QC.Qt.KeyboardModifier.NoModifier,
    btn=QC.Qt.MouseButton.LeftButton,
    click=True,
) -> None:
    """Simulates a mouse drag on the plot.

    Args:
        win: window containing the plot
        qapp: QApplication instance
        x_path: relative x plot coordinates of the path to simulate the mouse drag along
        y_path: relative y plot coordinates of the path to simulate the mouse drag along
        mod: keyboard modifier. Defaults to QC.Qt.KeyboardModifier.NoModifier.
        click: Whether a click must be simulated (mouse hold -> drag -> mouse release).
         Defaults to True.
    """
    x0, y0 = x_path[0], y_path[0]
    xn, yn = x_path[-1], y_path[-1]
    press = (QC.QEvent.Type.MouseButtonPress,)
    move = (QC.QEvent.Type.MouseMove,)
    release = (QC.QEvent.Type.MouseButtonRelease,)

    if click:
        mouse_event_at_relative_plot_pos(win, qapp, (x0, y0), press, mod, btn)
    for x, y in zip(x_path, y_path):
        mouse_event_at_relative_plot_pos(win, qapp, (x, y), move, mod, btn)
    if click:
        mouse_event_at_relative_plot_pos(win, qapp, (xn, yn), release, mod, btn)


def create_window(
    tool_class: type[ToolT],
    active_item_type: type[IItemType] = ICurveItemType,
    panels: list[type[PanelWidget]] | None = None,
    items: list[QwtPlotItem] | None = None,
) -> tuple[PlotWindow, ToolT]:
    """Create a window with the given tool. The plot contains a curve, an image and a
     legend.

    Args:
        tool_class: tool class to add to the window.
        active_item_type: Type of Item to set to active (curve or image).
         Defaults to ICurveItemType.
        panels: PanelWidget classes to add. Defaults to None.

    Returns:
        The window containing the activated tool and the tool instance itself.
    """
    if items is None:
        items = make_curve_image_legend()
    win = ptv.show_items(items, wintitle="Unit test plot", auto_tools=False)
    plot = win.manager.get_plot()
    for item in items:
        plot.set_active_item(item)
    last_active_item = plot.get_last_active_item(active_item_type)
    plot.set_active_item(last_active_item)
    if panels is not None:
        for panel in panels:
            win.manager.add_panel(panel())

    tool = win.manager.add_tool(tool_class)
    tool.activate()
    return win, tool
