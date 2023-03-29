# -*- coding: utf-8 -*-
#
# Copyright © 2018 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
DataItem groups and group selection

DataSet items may be included in groups (these items are then shown in group
box widgets in the editing dialog box) and item groups may be enabled/disabled
using one group parameter (a boolean item).
"""

import pytest
from guidata.dataset.qtitemwidgets import CheckBoxWidget, FloatSliderWidget, GroupWidget
from guidata.dataset.qtwidgets import DataSetEditDialog
from qtpy import QtCore as QC
from qtpy.QtWidgets import QApplication

from plotpy.tests.scripts.bool_selector import GroupSelection


def get_edit_dialog():
    top_level_widgets = QApplication.topLevelWidgets()
    for w in top_level_widgets:
        if isinstance(w, DataSetEditDialog):
            return w
    return None


def validate_edit_dialog(qtbot):
    """
    Closes QMessageBox's that can appear when testing.

    You can use this with QTimer to close a QMessageBox.
    Before calling anything that may show a QMessageBox call:
    QTimer.singleShot(1000, lambda: validate_edit_dialog(qtbot))
    """
    qtbot.keyClick(get_edit_dialog(), QC.Qt.Key_Enter)


@pytest.mark.skip(reason="Explose le framework en runtime")
def test_bool_selector(qtbot):
    """Test group selection when user doesn't not edit fields"""
    prm = GroupSelection()
    QC.QTimer.singleShot(500, lambda: validate_edit_dialog(qtbot))
    edited = prm.edit()
    assert edited
    assert not prm.enable1
    assert prm.enable2
    assert prm.param1_1 == 0
    assert prm.param1_2 == 0.93
    assert prm.param2_1 == 0
    assert prm.param2_2 == 0.93


@pytest.mark.skip(reason="Explose le framework en runtime")
def test_bool_selector_interaction(qtbot):
    """Test group selection when user:

    * activates the first checkbox
    * enters new values for param1_1 and param1_2
    * clicks on OK
    """
    prm = GroupSelection()
    dialog = DataSetEditDialog(prm)
    qtbot.addWidget(dialog)
    dialog.show()

    grp_widget = dialog.edit_layout[0].widgets[0]
    assert isinstance(grp_widget, GroupWidget)
    widgets = grp_widget.edit.widgets

    # Click on the "enable1" check box
    assert isinstance(widgets[0], CheckBoxWidget)
    qtbot.mouseClick(widgets[0].checkbox, QC.Qt.LeftButton)

    # Change values of param1_1 and param2_2
    assert isinstance(widgets[1], FloatSliderWidget)
    qtbot.keyClick(widgets[1].edit, QC.Qt.Key_Backspace)
    qtbot.keyClicks(widgets[1].edit, "2.3")
    assert isinstance(widgets[2], FloatSliderWidget)
    widgets[2].edit.setText("0.5")

    # Validate the dialog
    qtbot.keyClick(dialog, QC.Qt.Key_Enter)

    assert prm.enable1
    assert prm.enable2
    assert prm.param1_1 == 2.3
    assert prm.param1_2 == 0.5
    assert prm.param2_1 == 0
    assert prm.param2_2 == 0.93
