# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
PlotPy plot benchmark
---------------------

This script benchmarks PlotPy plotting features.


Results obtained with PlotPy v2.3.5 on Windows 11 with a i5-1335U CPU @ 1.30 GHz:

.. code-block:: none

    PlotPy plot benchmark [Python 3.12.3 64 bits, Qt 5.15.2, PyQt 5.15.10 on Windows]

            N | ∆t (ms) | Description
    --------------------------------------------------------------------------------
        5e+06 |     215 | Simple curve
        2e+05 |     774 | Curve with markers
        1e+06 |    2411 | Curve with sticks
        1e+04 |    2025 | Error bar curve (vertical bars only)
        1e+04 |     198 | Error bar curve (horizontal and vertical bars)
        1e+06 |     105 | Simple histogram
        1e+03 |     722 | Polar pcolor
        7e+03 |     902 | Simple image
"""

import time

import guidata
import numpy as np
import pytest
from guidata.env import execenv
from guidata.qthelpers import qt_app_context
from guidata.widgets import about
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.plot import PlotOptions, PlotWindow


class BaseBM:
    """Benchmark object"""

    MAKE_FUNC = make.curve  # to be overriden in subclasses
    WIN_TYPE = "auto"

    @classmethod
    def print_header(cls):
        """Print header for benchmark results"""
        execenv.print(f"PlotPy plot benchmark [{about.get_python_libs_infos()}]")
        execenv.print()
        table_header = (
            "N".rjust(10) + " | " + "∆t (ms)".rjust(7) + " | " + "Description"
        ).ljust(80)
        execenv.print(table_header)
        execenv.print("-" * len(table_header))

    def __init__(self, name, nsamples, **options):
        self.name = name
        self.nsamples = int(nsamples)
        self.options = options
        self._item = None

    def compute_data(self):
        raise NotImplementedError

    def make_item(self):
        data = self.compute_data()
        self._item = self.MAKE_FUNC(*data, **self.options)

    def add_to_plot(self, plot):
        assert self._item is not None
        plot.add_item(self._item)

    def start(self):
        # Create plot window
        win = PlotWindow(
            toolbar=True, title=self.name, options=PlotOptions(type=self.WIN_TYPE)
        )
        win.show()
        QW.QApplication.processEvents()
        plot = win.manager.get_plot()

        # Create item
        self.make_item()

        # Benchmarking
        t0 = time.time()
        self.add_to_plot(plot)
        plot.replot()  # Force replot
        QW.QApplication.processEvents()
        dt = (time.time() - t0) * 1e3

        row = f"{self.nsamples:10.0e} | {int(dt):7} | {self.name}"
        execenv.print(row)

        return win


class CurveBM(BaseBM):
    MAKE_FUNC = make.curve
    WIN_TYPE = "curve"

    def compute_data(self):
        x = np.linspace(-10, 10, self.nsamples)
        y = np.sin(np.sin(np.sin(x)))
        return x, y


class HistogramBM(CurveBM):
    MAKE_FUNC = make.histogram

    def compute_data(self):
        data = np.random.normal(size=int(self.nsamples))
        return (data,)


class ErrorBarBM(CurveBM):
    MAKE_FUNC = make.merror

    def __init__(self, name, nsamples, dx=False, **options):
        super().__init__(name, nsamples, **options)
        self.dx = dx

    def compute_data(self):
        x, y = super().compute_data()
        if not self.dx:
            return x, y, x / 100.0
        else:
            return x, y, x / 100.0, x / 20.0


class ImageBM(BaseBM):
    MAKE_FUNC = make.image
    WIN_TYPE = "image"

    def compute_data(self):
        data = np.zeros((int(self.nsamples), int(self.nsamples)), dtype=np.float32)
        m = 10
        step = int(self.nsamples / m)
        for i in range(m):
            for j in range(m):
                data[i * step : (i + 1) * step, j * step : (j + 1) * step] = i * m + j
        return (data,)


class PColorBM(BaseBM):
    MAKE_FUNC = make.pcolor
    WIN_TYPE = "image"

    def compute_data(self):
        N = self.nsamples
        r, th = np.meshgrid(np.linspace(1.0, 16, N), np.linspace(0.0, np.pi, N))
        x = r * np.cos(th)
        y = r * np.sin(th)
        z = 4 * th + r
        return x, y, z


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_benchmarks():
    """Run benchmark"""
    # Print(informations banner)
    BaseBM.print_header()

    _app = guidata.qapplication()

    # Run benchmarks
    persist = []
    with qt_app_context(exec_loop=True):
        for benchmark in (
            CurveBM("Simple curve", 5e6),
            CurveBM("Curve with markers", 2e5, marker="Ellipse", markersize=10),
            CurveBM("Curve with sticks", 1e6, curvestyle="Sticks"),
            ErrorBarBM("Error bar curve (vertical bars only)", 1e4),
            ErrorBarBM("Error bar curve (horizontal and vertical bars)", 1e4, dx=True),
            HistogramBM("Simple histogram", 1e6, bins=10000),
            PColorBM("Polar pcolor", 1e3),
            ImageBM("Simple image", 7e3, interpolation="antialiasing"),
        ):
            persist.append(benchmark.start())


if __name__ == "__main__":
    test_benchmarks()
