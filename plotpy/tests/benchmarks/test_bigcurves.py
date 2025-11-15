# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve plotting test with large datasets"""

# guitest: show

import timeit

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def __create_curve(npts: int, linewidth: float):
    """Create a curve with random data"""
    x = np.linspace(-10, 10, npts)
    y = np.random.normal(size=npts)
    curve = make.curve(x, y, color="g", linewidth=linewidth)
    return curve


def __show_curve(curve, benchmark: bool = False):
    """Show the curve in a plot window"""
    with qt_app_context(exec_loop=not benchmark):
        _win = ptv.show_items(
            [curve],
            wintitle=test_curve_rendering_performance.__doc__,
            title="Curves",
            plot_type="curve",
            disable_readonly_for_items=False,
        )
        if benchmark:
            QW.QApplication.processEvents()
    return _win


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_interactive_curve_rendering(npts: int = 500000, linewidth: float = 1.0):
    """Interactive test for curve rendering with large datasets"""
    curve = __create_curve(npts, linewidth)
    _win = __show_curve(curve, benchmark=False)


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_curve_rendering_performance(npts: int = 500000, linewidth: float = 1.0):
    """Test curve rendering performance with large datasets"""
    curve = __create_curve(npts, linewidth)

    # Show once before benchmarking
    _win = __show_curve(curve, benchmark=True)

    # Benchmark with multiple runs
    n_runs = 5
    times = []

    print("Benchmarking in progress", end="")
    for i in range(n_runs):
        start_time = timeit.default_timer()
        _win = __show_curve(curve, benchmark=True)
        elapsed_time = timeit.default_timer() - start_time
        times.append(elapsed_time)
        print(".", end="", flush=True)
    print(" done.")

    # Display statistics
    print(
        f"Results ({n_runs} runs): {np.mean(times):.4f} ± {np.std(times):.4f} seconds"
    )


if __name__ == "__main__":
    # test_interactive_curve_rendering(10000, 2.0, False)
    # Test with different linewidths and antialiasing settings
    print("\n" + "=" * 70)
    print("Curve Rendering Performance Benchmark")
    print("=" * 70)

    print("\n--- Test 1: linewidth=1.0 ---")
    test_curve_rendering_performance(10000, 1.0)

    print("\n--- Test 2: linewidth=2.0 ---")
    test_curve_rendering_performance(10000, 2.0)
