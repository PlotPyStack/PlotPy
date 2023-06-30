# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Image superposition test"""

# guitest: show

import os

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.axes import PlaceAxesTool
from plotpy.core.tools.shapes import EllipseTool, FreeFormTool, RectangleTool


def create_window():
    gridparam = make.gridparam(
        background="black", minor_enabled=(False, False), major_style=(".", "gray", 1)
    )
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="Region of interest (ROI) test",
        options=dict(gridparam=gridparam, type=PlotType.IMAGE),
    )
    for toolklass in (RectangleTool, EllipseTool, FreeFormTool, PlaceAxesTool):
        win.manager.add_tool(toolklass)
    return win


def test_imagesuperp():
    """Test image superposition"""

    filename = os.path.join(os.path.dirname(__file__), "brain.png")
    with qt_app_context(exec_loop=True):
        win = create_window()
        image1 = make.image(
            filename=filename, title="Original", alpha_mask=False, colormap="gray"
        )
        data2 = np.array(image1.data.T[200:], copy=True)
        image2 = make.image(data2, title="Modified")  # , alpha_mask=True)
        plot = win.manager.get_plot()
        plot.add_item(image1, z=0)
        plot.add_item(image2, z=1)
        plot.set_items_readonly(False)
        image2.set_readonly(True)
        win.manager.get_itemlist_panel().show()
        win.show()


if __name__ == "__main__":
    test_imagesuperp()
