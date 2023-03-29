# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotDialog test"""


import numpy as np
from numpy import linspace, sin

import plotpy.widgets
from plotpy.env import execenv
from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.qthelpers_guidata import qt_app_context

SHOW = True  # Show test in GUI-based test launcher


def compute_image(N=2000, grid=True):
    T = np.float32
    x = np.array(np.linspace(-5, 5, N), T)
    img = np.zeros((N, N), T)
    x.shape = (1, N)
    img += x**2
    x.shape = (N, 1)
    img += x**2
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


def plot(*items):
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="PlotDialog test (curve and image)",
        options=dict(
            title="Title", xlabel="xlabel", ylabel="ylabel", type=PlotType.AUTO
        ),
    )
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    win.manager.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    return win


def test_auto_curve_image():
    """Test auto curve image"""

    x = linspace(0, 2000, 20000)
    y = (sin(sin(sin(x / 50))) - 1) * -1000
    with qt_app_context(exec_loop=True):
        _persist_obj = plot(
            make.image(compute_image()), make.curve(x, y, color="b"), make.legend("TR")
        )


if __name__ == "__main__":
    test_auto_curve_image()
