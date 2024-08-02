# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
EditPointTool test

This plotpy tool can be used to edit (move and/or add points) to a curve.
"""

# guitest: show

from __future__ import annotations

import numpy as np
from guidata.qthelpers import exec_dialog, qt_app_context
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.config import _
from plotpy.interfaces.items import ICurveItemType
from plotpy.plot.plotwidget import PlotDialog
from plotpy.tools import EditPointTool


def callback_function(tool: EditPointTool):
    """Callback function to be called by the tool after a point has moved

    Args:
        tool: EditPointTool instance that will use this callback
    """
    print("Indexed changes:", tool.get_changes())


def make_new_bbox(dialog: PlotDialog):
    """Add a new button to the dialog to insert a point at the current selection

    Args:
        dialog: PlotDialog instance
    """
    if (
        dialog.button_box is not None
        and dialog.button_layout is not None
        and (tool := dialog.manager.get_tool(EditPointTool)) is not None
    ):
        insert_btn = QW.QPushButton(_("Insert point"), dialog)
        insert_btn.clicked.connect(tool.trigger_insert_point_at_selection)
        dialog.button_layout.insertWidget(0, insert_btn)


def edit_curve(
    cdata: tuple[tuple[float, float], ...],
) -> tuple[tuple[float, float], ...]:
    """
    Plot curves and return selected point(s) coordinates

    Args:
        cdata: tuple of curves to plot

    Returns:
        tuple of modified curves
    """
    win: PlotDialog = make.dialog(
        wintitle=_("Select one point then press OK to accept"),
        edit=True,
        type="curve",
        size=(800, 600),
    )
    default = win.manager.add_tool(
        EditPointTool,
        title="Test",
        end_callback=callback_function,
    )
    default.activate()
    plot = win.manager.get_plot()
    for cx, cy in cdata[:-1]:
        item = make.mcurve(cx, cy)
        plot.add_item(item)
    item = make.mcurve(*cdata[-1], "r-+")
    plot.add_item(item)
    plot.set_active_item(item)
    plot.unselect_item(item)
    make_new_bbox(win)
    exec_dialog(win)
    return [curve.get_data() for curve in plot.get_items(item_type=ICurveItemType)]


def test_edit_curve() -> None:
    """Test"""
    with qt_app_context():
        x = np.linspace(-10, 10, num=100)
        y = 0.25 * np.sin(np.sin(np.sin(x * 0.5)))
        x2 = np.linspace(-10, 10, num=100)
        y2 = np.sin(np.sin(np.sin(x2)))
        new_cdata = edit_curve(((x, y), (x2, y2), (x, np.sin(2 * y))))
        edit_curve(new_cdata)
        print((y2 == new_cdata[1][1]).all())


if __name__ == "__main__":
    test_edit_curve()
