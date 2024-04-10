# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Rotate/crop test: using the scaler C++ engine to rotate/crop images"""

# guitest: show

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import exec_dialog, qt_app_context
from qtpy import QtWidgets as QW

from plotpy import io
from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.widgets.rotatecrop import (
    MultipleRotateCropWidget,
    RotateCropDialog,
    RotateCropWidget,
)


def create_test_data(fname, func=None):
    """Create test data"""
    array0 = io.imread(get_path(fname), to_grayscale=True)
    if func is not None:
        array0 = func(array0)
    item0 = make.trimage(array0, dx=0.1, dy=0.1)
    return array0, item0


def widget_test(fname="brain.png"):
    """Test the rotate/crop widget"""
    _array0, item = create_test_data(fname)
    widget = RotateCropWidget(None, toolbar=True)
    widget.transform.set_item(item)
    widget.show()
    return widget


def multiple_widget_test(fname="brain.png"):
    """Test the multiple rotate/crop widget"""
    _array0, item0 = create_test_data(fname)
    _array1, item1 = create_test_data(fname, func=lambda arr: np.rot90(arr, 1))
    _array2, item2 = create_test_data(fname, func=lambda arr: np.rot90(arr, 2))
    widget = MultipleRotateCropWidget(None)
    widget.set_items(item0, item1, item2)
    widget.show()
    return widget


def imshow(data, title=None, hold=False):
    """Show image"""
    dlg = make.dialog(wintitle=title, type="image")
    dlg.manager.get_plot().add_item(make.image(data))
    if hold:
        dlg.show()
    else:
        exec_dialog(dlg)
    return dlg


def dialog_test(fname="brain.png"):
    """Test the rotate/crop dialog"""
    array0, item = create_test_data(fname)
    dlg = RotateCropDialog(None, toolbar=True)
    dlg.transform.set_item(item)
    if exec_dialog(dlg) == QW.QDialog.Accepted:
        array1 = dlg.transform.get_result()
        if array0.shape == array1.shape:
            assert (array1 == array0).all()
            imshow(array1 - array0, title="array1-array0")
        else:
            print(array0.shape, "-->", array1.shape)
        dlg1 = imshow(array0, title="array0")
        dlg2 = imshow(array1, title="array1")
        return dlg, dlg1, dlg2


def test_rotate_crop():
    """Test the flip/rotate widget and dialog"""
    persist_list = []
    with qt_app_context(exec_loop=not execenv.unattended):
        persist_list.append(multiple_widget_test("brain.png"))
    with qt_app_context(exec_loop=not execenv.unattended):
        persist_list.append(widget_test("brain.png"))
    with qt_app_context(exec_loop=False):
        persist_list.append(dialog_test("brain.png"))


if __name__ == "__main__":
    test_rotate_crop()
