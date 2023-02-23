# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Renders a cross section chosen by a cross marker"""


import os

import numpy as np

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType

SHOW = True  # Show test in GUI-based test launcher


def create_window():
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="Cross sections test",
        options=dict(
            show_xsection=True,
            show_ysection=True,
            show_itemlist=True,
            type=PlotType.IMAGE,
        ),
    )
    win.resize(800, 600)
    return win


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    win = create_window()
    image = make.image(filename=filename, colormap="bone")
    data2 = np.array(image.data.T[200:], copy=True)
    image2 = make.image(data2, title="Modified", alpha_mask=True)
    plot = win.manager.get_plot()
    plot.add_item(image)
    plot.add_item(image2, z=1)
    win.exec_()


if __name__ == "__main__":
    test()
