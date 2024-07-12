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
from plotpy.tests.data import gen_xyz_data


def test_contour():
    """Contour plotting test"""
    with qt_app_context(exec_loop=True):
        _x, _y, z = gen_xyz_data()
        _win = ptv.show_items(
            [make.image(z)] + make.contours(z, np.arange(-2, 2, 0.5)),
            wintitle=test_contour.__doc__,
            curve_antialiasing=False,
            lock_aspect_ratio=True,
        )


if __name__ == "__main__":
    test_contour()
