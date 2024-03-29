# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Test ``get_segment`` feature: select a segment on an image.

This plotpy tool provide a MATLAB-like "ginput" feature.
"""

# guitest: show

import numpy as np
import qtpy.QtCore as QC
from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.coords import axes_to_canvas
from plotpy.tools import AnnotatedSegmentTool
from plotpy.widgets.selectdialog import SelectDialog, select_with_shape_tool

SEG_AXES_COORDS = [20, 20, 70, 70]


class PatchedSelectDialog(SelectDialog):
    """Patched SelectDialog"""

    def set_image_and_tool(self, item, toolclass, **kwargs):
        """Reimplement SelectDialog method"""
        super().set_image_and_tool(item, toolclass, **kwargs)
        if execenv.unattended:
            self.show()
            self.sel_tool.add_shape_to_plot(
                self.manager.get_plot(),
                QC.QPointF(*axes_to_canvas(item, *SEG_AXES_COORDS[:2])),
                QC.QPointF(*axes_to_canvas(item, *SEG_AXES_COORDS[2:])),
            )


def test_get_segment():
    """Test get_segment"""
    with qt_app_context():
        image = make.image(data=np.random.rand(200, 200), colormap="gray")
        shape = select_with_shape_tool(
            None,
            AnnotatedSegmentTool,
            image,
            "Test",
            tooldialogclass=PatchedSelectDialog,
        )
        if shape is not None:
            rect = shape.get_rect()
            if execenv.unattended:
                assert [round(i) for i in list(rect)] == SEG_AXES_COORDS
            elif rect is not None:
                distance = np.sqrt((rect[2] - rect[0]) ** 2 + (rect[3] - rect[1]) ** 2)
                print("Distance:", distance)


if __name__ == "__main__":
    test_get_segment()
