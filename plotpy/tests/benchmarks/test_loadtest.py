# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Load test: instantiating a large number of image widgets"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

# import cProfile
# from pstats import Stats
from qtpy import QtWidgets as QW

from plotpy.builder import make


class PlotTab(QW.QWidget):
    """Tab containing a grid of image widgets"""

    def __init__(self):
        super().__init__()
        layout = QW.QGridLayout()
        self.setLayout(layout)

    def add_plot(self, iplt, irow, icol):
        """Add a plot to the grid"""
        widget = make.widget(self, title="Plot #%d" % (iplt + 1), type="image")
        widget.setMinimumSize(200, 150)
        xdata = np.linspace(-10, 10)
        ydata = np.sin(xdata + np.random.randint(0, 100) * 0.01 * np.pi)
        curve_item = make.curve(xdata, ydata, color="b")
        widget.plot.add_item(curve_item)
        self.layout().addWidget(widget, irow, icol, 1, 1)


class LoadTest(QW.QMainWindow):
    """Main window containing a tab widget with a large number of plots"""

    def __init__(self, nplots=150, ncols=6, nrows=5):
        super().__init__()
        self.tabw = QW.QTabWidget()
        self.setCentralWidget(self.tabw)
        irow, icol, itab = 0, 0, 0
        add_tab_at_next_step = True
        for iplt in range(nplots):
            if add_tab_at_next_step:
                plottab = self.add_tab(itab)
                add_tab_at_next_step = False
            plottab.add_plot(iplt, irow, icol)
            icol += 1
            if icol == ncols:
                icol = 0
                irow += 1
                if irow == nrows:
                    irow = 0
                    itab += 1
                    add_tab_at_next_step = True
                    self.refresh()

    def add_tab(self, itab):
        """Add a tab to the tab widget"""
        plottab = PlotTab()
        self.tabw.addTab(plottab, "Tab #%d" % (itab + 1))
        return plottab

    def refresh(self):
        """Force window to show up and refresh (for test purpose only)"""
        self.show()
        QW.QApplication.processEvents()


if __name__ == "__main__":
    with qt_app_context(exec_loop=True):
        app = QW.QApplication([])
        # import time
        # t0 = time.time()
        # with cProfile.Profile() as pr:
        win = LoadTest(nplots=60, ncols=6, nrows=5)
        win.show()
        # print((time.time() - t0))
        # with open('profiling_stats.txt', 'w') as stream:
        #     stats = Stats(pr, stream=stream)
        #     stats.strip_dirs()
        #     stats.sort_stats('cumulative')
        #     stats.dump_stats('.prof_stats')
        #     stats.print_stats()
