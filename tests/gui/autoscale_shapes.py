# -*- coding: utf-8 -*-
#
# Copyright © 2019 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""This example shows autoscaling of plot with various shapes."""

SHOW = True  # Show test in GUI-based test launcher

import numpy as np

from plotpy.gui.widgets.items.annotations import AnnotatedRectangle
from plotpy.gui.widgets.items import shapes
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.styles import ShapeParam, AnnotationParam
from plotpy.gui.widgets.tools import (
    RectangleTool,
    EllipseTool,
    PlaceAxesTool,
    MultiLineTool,
    FreeFormTool,
    SegmentTool,
    CircleTool,
    AnnotatedRectangleTool,
    AnnotatedEllipseTool,
    AnnotatedSegmentTool,
    AnnotatedCircleTool,
    LabelTool,
    AnnotatedPointTool,
    ObliqueRectangleTool,
    AnnotatedObliqueRectangleTool,
)


def create_window():
    win = PlotDialog(edit=False, toolbar=True, wintitle="Autoscaling of shapes")
    for toolklass in (
        LabelTool,
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
    win = create_window()
    plot = win.get_plot()
    plot.set_aspect_ratio(lock=True)
    plot.set_antialiasing(False)
    win.get_itemlist_panel().show()

    # Add a polygon
    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    param = ShapeParam()
    param.label = "Polygon"
    crv = shapes.PolygonShape(closed=False, shapeparam=param)
    crv.set_points(np.column_stack((x, np.sin(x))))
    plot.add_item(crv)

    # Add a circle
    param = ShapeParam()
    param.label = "Circle"
    circle = shapes.EllipseShape(-1, 2, shapeparam=param)
    plot.add_item(circle)

    # Add an annotated rectangle
    param = AnnotationParam()
    param.title = "Annotated rectangle"
    rect = AnnotatedRectangle(2.5, 1, 4, 1.2, annotationparam=param)
    plot.add_item(rect)

    # Add an annotated rectangle excluded
    param = AnnotationParam()
    param.title = "Annotated rectangle excluded from autoscale"
    rect = AnnotatedRectangle(1., 2., 5, 10, annotationparam=param)
    plot.add_item(rect)
    
    plot.add_autoscale_excludes([rect])

    win.show()
    win.exec_()


if __name__ == "__main__":
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    test()
