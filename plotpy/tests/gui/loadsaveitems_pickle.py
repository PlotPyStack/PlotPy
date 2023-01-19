# -*- coding: utf-8 -*-
#
# Copyright © 2009-2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Load/save items using Python's pickle protocol"""


# WARNING:
# This script requires read/write permissions on current directory

import os

import numpy as np

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.tools.axes import Axes
from plotpy.widgets.tools.image import ImageMaskTool
from plotpy.widgets.tools.item import LoadItemsTool, SaveItemsTool
from plotpy.widgets.tools.shapes import PolygonShape

SHOW = True  # Show test in GUI-based test launcher


def build_items():
    x = np.linspace(-10, 10, 200)
    y = np.sin(np.sin(np.sin(x)))
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    xydata = make._get_image_data(None, filename, "XY Brain Image", to_grayscale=True)[
        0
    ]

    x = [0]
    delta = 1
    for x_val in range(xydata.shape[0] - 1):
        delta = delta + 0.01
        x.append(x[-1] + delta)
    y = [0]
    for y_val in range(xydata.shape[1] - 1):
        delta = delta + 0.01
        y.append(y[-1] + delta)

    items = [
        make.curve(x, y, color="b"),
        make.image(filename=filename),
        make.trimage(filename=filename),
        make.maskedimage(
            filename=filename,
            colormap="gray",
            show_mask=True,
            xdata=[0, 40],
            ydata=[0, 50],
        ),
        make.maskedxyimage(data=xydata, colormap="gray", show_mask=True, x=x, y=y),
        make.label("Relative position <b>outside</b>", (x[0], y[0]), (-10, -10), "BR"),
        make.label("Relative position <i>inside</i>", (x[0], y[0]), (10, 10), "TL"),
        make.label("Absolute position", "R", (0, 0), "R"),
        make.legend("TR"),
        make.rectangle(-3, -0.8, -0.5, -1.0, "rc1"),
        make.segment(-3, -0.8, -0.5, -1.0, "se1"),
        make.ellipse(-10, 0.0, 0, 0, "el1"),
        make.annotated_rectangle(0.5, 0.8, 3, 1.0, "rc1", "tutu"),
        make.annotated_segment(-1, -1, 1, 1.0, "rc1", "tutu"),
        Axes((0, 0), (1, 0), (0, 1)),
        PolygonShape(
            np.array(
                [
                    [150.0, 330.0],
                    [270.0, 520.0],
                    [470.0, 480.0],
                    [520.0, 360.0],
                    [460.0, 200.0],
                    [250.0, 240.0],
                ]
            )
        ),
    ]
    return items


class IOTest(object):
    FNAME = None

    def __init__(self):
        self.dlg = None

    @property
    def plot(self):
        if self.dlg is not None:
            return self.dlg.get_plot()

    def run(self):
        """Run test"""
        self.create_dialog()
        self.add_items()
        self.dlg.exec_()
        print("Saving items...", end=" ")
        self.save_items()
        print("OK")

    def create_dialog(self):
        self.dlg = dlg = PlotDialog(
            edit=False,
            toolbar=True,
            wintitle="Load/save test",
            options=dict(
                title="Title", xlabel="xlabel", ylabel="ylabel", type=PlotType.IMAGE
            ),
        )
        dlg.add_separator_tool()
        dlg.add_tool(LoadItemsTool)
        dlg.add_tool(SaveItemsTool)
        dlg.add_tool(ImageMaskTool)

    def add_items(self):
        if os.access(self.FNAME, os.R_OK):
            print("Restoring items...", end=" ")
            self.restore_items()
            print("OK")
        else:
            for item in build_items():
                self.plot.add_item(item)
            print("Building items and add them to plotting canvas", end=" ")
        self.dlg.get_itemlist_panel().show()
        self.plot.set_items_readonly(False)

    def restore_items(self):
        raise NotImplementedError

    def save_items(self):
        raise NotImplementedError


class PickleTest(IOTest):
    FNAME = "loadsavecanvas.pickle"

    def restore_items(self):
        f = open(self.FNAME, "rb")
        self.plot.restore_items(f)

    def save_items(self):
        f = open(self.FNAME, "wb")
        self.plot.save_items(f)


if __name__ == "__main__":
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    test = PickleTest()
    test.run()
