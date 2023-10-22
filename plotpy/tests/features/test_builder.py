# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Builder tests"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def test_builder():
    """Testing plot builder"""
    data = ptd.gen_image1()
    show = ptv.show_items
    with qt_app_context(exec_loop=True):
        _win0 = show([make.image(data, colormap="pink")], wintitle="Pink colormap test")
        _win1 = show([make.image(data)], wintitle="Default LUT range")
        img1 = make.image(data)
        img1.set_lut_range([0, 1])
        _win2 = show([img1], wintitle="0->1 LUT range through item")
        img2 = make.image(data, lut_range=[0, 1])
        _win3 = show([img2], wintitle="0->1 LUT range through builder")
        x = np.linspace(1, 10, 200)
        y = np.sin(x)

        crv1 = make.curve(x, y, dx=x * 0.1, dy=y * 0.23)
        crv2 = make.curve(x, np.cos(x), color="#FF0000")
        _win4 = show([crv1, crv2], wintitle="Error bars with make.curve()")

        dat22 = np.zeros((2, 2), np.float32)
        dat22[0, 0] = 1
        dat22[0, 1] = 2
        dat22[1, 0] = 3
        dat22[1, 1] = 4
        img3 = make.image(dat22, xdata=[-1, 3], ydata=[-1, 3], interpolation="nearest")
        _win5 = show([img3], wintitle="2x2 image")

        img4 = make.image(dat22, x=[0, 2], y=[0, 2], interpolation="nearest")
        _win6 = show([img4], wintitle="Equivalent 2x2 XY image")


if __name__ == "__main__":
    test_builder()
