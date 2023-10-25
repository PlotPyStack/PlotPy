# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve plotting test"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_plot():
    """Curve plotting test"""
    x = np.linspace(-10, 10, 200)
    dy = x / 100.0
    y = np.sin(np.sin(np.sin(x)))
    x2 = np.linspace(-10, 10, 20)
    y2 = np.sin(np.sin(np.sin(x2)))
    with qt_app_context(exec_loop=True):
        items = [
            make.curve(x, y, color="b"),
            make.curve(x2, y2, color="g", curvestyle="Sticks", title="toto"),
            make.curve(x, np.sin(2 * y), color="r"),
            make.merror(x, y / 2, dy),
            make.label(
                "Relative position <b>outside</b>", (x[0], y[0]), (-10, -10), "BR"
            ),
            make.label("Relative position <i>inside</i>", (x[0], y[0]), (10, 10), "TL"),
            make.label("Absolute position", "R", (0, 0), "R"),
            make.legend("TR"),
            make.marker(
                position=(5.0, 0.8),
                label_cb=lambda x, y: "A = %.2f" % x,
                markerstyle="|",
                movable=False,
            ),
        ]
        _win = ptv.show_items(
            items, wintitle=test_plot.__doc__, title="Curves", plot_type="curve"
        )


if __name__ == "__main__":
    test_plot()
