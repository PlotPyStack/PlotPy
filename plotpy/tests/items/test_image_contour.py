# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Contour test"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_contour():
    with qt_app_context(exec_loop=True):
        # compute the image
        delta = 0.025
        x, y = np.arange(-3.0, 3.0, delta), np.arange(-2.0, 2.0, delta)
        X, Y = np.meshgrid(x, y)
        Z1 = np.exp(-(X**2) - Y**2)
        Z2 = np.exp(-((X - 1) ** 2) - (Y - 1) ** 2)
        Z = (Z1 - Z2) * 2

        # show the image
        _win = ptv.show_items(
            [make.image(Z)] + make.contours(Z, np.arange(-2, 2, 0.5)),
            wintitle="Sample contour plotting",
            curve_antialiasing=False,
            lock_aspect_ratio=True,
        )


if __name__ == "__main__":
    test_contour()
