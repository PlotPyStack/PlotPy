from typing import Callable, Protocol

import numpy as np
import pytest
import qtpy.QtCore as QC
import qtpy.QtWidgets as QW
from guidata.qthelpers import exec_dialog, qt_app_context
from qwt import QwtPlotItem
from typing_extensions import TypeVar

from plotpy.builder import make
from plotpy.interfaces.items import (
    IBasePlotItem,
    IImageItemType,
    IItemType,
    IShapeItemType,
)
from plotpy.items.image.base import BaseImageItem
from plotpy.items.image.transform import TrImageItem
from plotpy.plot.base import BasePlot
from plotpy.plot.plotwidget import PlotWindow
from plotpy.tests.data import gen_image4
from plotpy.tests.items.test_transform import make_items
from plotpy.tests.unit.utils import (
    create_window,
    drag_mouse,
    keyboard_event,
    undo_redo,
)
from plotpy.tools import RectangularSelectionTool, SelectTool

# guitest: show

BaseImageItemT = TypeVar("BaseImageItemT", bound=BaseImageItem)


def _assert_images_angle(
    images: list[TrImageItem], ref_angle: float, target_angle: float | None = None
) -> None:
    angle = images[0].param.pos_angle
    assert angle > ref_angle
    if target_angle is not None:
        assert np.isclose(angle, target_angle, 0.5)
    for img in images:
        assert np.isclose(angle, img.param.pos_angle)


def _assert_images_pos(images: list[TrImageItem], x0: float, y0: float) -> None:
    x = images[0].param.pos_x0
    y = images[0].param.pos_y0
    assert x > x0
    assert y > y0
    for img in images:
        assert img.param.pos_angle == 0
        assert np.isclose(x, img.param.pos_x0)
        assert np.isclose(y, img.param.pos_y0)


def _get_xy_coords(tr_img: BaseImageItem) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = tr_img.boundingRect().getCoords()
    assert isinstance(x1, float)
    assert isinstance(y1, float)
    assert isinstance(x2, float)
    assert isinstance(y2, float)
    return x1, y1, x2, y2


def _setup_plot(
    img_item: BaseImageItem | None = None,
) -> tuple[PlotWindow, SelectTool, BasePlot, BaseImageItem]:
    if img_item is None:
        img_item = make.trimage(gen_image4(100, 100), x0=100, y0=100)
    win, tool = create_window(SelectTool, IImageItemType, None, [img_item])
    win.show()

    assert isinstance(tool, SelectTool)

    plot = win.manager.get_plot()
    assert plot.get_selected_items() == [img_item]

    return win, tool, plot, img_item


@pytest.mark.parametrize(
    "img_item_builder",
    [
        lambda: make.trimage(gen_image4(100, 100), x0=100, y0=100),
        lambda: make.image(
            gen_image4(100, 100),
            center_on=(100, 100),
            pixel_size=1,
            lock_position=False,
        ),
    ],
)
def test_move_with_mouse(img_item_builder: Callable[[], BaseImageItem] | None):
    """Test the select tool."""

    with qt_app_context(exec_loop=False) as qapp:
        img_item = None if img_item_builder is None else img_item_builder()
        win, tool, plot, img_item = _setup_plot(img_item)
        x1, y1, *_ = _get_xy_coords(img_item)

        if img_item.can_rotate():
            initial_angle = img_item.param.pos_angle  # type: ignore
            assert initial_angle == 0
        assert plot.get_selected_items() == [img_item]

        drag_mouse(win, qapp, np.array([0.5, 0.6, 0.7]), np.array([0.5, 0.6, 0.7]))

        assert plot.get_selected_items() == [img_item]
        x2, y2, *_ = _get_xy_coords(img_item)
        assert x2 > x1 and y2 > y1
        if img_item.can_rotate():
            assert img_item.param.pos_angle == initial_angle  # type: ignore

        undo_redo(qapp, win)
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

        undo_redo(qapp, win)
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

        undo_redo(qapp, win)
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
        win.show()

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

        drag_mouse(win, qapp, np.linspace(0, 0.5, 100), np.linspace(0, 0.0, 100))

        assert plot.get_selected_items() == [tr_img]
        assert np.isclose(abs(tr_img.param.pos_angle), 45, 0.5)  # type: ignore

        undo_redo(qapp, win)
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
        win.show()

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

        exec_dialog(win)


@pytest.mark.parametrize(
    "mouse_path, rotation",
    [
        ((np.linspace(0.0, 0.5, 100), np.zeros(100)), True),
        ((np.linspace(0.5, 0.8, 100), np.linspace(0.5, 0.8, 100)), False),
    ],
)
def test_multi_rotate_move_with_mouse(
    mouse_path: tuple[np.ndarray, np.ndarray], rotation: bool
):
    n = 100
    x0 = n
    y0 = 0

    with qt_app_context() as qapp:
        # All images are superimposed so that it is easy to select the corners for
        # rotations
        images = [make.trimage(gen_image4(n, n), x0=x0, y0=y0) for i in range(3)]
        initial_angle = 0

        win, tool = create_window(
            SelectTool, active_item_type=IImageItemType, items=images
        )
        win.show()
        keyboard_event(
            win, qapp, QC.Qt.Key.Key_A, mod=QC.Qt.KeyboardModifier.ControlModifier
        )
        drag_mouse(win, qapp, mouse_path[0], mouse_path[1])

        if rotation:
            _assert_images_angle(images, ref_angle=initial_angle)
        else:
            _assert_images_pos(images, x0, y0)

        undo_redo(qapp, win)
        exec_dialog(win)


@pytest.mark.parametrize(
    "keymod, rotation",
    [
        (QC.Qt.KeyboardModifier.ControlModifier, False),
        (QC.Qt.KeyboardModifier.ShiftModifier, True),
        (
            QC.Qt.KeyboardModifier.ControlModifier
            | QC.Qt.KeyboardModifier.ShiftModifier,
            True,
        ),
    ],
)
def test_multi_rotate_move_with_keyboard(
    keymod: QC.Qt.KeyboardModifier, rotation: bool
):
    n = 100
    x0 = n
    y0 = 0

    with qt_app_context() as qapp:
        # All images are superimposed so that it is easy to select the corners for
        # rotations
        images = [make.trimage(gen_image4(n, n), x0=x0, y0=y0) for i in range(3)]

        win, tool = create_window(
            SelectTool, active_item_type=IImageItemType, items=images
        )
        win.show()
        keyboard_event(
            win, qapp, QC.Qt.Key.Key_A, mod=QC.Qt.KeyboardModifier.ControlModifier
        )
        for _ in range(10):
            # Should rotate/move left depending on modifier
            keyboard_event(win, qapp, QC.Qt.Key.Key_Right, mod=keymod)
            # Should never rotate
            keyboard_event(win, qapp, QC.Qt.Key.Key_Down, mod=keymod)

        if rotation:
            _assert_images_angle(images, ref_angle=0)
        else:
            _assert_images_pos(images, x0, y0)

        undo_redo(qapp, win)
        exec_dialog(win)


if __name__ == "__main__":
    test_move_with_mouse(None)
    test_move_with_arrows(QC.Qt.KeyboardModifier.NoModifier)
    test_rotate_with_arrow(QC.Qt.KeyboardModifier.ShiftModifier)
    test_select_all_items()
    test_rotate_with_mouse()
    test_rectangular_selection()
    test_multi_rotate_move_with_mouse((np.linspace(0.0, 0.5, 100), np.zeros(100)), True)
    test_multi_rotate_move_with_mouse((np.linspace(0.0, 0.5, 100), np.zeros(100)), True)
    test_multi_rotate_move_with_keyboard(
        QC.Qt.KeyboardModifier.ShiftModifier, rotation=True
    )
