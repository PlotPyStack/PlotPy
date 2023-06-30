# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Resize test: using the scaler C++ engine to resize images"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context

from plotpy.core import io, scaler
from plotpy.tests.gui.test_rotatecrop import imshow


def test_resize():
    """Test"""
    with qt_app_context(exec_loop=False):
        filename = os.path.join(os.path.dirname(__file__), "brain.png")
        data = io.imread(filename)
        dst_image = scaler.resize(data, (2000, 3000))
        imshow(dst_image)


if __name__ == "__main__":
    test_resize()
