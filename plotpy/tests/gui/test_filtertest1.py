# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Simple filter testing application based on PyQt and plotpy"""


import numpy as np
import scipy.ndimage as spi
import scipy.signal as sps
from guidata.configtools import get_icon
from guidata.qthelpers import qt_app_context
from qtpy import QtWidgets as QW

import plotpy.config  # Loading icons
from plotpy.core.builder import make

# ---Import plot widget base class
from plotpy.core.plot.plotwidget import PlotType, PlotWidget

# guitest: show
# ---


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
        # ---plotpy curve item attribute:
        self.curve_item = None
        # ---

    def setup_widget(self, title):
        # ---Create the plot widget:
        curvewidget = PlotWidget(self, options={"type": PlotType.CURVE})
        curvewidget.manager.register_all_curve_tools()
        self.curve_item = make.curve([], [], color="b")
        curvewidget.plot.add_item(self.curve_item)
        curvewidget.plot.set_antialiasing(True)
        # ---

        button = QW.QPushButton("Test filter: {}".format(title))
        button.clicked.connect(self.process_data)
        vlayout = QW.QVBoxLayout()
        vlayout.addWidget(curvewidget)
        vlayout.addWidget(button)
        self.setLayout(vlayout)

        self.update_curve()

    def process_data(self):
        self.y = self.func(self.y)
        self.update_curve()

    def update_curve(self):
        # ---Update curve
        self.curve_item.set_data(self.x, self.y)
        self.curve_item.plot().replot()
        # ---


class WindowTest(QW.QWidget):
    def __init__(self):
        QW.QWidget.__init__(self)
        self.setWindowTitle("Signal filtering (plotpy)")
        self.setWindowIcon(get_icon("plotpy.svg"))
        hlayout = QW.QHBoxLayout()
        self.setLayout(hlayout)

    def add_plot(self, x, y, func, title):
        widget = FilterTestWidget(self, x, y, func)
        widget.setup_widget(title)
        self.layout().addWidget(widget)


def test_filtre1():
    """Testing this simple Qt/plotpy example"""
    x = np.linspace(-10, 10, 500)
    y = np.random.rand(len(x)) + 5 * np.sin(2 * x**2) / x
    with qt_app_context(exec_loop=True):
        win = WindowTest()
        win.add_plot(x, y, lambda x: spi.gaussian_filter1d(x, 1.0), "Gaussian")
        win.add_plot(x, y, sps.wiener, "Wiener")
        win.show()


if __name__ == "__main__":
    test_filtre1()
