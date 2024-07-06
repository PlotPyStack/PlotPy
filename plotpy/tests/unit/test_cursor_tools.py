from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.tests.unit.utils import (
    create_window,
    drag_mouse,
)
from plotpy.tools import (
    HCursorTool,
    HRangeTool,
    VCursorTool,
    XCursorTool,
)

if TYPE_CHECKING:
    from plotpy.tools.cursor import BaseCursorTool


@pytest.mark.parametrize(
    "cursor_tool", [HCursorTool, VCursorTool, XCursorTool, HRangeTool]
)
def test_cursor_tool(cursor_tool: type[BaseCursorTool]):
    """Test the cursor tools. by simulating a mouse drag and checking if the tool
    shape is created.

    Args:
        cursor_tool: Cursor tool class to test.
    """
    with qt_app_context():
        win, _tool = create_window(cursor_tool)
        win.show()
        plot = win.manager.get_plot()

        active_tool = win.manager.get_active_tool()
        assert isinstance(active_tool, cursor_tool)
        tool_shape_type = type(active_tool.create_shape())
        assert tool_shape_type not in (type(item) for item in plot.get_items())

        drag_mouse(win, np.array([0.5, 0.6, 0.7]), np.array([0.5, 0.6, 0.7]))
        assert tool_shape_type in (type(item) for item in plot.get_items())

        exec_dialog(win)


if __name__ == "__main__":
    for tool in (HCursorTool, VCursorTool, XCursorTool, HRangeTool):
        test_cursor_tool(tool)
