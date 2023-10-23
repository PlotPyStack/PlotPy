# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""RGB Image test, creating the RGBImageItem object via make.rgbimage"""

# guitest: show

from guidata.configtools import get_image_file_path
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_image_rgb():
    """Testing RGB image item"""
    with qt_app_context(exec_loop=True):
        item = make.rgbimage(
            filename=get_image_file_path("image.png"), xdata=[-1, 1], ydata=[-1, 1]
        )
        _wn = ptv.show_items([item], plot_type="image", wintitle=test_image_rgb.__doc__)


if __name__ == "__main__":
    test_image_rgb()
