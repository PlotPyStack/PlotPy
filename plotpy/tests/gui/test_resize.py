# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Resize test: using the scaler C++ engine to resize images"""

import os

from plotpy.widgets import io, qapplication, scaler
from plotpy.widgets.plot.interactive import imshow, show

SHOW = True  # Show test in GUI-based test launcher


def test_resize():
    """Test"""
    app = qapplication()

    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    data = io.imread(filename)
    dst_image = scaler.resize(data, (2000, 3000))

    imshow(dst_image, interpolation="nearest")
    show()


if __name__ == "__main__":
    test_resize()
