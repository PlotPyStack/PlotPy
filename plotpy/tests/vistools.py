# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Visualisation tools for plotpy tests"""

from __future__ import annotations

from typing import TYPE_CHECKING

from plotpy.builder import make

if TYPE_CHECKING:
    from plotpy.items import BaseImageItem, CurveItem
    from plotpy.plot import PlotDialog


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
    show_itemlist: bool = True,
    show_contrast: bool = False,
    winsize: tuple[int, int] | None = None,
    disable_readonly_for_items: bool = True,
) -> PlotDialog:
    """Show plot items in a dialog box"""
    winsize = (640, 480) if winsize is None else winsize
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
        show_itemlist=show_itemlist,
        show_contrast=show_contrast,
        size=winsize,
    )
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    if disable_readonly_for_items:
        plot.set_items_readonly(False)
    win.show()
    return win
