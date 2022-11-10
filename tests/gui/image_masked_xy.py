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

import os, os.path as osp, pickle

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.tools import ImageMaskTool
from plotpy.gui.widgets.builder import make

SHOW = True  # Show test in GUI-based test launcher

FNAME = "image_masked_xy.pickle"

if __name__ == "__main__":
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    win = PlotDialog(
        toolbar=True,
        wintitle="Masked XY image item test",
        options={"type": PlotType.IMAGE},
    )
    win.add_tool(ImageMaskTool)
    if os.access(FNAME, os.R_OK):
        print("Restoring mask...", end=" ")
        iofile = open(FNAME, "rb")
        image = pickle.load(iofile)
        iofile.close()
        print("OK")
    else:
        fname = osp.join(osp.abspath(osp.dirname(__file__)), "brain.png")
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
    win.get_plot().add_item(image)
    win.show()
    win.exec_()
    iofile = open(FNAME, "wb")
    pickle.dump(image, iofile)
