# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Image filter demo"""

# guitest: show

import os

import numpy as np
from guidata.qthelpers import qt_app_context
from scipy.ndimage import gaussian_filter

from plotpy.core import io
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.tests.gui.test_imagexy import compute_image


def imshow(x, y, data, filter_area, yreverse=True):
    with qt_app_context(exec_loop=True):
        win = PlotDialog(
            edit=False,
            toolbar=True,
            wintitle="Image filter demo",
            options=dict(
                xlabel="x (cm)", ylabel="y (cm)", yreverse=yreverse, type=PlotType.IMAGE
            ),
        )
        image = make.xyimage(x, y, data)
        plot = win.manager.get_plot()
        plot.add_item(image)
        xmin, xmax, ymin, ymax = filter_area
        flt = make.imagefilter(
            xmin,
            xmax,
            ymin,
            ymax,
            image,
            filter=lambda x, y, data: gaussian_filter(data, 5),
        )
        plot.add_item(flt, z=1)
        plot.replot()
        win.show()


def test_imagefilter():
    """Test image filter"""
    x, y, data = compute_image()
    imshow(x, y, data, filter_area=(-3.0, -1.0, 0.0, 2.0), yreverse=False)

    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    data = io.imread(filename, to_grayscale=True)
    x = np.linspace(0, 30.0, data.shape[1])
    y = np.linspace(0, 30.0, data.shape[0])
    imshow(x, y, data, filter_area=(10, 20, 5, 15))


if __name__ == "__main__":
    test_imagefilter()
