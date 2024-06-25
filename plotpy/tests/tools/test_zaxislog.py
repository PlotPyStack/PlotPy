# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Z-axis log scale tool test"""

# guitest: show

from __future__ import annotations

import numpy as np
from guidata.qthelpers import qt_app_context, qt_wait

from plotpy.builder import make
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests.data import gen_2d_gaussian
from plotpy.tools import ZAxisLogTool


class MyPlotDialog(PlotDialog):
    def __init__(self) -> None:
        """Reimplement PlotDialog method"""
        super().__init__(
            title="Z-axis log scale tool test",
            toolbar=True,
            options=PlotOptions(type="image"),
        )
        # No need to add the tools to the manager, they are automatically added
        # when the `register_curve_tools` or `register_image_tools` method is called
        self.setup_items()

    def setup_items(self) -> None:
        """Setup items"""
        plot = self.get_plot()
        data = gen_2d_gaussian(512, np.uint16)
        item = make.image(data, title="Image", colormap="plasma")
        plot.add_item(item)
        plot.set_active_item(item)
        item.unselect()


def test_zaxislogtool() -> None:
    """Test the Z-axis log scale tool"""
    with qt_app_context(exec_loop=True):
        win = MyPlotDialog()
        win.show()
        tool = win.manager.get_tool(ZAxisLogTool)
        qt_wait(1, except_unattended=True)
        for _index in range(2):
            tool.activate()
            qt_wait(1, except_unattended=True)


if __name__ == "__main__":
    test_zaxislogtool()
