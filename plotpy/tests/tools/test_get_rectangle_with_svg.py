# -*- coding: utf-8 -*-
#
# For licensing and distribution details, please read carefully xgrid/__init__.py

"""
Get rectangular selection from image with SVG shape
"""

# guitest: show

from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.tests.data import gen_image4
from plotpy.tests.tools.test_get_segment import SEG_AXES_COORDS, PatchedSelectDialog
from plotpy.tools import RectangularShapeTool
from plotpy.widgets.selectdialog import select_with_shape_tool


class SVGToolExample(RectangularShapeTool):
    """Tool to select a rectangular area and create a pattern from it"""

    TITLE = "Pattern selection tool"
    ICON = "pattern.svg"
    AVOID_NULL_SHAPE = True
    SVG_FNAME = get_path("svg_tool.svg")

    def create_shape(self):
        """Create shape to be drawn"""
        svg_data = open(self.SVG_FNAME, "rb").read()
        shape = make.svg("rectangle", svg_data, 0, 0, 1, 1, "SVG")
        self.set_shape_style(shape)
        return shape, 0, 2


def test_get_rectangle_with_svg():
    """Test get_rectangle_with_svg"""
    with qt_app_context():
        image = make.image(data=gen_image4(200, 200), colormap="gray")
        shape = select_with_shape_tool(
            None, SVGToolExample, image, "Test", tooldialogclass=PatchedSelectDialog
        )
        if shape is not None:
            rect = shape.get_rect()
            if execenv.unattended:
                assert [round(i) for i in list(rect)] == SEG_AXES_COORDS
            elif rect is not None:
                print("Area:", rect)


if __name__ == "__main__":
    test_get_rectangle_with_svg()
