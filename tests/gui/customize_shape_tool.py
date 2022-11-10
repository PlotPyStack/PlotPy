# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Shows how to customize a shape created with a tool like RectangleTool"""

SHOW = True  # Show test in GUI-based test launcher

import os.path as osp

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.tools import (
    RectangleTool,
    EllipseTool,
    SegmentTool,
    MultiLineTool,
    FreeFormTool,
)
from plotpy.gui.widgets.builder import make
from plotpy.gui.widgets.styles import style_generator, update_style_attr

STYLE = style_generator()


def customize_shape(shape):
    global STYLE
    param = shape.shapeparam
    style = next(STYLE)
    update_style_attr(style, param)
    param.update_shape(shape)
    shape.plot().replot()


def create_window():
    gridparam = make.gridparam(
        background="black", minor_enabled=(False, False), major_style=(".", "gray", 1)
    )
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="All image and plot tools test",
        options=dict(gridparam=gridparam, type=PlotType.IMAGE),
    )
    for toolklass in (
        RectangleTool,
        EllipseTool,
        SegmentTool,
        MultiLineTool,
        FreeFormTool,
    ):
        win.add_tool(toolklass, handle_final_shape_cb=customize_shape)
    return win


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    # --
    filename = osp.join(osp.dirname(__file__), "brain.png")
    win = create_window()
    image = make.image(filename=filename, colormap="bone", alpha_mask=True)
    plot = win.get_plot()
    plot.add_item(image)
    win.exec_()


if __name__ == "__main__":
    test()
