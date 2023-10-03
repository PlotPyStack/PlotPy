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
from plotpy.tools import DisplayCoordsTool


def create_2d_gaussian(size, dtype, x0=0, y0=0, mu=0.0, sigma=2.0, amp=None):
    """Creating 2D Gaussian (-10 <= x <= 10 and -10 <= y <= 10)"""
    xydata = np.linspace(-10, 10, size)
    x, y = np.meshgrid(xydata, xydata)
    if amp is None:
        amp = np.iinfo(dtype).max * 0.5
    t = (np.sqrt((x - x0) ** 2 + (y - y0) ** 2) - mu) ** 2
    return np.array(amp * np.exp(-t / (2.0 * sigma**2)), dtype=dtype)


def imshow(data, makefunc, title=None):
    """Show image in a new window"""
    with qt_app_context(exec_loop=True):
        win = make.dialog(edit=False, toolbar=True, wintitle=__doc__)
        image = makefunc(data, interpolation="nearest")
        text = "First pixel should be centered on (0, 0) coordinates"
        label = make.label(text, (1, 1), (0, 0), "L")
        rect = make.rectangle(5, 5, 10, 10, "Rectangle")
        cursors = []
        for i_cursor in range(0, 21, 10):
            cursors.append(make.vcursor(i_cursor, movable=False))
            cursors.append(make.hcursor(i_cursor, movable=False))
        plot = win.get_plot()
        plot.set_title(title)
        for item in [image, label, rect] + cursors:
            plot.add_item(item)
        plot.select_item(image)
        win.manager.get_tool(DisplayCoordsTool).activate_curve_pointer(True)
        win.show()


def test_pixel_coords():
    """Testing image pixel coordinates"""
    img = create_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=7, sigma=10.0)
    imshow(img, make.image, "ImageItem")


if __name__ == "__main__":
    test_pixel_coords()
