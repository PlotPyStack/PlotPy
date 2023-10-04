# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Image with custom X/Y axes linear scales"""

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def test_imagexy():
    """Testing XYImageItem"""
    with qt_app_context(exec_loop=True):
        x, y, data = ptd.gen_xyimage()
        _win = ptv.show_items(
            [make.xyimage(x, y, data)],
            plot_type="image",
            xlabel="x (a.u.)",
            ylabel="y (a.u.)",
            wintitle=test_imagexy.__doc__,
        )


if __name__ == "__main__":
    test_imagexy()
