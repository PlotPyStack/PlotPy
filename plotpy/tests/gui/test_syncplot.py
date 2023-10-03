# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing plot with synchronized axes"""


# ===============================================================================
# todo: Make this test work!!
# ===============================================================================


import guidata
import numpy as np

from plotpy.builder import make
from plotpy.plot import BasePlot, BasePlotOptions, PlotDialog, PlotOptions, PlotWidget
from plotpy.plot.manager import PlotManager


class MyPlotDialog(PlotDialog):
    def __init__(self, parent=None, toolbar=False, title="", options=None, edit=False):
        super().__init__(
            parent, toolbar=toolbar, options=options, edit=edit, title=title
        )
        self.create_plot(options)

    def create_plot(self, options):
        manager = PlotManager(None)
        self.plotwidget = PlotWidget(self, options=options)
        manager.set_main(self.plotwidget)
        plot_tl = BasePlot(options=BasePlotOptions(title="TL", type="curve"))
        plot_tr = BasePlot(options=BasePlotOptions(title="TR", type="curve"))
        plot_bl = BasePlot(options=BasePlotOptions(title="BL", type="curve"))
        plot_br = BasePlot(options=BasePlotOptions(title="BR", type="curve"))
        self.plotwidget.add_plot(plot_tl, 0, 0, "1")
        self.plotwidget.add_plot(plot_tr, 0, 1, "2")
        self.plotwidget.add_plot(plot_bl, 1, 0, "3")
        self.plotwidget.add_plot(plot_br, 1, 1, "4")
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
        title="Synchronized axes plot",
        options=PlotOptions(title="Title", xlabel="xlabel", ylabel="ylabel"),
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
    nottest_syncplot()
