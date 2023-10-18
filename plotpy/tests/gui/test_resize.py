# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Resize test: using the scaler C++ engine to resize images"""

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy import io
from plotpy.mathutils import scaler
from plotpy.tests import get_path
from plotpy.tests.gui.test_rotatecrop import imshow


def test_resize():
    """Test"""
    with qt_app_context(exec_loop=False):
        filename = get_path("brain.png")
        data = io.imread(filename)
        dst_image = scaler.resize(data, (2000, 3000))
        imshow(dst_image)


if __name__ == "__main__":
    test_resize()
