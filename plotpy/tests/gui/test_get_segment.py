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
from plotpy.core.coords import axes_to_canvas
from plotpy.core.plot import PlotDialog
from plotpy.core.tools import AnnotatedSegmentTool, SelectTool

SEG_AXES_COORDS = [20, 20, 70, 70]


def get_segment(*items):
    """Show image and return selected segment coordinates"""
    win = PlotDialog(
        _("Select a segment then press OK to accept"), edit=True, toolbar=True
    )
    default = win.manager.add_tool(SelectTool)
    win.manager.set_default_tool(default)
    segtool: AnnotatedSegmentTool = win.manager.add_tool(
        AnnotatedSegmentTool, title="Test", switch_to_default_tool=True
    )
    segtool.activate()
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
        plot.set_active_item(item)
    if execenv.unattended:
        segtool.add_shape_to_plot(
            win.manager.get_plot(),
            QC.QPointF(*axes_to_canvas(item, *SEG_AXES_COORDS[:2])),
            QC.QPointF(*axes_to_canvas(item, *SEG_AXES_COORDS[2:])),
        )
    win.show()
    return win, segtool


def test_get_segment():
    """Test get_segment"""
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    with qt_app_context(exec_loop=True):
        image = make.image(filename=filename, colormap="bone")
        _win_persist, segtool = get_segment(image)

    shape = segtool.get_last_final_shape()
    rect = shape.get_rect()
    if execenv.unattended:
        assert [round(i) for i in list(rect)] == SEG_AXES_COORDS
    elif rect is not None:
        print(
            "Distance:",
            np.sqrt((rect[2] - rect[0]) ** 2 + (rect[3] - rect[1]) ** 2),
        )


if __name__ == "__main__":
    test_get_segment()
