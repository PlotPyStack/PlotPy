# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Simple filter testing application based on PyQt and plotpy
filtertest1.py + plot manager"""

# guitest: show

import numpy as np
import scipy.ndimage as spi
import scipy.signal as sps
from guidata.configtools import get_icon
from guidata.qthelpers import qt_app_context, win32_fix_title_bar_background
from qtpy import QtWidgets as QW

import plotpy.config  # Loading icons
from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import BasePlot, PlotManager, PlotType


class FilterTestWidget(QW.QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    """

    def __init__(self, parent, x, y, func):
        QW.QWidget.__init__(self, parent)
        self.setMinimumSize(320, 200)
        self.x = x
        self.y = y
        self.func = func
        # ---plotpy related attributes:
        self.plot = None
        self.curve_item = None
        # ---

    def setup_widget(self, title):
        # ---Create the plot widget:
        self.plot = BasePlot(self, type=PlotType.CURVE)
        self.curve_item = make.curve([], [], color="b")
        self.plot.add_item(self.curve_item)
        self.plot.set_antialiasing(True)
        # ---

        button = QW.QPushButton("Test filter: {}".format(title))
        button.clicked.connect(self.process_data)
        vlayout = QW.QVBoxLayout()
        vlayout.addWidget(self.plot)
        vlayout.addWidget(button)
        self.setLayout(vlayout)

        self.update_curve()

    def process_data(self):
        self.y = self.func(self.y)
        self.update_curve()

    def update_curve(self):
        # ---Update curve
        self.curve_item.set_data(self.x, self.y)
        self.plot.replot()
        # ---


class WindowTest(QW.QMainWindow):
    def __init__(self):
        super().__init__()
        win32_fix_title_bar_background(self)
        self.setWindowTitle("Signal filtering 2 (plotpy)")
        self.setWindowIcon(get_icon("plotpy.svg"))

        hlayout = QW.QHBoxLayout()
        central_widget = QW.QWidget(self)
        central_widget.setLayout(hlayout)
        self.setCentralWidget(central_widget)
        # ---plotpy plot manager
        self.manager = PlotManager(self)
        # ---

    def add_plot(self, x, y, func, title):
        widget = FilterTestWidget(self, x, y, func)
        widget.setup_widget(title)
        self.centralWidget().layout().addWidget(widget)
        # ---Register plot to manager
        self.manager.add_plot(widget.plot)
        # ---

    def setup_window(self):
        # ---Add toolbar and register manager tools
        toolbar = self.addToolBar("tools")
        self.manager.add_toolbar(toolbar, id(toolbar))
        self.manager.register_all_curve_tools()
        # ---


def test_filtre2():
    """Testing this simple Qt/plotpy example"""
    x = np.linspace(-10, 10, 500)
    y = np.random.rand(len(x)) + 5 * np.sin(2 * x**2) / x
    with qt_app_context(exec_loop=True):
        win = WindowTest()
        win.add_plot(x, y, lambda x: spi.gaussian_filter1d(x, 1.0), "Gaussian")
        win.add_plot(x, y, sps.wiener, "Wiener")
        win.setup_window()
        win.show()


if __name__ == "__main__":
    test_filtre2()
