# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Load/save items using Python's pickle protocol"""

# guitest: show

# WARNING:
# This script requires read/write permissions on current directory

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.items import Axes, PolygonShape
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests import get_path
from plotpy.tools import ImageMaskTool, LoadItemsTool, SaveItemsTool

if TYPE_CHECKING:
    from plotpy.plot import BasePlot


def build_items() -> list:
    """Build items"""
    x = np.linspace(-10, 10, 200)
    y = np.sin(np.sin(np.sin(x)))
    filename = get_path("brain.png")
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

    polypoints1 = np.array(
        [
            [150.0, 330.0],
            [270.0, 520.0],
            [470.0, 480.0],
            [520.0, 360.0],
            [460.0, 200.0],
            [250.0, 240.0],
        ]
    )
    polypoints2 = polypoints1 * 0.5

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
        make.annotated_polygon(polypoints2, "rc1", "tutu"),
        Axes((0, 0), (1, 0), (0, 1)),
        PolygonShape(polypoints1),
    ]
    return items


class LoadSaveDialog(PlotDialog):
    """Test dialog"""

    SIG_SAVE_RESTORE_ITEMS = QC.Signal()

    def __init__(self, title: str) -> None:
        super().__init__(
            edit=False,
            toolbar=True,
            title=title,
            options=PlotOptions(
                title="Title", xlabel="xlabel", ylabel="ylabel", type="image"
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

    FNAME: str = ""

    def __init__(self, title: str) -> None:
        self.title = title
        self.dlg = None

    @property
    def plot(self) -> BasePlot:
        """Get the plot object"""
        if self.dlg is None:
            raise RuntimeError("No dialog")
        return self.dlg.manager.get_plot()

    def run(self) -> None:
        """Run test"""
        with qt_app_context(exec_loop=True):
            self.dlg = LoadSaveDialog(self.title)
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

    def save_and_restore_items(self) -> None:
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

    def build_items(self) -> list:
        """Build items"""
        return build_items()

    def add_items(self) -> None:
        """Add items to plotting canvas"""
        for item in self.build_items():
            self.plot.add_item(item)
        self.dlg.manager.get_itemlist_panel().show()
        self.plot.set_items_readonly(False)

    def restore_items(self) -> None:
        """Restore items"""
        raise NotImplementedError

    def save_items(self) -> None:
        """Save items"""
        raise NotImplementedError


class PickleTest(IOTest):
    """Test load/save items using Python's pickle protocol"""

    FNAME = "loadsavecanvas.pickle"

    def restore_items(self) -> None:
        """Restore items"""
        with open(self.FNAME, "rb") as f:
            self.plot.restore_items(f)

    def save_items(self) -> None:
        """Save items"""
        self.plot.select_all()
        with open(self.FNAME, "wb") as f:
            self.plot.save_items(f, selected=True)


def test_pickle() -> None:
    """Test load/save items using Python's pickle protocol"""
    test = PickleTest("Load/save items using Python's pickle protocol")
    test.run()


if __name__ == "__main__":
    test_pickle()
