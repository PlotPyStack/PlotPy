# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotDialog test"""


SHOW = True  # Show test in GUI-based test launcher

import numpy as np

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make


def imshow():
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="Displaying 10 big images test",
        options=dict(
            xlabel="Concentration", xunit="ppm", yunit="pixels", type=PlotType.IMAGE
        ),
    )

    plot = win.get_plot()

    for i in range(10):
        plot.add_item(make.image(compute_image(i)))

    win.show()
    win.exec_()


def compute_image(i, N=7500, M=1750):
    if i % 2 == 0:
        N, M = M, N
    return (np.random.rand(N, M) * 65536).astype(np.int16)


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    # --

    imshow()


if __name__ == "__main__":
    test()
