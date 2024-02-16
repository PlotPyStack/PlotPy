# guitest: show

from __future__ import annotations

from typing import TYPE_CHECKING

import qtpy.QtCore as QC
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.tests import vistools as ptv
from plotpy.tests.features.test_auto_curve_image import make_curve_image_legend
from plotpy.tools.annotation import (
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
)
from plotpy.tools.cross_section import (
    AverageCrossSectionTool,
    CrossSectionTool,
    ObliqueCrossSectionTool,
)
from plotpy.tools.image import ImageStatsTool
from plotpy.tools.misc import SnapshotTool
from plotpy.tools.shape import (
    CircleTool,
    EllipseTool,
    ObliqueRectangleTool,
    PointTool,
    RectangleTool,
    SegmentTool,
)

if TYPE_CHECKING:
    from plotpy.plot.plotwidget import PlotDialog, PlotWindow
    from plotpy.tools.base import RectangularActionTool

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
    ObliqueCrossSectionTool,
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
        tool = win.manager.add_tool(toolklass)

    assert len(tool_classes) > 0
    win.manager.set_default_tool(tool)

    return win


def use_tool(win: PlotDialog, tool_class: type[RectangularActionTool]):
    filter_ = win.manager.get_plot().filter
    if (tool := win.manager.get_tool(tool_class)) is not None:
        tool.end_rect(filter_, P0, P1)


def _test_annotation_tools(tool_classes: tuple[type[RectangularActionTool], ...]):
    with qt_app_context(exec_loop=False):
        win = create_window(tool_classes)
        for tool_class in tool_classes:
            use_tool(win, tool_class)
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


def test_oblique_cross_section_tool():
    _test_annotation_tools((ObliqueCrossSectionTool,))


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
