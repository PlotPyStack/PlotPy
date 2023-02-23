# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Shows how to customize a shape created with a tool like RectangleTool"""


import os

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.styles.base import style_generator, update_style_attr
from plotpy.widgets.tools.shapes import (
    EllipseTool,
    FreeFormTool,
    MultiLineTool,
    RectangleTool,
    SegmentTool,
)

SHOW = True  # Show test in GUI-based test launcher
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
        win.manager.add_tool(toolklass, handle_final_shape_cb=customize_shape)
    return win


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    win = create_window()
    image = make.image(filename=filename, colormap="bone", alpha_mask=True)
    plot = win.manager.get_plot()
    plot.add_item(image)
    win.exec_()


if __name__ == "__main__":
    test()
