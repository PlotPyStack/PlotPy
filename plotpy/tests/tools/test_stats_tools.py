# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve and Image Statistics tools tests"""

# guitest: show

from __future__ import annotations

from typing import TYPE_CHECKING, Type

import numpy as np
from guidata.qthelpers import create_toolbutton, execenv, qt_app_context

from plotpy.builder import make
from plotpy.config import _
from plotpy.constants import PlotType
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests.data import gen_image4
from plotpy.tests.unit.utils import drag_mouse
from plotpy.tools import (
    CurveStatsTool,
    ImageStatsTool,
    InteractiveTool,
    YRangeCursorTool,
)

if TYPE_CHECKING:
    from plotpy.items.image.base import BaseImageItem
    from plotpy.styles import BaseImageParam


class MyPlotDialog(PlotDialog):
    def __init__(self, type: PlotType, toolclass: Type[InteractiveTool]) -> None:
        """Reimplement PlotDialog method"""
        super().__init__(
            title=f"{type.name.lower().capitalize()} Statistics tools test",
            toolbar=True,
            options=PlotOptions(type=type),
        )
        self.toolclass = toolclass
        # No need to add the tools to the manager, they are automatically added
        # when the `register_curve_tools` or `register_image_tools` method is called
        self.setup_items()
        if execenv.unattended:
            self.simulate_stats_tool()

    def populate_plot_layout(self) -> None:
        """Populate the plot layout"""
        super().populate_plot_layout()
        options = self.plot_widget.options
        btn = create_toolbutton(
            self,
            None,
            f"Simulate {options.type.name.lower()} statistics tool",
            self.simulate_stats_tool,
        )
        self.add_widget(btn)

    def simulate_stats_tool(self) -> None:
        """Simulate the statistics tool"""
        tool = self.manager.get_tool(self.toolclass)
        tool.activate()
        drag_mouse(self, np.array([0.4, 0.8]), np.array([0.2, 0.7]))

    def setup_items(self) -> None:
        """Setup items"""
        plot = self.get_plot()
        if self.plot_widget.options.type is PlotType.CURVE:
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            item = make.curve(x, y, title="Curve")
        else:
            item = make.image(gen_image4(500, 500), title="Image", colormap="cool")
        plot.add_item(item)
        plot.select_item(item)


def test_curve_x_stats_tools() -> None:
    """Test CurveStatsTool"""
    with qt_app_context(exec_loop=True):
        win = MyPlotDialog(type=PlotType.CURVE, toolclass=CurveStatsTool)
        tool = win.manager.get_tool(CurveStatsTool)
        labelfuncs = (
            ("Mean = %g", lambda *args: np.mean(args[1])),
            ("Std = %g", lambda *args: np.std(args[1])),
            ("Max = %g", lambda *args: np.max(args[1])),
            ("Min = %g", lambda *args: np.min(args[1])),
        )
        tool.set_labelfuncs(labelfuncs)
        win.show()


def test_y_range_cursor_tool() -> None:
    """Test YRangeCursorTool"""
    with qt_app_context(exec_loop=True):
        win = MyPlotDialog(type=PlotType.CURVE, toolclass=YRangeCursorTool)
        tool = win.manager.get_tool(YRangeCursorTool)
        labelfuncs = (
            ("Mean = %g", lambda *args: np.mean(args[1])),
            ("Std = %g", lambda *args: np.std(args[1])),
            ("Max = %g", lambda *args: np.max(args[1])),
            ("Min = %g", lambda *args: np.min(args[1])),
        )
        tool.set_labelfuncs(labelfuncs)
        win.show()


# Note:
# -----
#
# Using the following `get_more_stats` function, the `ImageStatsTool` will display
# the surface, the sum and the density of the selected area - as additional stats
# if the `replace` parameter is set to `False` (default value).
#
# This is the way of reimplementing the old `show_surface` and `show_integral`
# arguments of the `ImageStatsTool` class in previous versions of PlotPy.


def get_more_stats(
    item: BaseImageItem,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> str:
    """Return formatted string with stats on image rectangular area
    (output should be compatible with AnnotatedShape.get_infos)

    Args:
        item: image item
        x0: X0
        y0: Y0
        x1: X1
        y1: Y1
    """
    ix0, iy0, ix1, iy1 = item.get_closest_index_rect(x0, y0, x1, y1)
    data = item.data[iy0:iy1, ix0:ix1]
    p: BaseImageParam = item.param
    xunit, yunit, zunit = p.get_units()
    infos = ""
    if xunit == yunit:
        surfacefmt = p.xformat.split()[0] + " " + xunit
        if xunit != "":
            surfacefmt = surfacefmt + "²"
        surface = abs((x1 - x0) * (y1 - y0))
        infos += _("surface = %s") % (surfacefmt % surface)
    integral = data.sum()
    integral_fmt = r"%.3e " + zunit
    infos = infos + "<br>" + _("sum = %s") % (integral_fmt % integral)
    if xunit == yunit and xunit is not None and zunit is not None:
        if surface != 0:
            density = integral / surface
            densityfmt = r"%.3e"
            if xunit and zunit:
                densityfmt += " " + zunit + "/" + xunit + "²"
            infos = infos + "<br>" + _("density = %s") % (densityfmt % density)
        else:
            infos = infos + "<br>" + _("density not computed : surface is null !")
    return infos


def test_image_stats_tools() -> None:
    """Test"""
    with qt_app_context(exec_loop=True):
        win = MyPlotDialog(type=PlotType.IMAGE, toolclass=ImageStatsTool)
        tool = win.manager.get_tool(ImageStatsTool)
        tool.set_stats_func(get_more_stats, replace=False)
        win.show()


if __name__ == "__main__":
    test_curve_x_stats_tools()
    test_y_range_cursor_tool()
    test_image_stats_tools()
