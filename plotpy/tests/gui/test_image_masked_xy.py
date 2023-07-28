# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Masked Image test, creating the MaskedXYImageItem object via make.maskedxyimage

Masked image XY items are constructed using a masked array item. Masked data is
ignored in computations, like the average cross sections.
"""

# guitest: show

import os
import pickle

from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.image import ImageMaskTool

FNAME = "image_masked_xy.pickle"

# TODO: Rewrite the test so that it does not leave a file behind
# (do something like in test_loadsaveitems_pickle.py)


def test_image_masked_xy():
    with qt_app_context(exec_loop=True):
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
            fname = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "brain.png"
            )
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
            image = make.maskedimage(
                data=data, colormap="gray", show_mask=True, x=x, y=y
            )
        win.manager.get_plot().add_item(image)
        win.show()

    iofile = open(FNAME, "wb")
    pickle.dump(image, iofile)


if __name__ == "__main__":
    test_image_masked_xy()
