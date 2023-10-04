# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Visualisation tools for plotpy tests"""

from __future__ import annotations

from typing import TYPE_CHECKING

from plotpy.builder import make

if TYPE_CHECKING:  # pragma: no cover
    from plotpy.items import BaseImageItem, CurveItem
    from plotpy.plot import PlotWindow


def show_items(
    items: list[CurveItem | BaseImageItem],
    plot_type: str = "auto",
    wintitle: str = "Plot items",
    title: str = "Title",
    xlabel: str = "X",
    ylabel: str = "Y",
    auto_tools: bool = True,
    lock_aspect_ratio: bool | None = None,
    curve_antialiasing: bool | None = None,
) -> PlotWindow:
    """Show plot items in a dialog box"""
    win = make.dialog(
        edit=False,
        toolbar=True,
        wintitle=wintitle,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        type=plot_type,
        auto_tools=auto_tools,
        lock_aspect_ratio=lock_aspect_ratio,
        curve_antialiasing=curve_antialiasing,
    )
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    win.manager.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    return win
