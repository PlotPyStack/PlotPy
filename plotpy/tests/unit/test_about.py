# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Python and libraries information shown by PlotPy (Issue #89)."""

from __future__ import annotations

import plotpy
from plotpy.tests.benchmarks.test_benchmarks import BaseBM
from plotpy.widgets.about import about, get_python_libs_info


def test_python_libs_info() -> None:
    """The information gives the versions of Python and PlotPy"""
    info = get_python_libs_info()
    assert info.startswith("Python ")
    assert f"PlotPy {plotpy.__version__}" in info
    assert f"PlotPy {plotpy.__version__}, extra" in get_python_libs_info("extra")


def test_about_text() -> None:
    """The about text gives the version of PlotPy"""
    assert plotpy.__version__ in about(html=False)


def test_benchmark_header() -> None:
    """The benchmark header (`plotpy-benchmarks`) can be printed"""
    BaseBM.print_header()


if __name__ == "__main__":
    test_python_libs_info()
    test_about_text()
    test_benchmark_header()
