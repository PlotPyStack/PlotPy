# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing 'auto' plot type"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def test_auto_curve_image():
    """Test auto curve image"""
    x = linspace(0, 2000, 20000)
    y = (sin(sin(sin(x / 50))) - 1) * -1000
    with qt_app_context(exec_loop=True):
        items = [
            make.image(ptd.gen_image1()),
            make.curve(x, y, color="b"),
            make.legend("TR"),
        ]
        _win = ptv.show_items(items, wintitle="Testing 'auto' plot type")


if __name__ == "__main__":
    test_auto_curve_image()
