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

from plotpy.config import _
from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog
from plotpy.widgets.tools.annotations import AnnotatedSegmentTool
from plotpy.widgets.tools.selection import SelectTool

SHOW = True  # Show test in GUI-based test launcher


def get_segment(item):
    """Show image and return selected segment coordinates"""
    win = PlotDialog(_("Select a segment then press OK to accept"), edit=True)
    default = win.manager.add_tool(SelectTool)
    win.set_default_tool(default)
    segtool = win.manager.add_tool(
        AnnotatedSegmentTool, title="Test", switch_to_default_tool=True
    )
    segtool.activate()
    plot = win.manager.get_plot()
    plot.add_item(item)
    plot.set_active_item(item)
    win.show()
    if win.exec_():
        shape = segtool.get_last_final_shape()
        return shape.get_rect()


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    image = make.image(filename=filename, colormap="bone")
    rect = get_segment(image)
    print("Coordinates:", rect)
    print("Distance:", np.sqrt((rect[2] - rect[0]) ** 2 + (rect[3] - rect[1]) ** 2))


if __name__ == "__main__":
    test()
