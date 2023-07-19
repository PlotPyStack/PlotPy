# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Renders a cross section chosen by a cross marker"""

# guitest: show

import os

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType


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


def test_cross_section():
    """Test cross section"""
    with qt_app_context(exec_loop=True):
        filename = os.path.join(os.path.dirname(__file__), "brain.png")
        win = create_window()
        image = make.image(filename=filename, colormap="bone")
        data2 = np.array(image.data.T[200:], copy=True)
        image2 = make.image(data2, title="Modified", alpha_mask=True)
        plot = win.manager.get_plot()
        plot.add_item(image)
        plot.add_item(image2, z=1)


if __name__ == "__main__":
    test_cross_section()
