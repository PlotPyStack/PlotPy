# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Image superposition test"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.tools import EllipseTool, FreeFormTool, PlaceAxesTool, RectangleTool


def create_window():
    gridparam = make.gridparam(
        background="black", minor_enabled=(False, False), major_style=(".", "gray", 1)
    )
    win = make.dialog(
        toolbar=True,
        wintitle="Image superposition test",
        gridparam=gridparam,
        type="image",
        size=(800, 600),
    )
    for toolklass in (RectangleTool, EllipseTool, FreeFormTool, PlaceAxesTool):
        win.manager.add_tool(toolklass)
    return win


def test_imagesuperp():
    """Test image superposition"""
    filename = get_path("brain.png")
    with qt_app_context(exec_loop=True):
        win = create_window()
        image1 = make.image(filename=filename, title="Original", colormap="gray")
        data2 = np.array(image1.data[:, :150], copy=True)
        data2[:100] = data2[-100:] = 0
        image2 = make.image(data2, title="Modified", alpha_function="step")
        plot = win.manager.get_plot()
        plot.add_item(image1, z=0)
        plot.add_item(image2, z=1)
        plot.set_items_readonly(False)
        image2.set_readonly(True)
        win.manager.get_itemlist_panel().show()
        win.show()


if __name__ == "__main__":
    test_imagesuperp()
