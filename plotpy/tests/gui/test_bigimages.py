# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""PlotDialog test"""

# guitest: show

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.constants import PlotType
from plotpy.core.plot import PlotDialog


def imshow():
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="Displaying 10 big images test",
        options=dict(
            xlabel="Concentration", xunit="ppm", yunit="pixels", type=PlotType.IMAGE
        ),
    )

    plot = win.manager.get_plot()

    for i in range(10):
        plot.add_item(make.image(compute_image(i)))

    win.show()
    return win


def compute_image(i, N=7500, M=1750):
    if i % 2 == 0:
        N, M = M, N
    return (np.random.rand(N, M) * 65536).astype(np.int16)


def test_bigimages():
    """Test Bigimages"""
    with qt_app_context(exec_loop=True):
        _persist_obj = imshow()


if __name__ == "__main__":
    test_bigimages()
