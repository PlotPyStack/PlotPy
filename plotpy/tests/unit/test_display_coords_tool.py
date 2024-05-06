from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
import qtpy.QtCore as QC
from guidata.qthelpers import qt_app_context

from plotpy.interfaces.items import ICurveItemType, IImageItemType
from plotpy.tests.unit.utils import create_window, drag_mouse
from plotpy.tools import DisplayCoordsTool

if TYPE_CHECKING:
    from plotpy.interfaces.items import IItemType


@pytest.mark.parametrize("active_item", [ICurveItemType, IImageItemType, None])
def test_display_coords(active_item: type[IItemType] | None):
    """Test display coordinates tool on a curve and on an image."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(DisplayCoordsTool, active_item_type=active_item)
        plot = win.manager.get_plot()

        # The is no way to test a condition while the mouse is moving so it is
        # not possible to test the display of the coordinates while the mouse is moving.
        assert plot.curve_pointer is False and plot.canvas_pointer is False
        drag_mouse(win, qapp, np.array([0.5]), np.array([0.5]), click=False)
        assert plot.curve_pointer is False and plot.canvas_pointer is False
        drag_mouse(win, qapp, np.array([0.5]), np.array([0.5]), click=True)
        assert plot.curve_pointer is False and plot.canvas_pointer is False
        drag_mouse(
            win,
            qapp,
            np.array([0.5]),
            np.array([0.5]),
            click=False,
            mod=QC.Qt.KeyboardModifier.AltModifier,
        )
        assert plot.curve_pointer is False and plot.canvas_pointer is False
        drag_mouse(
            win,
            qapp,
            np.array([0.5]),
            np.array([0.5]),
            click=False,
            mod=QC.Qt.KeyboardModifier.ControlModifier,
        )
        assert plot.curve_pointer is False and plot.canvas_pointer is False


if __name__ == "__main__":
    for item in (ICurveItemType, IImageItemType):
        test_display_coords(item)
