from __future__ import annotations

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.interfaces.items import IImageItemType
from plotpy.tests.unit.utils import create_window, drag_mouse
from plotpy.tools import DisplayCoordsTool


def test_display_coords_on_curve():
    """Test display coordinates tool on a curve."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(DisplayCoordsTool)
        drag_mouse(win, qapp, np.array([0.5]), np.array([0.5]), click=False)
        drag_mouse(win, qapp, np.array([0.5]), np.array([0.5]), click=True)


def test_display_coords_on_image():
    """Test display coordinates tool on an image."""
    with qt_app_context(exec_loop=False) as qapp:
        win, tool = create_window(DisplayCoordsTool, active_item_type=IImageItemType)
        drag_mouse(win, qapp, np.array([0.5]), np.array([0.5]), click=False)
        drag_mouse(win, qapp, np.array([0.5]), np.array([0.5]), click=True)


if __name__ == "__main__":
    test_display_coords_on_curve()
    test_display_coords_on_image()
