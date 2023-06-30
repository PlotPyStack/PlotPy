# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""All image and plot tools test"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context

import plotpy.widgets
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.annotations import (
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
    CircleTool,
    EllipseTool,
    ObliqueRectangleTool,
    RectangleTool,
    SegmentTool,
)
from plotpy.core.tools.axes import PlaceAxesTool
from plotpy.core.tools.cursor import HCursorTool, HRangeTool, VCursorTool, XCursorTool
from plotpy.core.tools.label import LabelTool
from plotpy.core.tools.shapes import FreeFormTool, MultiLineTool


def create_window():
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="All image and plot tools test",
        options={"type": PlotType.IMAGE},
    )
    for toolklass in (
        LabelTool,
        HRangeTool,
        VCursorTool,
        HCursorTool,
        XCursorTool,
        SegmentTool,
        RectangleTool,
        ObliqueRectangleTool,
        CircleTool,
        EllipseTool,
        MultiLineTool,
        FreeFormTool,
        PlaceAxesTool,
        AnnotatedRectangleTool,
        AnnotatedObliqueRectangleTool,
        AnnotatedCircleTool,
        AnnotatedEllipseTool,
        AnnotatedSegmentTool,
        AnnotatedPointTool,
    ):
        win.manager.add_tool(toolklass)
    return win


def test_image_plot_tools():
    """Test"""
    with qt_app_context(exec_loop=True):
        filename = os.path.join(os.path.dirname(__file__), "brain.png")
        win = create_window()
        win.show()
        image = make.image(filename=filename, colormap="bone")
        plot = win.manager.get_plot()
        plot.add_item(image)


if __name__ == "__main__":
    test_image_plot_tools()
