from __future__ import annotations

import numpy as np
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.interfaces.items import IImageItemType
from plotpy.panels.csection.cswidget import LineCrossSection
from plotpy.tests.unit.utils import create_window, drag_mouse
from plotpy.tools import LineCrossSectionTool


def test_line_cross_section():
    """Test the line cross section tool."""
    with qt_app_context(exec_loop=False):
        win, _tool = create_window(
            LineCrossSectionTool,
            active_item_type=IImageItemType,
            panels=[LineCrossSection],
        )
        n = 100
        drag_mouse(win, np.linspace(0.25, 0.75, n), np.linspace(0.25, 0.75, n))
        exec_dialog(win)


if __name__ == "__main__":
    test_line_cross_section()
