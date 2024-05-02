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

    # Performance should be the same with "1" and "2" scale factors:
    # (as of today, this is not the case, but it has to be fixed in the future:
    #  https://github.com/PlotPyStack/PlotPy/issues/10)
    os.environ["QT_SCALE_FACTOR"] = "2"

    x = np.linspace(-10, 10, 5000000)  # 5M points are needed to see the difference
    y = np.sin(np.sin(np.sin(x)))
    with qt_app_context(exec_loop=True):
        _win = ptv.show_items(
            [make.curve(x, y, color="b"), make.legend("TR")],
            wintitle=test_plot_highdpi.__doc__,
            title="Curves with high DPI",
            plot_type="curve",
        )


if __name__ == "__main__":
    test_plot_highdpi()
