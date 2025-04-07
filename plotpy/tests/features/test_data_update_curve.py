# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Testing curve plot with data update
====================================

The purpose of this test is to implement a simple use case where a curve is
updated in a loop. The curve is created with random data and the values are
updated in a loop. The test is successful if the curve is updated in the
plot window.
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


def get_data(variable_size: bool) -> tuple[np.ndarray, np.ndarray]:
    """Compute 1D Gaussian data and add a narrower Gaussian on top with a random
    position and amplitude."""
    size = np.random.randint(10, 200) if variable_size else 100
    amp = 0.3
    x, y = ptd.gen_1d_gaussian(size, sigma=10.0, x0=0.0, amp=amp)
    # Choose a random position: x0 has to be in the range [-10.0, 10.0]
    x0 = np.random.uniform(-10.0, 10.0)
    # Choose a random amplitude: a has to be in the range [0.1, 0.5]
    a = np.random.uniform(0.1, 0.7)
    # Add the narrower Gaussian on top
    y += ptd.gen_1d_gaussian(size, sigma=4.0, x0=x0, amp=a)[1]
    return x, y


class CurveUpdateDialog(PlotDialog):
    """Dialog box for curve update"""

    def __init__(
        self, title: str, variable_size: bool = False, auto_scale: bool = True
    ) -> None:
        self.variable_size = variable_size
        self.auto_scale = auto_scale
        options = PlotOptions(title="-", show_contrast=True, type="curve")
        super().__init__(title=title, toolbar=True, edit=False, options=options)
        self.resize(600, 600)
        self.timer = QC.QTimer()
        self.item = make.curve(
            *get_data(variable_size),
            color="blue",
            marker="o",
            markersize=5,
            markerfacecolor="cyan",
            markeredgecolor="blue",
        )
        plot = self.get_plot()
        plot.add_item(self.item)
        plot.set_active_item(self.item, select=False)
        self.counter = 0

    def populate_plot_layout(self) -> None:
        """Populate the plot layout with the item"""
        start_btn = QW.QPushButton("Start curve update")
        start_btn.clicked.connect(self.start_curve_update)
        self.add_widget(start_btn, 0, 0)
        stop_btn = QW.QPushButton("Stop curve update")
        stop_btn.clicked.connect(self.stop_curve_update)
        self.add_widget(stop_btn, 0, 1)
        variable_size_cb = QW.QCheckBox("Variable size")
        variable_size_cb.setChecked(self.variable_size)
        variable_size_cb.stateChanged.connect(self.toggle_variable_size)
        self.add_widget(variable_size_cb, 0, 2)
        auto_scale_cb = QW.QCheckBox("Auto scale")
        auto_scale_cb.setChecked(True)
        auto_scale_cb.stateChanged.connect(self.toggle_auto_scale)
        self.add_widget(auto_scale_cb, 0, 3)
        self.add_widget(self.plot_widget, 1, 0, 1, 0)

    def toggle_variable_size(self, state: int) -> None:
        """Toggle variable size"""
        self.variable_size = state == QC.Qt.Checked

    def toggle_auto_scale(self, state: int) -> None:
        """Toggle auto scale"""
        self.auto_scale = state == QC.Qt.Checked
        plot = self.get_plot()
        if self.auto_scale:
            plot.do_autoscale()

    def start_curve_update(self) -> None:
        """Start curve update"""
        self.timer.timeout.connect(self.update_curve)
        self.timer.start(100)

    def stop_curve_update(self) -> None:
        """Stop curve update"""
        self.timer.stop()

    def update_curve(self) -> None:
        """Update curve data"""
        data = get_data(self.variable_size)
        self.counter += 1
        plot = self.get_plot()
        self.item.set_data(data[0], data[1])
        plot.set_title(f"Curve update {self.counter:03d}")
        if self.auto_scale:
            plot.do_autoscale()
        else:
            plot.replot()

    def closeEvent(self, event: QG.QCloseEvent) -> None:
        """Close the dialog and stop the timer"""
        self.timer.stop()
        super().closeEvent(event)


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_curve_update() -> None:
    """Test curve update"""
    title = test_curve_update.__doc__
    with qt_app_context(exec_loop=False):
        dlg = CurveUpdateDialog(title)
        exec_dialog(dlg)


if __name__ == "__main__":
    test_curve_update()
