# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""This example shows autoscaling of plot with various shapes."""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.plot import PlotDialog
from plotpy.tools import (
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
    CircleTool,
    EllipseTool,
    LabelTool,
    MultiLineTool,
    ObliqueRectangleTool,
    PlaceAxesTool,
    PolygonTool,
    RectangleTool,
    SegmentTool,
)


def create_window():
    win = PlotDialog(edit=False, toolbar=True, title="Autoscaling of shapes")
    for toolklass in (
        LabelTool,
        SegmentTool,
        RectangleTool,
        ObliqueRectangleTool,
        CircleTool,
        EllipseTool,
        MultiLineTool,
        PolygonTool,
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

        incl = "Included in autoscale"
        noti = "Excluded from autoscale"

        # Add a polygon
        x = np.arange(-3.0, 3.0, 0.2)
        crv = make.polygon(x, np.sin(x), False, "Polygon")
        plot.add_item(crv)

        # Add a circle
        circle = make.annotated_circle(-1, 2, 0, 0, incl, show_computations=False)
        plot.add_item(circle)

        # Add an annotated rectangle
        rect = make.annotated_rectangle(2.5, 1, 4, 1.2, incl, show_computations=False)
        plot.add_item(rect)
        plot.add_autoscale_excludes([rect])
        plot.remove_autoscale_excludes([rect])  # Just to test the method

        # Add an annotated rectangle excluded
        rect = make.annotated_rectangle(1.0, 2.0, 5, 10, noti, show_computations=False)
        plot.add_item(rect)

        plot.add_autoscale_excludes([rect])

        win.show()


if __name__ == "__main__":
    test_autoscale_shapes()
