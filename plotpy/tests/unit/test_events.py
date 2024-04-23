"""
This files tests the vent handlers not covered by other tests.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pytest
import qtpy.QtCore as QC
import qtpy.QtWidgets as QW
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.plot.plotwidget import PlotDialog, PlotWindow
from plotpy.tests.unit.utils import (
    create_window,
    drag_mouse,
    scroll_wheel,
)
from plotpy.tools.selection import SelectTool

# guitest: show


def _zoom_with_mouse(qapp: QW.QApplication, win: PlotWindow | PlotDialog):
    drag_mouse(
        win,
        qapp,
        np.array([0.5, 0.8]),
        np.array([0.5, 0.5]),
        btn=QC.Qt.MouseButton.RightButton,
    )


def _zoom_with_wheel(qapp: QW.QApplication, win: PlotWindow | PlotDialog):
    scroll_wheel(
        win,
        qapp,
        (0.5, 0.5),
        360,
        0,
        mods=QC.Qt.KeyboardModifier.ControlModifier,
    )


@pytest.mark.parametrize(
    "zoom_func",
    [_zoom_with_mouse, _zoom_with_wheel],
)
def test_zoom(
    zoom_func: Callable[[QW.QApplication, PlotWindow | PlotDialog], None],
):
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

        print(x_min0, x_max0, y_min0, y_max0)
        print(x_min1, x_max1, y_min1, y_max1)
        assert x_min1 > x_min0
        assert x_max1 < x_max0
        assert y_min1 < y_min0
        assert y_max1 > y_max0

        exec_dialog(win)


def test_pan():
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

        print(x_min0, x_max0, y_min0, y_max0)
        print(x_min1, x_max1, y_min1, y_max1)
        # assert x_min1 > x_min0
        # assert x_max1 > x_max0
        # assert y_min1 > y_min0
        # assert y_max1 > y_max0

        exec_dialog(win)


if __name__ == "__main__":
    test_zoom(_zoom_with_mouse)
    test_zoom(_zoom_with_wheel)
    test_pan()
