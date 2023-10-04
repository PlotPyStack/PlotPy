# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test showing an image"""

# FIXME: unexpected behavior when changing the xmin/xmax/ymin/ymax values in
#       the image parameters (2nd tab: "Axes")

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def test_image():
    """Testing ImageItem object"""
    for index, func in enumerate((ptd.gen_image1, ptd.gen_image2, ptd.gen_image3)):
        title = test_image.__doc__ + f" #{index+1}"
        data = func()
        with qt_app_context(exec_loop=True):
            _win = ptv.show_items([make.image(data)], wintitle=title)


if __name__ == "__main__":
    test_image()
