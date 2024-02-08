# -*- coding: utf-8 -*-
"""
ResizeDialog test
"""

# guitest: show

import pytest
from guidata.qthelpers import exec_dialog, qt_app_context
from qtpy import QtCore as QC
from qtpy.QtCore import Qt

from plotpy.widgets.resizedialog import ResizeDialog

size_list = [  # new_size, old_size, kepp_size, result[widtg, height, zoom]
    ((150, 100), (300, 200), False, (150, 100, 0.5)),
    ((800, 400), (200, 100), False, (800, 400, 4)),
    ((800, 400), (200, 100), True, (800, 400, 1)),
]


@pytest.mark.parametrize("new_size,old_size,keep_original_size,result", size_list)
def test_resize_dialog(new_size, old_size, keep_original_size, result):
    with qt_app_context():
        dialog = ResizeDialog(
            None, new_size, old_size, "Enter the new size:", keep_original_size
        )
        assert result[0] == dialog.width
        assert result[1] == dialog.height
        assert result[2] == dialog.get_zoom()
        assert dialog.keep_original_size is keep_original_size


def test_resize_dialog_qtbot_accept():
    with qt_app_context():
        result = (1500, 1000, 5)
        dialog = ResizeDialog(None, (150, 100), (300, 200), "Enter the new size:")
        dialog.show()
        dialog.w_edit.setText("1500")
        QC.QTimer.singleShot(10, dialog.accept)
        dialog.exec()
        assert result[0] == dialog.width
        assert result[1] == dialog.height
        assert result[2] == dialog.get_zoom()
        assert dialog.keep_original_size is False


def test_resize_dialog_qtbot_reject():
    with qt_app_context():
        result = (150, 100, 0.5)
        dialog = ResizeDialog(None, (150, 100), (300, 200), "Enter the new size:")
        dialog.show()
        exec_dialog(dialog)

        assert result[0] == dialog.width
        assert result[1] == dialog.height
        assert result[2] == dialog.get_zoom()
        assert dialog.keep_original_size is False


def simple_test():
    """ResizeDialog simple test"""
    with qt_app_context():
        dialog = ResizeDialog(None, (150, 100), (300, 250), "Enter the new size:")
        exec_dialog(dialog)


if __name__ == "__main__":
    simple_test()
