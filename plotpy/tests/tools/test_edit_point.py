# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
SelectPointTool test

This plotpy tool provide a MATLAB-like "ginput" feature.
"""

# guitest: show

import qtpy.QtWidgets as QW
from guidata.qthelpers import exec_dialog, qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.config import _
from plotpy.interfaces.items import ICurveItemType
from plotpy.items.curve.base import CurveItem
from plotpy.plot.plotwidget import PlotDialog
from plotpy.tools import EditPointTool


def callback_function(tool: EditPointTool):
    # print("New arrays:", tool.get_arrays())
    print("Indexed changes:", tool.get_changes())


def make_new_bbox(dialog: PlotDialog):
    # new_bbox = QW.QDialogButtonBox(QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel)
    # bbox.accepted.connect(dialog.accept)
    # bbox.rejected.connect(dialog.reject)
    # dialog.button_layout.addWidget(bbox)
    if (
        dialog.button_box is not None
        and dialog.button_layout is not None
        and (tool := dialog.manager.get_tool(EditPointTool)) is not None
    ):
        custom_button = QW.QPushButton(_("Insert point"), dialog)
        custom_button.clicked.connect(tool.trigger_insert_point_at_selection)
        dialog.button_layout.insertWidget(0, custom_button)


def edit_curve(*args):
    """
    Plot curves and return selected point(s) coordinates
    """
    win: PlotDialog = make.dialog(
        wintitle=_("Select one point then press OK to accept"),
        edit=True,
        type="curve",
    )
    default = win.manager.add_tool(
        EditPointTool,
        title="Test",
        end_callback=callback_function,
    )
    default.activate()
    plot = win.manager.get_plot()
    for cx, cy in args[:-1]:
        item: CurveItem = make.mcurve(cx, cy)
        plot.add_item(item)
    item = make.mcurve(*args[-1], "r-+")
    plot.add_item(item)
    plot.set_active_item(item)
    plot.unselect_item(item)
    make_new_bbox(win)
    exec_dialog(win)
    return [curve.get_data() for curve in plot.get_items(item_type=ICurveItemType)]


def test_edit_curve():
    """Test"""
    with qt_app_context(exec_loop=False):
        x = linspace(-10, 10, num=100)
        y = 0.25 * sin(sin(sin(x * 0.5)))
        x2 = linspace(-10, 10, num=100)
        y2 = sin(sin(sin(x2)))
        edited_args = edit_curve((x, y), (x2, y2), (x, sin(2 * y)))
        edit_curve(*edited_args)
        print((y2 == edited_args[1][1]).all())


if __name__ == "__main__":
    test_edit_curve()
