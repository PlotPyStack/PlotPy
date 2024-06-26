# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Flip/rotate test"""

# guitest: show

from guidata.qthelpers import exec_dialog, qt_app_context
from qtpy import QtWidgets as QW

from plotpy.tests.widgets.test_rotatecrop import create_test_data, imshow
from plotpy.tools import RotationCenterTool
from plotpy.widgets.fliprotate import FlipRotateDialog, FlipRotateWidget


def widget_test(fname):
    """Test the flip/rotate widget"""
    array0, item = create_test_data(fname)
    widget = FlipRotateWidget(None, toolbar=True)
    widget.transform.set_item(item)
    widget.set_parameters(-90, True, False)
    widget.show()
    return widget


def dialog_test(fname):
    """Test the flip/rotate dialog with rotation point changeable"""
    array0, item = create_test_data(fname)
    dlg = FlipRotateDialog(None, toolbar=True)
    dlg.manager.add_tool(
        RotationCenterTool,
        rotation_center=False,
        rotation_point_move_with_shape=True,
        on_all_items=True,
    )
    dlg.transform.set_item(item)
    if exec_dialog(dlg) == QW.QDialog.Accepted:
        array1 = dlg.transform.get_result()
        dlg1 = imshow(array0, title="array0")
        dlg2 = imshow(array1, title="array1")
        return dlg, dlg1, dlg2


def test_flip_rotate():
    """Test the flip/rotate widget and dialog"""
    persist_list = []
    with qt_app_context(exec_loop=True):
        persist_list.append(widget_test("brain.png"))
    with qt_app_context(exec_loop=False):
        persist_list.append(dialog_test("brain.png"))


if __name__ == "__main__":
    test_flip_rotate()
