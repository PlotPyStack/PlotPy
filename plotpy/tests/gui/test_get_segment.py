# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
AnnotatedSegmentTool test

This plotpy tool provide a MATLAB-like "ginput" feature.
"""

# guitest: show

import os

import numpy as np
import qtpy.QtCore as QC
from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.config import _
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog
from plotpy.core.tools.annotations import AnnotatedSegmentTool
from plotpy.core.tools.selection import SelectTool

# Input coordinate in pixel, in window reference frame
SEG_COORDINATES_INPUT = [0, 0, 0, 0]
# output coordinate in pixel, in plot reference frame
SEG_COORDINATES_OUTPUT = [8, -643, 8, -643]


def get_segment(*items):
    """Show image and return selected segment coordinates"""
    win = PlotDialog(
        _("Select a segment then press OK to accept"), edit=True, toolbar=True
    )
    default = win.manager.add_tool(SelectTool)
    win.manager.set_default_tool(default)
    segtool = win.manager.add_tool(
        AnnotatedSegmentTool, title="Test", switch_to_default_tool=True
    )
    segtool.activate()
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
        plot.set_active_item(item)
    if execenv.unattended:
        p0 = QC.QPointF(SEG_COORDINATES_INPUT[0], SEG_COORDINATES_INPUT[1])
        p1 = QC.QPointF(SEG_COORDINATES_INPUT[2], SEG_COORDINATES_INPUT[3])
        segtool.add_shape_to_plot(
            win.manager.get_plot(),
            p0,
            p1,
        )
    win.show()
    return win, segtool


def test_get_segment():
    """Test"""
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    with qt_app_context(exec_loop=True):
        image = make.image(filename=filename, colormap="bone")
        _win_persist, segtool = get_segment(image)

    shape = segtool.get_last_final_shape()
    rect = shape.get_rect()
    if execenv.unattended and shape is not None:
        rect_int = [int(i) for i in list(rect)]
        assert rect_int == SEG_COORDINATES_OUTPUT
    elif rect is not None:
        print(
            "Distance:",
            np.sqrt((rect[2] - rect[0]) ** 2 + (rect[3] - rect[1]) ** 2),
        )


if __name__ == "__main__":
    test_get_segment()
