from typing import Protocol

import numpy as np
import pytest
import qtpy.QtCore as QC
from guidata.qthelpers import exec_dialog, qt_app_context
from qwt import QwtPlotItem

from plotpy.builder import make
from plotpy.interfaces.items import (
    IBasePlotItem,
    IImageItemType,
    IItemType,
    IShapeItemType,
)
from plotpy.items.image.transform import TrImageItem
from plotpy.plot.base import BasePlot
from plotpy.plot.plotwidget import PlotWindow
from plotpy.tests.data import gen_image4
from plotpy.tests.unit.utils import (
    create_window,
    drag_mouse,
    keyboard_event,
)
from plotpy.tools import RectangularSelectionTool, SelectTool

# guitest: show


def _get_xy_coords(tr_img: TrImageItem) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = tr_img.boundingRect().getCoords()
    assert isinstance(x1, float)
    assert isinstance(y1, float)
    assert isinstance(x2, float)
    assert isinstance(y2, float)
    return x1, y1, x2, y2


def _setup_plot() -> tuple[PlotWindow, SelectTool, BasePlot, TrImageItem]:
    tr_img = make.trimage(gen_image4(100, 100), x0=100, y0=100)
    win, tool = create_window(SelectTool, IImageItemType, None, [tr_img])

    assert isinstance(tool, SelectTool)

    plot = win.manager.get_plot()
    assert plot.get_selected_items() == [tr_img]

    return win, tool, plot, tr_img


def test_move_with_mouse():
    """Test the select tool."""

    with qt_app_context(exec_loop=False) as qapp:
        win, tool, plot, tr_img = _setup_plot()
        x1, y1, *_ = _get_xy_coords(tr_img)
        initial_angle = tr_img.param.pos_angle  # type: ignore

        assert initial_angle == 0
        assert plot.get_selected_items() == [tr_img]

        drag_mouse(win, qapp, np.array([0.5, 0.6, 0.7]), np.array([0.5, 0.6, 0.7]))

        assert plot.get_selected_items() == [tr_img]
        x2, y2, *_ = _get_xy_coords(tr_img)
        assert x2 > x1 and y2 > y1
        assert tr_img.param.pos_angle == initial_angle  # type: ignore

        exec_dialog(win)


@pytest.mark.parametrize(
    "mod", [QC.Qt.KeyboardModifier.NoModifier, QC.Qt.KeyboardModifier.ControlModifier]
)
def test_move_with_arrows(
    mod: QC.Qt.KeyboardModifier,
):
    with qt_app_context(exec_loop=False) as qapp:
        win, tool, plot, tr_img = _setup_plot()
        x1, y1, *_ = _get_xy_coords(tr_img)
        plot.select_item(tr_img)  # type: ignore
        initial_angle = tr_img.param.pos_angle  # type: ignore

        assert initial_angle == 0
        assert plot.get_selected_items() == [tr_img]

        keyboard_event(win, qapp, QC.Qt.Key.Key_Right, mod=mod)
        assert plot.get_selected_items() == [tr_img]
        x2, y2, *_ = _get_xy_coords(tr_img)
        assert x2 > x1 and y2 == y1
        assert tr_img.param.pos_angle == initial_angle  # type: ignore

        keyboard_event(win, qapp, QC.Qt.Key.Key_Down, mod=mod)
        assert plot.get_selected_items() == [tr_img]
        x3, y3, *_ = _get_xy_coords(tr_img)
        assert x3 == x2 and y3 > y2
        assert tr_img.param.pos_angle == initial_angle  # type: ignore

        keyboard_event(win, qapp, QC.Qt.Key.Key_Left, mod=mod)
        assert plot.get_selected_items() == [tr_img]
        x4, y4, *_ = _get_xy_coords(tr_img)
        assert x4 < x3 and y4 == y3
        assert tr_img.param.pos_angle == initial_angle  # type: ignore

        keyboard_event(win, qapp, QC.Qt.Key.Key_Up, mod=mod)
        assert plot.get_selected_items() == [tr_img]
        x5, y5, *_ = _get_xy_coords(tr_img)
        assert x5 == x4 and y5 < y4 and np.isclose(x5, x1) and np.isclose(y5, y1)
        assert tr_img.param.pos_angle == initial_angle  # type: ignore

        keyboard_event(win, qapp, QC.Qt.Key.Key_Enter)
        exec_dialog(win)


@pytest.mark.parametrize(
    "mod",
    [
        QC.Qt.KeyboardModifier.ShiftModifier,
        QC.Qt.KeyboardModifier.ShiftModifier | QC.Qt.KeyboardModifier.ControlModifier,
    ],
)
def test_rotate_with_arrow(
    mod: QC.Qt.KeyboardModifier,
):
    with qt_app_context(exec_loop=False) as qapp:
        win, tool, plot, tr_img = _setup_plot()
        x1_a, y1_a, x1_b, y1_b = _get_xy_coords(tr_img)
        plot.select_item(tr_img)  # type: ignore
        initial_angle = tr_img.param.pos_angle  # type: ignore

        assert initial_angle == 0
        assert plot.get_selected_items() == [tr_img]

        for _ in range(3):
            keyboard_event(win, qapp, QC.Qt.Key.Key_Right, mod=mod)
        assert plot.get_selected_items() == [tr_img]
        assert tr_img.param.pos_angle > initial_angle  # type: ignore

        for _ in range(3):
            keyboard_event(win, qapp, QC.Qt.Key.Key_Left, mod=mod)

        assert plot.get_selected_items() == [tr_img]

        x3_a, y3_a, x3_b, y3_b = _get_xy_coords(tr_img)
        assert (
            np.isclose(x3_a, x1_a)
            and np.isclose(y3_a, y1_a)
            and np.isclose(x3_b, x1_b)
            and np.isclose(y3_b, y1_b)
        )
        assert np.isclose(tr_img.param.pos_angle, initial_angle)  # type: ignore

        exec_dialog(win)


def test_select_all_items():
    with qt_app_context() as qapp:
        n = 100
        x = np.arange(n)
        items = [
            make.image(gen_image4(n, n)),
            make.curve(x, np.cos(x)),
            make.annotated_rectangle(0, 0, 10, 10),
            make.legend(),
        ]
        win, tool = create_window(SelectTool, items=items)

        # The item list should contain none selectable items like the plot grid
        selectable_items = [item for item in items if item.can_select()]
        assert len(selectable_items) < len(win.manager.get_plot().get_items())

        keyboard_event(
            win, qapp, QC.Qt.Key.Key_A, mod=QC.Qt.KeyboardModifier.ControlModifier
        )
        selected_items = win.manager.get_plot().get_selected_items()
        assert selectable_items == selected_items

        exec_dialog(win)


def test_rotate_with_mouse():
    with qt_app_context(exec_loop=False) as qapp:
        win, tool, plot, tr_img = _setup_plot()
        init_angle = tr_img.param.pos_angle  # type: ignore
        assert init_angle == 0
        assert plot.get_selected_items() == [tr_img]

        drag_mouse(win, qapp, np.linspace(0, 1, 100), np.linspace(0, 1, 100))

        assert plot.get_selected_items() == [tr_img]
        assert 179 < abs(tr_img.param.pos_angle) < 181  # type: ignore

        exec_dialog(win)


def test_rectangular_selection():
    with qt_app_context(exec_loop=False) as qapp:
        items = [
            make.image(gen_image4(100, 100)),
            make.trimage(gen_image4(100, 100), x0=100, y0=100),
            make.curve(np.arange(100), 100 + 20 * np.cos(np.arange(100))),
            make.annotated_rectangle(50, 50, 100, 100),
            make.legend(),
            make.label("Test", (100, 100), (0, 0), "R"),
        ]

        is_rect_selectable = [
            (
                IShapeItemType in item.__implements__
                or IImageItemType in item.__implements__
            )
            for item in items
        ]
        win, tool = create_window(RectangularSelectionTool, items=items)
        plot = win.manager.get_plot()

        drag_mouse(
            win,
            qapp,
            np.linspace(-0.1, 1.1, 52),
            np.linspace(-0.1, 1.1, 52),
        )

        selected_items = win.manager.get_plot().get_selected_items()

        for item, selectable in zip(items, is_rect_selectable):
            if selectable:
                assert item in selected_items


if __name__ == "__main__":
    test_move_with_mouse()
    test_move_with_arrows(QC.Qt.KeyboardModifier.NoModifier)
    test_rotate_with_arrow(QC.Qt.KeyboardModifier.ShiftModifier)
    test_select_all_items()
    test_rotate_with_mouse()
    test_rectangular_selection()
