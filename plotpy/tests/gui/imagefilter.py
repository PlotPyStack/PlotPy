# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Image filter demo"""


from scipy.ndimage import gaussian_filter

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType

SHOW = True  # Show test in GUI-based test launcher


def imshow(x, y, data, filter_area, yreverse=True):
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
    win.exec_()


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    try:
        from tests.gui.imagexy import compute_image
    except ImportError:
        from plotpy.tests.gui.imagexy import compute_image

    x, y, data = compute_image()
    imshow(x, y, data, filter_area=(-3.0, -1.0, 0.0, 2.0), yreverse=False)
    # --
    import os

    import numpy as np

    from plotpy.widgets import io

    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    data = io.imread(filename, to_grayscale=True)
    x = np.linspace(0, 30.0, data.shape[1])
    y = np.linspace(0, 30.0, data.shape[0])
    imshow(x, y, data, filter_area=(10, 20, 5, 15))


if __name__ == "__main__":
    test()
