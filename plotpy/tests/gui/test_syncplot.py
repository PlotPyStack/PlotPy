# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing plot with synchronized axes"""

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.config import _
from plotpy.plot import BasePlot, BasePlotOptions, SubplotWidget, set_widget_title_icon
from plotpy.plot.manager import PlotManager


class SyncPlotWindow(QW.QMainWindow):
    """Dialog demonstrating plot synchronization feature"""

    def __init__(self, parent=None):
        super().__init__(parent)
        set_widget_title_icon(self, self.__doc__, "plotpy.svg")

        self.manager = mgr = PlotManager(None)
        mgr.set_main(self)

        self.toolbar = QW.QToolBar(_("Tools"), self)
        mgr.add_toolbar(self.toolbar, "default")
        self.toolbar.setMovable(True)
        self.toolbar.setFloatable(True)
        self.addToolBar(QC.Qt.TopToolBarArea, self.toolbar)

        self.subplotwidget = subplotw = SubplotWidget(mgr, parent=self)
        self.setCentralWidget(subplotw)

        p_opts = [("TL", 0, 0), ("TR", 0, 1), ("BL", 1, 0), ("BR", 1, 1)]
        for index, (title, row, col) in enumerate(p_opts):
            plot = BasePlot(self, BasePlotOptions(title=title))
            subplotw.add_plot(plot, row, col, str(index + 1))

        subplotw.configure_manager()

        mgr.synchronize_axis(BasePlot.X_BOTTOM, ["1", "3"])
        mgr.synchronize_axis(BasePlot.X_BOTTOM, ["2", "4"])
        mgr.synchronize_axis(BasePlot.Y_LEFT, ["1", "2"])
        mgr.synchronize_axis(BasePlot.Y_LEFT, ["3", "4"])

        mgr.register_all_curve_tools()

    def get_plots(self) -> list[BasePlot]:
        """Return the plots

        Returns:
            list[BasePlot]: The plots
        """
        return self.subplotwidget.get_plots()


def plot(items1, items2, items3, items4):
    """Plot items in SyncPlotDialog"""
    win = SyncPlotWindow()
    items = [items1, items2, items3, items4]
    for i, plot in enumerate(win.get_plots()):
        for item in items[i]:
            plot.add_item(item)
        plot.set_axis_font("left", QG.QFont("Courier"))
        plot.set_items_readonly(False)
    win.manager.get_panel("itemlist").show()
    win.show()


def test_syncplot():
    """Test plot synchronization"""
    with qt_app_context(exec_loop=True):
        x = np.linspace(-10, 10, 200)
        dy = x / 100.0
        y = np.sin(np.sin(np.sin(x)))
        x2 = np.linspace(-10, 10, 20)
        y2 = np.sin(np.sin(np.sin(x2)))
        plot(
            [
                make.curve(x, y, color="b"),
                make.label(
                    "Relative position <b>outside</b>", (x[0], y[0]), (-10, -10), "BR"
                ),
            ],
            [make.curve(x2, y2, color="g")],
            [
                make.curve(x, np.sin(2 * y), color="r"),
                make.label(
                    "Relative position <i>inside</i>", (x[0], y[0]), (10, 10), "TL"
                ),
            ],
            [
                make.merror(x, y / 2, dy),
                make.label("Absolute position", "R", (0, 0), "R"),
                make.legend("TR"),
            ],
        )


if __name__ == "__main__":
    test_syncplot()
