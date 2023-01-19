# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""All image and plot tools test"""


import os

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.tools.annotations import (
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
from plotpy.widgets.tools.axes import PlaceAxesTool
from plotpy.widgets.tools.cursor import (
    HCursorTool,
    HRangeTool,
    VCursorTool,
    XCursorTool,
)
from plotpy.widgets.tools.label import LabelTool
from plotpy.widgets.tools.shapes import FreeFormTool, MultiLineTool

SHOW = True  # Show test in GUI-based test launcher


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
        win.add_tool(toolklass)
    return win


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    win = create_window()
    image = make.image(filename=filename, colormap="bone")
    plot = win.get_plot()
    plot.add_item(image)
    win.exec_()


if __name__ == "__main__":
    test()
