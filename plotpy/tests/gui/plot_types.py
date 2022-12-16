# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotTypes test"""

SHOW = True  # Show test in GUI-based test launcher

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make

import numpy as np


def compute_image(N=2000, grid=True):
    T = np.float32
    x = np.array(np.linspace(-5, 5, N), T)
    img = np.zeros((N, N), T)
    x.shape = (1, N)
    img += x ** 2
    x.shape = (N, 1)
    img += x ** 2
    np.cos(img, img)  # inplace cosine
    if not grid:
        return img
    x.shape = (N,)
    for k in range(-5, 5):
        i = x.searchsorted(k)
        if k < 0:
            v = -1.1
        else:
            v = 1.1
        img[i, :] = v
        img[:, i] = v
    m1, m2, m3, m4 = -1.1, -0.3, 0.3, 1.1
    K = 100
    img[:K, :K] = m1  # (0,0)
    img[:K, -K:] = m2  # (0,N)
    img[-K:, -K:] = m3  # (N,N)
    img[-K:, :K] = m4  # (N,0)
    # img = array( 30000*(img+1.1), uint16 )
    return img


def plot(*items, type=PlotType.AUTO, title=""):
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle=title,
        options=dict(title=title, xlabel="xlabel", ylabel="ylabel", type=type),
    )

    plot = win.get_plot()
    for item in items:
        plot.add_item(item)
    win.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    win.exec_()


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    # --
    from numpy import linspace, sin

    x = linspace(-10, 10, 200)
    y = sin(sin(sin(x)))

    plot(
        make.curve(x, y, color="b"),
        make.image(compute_image()),
        type=PlotType.CURVE,
        title="Curve specialized plot",
    )

    plot(
        make.curve(x, y, color="b"),
        make.image(compute_image()),
        type=PlotType.IMAGE,
        title="Image specialized plot",
    )

    plot(
        make.curve(x, y, color="b"),
        make.image(compute_image()),
        title="PlotType = AUTO with curve added first",
    )

    plot(
        make.image(compute_image()),
        make.curve(x, y, color="b"),
        title="PlotType = AUTO with image added first",
    )

    plot(
        make.curve(x, y, color="b"),
        make.image(compute_image()),
        type=PlotType.MANUAL,
        title="PlotType = MANUAL",
    )


if __name__ == "__main__":
    test()
