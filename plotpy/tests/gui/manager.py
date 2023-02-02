# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotManager test"""


import os

from qtpy import QtWidgets as QW

from plotpy.widgets.builder import make
from plotpy.widgets.plot.histogram.contrastadjustment import ContrastAdjustment
from plotpy.widgets.plot.manager import PlotManager
from plotpy.widgets.plot.plotwidget import BasePlot, PlotItemList, PlotType

try:
    from tests.gui.image import compute_image
except ImportError:
    from plotpy.tests.gui.image import compute_image

SHOW = True  # Show test in GUI-based test launcher


class CentralWidget(QW.QWidget):
    def __init__(self, parent):
        QW.QWidget.__init__(self, parent)

        layout = QW.QGridLayout()
        self.setLayout(layout)

        self.plot1 = BasePlot(self, type=PlotType.IMAGE)
        layout.addWidget(self.plot1, 0, 0, 1, 1)
        self.plot2 = BasePlot(self, type=PlotType.IMAGE)
        layout.addWidget(self.plot2, 1, 0, 1, 1)

        self.contrast = ContrastAdjustment(self)
        layout.addWidget(self.contrast, 2, 0, 1, 2)
        self.itemlist = PlotItemList(self)
        layout.addWidget(self.itemlist, 0, 1, 2, 1)

        self.manager = PlotManager(self)
        for plot in (self.plot1, self.plot2):
            self.manager.add_plot(plot)
        for panel in (self.itemlist, self.contrast):
            self.manager.add_panel(panel)

    def register_tools(self):
        self.manager.register_all_image_tools()


class Window(QW.QMainWindow):
    def __init__(self):
        QW.QMainWindow.__init__(self)

        filename = os.path.join(os.path.dirname(__file__), "brain.png")
        image1 = make.image(filename=filename, title="Original", colormap="gray")

        image2 = make.image(compute_image())

        widget = CentralWidget(self)
        self.setCentralWidget(widget)

        widget.plot1.add_item(image1)
        widget.plot2.add_item(image2)

        toolbar = self.addToolBar("tools")
        widget.manager.add_toolbar(toolbar, id(toolbar))
        #        widget.manager.set_default_toolbar(toolbar)
        widget.register_tools()


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    win = Window()
    win.show()
    _app.exec_()


if __name__ == "__main__":
    test()
