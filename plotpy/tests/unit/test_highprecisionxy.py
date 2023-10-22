# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test high precision XYImageItem bug"""

# guitest: skip

# TODO: What is this test supposed to do? Check what's all about.

import numpy
from guidata.qthelpers import qt_app_context

from plotpy.builder import make


def test_xyimagebug():
    for offset in (1e3, 1e6, 1e9, 1e12):
        data = numpy.random.rand(100, 100)
        x = numpy.arange(100) + offset
        y = numpy.arange(100)
        with qt_app_context(exec_loop=True):
            image = make.xyimage(x, y, data=data, interpolation="nearest")
            win = make.dialog(type="image")
            plot = win.manager.get_plot()
            plot.add_item(image)
            plot.select_item(image)  # this helps in seeing where the image should be
            win.show()


if __name__ == "__main__":
    test_xyimagebug()
