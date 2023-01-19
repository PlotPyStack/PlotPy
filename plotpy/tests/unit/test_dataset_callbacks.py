# -*- coding: utf-8 -*-
#
# Copyright © 2018 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
Unit tests for callback option of DataSetItem
"""
from unittest import mock

from guidata.dataset.dataitems import StringItem
from guidata.dataset.datatypes import DataSet
from guidata.dataset.qtwidgets import DataSetEditDialog
from qtpy.QtCore import Qt

callback = mock.Mock(return_value=None)


class CallbackParameter(DataSet):

    string = StringItem("String", default="foobar").set_prop(
        "display", callback=callback
    )


def test_dataset_callback(qtbot):
    """Test callback option of DataSetItem"""

    tp = CallbackParameter()
    dialog = DataSetEditDialog(tp)
    qtbot.addWidget(dialog)
    dialog.show()

    callback.reset_mock()
    string_field = dialog.edit_layout[0].widgets[0]
    string_field.edit.setText("test")
    callback.assert_called_once_with(tp, CallbackParameter.string, "test")

    qtbot.keyClick(dialog, Qt.Key_Enter)
