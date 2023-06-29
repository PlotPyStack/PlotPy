#!/usr/bin/python


"""Benchmark that animates a curve"""

import sys
import time

import numpy as np
import pytest
from guidata.env import execenv
from guidata.qthelpers import exec_dialog
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType

NPOINTS = 500000
NB_FRAMES_FOR_MEAN_FPS = 10


class AnimationApp(QW.QApplication):
    """Test application"""

    def __init__(self):
        super(QW.QApplication, self).__init__(sys.argv)

        self.x = None
        self.y = None
        self.curve = None
        self.plot = None

        self.last_phase = 0
        self.last_time = time.time()
        self.count = 0

        self.timer = QC.QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.plotdialog = PlotDialog(
            edit=False,
            toolbar=True,
            wintitle="PlotDialog test",
            options=dict(
                title="Title", xlabel="xlabel", ylabel="ylabel", type=PlotType.CURVE
            ),
        )

    def start_animation(self):
        """Start animation"""
        self.x = x = np.linspace(0.0, 4 * np.pi, NPOINTS)
        self.y = y = np.sin(x)
        self.curve = make.curve(x, y, color="b")
        self.plot = plot = self.plotdialog.manager.get_plot()
        plot.add_item(self.curve)
        plot.setAutoReplot()
        self.plotdialog.manager.get_itemlist_panel().show()
        plot.set_items_readonly(False)
        self.plotdialog.show()
        self.timer.start(1)

    def update_plot(self):
        """Update plot"""
        self.last_phase = (self.last_phase + np.pi / 16) % (2 * np.pi)
        self.y[:] = np.sin(self.x + self.last_phase)
        self.curve.set_data(self.x, self.y)
        self.count = self.count + 1
        if self.count % NB_FRAMES_FOR_MEAN_FPS == 0:
            current_time = time.time()
            self.plot.set_title(
                "FPS : " + str(NB_FRAMES_FOR_MEAN_FPS / (current_time - self.last_time))
            )
            self.last_time = current_time


@pytest.mark.skip(reason="Test not working with pytest")
def test_annimation():
    """Test"""
    app = AnimationApp()
    if execenv.unattended:
        return
    app.start_animation()
    exec_dialog(app.plotdialog)


if __name__ == "__main__":
    test_annimation()
