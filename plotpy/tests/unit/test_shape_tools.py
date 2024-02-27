from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import qtpy.QtCore as QC
from guidata.qthelpers import exec_dialog, qt_app_context

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
    SnapshotTool,
)

if TYPE_CHECKING:
    from plotpy.plot.plotwidget import PlotWindow
    from plotpy.tools.base import RectangularActionTool

from plotpy.tests.unit.test_point_tools import drag_mouse

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


def create_window(tool_classes: tuple[type[RectangularActionTool], ...]) -> PlotWindow:
    items = make_curve_image_legend()
    win = ptv.show_items(
        items, wintitle="Unit tests for RectangularActionTools", auto_tools=True
    )

    for toolklass in tool_classes:
        _ = win.manager.add_tool(toolklass)

    assert len(tool_classes) > 0
    # win.manager.set_default_tool(tool)

    return win


def use_tool(win: PlotWindow, tool_class: type[RectangularActionTool]):
    filter_ = win.manager.get_plot().filter
    if (tool := win.manager.get_tool(tool_class)) is not None:
        tool.end_rect(filter_, P0, P1)


def _test_annotation_tools(tool_classes: tuple[type[RectangularActionTool], ...]):
    with qt_app_context(exec_loop=False) as qapp:
        win = create_window(tool_classes)
        default_tool = win.manager.get_default_tool()
        for tool_class in tool_classes:

            win.manager.get_tool(tool_class).activate()
            x_path = np.linspace(0, 0.5, 100)
            y_path = np.linspace(0, 0.5, 100)
            drag_mouse(win, qapp, x_path, y_path)
            if getattr(tool_class, "SWITCH_TO_DEFAULT_TOOL", False):
                assert win.manager.get_default_tool() == default_tool

        exec_dialog(win)


def test_annotated_circle_tool():
    _test_annotation_tools((AnnotatedCircleTool,))


def test_annotated_ellipse_tool():
    _test_annotation_tools((AnnotatedEllipseTool,))


def test_annotated_oblique_rectangle_tool():
    _test_annotation_tools((AnnotatedObliqueRectangleTool,))


def test_annotated_point_tool():
    _test_annotation_tools((AnnotatedPointTool,))


def test_annotated_rectangle_tool():
    _test_annotation_tools((AnnotatedRectangleTool,))


def test_annotated_segment_tool():
    _test_annotation_tools((AnnotatedSegmentTool,))


def test_avg_cross_section_tool():
    _test_annotation_tools((AverageCrossSectionTool,))


def test_cross_section_tool():
    _test_annotation_tools((CrossSectionTool,))


def test_snapshot_tool():
    _test_annotation_tools((SnapshotTool,))


def test_image_stats_tool():
    _test_annotation_tools((ImageStatsTool,))


def test_circle_tool():
    _test_annotation_tools((CircleTool,))


def test_ellipse_tool():
    _test_annotation_tools((EllipseTool,))


def test_oblique_rectangle_tool():
    _test_annotation_tools((ObliqueRectangleTool,))


def test_point_tool():
    _test_annotation_tools((PointTool,))


def test_rectangle_tool():
    _test_annotation_tools((RectangleTool,))


def test_segment_tool():
    _test_annotation_tools((SegmentTool,))


if __name__ == "__main__":
    _test_annotation_tools(TOOLS)
