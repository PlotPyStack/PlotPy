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
from plotpy.plot import BasePlot, PlotOptions, SubplotWidget, set_widget_title_icon
from plotpy.plot.manager import PlotManager
from plotpy.tests.data import gen_2d_gaussian


class SyncPlotWindow(QW.QMainWindow):
    """Window for showing plots, optionally synchronized"""

    def __init__(self, parent=None, title=None, options=None):
        super().__init__(parent)
        title = self.__doc__ if title is None else title
        set_widget_title_icon(self, title, "plotpy.svg")
        self.manager = PlotManager(None)
        self.manager.set_main(self)
        self.subplotwidget = SubplotWidget(self.manager, parent=self, options=options)
        self.setCentralWidget(self.subplotwidget)
        toolbar = QW.QToolBar(_("Tools"), self)
        self.manager.add_toolbar(toolbar, "default")
        toolbar.setMovable(True)
        toolbar.setFloatable(True)
        self.addToolBar(toolbar)

    def finalize_configuration(self):
        """Configure plot manager and register all tools"""
        self.subplotwidget.add_panels_to_manager()
        self.subplotwidget.register_tools()

    def rescale_plots(self):
        """Rescale all plots"""
        QW.QApplication.instance().processEvents()
        for plot in self.subplotwidget.plots:
            plot.do_autoscale()

    def showEvent(self, event):  # pylint: disable=C0103
        """Reimplement Qt method"""
        super().showEvent(event)
        QC.QTimer.singleShot(0, self.rescale_plots)

    def add_plot(self, row, col, plot, sync=False, plot_id=None):
        """Add plot to window"""
        if plot_id is None:
            plot_id = str(len(self.subplotwidget.plots) + 1)
        self.subplotwidget.add_plot(plot, row, col, plot_id)
        if sync and len(self.subplotwidget.plots) > 1:
            syncaxis = self.manager.synchronize_axis
            for i_plot in range(len(self.subplotwidget.plots) - 1):
                syncaxis(BasePlot.X_BOTTOM, [plot_id, f"{i_plot + 1}"])
                syncaxis(BasePlot.Y_LEFT, [plot_id, f"{i_plot + 1}"])

    def get_plots(self) -> list[BasePlot]:
        """Return the plots

        Returns:
            list[BasePlot]: The plots
        """
        return self.subplotwidget.get_plots()


def plot(plot_type, *itemlists):
    """Plot items in SyncPlotDialog"""
    win = SyncPlotWindow(options=PlotOptions(type=plot_type))
    row, col = 0, 0
    for items in itemlists:
        plot = BasePlot()
        for item in items:
            plot.add_item(item)
        plot.set_axis_font("left", QG.QFont("Courier"))
        plot.set_items_readonly(False)
        win.add_plot(row, col, plot, sync=True)
        col += 1
        if col == 2:
            row += 1
            col = 0
    win.finalize_configuration()
    if plot_type == "image":
        win.manager.get_contrast_panel().show()
    win.resize(800, 600)
    win.show()


def test_syncplot_curves():
    """Test plot synchronization: curves"""
    x = np.linspace(-10, 10, 200)
    dy = x / 100.0
    y = np.sin(np.sin(np.sin(x)))
    x2 = np.linspace(-10, 10, 20)
    y2 = np.sin(np.sin(np.sin(x2)))
    with qt_app_context(exec_loop=True):
        plot(
            "curve",
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


def test_syncplot_images():
    """Test plot synchronization: images"""
    img1 = gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=7, sigma=10.0)
    img2 = gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=5, sigma=8.0)
    img3 = gen_2d_gaussian(20, np.uint8, x0=-10, y0=-10, mu=3, sigma=6.0)
    with qt_app_context(exec_loop=True):

        def makeim(data):
            """Make image item"""
            return make.image(data, interpolation="nearest")

        plot("image", [makeim(img1)], [makeim(img2)], [makeim(img3)])


if __name__ == "__main__":
    test_syncplot_curves()
    test_syncplot_images()
