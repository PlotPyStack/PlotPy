# -*- coding: utf-8 -*-
#
# Copyright © 2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# ((see plotpy/__init__.py for details))

# _process_mime_path and mimedata2url
# Origin: Spyder IDE 3.3.2, file spyder/utils/qthelper.py
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)


"""
plotpy.utils.qthelpers
----------------------------

The :py:mod:``.qthelpers`` module provides helper functions for developing
easily Qt-based graphical user interfaces with plotpy.

Ready-to-use open/save dialogs:
    :py:func:`.qthelpers.exec_image_save_dialog`
        Executes an image save dialog box (QFileDialog.getSaveFileName)
    :py:func:`.qthelpers.exec_image_open_dialog`
        Executes an image open dialog box (QFileDialog.getOpenFileName)
    :py:func:`.qthelpers.exec_images_open_dialog`
        Executes an image*s* open dialog box (QFileDialog.getOpenFileNames)

Reference
~~~~~~~~~

.. autofunction:: exec_image_save_dialog
.. autofunction:: exec_image_open_dialog
.. autofunction:: exec_images_open_dialog
"""
import os
import os.path as osp
import sys

from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.core import io

# from plotpy.widgets.dialog import (
#     get_open_filename,
#     get_open_filenames,
#     get_save_filename,
# )


# ===============================================================================
# Ready-to-use open/save dialogs
# ===============================================================================
def exec_image_save_dialog(parent, data, template=None, basedir="", app_name=None):
    """
    Executes an image save dialog box (QFileDialog.getSaveFileName)
        * parent: parent widget (None means no parent)
        * data: image pixel array data
        * template: image template (pydicom dataset) for DICOM files
        * basedir: base directory ('' means current directory)
        * app_name (opt.): application name (used as a title for an eventual
          error message box in case something goes wrong when saving image)

    Returns filename if dialog is accepted, None otherwise
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
    parent, basedir="", app_name=None, to_grayscale=True, dtype=None
):
    """
    Executes an image open dialog box (QFileDialog.getOpenFileName)
        * parent: parent widget (None means no parent)
        * basedir: base directory ('' means current directory)
        * app_name (opt.): application name (used as a title for an eventual
          error message box in case something goes wrong when saving image)
        * to_grayscale (default=True): convert image to grayscale

    Returns (filename, data) tuple if dialog is accepted, None otherwise
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
    parent, basedir="", app_name=None, to_grayscale=True, dtype=None
):
    """
    Executes an image*s* open dialog box (QFileDialog.getOpenFileNames)
        * parent: parent widget (None means no parent)
        * basedir: base directory ('' means current directory)
        * app_name (opt.): application name (used as a title for an eventual
          error message box in case something goes wrong when saving image)
        * to_grayscale (default=True): convert image to grayscale

    Yields (filename, data) tuples if dialog is accepted, None otherwise
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


def _process_mime_path(path, extlist):
    if path.startswith(r"file://"):
        if os.name == "nt":
            # On Windows platforms, a local path reads: file:///c:/...
            # and a UNC based path reads like: file://server/share
            if path.startswith(r"file:///"):  # this is a local path
                path = path[8:]
            else:  # this is a unc path
                path = path[5:]
        else:
            path = path[7:]
    path = path.replace("%5C", os.sep)  # Transforming backslashes
    if osp.exists(path):
        if extlist is None or osp.splitext(path)[1] in extlist:
            return path


def mimedata2url(source, extlist=None):
    """
    Extract url list from MIME data
    extlist: for example ('.py', '.pyw')
    """
    pathlist = []
    if source.hasUrls():
        for url in source.urls():
            path = _process_mime_path(str(url.toString()), extlist)
            if path is not None:
                pathlist.append(path)
    elif source.hasText():
        for rawpath in str(source.text()).splitlines():
            path = _process_mime_path(rawpath, extlist)
            if path is not None:
                pathlist.append(path)
    if pathlist:
        return pathlist
