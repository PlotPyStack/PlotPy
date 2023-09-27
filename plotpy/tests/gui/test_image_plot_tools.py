# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""All image and plot tools test"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.items import Marker
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
        title = "toto"
        marker1 = Marker(label_cb=lambda x, y: f"{title}x = {x:g}<br>y = {y:g}")
        plot.add_item(marker1)
        marker2 = Marker(label_cb=lambda x, y: f"{title}x = {x:g}<br>y = {y:g}")
        plot.add_item(marker2)


if __name__ == "__main__":
    test_image_plot_tools()
