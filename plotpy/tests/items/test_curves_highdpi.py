# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve plotting test with high DPI"""

# guitest: show,skip

import os

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


@pytest.mark.skip(reason="This test is not relevant for the automated test suite")
def test_plot_highdpi():
    """Curve plotting test with high DPI"""

    # When setting the QT_SCALE_FACTOR to "2", performance is degraded, due to the
    # increased number of points to be drawn. As a workaround, we use the downsampling
    # feature to reduce the number of points to be drawn.
    # We also enable the antialiasing feature to improve the rendering of the curves,
    # which is also affected by the high DPI setting.
    # See https://github.com/PlotPyStack/PlotPy/issues/10
    os.environ["QT_SCALE_FACTOR"] = "2"

    npoints = 5000000  # 5M points are needed to see the difference
    dsamp_factor = npoints // 50000  # Max 50000 points to be drawn
    x = np.linspace(-10, 10, npoints)
    y = np.sin(np.sin(np.sin(x)))
    with qt_app_context(exec_loop=True):
        _win = ptv.show_items(
            [
                make.curve(x, y, color="b", dsamp_factor=dsamp_factor, use_dsamp=True),
                make.legend("TR"),
            ],
            curve_antialiasing=True,
            wintitle=test_plot_highdpi.__doc__,
            title="Curves with high DPI",
            plot_type="curve",
        )


if __name__ == "__main__":
    test_plot_highdpi()
