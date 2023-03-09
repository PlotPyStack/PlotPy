# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Flip/rotate test"""


from guidata.configtools import get_icon
from qtpy import QtWidgets as QW

from plotpy.tests.gui.test_rotatecrop import create_test_data, imshow
from plotpy.utils.misc_from_gui import add_actions, create_toolbutton
from plotpy.widgets import qapplication
from plotpy.widgets.fliprotate import FlipRotateDialog, FlipRotateWidget
from plotpy.widgets.tools.image import RotationCenterTool

SHOW = True  # Show test in GUI-based test launcher


def widget_test(fname, qapp):
    """Test the rotate/crop widget"""
    array0, item = create_test_data(fname)
    widget = FlipRotateWidget(None, toolbar=True)
    widget.tools.set_item(item)
    widget.set_parameters(-90, True, False)
    widget.show()
    qapp.exec_()


def dialog_test(fname, interactive=True):
    """Test the rotate/crop dialog with rotation point changeable"""
    array0, item = create_test_data(fname)
    dlg = FlipRotateDialog(None, toolbar=True)
    tool = dlg.manager.add_tool(
        RotationCenterTool,
        rotation_center=False,
        rotation_point_move_with_shape=True,
        on_all_items=True,
        toolbar_id=None,
    )
    action = tool.action

    rot_point_btn = create_toolbutton(
        dlg.imagewidget, icon=get_icon("rotationcenter.jpg")
    )
    rot_point_btn.setPopupMode(QW.QToolButton.InstantPopup)
    rotation_tool_menu = QW.QMenu(dlg.imagewidget)
    add_actions(rotation_tool_menu, (action,))
    rot_point_btn.setMenu(rotation_tool_menu)
    dlg.toolbar.addWidget(rot_point_btn)

    dlg.tools.set_item(item)
    if dlg.exec():
        array1 = dlg.tools.output_array
        imshow(array0, title="array0")
        imshow(array1, title="array1")


if __name__ == "__main__":
    qapp = qapplication()  # analysis:ignore

    widget_test("brain.png", qapp)
    dialog_test(fname="brain.png", interactive=True)
