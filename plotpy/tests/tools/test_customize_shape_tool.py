# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Shows how to customize a shape created with a tool like RectangleTool"""

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.constants import LUTAlpha
from plotpy.styles import style_generator, update_style_attr
from plotpy.tests import get_path
from plotpy.tools import (
    EllipseTool,
    MultiLineTool,
    PolygonTool,
    RectangleTool,
    SegmentTool,
)

STYLE = style_generator()


def customize_shape(shape):
    global STYLE
    param = shape.shapeparam
    style = next(STYLE)
    update_style_attr(style, param)
    param.update_item(shape)
    shape.plot().replot()


def create_window():
    gridparam = make.gridparam(
        background="black", minor_enabled=(False, False), major_style=(":", "gray", 1)
    )
    win = make.dialog(
        edit=False,
        toolbar=True,
        wintitle="All image and plot tools test",
        gridparam=gridparam,
        type="image",
        size=(800, 600),
    )
    for toolklass in (
        RectangleTool,
        EllipseTool,
        SegmentTool,
        MultiLineTool,
        PolygonTool,
    ):
        win.manager.add_tool(toolklass, handle_final_shape_cb=customize_shape)
    return win


def test_customize_shape_tool():
    """Test"""
    with qt_app_context(exec_loop=True):
        filename = get_path("brain.png")
        win = create_window()
        image = make.image(
            filename=filename, colormap="bone", alpha_function=LUTAlpha.LINEAR
        )
        plot = win.manager.get_plot()
        plot.add_item(image)
        win.show()


if __name__ == "__main__":
    test_customize_shape_tool()
