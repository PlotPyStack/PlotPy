# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Image file dialog helpers
-------------------------

Overview
^^^^^^^^

The :py:mod:``.imagefile`` module provides helper functions for opening and
saving image files using Qt dialogs and plotpy's I/O features.

Ready-to-use open/save dialogs:

    :py:func:`.imagefile.exec_image_save_dialog`
        Executes an image save dialog box (QFileDialog.getSaveFileName)
    :py:func:`.imagefile.exec_image_open_dialog`
        Executes an image open dialog box (QFileDialog.getOpenFileName)
    :py:func:`.imagefile.exec_images_open_dialog`
        Executes an image*s* open dialog box (QFileDialog.getOpenFileNames)

Reference
^^^^^^^^^

.. autofunction:: exec_image_save_dialog
.. autofunction:: exec_image_open_dialog
.. autofunction:: exec_images_open_dialog
"""

from __future__ import annotations

import os.path as osp
import sys

import numpy as np
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QWidget  # only to help intersphinx find QWidget

from plotpy.config import _
from plotpy.core import io


# ===============================================================================
# Ready-to-use open/save dialogs
# ===============================================================================
def exec_image_save_dialog(
    parent: QWidget,
    data: np.ndarray,
    template: dict | None = None,
    basedir: str = "",
    app_name: str | None = None,
) -> str | None:
    """Executes an image save dialog box (QFileDialog.getSaveFileName)

    Args:
        parent: parent widget (None means no parent)
        data: image pixel array data
        template: image template (pydicom dataset) for DICOM files
        basedir: base directory ('' means current directory)
        app_name: application name (used as a title for an eventual
         error message box in case something goes wrong when saving image)

    Returns:
        Filename if dialog is accepted, None otherwise
    """
    saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
    sys.stdout = None
    filename, _filter = QW.QFileDialog.getSaveFileName(
        parent,
        _("Save as"),
        basedir,
        io.iohandler.get_filters("save", dtype=data.dtype, template=template),
    )
    sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    if filename:
        filename = str(filename)
        kwargs = {}
        if osp.splitext(filename)[1].lower() == ".dcm":
            kwargs["template"] = template
        try:
            io.imwrite(filename, data, **kwargs)
            return filename
        except Exception as msg:
            import traceback

            traceback.print_exc()
            message = _("{filename} could not be written:\n{msg}").format(
                filename=osp.basename(filename), msg=msg
            )
            QW.QMessageBox.critical(
                parent, _("Error") if app_name is None else app_name, message
            )
            return


def exec_image_open_dialog(
    parent: QWidget,
    basedir: str = "",
    app_name: str | None = None,
    to_grayscale: bool = True,
    dtype: np.dtype | None = None,
) -> tuple[str, np.ndarray] | None:
    """Executes an image open dialog box (QFileDialog.getOpenFileName)

    Args:
        parent: parent widget (None means no parent)
        basedir: base directory ('' means current directory)
        app_name: application name (used as a title for an eventual
         error message box in case something goes wrong when saving image)
        to_grayscale (bool | None): convert image to grayscale
        dtype: data type of the image

    Returns:
        (filename, data) tuple if dialog is accepted, None otherwise
    """
    saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
    sys.stdout = None
    filename, _filter = QW.QFileDialog.getOpenFileName(
        parent, _("Open"), basedir, io.iohandler.get_filters("load", dtype=dtype)
    )
    sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    filename = str(filename)
    try:
        data = io.imread(filename, to_grayscale=to_grayscale)
    except Exception as msg:
        import traceback

        traceback.print_exc()
        message = _("{filename} could not be opened:\n{msg}").format(
            filename=osp.basename(filename), msg=msg
        )
        QW.QMessageBox.critical(
            parent, _("Error") if app_name is None else app_name, message
        )
        return
    return filename, data


def exec_images_open_dialog(
    parent: QWidget,
    basedir: str = "",
    app_name: str | None = None,
    to_grayscale: bool = True,
    dtype: np.dtype | None = None,
) -> list[tuple[str, np.ndarray]] | None:
    """Executes an image*s* open dialog box (QFileDialog.getOpenFileNames)

    Args:
        parent: parent widget (None means no parent)
        basedir: base directory ('' means current directory)
        app_name: application name (used as a title for an eventual
         error message box in case something goes wrong when saving image)
        to_grayscale (bool | None): convert image to grayscale
        dtype: data type

    Returns:
        (filename, data) tuples if dialog is accepted, None otherwise
    """
    saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
    sys.stdout = None
    filenames, _filter = QW.QFileDialog.getOpenFileNames(
        parent, _("Open"), basedir, io.iohandler.get_filters("load", dtype=dtype)
    )
    sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    filenames = [str(fname) for fname in list(filenames)]
    for filename in filenames:
        try:
            data = io.imread(filename, to_grayscale=to_grayscale)
        except Exception as msg:
            import traceback

            traceback.print_exc()
            message = _("{filename} could not be opened:\n{msg}").format(
                filename=osp.basename(filename), msg=msg
            )
            QW.QMessageBox.critical(
                parent, _("Error") if app_name is None else app_name, message
            )
            return
        yield filename, data
