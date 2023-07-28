# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Load/save items using Python's pickle protocol"""

# guitest: show

# WARNING:
# This script requires read/write permissions on current directory

import os

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.axes import Axes
from plotpy.core.tools.image import ImageMaskTool
from plotpy.core.tools.item import LoadItemsTool, SaveItemsTool
from plotpy.core.tools.shapes import PolygonShape


def build_items():
    """Build items"""
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


class LoadSaveDialog(PlotDialog):
    """Test dialog"""

    SIG_SAVE_RESTORE_ITEMS = QC.Signal()

    def __init__(self):
        super().__init__(
            edit=False,
            toolbar=True,
            wintitle="Load/save test",
            options=dict(
                title="Title", xlabel="xlabel", ylabel="ylabel", type=PlotType.IMAGE
            ),
        )
        self.manager.add_separator_tool()
        self.manager.add_tool(LoadItemsTool)
        self.manager.add_tool(SaveItemsTool)
        self.manager.add_tool(ImageMaskTool)
        self.manager.get_itemlist_panel().show()

    def populate_plot_layout(self) -> None:
        """Populate the plot layout"""
        super().populate_plot_layout()
        if not execenv.unattended:
            continue_btn = QW.QPushButton("Save and restore items")
            continue_btn.clicked.connect(lambda: self.SIG_SAVE_RESTORE_ITEMS.emit())
            self.add_widget(continue_btn)


class IOTest:
    """Base class for load/save items tests"""

    FNAME = None

    def __init__(self):
        self.dlg = None

    @property
    def plot(self):
        """Return the plot"""
        if self.dlg is not None:
            return self.dlg.manager.get_plot()

    def run(self):
        """Run test"""
        with qt_app_context(exec_loop=True):
            self.dlg = LoadSaveDialog()
            self.dlg.SIG_SAVE_RESTORE_ITEMS.connect(self.save_and_restore_items)
            print("Building items and add them to plotting canvas", end=" ")
            self.add_items()
            print("OK")
            self.dlg.show()
            if execenv.unattended:
                self.save_and_restore_items()
        print("Cleaning up...", end=" ")
        if os.path.isfile(self.FNAME):
            os.unlink(self.FNAME)
            print("OK")
        else:
            print("No file to clean up")

    def save_and_restore_items(self):
        """Save and restore items"""
        print("Saving items...", end=" ")
        self.save_items()
        print("OK")
        print("Remove items from plotting canvas...", end=" ")
        self.plot.del_all_items()
        print("OK")
        print("Restoring items...", end=" ")
        self.restore_items()
        print("OK")

    def add_items(self):
        """Add items to plotting canvas"""
        for item in build_items():
            self.plot.add_item(item)
        self.dlg.manager.get_itemlist_panel().show()
        self.plot.set_items_readonly(False)

    def restore_items(self):
        """Restore items"""
        raise NotImplementedError

    def save_items(self):
        """Save items"""
        raise NotImplementedError


class PickleTest(IOTest):
    """Test load/save items using Python's pickle protocol"""

    FNAME = "loadsavecanvas.pickle"

    def restore_items(self):
        """Restore items"""
        f = open(self.FNAME, "rb")
        self.plot.restore_items(f)

    def save_items(self):
        """Save items"""
        f = open(self.FNAME, "wb")
        self.plot.save_items(f)


def test_pickle():
    """Test load/save items using Python's pickle protocol"""
    test = PickleTest()
    test.run()


if __name__ == "__main__":
    test_pickle()
