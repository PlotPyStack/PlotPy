# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Image filter demo"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context
from scipy.ndimage import gaussian_filter

from plotpy import io
from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import get_path


def imshow(x, y, data, filter_area, yreverse=True):
    with qt_app_context(exec_loop=True):
        win = make.dialog(
            edit=False,
            toolbar=True,
            wintitle="Image filter demo",
            xlabel="x (cm)",
            ylabel="y (cm)",
            yreverse=yreverse,
            type="image",
            size=(800, 600),
        )
        image = make.xyimage(x, y, data)
        plot = win.manager.get_plot()
        plot.add_item(image)
        xmin, xmax, ymin, ymax = filter_area

        def ifilter(x, y, data):
            """Image filter function"""
            return gaussian_filter(data, 5)

        flt = make.imagefilter(xmin, xmax, ymin, ymax, image, filter=ifilter)
        plot.add_item(flt, z=1)
        plot.replot()
        win.show()


def test_imagefilter():
    """Test image filter"""
    x, y, data = ptd.gen_xyimage()
    imshow(x, y, data, filter_area=(-3.0, -1.0, 0.0, 2.0), yreverse=False)

    filename = get_path("brain.png")
    data = io.imread(filename, to_grayscale=True)
    x = np.linspace(0, 30.0, data.shape[1])
    y = np.linspace(0, 30.0, data.shape[0])
    imshow(x, y, data, filter_area=(10, 20, 5, 15))


if __name__ == "__main__":
    test_imagefilter()
