# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Testing image coordinates issues

Check that the first image pixel is centered on (0, 0) coordinates.

See https://github.com/PlotPyStack/guiqwt/issues/90
"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv
from plotpy.tools import DisplayCoordsTool


def test_pixel_coords():
    """Testing image pixel coordinates"""
    title = test_pixel_coords.__doc__
    data = ptd.gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=7, sigma=10.0)
    with qt_app_context(exec_loop=True):
        image = make.image(data, interpolation="nearest")
        text = "First pixel should be centered on (0, 0) coordinates"
        label = make.label(text, (1, 1), (0, 0), "L")
        rect = make.rectangle(5, 5, 10, 10, "Rectangle")
        cursors = []
        for i_cursor in range(0, 21, 10):
            cursors.append(make.vcursor(i_cursor, movable=False))
            cursors.append(make.hcursor(i_cursor, movable=False))
        win = ptv.show_items([image, label, rect] + cursors, wintitle=title)
        plot = win.get_plot()
        plot.select_item(image)
        win.manager.get_tool(DisplayCoordsTool).activate_curve_pointer(True)


if __name__ == "__main__":
    test_pixel_coords()
