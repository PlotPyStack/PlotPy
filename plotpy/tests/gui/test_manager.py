# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""PlotManager test"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context, win32_fix_title_bar_background
from qtpy import QtWidgets as QW

from plotpy.core.builder import make
from plotpy.core.panels.contrastadjustment import ContrastAdjustment
from plotpy.core.plot.manager import PlotManager
from plotpy.core.plot.plotwidget import BasePlot, PlotItemList, PlotType
from plotpy.tests.gui.test_image import compute_image


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
        super().__init__()
        win32_fix_title_bar_background(self)

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


def test_manager():
    """Test"""
    with qt_app_context(exec_loop=True):
        win = Window()
        win.show()


if __name__ == "__main__":
    test_manager()
