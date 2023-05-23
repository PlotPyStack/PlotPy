# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""RGB Image test, creating the RGBImageItem object via make.rgbimage"""

import os

from guidata.qthelpers import qt_app_context

import plotpy
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType

SHOW = True  # Show test in GUI-based test launcher

PLOTPYDIR = os.path.abspath(os.path.dirname(plotpy.__file__))
IMGFILE = os.path.join(PLOTPYDIR, "images", "items", "image.png")


def imshow(filename):
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="RGB image item test",
        options={"type": PlotType.IMAGE},
    )
    item = make.rgbimage(filename=filename, xdata=[-1, 1], ydata=[-1, 1])
    plot = win.manager.get_plot()
    plot.add_item(item)
    win.show()
    return win


def test_image_rgb():
    """Test"""
    with qt_app_context(exec_loop=True):
        _win_persist = imshow(IMGFILE)


if __name__ == "__main__":
    test_image_rgb()
