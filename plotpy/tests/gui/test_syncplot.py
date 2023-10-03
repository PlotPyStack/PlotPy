# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing plot with synchronized axes"""

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.config import _
from plotpy.plot import BasePlot, BasePlotOptions, SubplotWidget, set_widget_title_icon
from plotpy.plot.manager import PlotManager


class SyncPlotDialog(QW.QDialog):
    """Dialog demonstrating plot synchronization feature"""

    def __init__(self, parent=None):
        super().__init__(parent)
        set_widget_title_icon(self, self.__doc__, "plotpy.svg")

        self.manager = manager = PlotManager(None)
        manager.set_main(self)
        self.subplotwidget = spwidget = SubplotWidget(manager, parent=self)
        self.setLayout(QW.QVBoxLayout())
        toolbar = QW.QToolBar(_("Tools"))
        manager.add_toolbar(toolbar)
        self.layout().addWidget(toolbar)
        self.layout().addWidget(spwidget)

        spwidget.add_plot(BasePlot(self, BasePlotOptions(title="TL")), 0, 0, "1")
        spwidget.add_plot(BasePlot(self, BasePlotOptions(title="TR")), 0, 1, "2")
        spwidget.add_plot(BasePlot(self, BasePlotOptions(title="BL")), 1, 0, "3")
        spwidget.add_plot(BasePlot(self, BasePlotOptions(title="BR")), 1, 1, "4")

        spwidget.add_itemlist()

        manager.synchronize_axis(BasePlot.X_BOTTOM, ["1", "3"])
        manager.synchronize_axis(BasePlot.X_BOTTOM, ["2", "4"])
        manager.synchronize_axis(BasePlot.Y_LEFT, ["1", "2"])
        manager.synchronize_axis(BasePlot.Y_LEFT, ["3", "4"])

        self.manager.register_all_curve_tools()


def plot(items1, items2, items3, items4):
    """Plot items in SyncPlotDialog"""
    dlg = SyncPlotDialog()
    items = [items1, items2, items3, items4]
    for i, plot in enumerate(dlg.subplotwidget.plots):
        for item in items[i]:
            plot.add_item(item)
        plot.set_axis_font("left", QG.QFont("Courier"))
        plot.set_items_readonly(False)
    dlg.manager.get_panel("itemlist").show()
    dlg.show()
    dlg.exec_()


def test_syncplot():
    """Test plot synchronization"""
    with qt_app_context():
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
