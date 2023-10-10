# -*- coding: utf-8 -*-
#
# For licensing and distribution details, please read carefully xgrid/__init__.py

"""
Get rectangular selection from image
"""

# guitest: show

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests.gui.test_get_segment import SEG_AXES_COORDS, PatchedSelectDialog
from plotpy.tools import RectangleTool
from plotpy.widgets.selectdialog import select_with_shape_tool


def test_get_rectangle():
    """Test get_rectangle"""
    with qt_app_context():
        image = make.image(data=np.random.rand(200, 200), colormap="gray")
        shape = select_with_shape_tool(
            None, RectangleTool, image, "Test", tooldialogclass=PatchedSelectDialog
        )
        rect = shape.get_rect()
        if execenv.unattended:
            assert [round(i) for i in list(rect)] == SEG_AXES_COORDS
        elif rect is not None:
            print("Area:", rect)


if __name__ == "__main__":
    test_get_rectangle()
