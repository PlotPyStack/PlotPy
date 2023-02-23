# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
Masked Image test, creating the MaskedXYImageItem object via make.maskedxyimage

Masked image XY items are constructed using a masked array item. Masked data is
ignored in computations, like the average cross sections.
"""

import os
import pickle

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.tools.image import ImageMaskTool

SHOW = True  # Show test in GUI-based test launcher

FNAME = "image_masked_xy.pickle"

if __name__ == "__main__":
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    win = PlotDialog(
        toolbar=True,
        wintitle="Masked XY image item test",
        options={"type": PlotType.IMAGE},
    )
    win.manager.add_tool(ImageMaskTool)
    if os.access(FNAME, os.R_OK):
        print("Restoring mask...", end=" ")
        iofile = open(FNAME, "rb")
        image = pickle.load(iofile)
        iofile.close()
        print("OK")
    else:
        fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), "brain.png")
        data, fname, title = make._get_image_data(
            None, fname, "XY Brain Image", to_grayscale=True
        )
        x = [0]
        delta = 1
        for x_val in range(data.shape[0] - 1):
            delta = delta + 0.1
            x.append(x[-1] + delta)
        y = [0]
        for y_val in range(data.shape[1] - 1):
            delta = delta + 0.1
            y.append(y[-1] + delta)
        image = make.maskedimage(data=data, colormap="gray", show_mask=True, x=x, y=y)
    win.manager.get_plot().add_item(image)
    win.show()
    win.exec_()
    iofile = open(FNAME, "wb")
    pickle.dump(image, iofile)
