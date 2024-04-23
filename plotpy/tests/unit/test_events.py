"""
This files tests the vent handlers not covered by other tests.
"""

from __future__ import annotations

import operator
from enum import Enum
from typing import TYPE_CHECKING, Callable

import numpy as np
import pytest
import qtpy.QtCore as QC
import qtpy.QtWidgets as QW
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.tests.unit.utils import (
    create_window,
    drag_mouse,
    scroll_wheel,
)
from plotpy.tools.selection import SelectTool

if TYPE_CHECKING:
    from plotpy.plot.plotwidget import PlotDialog, PlotWindow


class ZoomType(Enum):
    NO_ZOOM = (operator.eq, operator.eq, operator.eq, operator.eq)
    ZOOM_IN = (operator.gt, operator.lt, operator.lt, operator.gt)
    ZOOM_OUT = (operator.lt, operator.gt, operator.gt, operator.lt)


class ZoomEvent(Enum):
    ZOOM_WITH_MOUSE = 0
    ZOOM_WITH_WHEEL = 1


def result_zoom(zoom_type: ZoomType, event_type: ZoomEvent):
    """Wrapper used to parametrize the test_zoom function.

    Args:
        zoom_type: enum to specify the expected zoom.
        event_type: enum to specify the event type (drag or scroll).

    Returns:
        A function used to zoom in the plot and the expected zoom type.
    """
    if event_type is ZoomEvent.ZOOM_WITH_MOUSE:
        if zoom_type is ZoomType.NO_ZOOM:
            btn = QC.Qt.MouseButton.NoButton
            x_path = np.array([0.5, 0.8])
        elif zoom_type is ZoomType.ZOOM_IN:
            btn = QC.Qt.MouseButton.RightButton
            x_path = np.array([0.5, 0.8])
        else:
            btn = QC.Qt.MouseButton.RightButton
            x_path = np.array([0.5, 0.2])

        def _zoom_with_mouse(qapp: QW.QApplication, win: PlotWindow | PlotDialog):
            """Zoom in the plot by dragging the mouse while holding right click.

            Args:
                qapp: QApplication instance.
                win: PlotWindow or PlotDialog instance.
            """
            drag_mouse(
                win,
                qapp,
                x_path,
                np.array([0.5, 0.5]),
                btn=btn,
            )

        return _zoom_with_mouse, zoom_type

    if zoom_type is ZoomType.NO_ZOOM:
        angle_delta = 360
        mod = QC.Qt.KeyboardModifier.NoModifier
    elif zoom_type is ZoomType.ZOOM_IN:
        angle_delta = 360
        mod = QC.Qt.KeyboardModifier.ControlModifier
    else:
        angle_delta = -360
        mod = QC.Qt.KeyboardModifier.ControlModifier

    def _zoom_with_wheel(qapp: QW.QApplication, win: PlotWindow | PlotDialog):
        """Zoom in the plot by scrolling the mouse wheel while holding control.

        Args:
            qapp: QApplication instance.
            win: PlotWindow or PlotDialog instance.
        """
        scroll_wheel(
            win,
            qapp,
            (0.5, 0.5),
            angle_delta,
            0,
            mods=mod,
        )

    return _zoom_with_wheel, zoom_type


@pytest.mark.parametrize(
    "zoom_func, zoom_type",
    [
        result_zoom(ZoomType.NO_ZOOM, ZoomEvent.ZOOM_WITH_MOUSE),
        result_zoom(ZoomType.NO_ZOOM, ZoomEvent.ZOOM_WITH_WHEEL),
        result_zoom(ZoomType.ZOOM_IN, ZoomEvent.ZOOM_WITH_MOUSE),
        result_zoom(ZoomType.ZOOM_IN, ZoomEvent.ZOOM_WITH_WHEEL),
        result_zoom(ZoomType.ZOOM_OUT, ZoomEvent.ZOOM_WITH_MOUSE),
        result_zoom(ZoomType.ZOOM_OUT, ZoomEvent.ZOOM_WITH_WHEEL),
    ],
)
def test_zoom(
    zoom_func: Callable[[QW.QApplication, PlotWindow | PlotDialog], None],
    zoom_type: ZoomType,
):
    """Test zooming on the plot by triggering several event types.

    Args:
        zoom_func: _description_
    """
    with qt_app_context(exec_loop=False) as qapp:
        win, _ = create_window(SelectTool)
        win.show()

        plot = win.manager.get_plot()
        plot.unselect_all()

        axis_x, axis_y = plot.get_active_axes()

        x_min0, x_max0 = plot.get_axis_limits(axis_x)
        y_min0, y_max0 = plot.get_axis_limits(axis_y)

        zoom_func(qapp, win)

        x_min1, x_max1 = plot.get_axis_limits(axis_x)
        y_min1, y_max1 = plot.get_axis_limits(axis_y)

        c1, c2, c3, c4 = zoom_type.value
        assert c1(x_min1, x_min0)
        assert c2(x_max1, x_max0)
        assert c3(y_min1, y_min0)
        assert c4(y_max1, y_max0)

        exec_dialog(win)


def test_pan():
    """Test panning the plot by dragging the mouse while holding middle click."""
    with qt_app_context(exec_loop=False) as qapp:
        win, _ = create_window(SelectTool)
        win.show()

        plot = win.manager.get_plot()
        plot.unselect_all()

        axis_x, axis_y = plot.get_active_axes()

        x_min0, x_max0 = plot.get_axis_limits(axis_x)
        y_min0, y_max0 = plot.get_axis_limits(axis_y)

        drag_mouse(
            win,
            qapp,
            np.linspace(0.5, 0, 100),
            np.linspace(0.5, 0, 100),
            btn=QC.Qt.MouseButton.MiddleButton,
        )

        x_min1, x_max1 = plot.get_axis_limits(axis_x)
        y_min1, y_max1 = plot.get_axis_limits(axis_y)

        assert x_min1 > x_min0
        assert x_max1 > x_max0
        assert y_min1 > y_min0
        assert y_max1 > y_max0

        exec_dialog(win)


if __name__ == "__main__":
    test_zoom(*result_zoom(ZoomType.ZOOM_OUT, ZoomEvent.ZOOM_WITH_WHEEL))
    test_pan()
