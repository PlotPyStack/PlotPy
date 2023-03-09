# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
AnnotatedSegmentTool test

This plotpy tool provide a MATLAB-like "ginput" feature.
"""

import os

import numpy as np
import qtpy.QtCore as QC

import plotpy.widgets
from plotpy.config import _
from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog
from plotpy.widgets.tools.annotations import AnnotatedSegmentTool
from plotpy.widgets.tools.selection import SelectTool

SHOW = True  # Show test in GUI-based test launcher
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
    # TODO A jouter un mode unatended, ajoute un segement segement sans action opérateur
    p0 = QC.QPointF(SEG_COORDINATES_INPUT[0], SEG_COORDINATES_INPUT[1])
    p1 = QC.QPointF(SEG_COORDINATES_INPUT[2], SEG_COORDINATES_INPUT[3])
    segtool.add_shape_to_plot(
        win.manager.get_plot(),
        p0,
        p1,
    )
    win.show()
    win.exec_()
    shape = segtool.get_last_final_shape()
    return shape.get_rect()


def test_get_segment():
    """Test"""
    # -- Create QApplication
    _app = plotpy.widgets.qapplication()
    # --
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    image = make.image(filename=filename, colormap="bone")
    rect = get_segment(image)
    rect_int = [int(i) for i in list(rect)]
    assert rect_int == SEG_COORDINATES_OUTPUT
    print("Distance:", np.sqrt((rect[2] - rect[0]) ** 2 + (rect[3] - rect[1]) ** 2))


if __name__ == "__main__":
    test_get_segment()
