# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Plot computations test"""

# guitest: show

import numpy as np
import scipy.integrate as spt
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_computations():
    """Test computations"""
    x = np.linspace(-10, 10, 1000)
    y = np.sin(np.sin(np.sin(x)))
    with qt_app_context(exec_loop=True):
        curve = make.curve(x, y, "ab", "b")
        range = make.xrange(-2, 2)
        disp0 = make.range_info_label(
            range, "BR", "x = %.1f ± %.1f cm", title="Range info"
        )

        disp1 = make.computation(
            range, "BL", "trapz=%g", curve, lambda x, y: spt.trapezoid(y, x)
        )

        disp2 = make.computations(
            range,
            "TL",
            [
                (curve, "min=%.5f", lambda x, y: y.min()),
                (curve, "max=%.5f", lambda x, y: y.max()),
                (curve, "avg=%.5f", lambda x, y: y.mean()),
            ],
        )
        legend = make.legend("TR")
        _win = ptv.show_items(
            wintitle="Plot computations",
            items=[curve, range, disp0, disp1, disp2, legend],
            plot_type="curve",
        )


if __name__ == "__main__":
    test_computations()
