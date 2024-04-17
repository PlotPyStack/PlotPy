from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
import qtpy.QtCore as QC
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.interfaces.items import IShapeItemType
from plotpy.tests import vistools as ptv
from plotpy.tests.features.test_auto_curve_image import make_curve_image_legend
from plotpy.tools import (
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
    AverageCrossSectionTool,
    CircleTool,
    CrossSectionTool,
    EllipseTool,
    ImageStatsTool,
    ObliqueRectangleTool,
    PointTool,
    RectangleTool,
    SegmentTool,
    SelectTool,
    SnapshotTool,
)

if TYPE_CHECKING:
    from plotpy.plot.plotwidget import PlotWindow
    from plotpy.tools.base import RectangularActionTool

from plotpy.tests.unit.utils import drag_mouse

P0 = QC.QPointF(10, 10)
P1 = QC.QPointF(100, 100)

TOOLS = (
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
    AverageCrossSectionTool,
    CrossSectionTool,
    SnapshotTool,
    ImageStatsTool,
    CircleTool,
    EllipseTool,
    ObliqueRectangleTool,
    PointTool,
    RectangleTool,
    SegmentTool,
)

# guitest: show


def create_window(tool_classes: tuple[type[RectangularActionTool], ...]) -> PlotWindow:
    """Create a window with the given tools. The plot contains a curve, an image and a
     legend.

    Args:
        tool_classes: tools to add to the window.

    Returns:
        PlotWindow: The window containing the tools.
    """
    items = make_curve_image_legend()
    win = ptv.show_items(
        items, wintitle="Unit tests for RectangularActionTools", auto_tools=True
    )

    for toolklass in tool_classes:
        _ = win.manager.add_tool(toolklass)

    assert len(tool_classes) > 0

    return win


def _test_annotation_tools(tool_classes: tuple[type[RectangularActionTool], ...]):
    """Generic test for annotation tool. Simulates a mouse drag on the plot and checks
    that the tool is activated and deactivated correctly."""
    with qt_app_context(exec_loop=False) as qapp:
        win = create_window(tool_classes)
        win.show()
        plot = win.manager.get_plot()
        default_tool = win.manager.get_default_tool()
        for tool_class in tool_classes:
            tool = win.manager.get_tool(tool_class)
            assert tool is not None
            tool.activate()
            x_path = np.linspace(0, 0.5, 100)
            y_path = np.linspace(0, 0.5, 100)
            drag_mouse(win, qapp, x_path, y_path)
            if hasattr(tool_class, "SWITCH_TO_DEFAULT_TOOL"):
                assert win.manager.get_default_tool() == default_tool
        plot.select_some_items(plot.get_items(item_type=IShapeItemType))
        select_tool = win.manager.get_tool(SelectTool)
        assert select_tool is not None
        select_tool.activate()
        drag_mouse(win, qapp, np.linspace(0.2, 0.5, 10), np.linspace(0.2, 0.5, 10))
        exec_dialog(win)


@pytest.mark.parametrize("tool", TOOLS)
def test_tool(tool: type[RectangularActionTool]) -> None:
    """Test a single tool."""
    _test_annotation_tools((tool,))


def test_all_tools():
    """Test all tools."""
    _test_annotation_tools(TOOLS)


if __name__ == "__main__":
    test_all_tools()
