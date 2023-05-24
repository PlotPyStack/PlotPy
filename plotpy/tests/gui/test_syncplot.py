# -*- coding: utf-8 -*-
#
# Copyright © 2010 CEA
# Ludovic Aubry
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotDialog test"""


# ===============================================================================
# todo: Make this test work!!
# ===============================================================================


import guidata
import numpy as np

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import (
    BasePlot,
    PlotDialog,
    PlotManager,
    PlotType,
    PlotWidget,
)

SHOW = False  # Show test in GUI-based test launcher


class MyPlotDialog(PlotDialog):
    def __init__(self, edit, toolbar, wintitle, options):
        super(MyPlotDialog, self).__init__(edit, toolbar, wintitle, options=options)
        self.create_plot(options)

    def create_plot(self, options):
        manager = PlotManager(None)
        self.plotwidget = PlotWidget(self, **options)
        manager.set_main(self.plotwidget)
        plot1 = BasePlot(title="TL", type=PlotType.CURVE)
        plot2 = BasePlot(title="TR", type=PlotType.CURVE)
        plot3 = BasePlot(title="BL", type=PlotType.CURVE)
        plot4 = BasePlot(title="BR", type=PlotType.CURVE)
        self.plotwidget.add_plot(plot1, 0, 0, "1")
        self.plotwidget.add_plot(plot2, 0, 1, "2")
        self.plotwidget.add_plot(plot3, 1, 0, "3")
        self.plotwidget.add_plot(plot4, 1, 1, "4")
        self.plotwidget.finalize()
        manager.synchronize_axis(BasePlot.X_BOTTOM, ["1", "3"])
        manager.synchronize_axis(BasePlot.X_BOTTOM, ["2", "4"])
        manager.synchronize_axis(BasePlot.Y_LEFT, ["1", "2"])
        manager.synchronize_axis(BasePlot.Y_LEFT, ["3", "4"])

        self.layout.addWidget(self.plotwidget, 0, 0)


def plot(items1, items2, items3, items4):
    win = MyPlotDialog(
        edit=False,
        toolbar=True,
        wintitle="PlotDialog test",
        options=dict(title="Title", xlabel="xlabel", ylabel="ylabel"),
    )
    items = [items1, items2, items3, items4]
    for i, plot in enumerate(win.plotwidget.plots):
        for item in items[i]:
            plot.add_item(item)
        plot.set_items_readonly(False)
    win.get_panel("itemlist").show()
    win.show()
    win.exec()


def nottest_syncplot():
    """Test"""
    # -- Create QApplication

    _app = guidata.qapplication()
    # --

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
            make.label("Relative position <i>inside</i>", (x[0], y[0]), (10, 10), "TL"),
        ],
        [
            make.merror(x, y / 2, dy),
            make.label("Absolute position", "R", (0, 0), "R"),
            make.legend("TR"),
        ],
    )


if __name__ == "__main__":
    test_syncplot()
