#!/usr/bin/python


"""Benchmark that animates a curve"""

import sys
import time

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPolygonF
from PyQt5.QtWidgets import QApplication

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType

NPOINTS = 500000
NB_FRAMES_FOR_MEAN_FPS = 10


class TestApp(QApplication):
    def __init__(self, argv):
        super(QApplication, self).__init__(argv)

        self.last_phase = 0
        self.last_time = time.time()
        self.count = 0

    def updateDataToDraw(self):
        self.last_phase = (self.last_phase + np.pi / 16) % (2 * np.pi)

        self.y[:] = np.sin(self.x + self.last_phase)
        size = len(self.x)
        polyline = QPolygonF(size)

        pointer = polyline.data()
        dtype, tinfo = np.single, np.finfo
        pointer.setsize(2 * size * tinfo(dtype).dtype.itemsize)
        memory = np.frombuffer(pointer, dtype)
        memory[: (size - 1) * 2 + 1 : 2] = self.x
        memory[1 : (size - 1) * 2 + 2 : 2] = self.y

        self.curve.setSamples(polyline)

        self.count = self.count + 1
        if self.count % NB_FRAMES_FOR_MEAN_FPS == 0:
            current_time = time.time()
            self.plot.set_title(
                "FPS : " + str(NB_FRAMES_FOR_MEAN_FPS / (current_time - self.last_time))
            )
            self.last_time = current_time


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    # --
    _app = TestApp(sys.argv)

    x = np.linspace(0.0, 4 * np.pi, NPOINTS)
    y = np.sin(x)
    curve = make.curve(x, y, color="b")
    _app.x = x
    _app.curve = curve
    _app.y = y

    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="PlotDialog test",
        options=dict(
            title="Title", xlabel="xlabel", ylabel="ylabel", type=PlotType.CURVE
        ),
    )
    plot = win.get_plot()
    plot.add_item(curve)
    plot.setAutoReplot()
    _app.plot = plot

    win.get_itemlist_panel().show()
    plot.set_items_readonly(False)

    timer = QTimer()
    timer.timeout.connect(_app.updateDataToDraw)
    timer.start(1)

    win.show()
    win.exec_()


if __name__ == "__main__":
    test()
