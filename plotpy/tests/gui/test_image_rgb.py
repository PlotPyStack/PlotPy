# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""RGB Image test, creating the RGBImageItem object via make.rgbimage"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context

import plotpy
from plotpy.builder import make
from plotpy.tests import vistools as ptv

PLOTPYDIR = os.path.abspath(os.path.dirname(plotpy.__file__))
IMGFILE = os.path.join(PLOTPYDIR, "images", "items", "image.png")


def test_image_rgb():
    """Testing RGB image item"""
    title = test_image_rgb.__doc__
    with qt_app_context(exec_loop=True):
        item = make.rgbimage(filename=IMGFILE, xdata=[-1, 1], ydata=[-1, 1])
        _win = ptv.show_items([item], plot_type="image", wintitle=title)


if __name__ == "__main__":
    test_image_rgb()
