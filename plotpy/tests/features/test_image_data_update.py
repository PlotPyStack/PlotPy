# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Testing image update
====================

The purpose of this test is to implement a simple use case where an image is
updated in a loop. The image is created with random data and the pixel values
are updated in a loop. The test is successful if the image is updated in the
plot window.

It is also a test for the "Update LUT range automatically" feature.
"""

# guitest: show

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import exec_dialog, qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests import data as ptd
from plotpy.tools import LockLUTRangeTool


def get_data(variable_size: bool) -> np.ndarray:
    """Compute 2D Gaussian data and add a narrower Gaussian on top with a random
    position and amplitude."""
    size = np.random.randint(50, 200) if variable_size else 100
    dtype = np.uint16
    amp = np.iinfo(dtype).max * 0.3
    data = ptd.gen_2d_gaussian(size, dtype, sigma=10.0, x0=0.0, y0=0.0, amp=amp)
    # Choose a random position: x0, y0 have to be in the range [-10.0, 10.0]
    x0 = np.random.uniform(-10.0, 10.0)
    y0 = np.random.uniform(-10.0, 10.0)
    # Choose a random amplitude: a has to be in the range [0.1, 0.5]
    a = np.random.uniform(0.1, 0.7) * np.iinfo(dtype).max
    # Add the narrower Gaussian on top
    data += ptd.gen_2d_gaussian(size, dtype, sigma=4.0, x0=x0, y0=y0, amp=a)
    return data


class ImageUpdateDialog(PlotDialog):
    """Dialog box for image update"""

    def __init__(self, title: str, variable_size: bool = False) -> None:
        self.variable_size = variable_size
        options = PlotOptions(title="-", show_contrast=True, type="image")
        super().__init__(title=title, toolbar=True, edit=False, options=options)
        self.resize(600, 600)
        self.timer = QC.QTimer()
        self.item = make.image(get_data(self.variable_size), interpolation="nearest")
        self.item.set_lut_range((15000, 28000))
        plot = self.get_plot()
        plot.add_item(self.item)
        plot.set_active_item(self.item, select=False)
        self.counter = 0
        self.keep_lut_cb: QW.QCheckBox | None = None

    def populate_plot_layout(self) -> None:
        """Populate the plot layout"""
        start_btn = QW.QPushButton("Start image update")
        start_btn.clicked.connect(self.start_image_update)
        self.add_widget(start_btn, 0, 0)
        stop_btn = QW.QPushButton("Stop image update")
        stop_btn.clicked.connect(self.stop_image_update)
        self.add_widget(stop_btn, 0, 1)
        self.keep_lut_cb = QW.QCheckBox()
        self.keep_lut_cb.setChecked(False)
        self.add_widget(self.keep_lut_cb, 0, 2)
        variable_size_cb = QW.QCheckBox("Variable size")
        variable_size_cb.setChecked(self.variable_size)
        variable_size_cb.stateChanged.connect(self.toggle_variable_size)
        self.add_widget(variable_size_cb, 0, 3)
        self.add_widget(self.plot_widget, 1, 0, 1, 0)

    def toggle_variable_size(self, state: int) -> None:
        """Toggle the variable size of the image"""
        self.variable_size = state == QC.Qt.Checked

    def register_tools(self) -> None:
        """Reimplement to connect the Keep LUT range checkbox to the item"""
        mgr = self.get_manager()
        keep_lut_tool = mgr.add_tool(LockLUTRangeTool)
        mgr.add_separator_tool()
        super().register_tools()
        keep_lut_tool.action.toggled.connect(self.keep_lut_cb.setChecked)
        self.keep_lut_cb.setText(keep_lut_tool.action.text())
        self.keep_lut_cb.setToolTip(keep_lut_tool.action.toolTip())
        self.keep_lut_cb.stateChanged.connect(keep_lut_tool.activate)

    def start_image_update(self) -> None:
        """Start updating the image"""
        self.timer.timeout.connect(self.update_image)
        self.timer.start(500)

    def stop_image_update(self) -> None:
        """Stop updating the image"""
        self.timer.stop()

    def update_image(self) -> None:
        """Update the image"""
        data = get_data(self.variable_size)
        self.counter += 1
        plot = self.get_plot()

        # Update the image data
        self.item.set_data(data)
        plot.update_colormap_axis(self.item)
        # Set item as active, again, to force the plot to update the LUT range
        plot.set_active_item(self.item, select=False)

        plot.set_title(f"Image update {self.counter:03d}")
        plot.replot()

    def closeEvent(self, event: QG.QCloseEvent) -> None:
        """Reimplement closeEvent to stop the timer before closing the dialog"""
        self.timer.stop()
        super().closeEvent(event)


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_image_update() -> None:
    """Testing image update"""
    title = test_image_update.__doc__
    with qt_app_context(exec_loop=False):
        dlg = ImageUpdateDialog(title)
        exec_dialog(dlg)


if __name__ == "__main__":
    test_image_update()
