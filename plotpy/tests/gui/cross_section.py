# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Renders a cross section chosen by a cross marker"""

SHOW = True  # Show test in GUI-based test launcher

import os.path as osp, numpy as np

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make


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
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    # --
    filename = osp.join(osp.dirname(__file__), "brain.png")
    win = create_window()
    image = make.image(filename=filename, colormap="bone")
    data2 = np.array(image.data.T[200:], copy=True)
    image2 = make.image(data2, title="Modified", alpha_mask=True)
    plot = win.get_plot()
    plot.add_item(image)
    plot.add_item(image2, z=1)
    win.exec_()


if __name__ == "__main__":
    test()
