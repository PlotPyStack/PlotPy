# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotDialog test"""


import numpy as np
from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType

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


def plot(*items, type=PlotType.AUTO):
    if type == PlotType.CURVE:
        title = "Curve specialized plot annotation tools"
    elif type == PlotType.IMAGE:
        title = "Image specialized plot annotation tools"
    else:
        title = "All annotation tools"
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle=title,
        options=dict(title="Title", xlabel="xlabel", ylabel="ylabel", type=type),
    )
    if type == PlotType.CURVE:
        win.manager.register_curve_annotation_tools()
    elif type == PlotType.IMAGE:
        win.manager.register_image_annotation_tools()
    else:
        win.manager.register_all_annotation_tools()

    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    win.manager.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    return win


def test_annotation():
    """Test annotation"""
    x = linspace(-10, 10, 200)
    y = sin(sin(sin(x)))
    persist = []
    with qt_app_context(exec_loop=True):
        persist.append(plot(make.curve(x, y, color="b"), type=PlotType.CURVE))
        persist.append(plot(make.image(compute_image()), type=PlotType.IMAGE))
        persist.append(plot(make.curve(x, y, color="b"), make.image(compute_image())))


if __name__ == "__main__":
    test_annotation()
