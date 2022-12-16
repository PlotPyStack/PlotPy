# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
Masked Image test, creating the MaskedImageItem object via make.maskedimage

Masked image items are constructed using a masked array item. Masked data is
ignored in computations, like the average cross sections.
"""

import os, os.path as osp, pickle

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.tools import ImageMaskTool
from plotpy.gui.widgets.builder import make

SHOW = True  # Show test in GUI-based test launcher

FNAME = "image_masked.pickle"

if __name__ == "__main__":
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    win = PlotDialog(
        toolbar=True,
        wintitle="Masked image item test",
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
        image = make.maskedimage(
            filename=fname,
            colormap="gray",
            show_mask=True,
            xdata=[0, 20],
            ydata=[0, 25],
        )
    win.get_plot().add_item(image)
    win.show()
    win.exec_()
    iofile = open(FNAME, "wb")
    pickle.dump(image, iofile)
