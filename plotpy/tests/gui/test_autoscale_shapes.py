# -*- coding: utf-8 -*-
#
# Copyright © 2019 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""This example shows autoscaling of plot with various shapes."""


import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.widgets.items.annotations import AnnotatedRectangle
from plotpy.widgets.items.shapes.ellipse import EllipseShape
from plotpy.widgets.items.shapes.polygon import PolygonShape
from plotpy.widgets.plot.plotwidget import PlotDialog
from plotpy.widgets.styles.shape import AnnotationParam, ShapeParam
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
from plotpy.widgets.tools.label import LabelTool
from plotpy.widgets.tools.shapes import FreeFormTool, MultiLineTool

SHOW = True  # Show test in GUI-based test launcher


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
        win.manager.add_tool(toolklass)
    return win


def test_autoscale_shapes():
    with qt_app_context(exec_loop=True):
        win = create_window()
        plot = win.manager.get_plot()
        plot.set_aspect_ratio(lock=True)
        plot.set_antialiasing(False)
        win.manager.get_itemlist_panel().show()

        # Add a polygon
        delta = 0.025
        x = np.arange(-3.0, 3.0, delta)
        param = ShapeParam()
        param.label = "Polygon"
        crv = PolygonShape(closed=False, shapeparam=param)
        crv.set_points(np.column_stack((x, np.sin(x))))
        plot.add_item(crv)

        # Add a circle
        param = ShapeParam()
        param.label = "Circle"
        circle = EllipseShape(-1, 2, shapeparam=param)
        plot.add_item(circle)

        # Add an annotated rectangle
        param = AnnotationParam()
        param.title = "Annotated rectangle"
        rect = AnnotatedRectangle(2.5, 1, 4, 1.2, annotationparam=param)
        plot.add_item(rect)

        # Add an annotated rectangle excluded
        param = AnnotationParam()
        param.title = "Annotated rectangle excluded from autoscale"
        rect = AnnotatedRectangle(1.0, 2.0, 5, 10, annotationparam=param)
        plot.add_item(rect)

        plot.add_autoscale_excludes([rect])

        win.show()


if __name__ == "__main__":
    test_autoscale_shapes()
