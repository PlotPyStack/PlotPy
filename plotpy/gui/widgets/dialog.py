"""
Module dialog
=============

:synopsis: Contains pre-set dialog window

:moduleauthor: CEA

:platform: All

"""
# Natif import
import sys

from plotpy.gui.widgets.ext_gui_lib import QFileDialog


def get_open_filename(
    parent=None,
    caption="",
    basedir="",
    filters="",
    selectedfilter="",
    options=QFileDialog.ShowDirsOnly,
):
    """
    Wrapper around QFileDialog.getOpenFileNameAndFilter static method

    :param parent: The parent for modal mode
    :type parent: object
    :param caption:
    :type caption: str
    :param basedir: the path of the folder to display
    :type basedir: str
    :param filters: the filter to apply to the dialog
    :type filters: str
    :param selectedfilter:
    :type selectedfilter: str
    :param options: the mode to use for the dialog
    :type options: int
    :return: filename & selectedfilter; empty if dialog is canceled
    :rtype: tuple
    """
    return QFileDialog.getOpenFileName(
        parent, caption, basedir, filters, selectedfilter, options
    )


def get_open_filenames(
    parent=None,
    caption="",
    basedir="",
    filters="",
    selectedfilter="",
    options=QFileDialog.ShowDirsOnly,
):
    """
    Wrapper around QFileDialog.getOpenFileNamesAndFilter static method

    :param parent: The parent for modal mode
    :type parent: object
    :param caption:
    :type caption: str
    :param basedir: the path of the folder to display
    :type basedir: str
    :param filters: the filter to apply to the dialog
    :type filters: str
    :param selectedfilter:
    :type selectedfilter: str
    :param options: the mode to use for the dialog
    :type options: int
    :return: filename & selectedfilter; empty if dialog is canceled
    :rtype: tuple
    """
    return QFileDialog.getOpenFileNames(
        parent, caption, basedir, filters, selectedfilter, options
    )


def get_save_filename(
    parent=None,
    caption="",
    basedir="",
    filters="",
    selectedfilter="",
    options=QFileDialog.ShowDirsOnly,
):
    """
    Wrapper around QFileDialog.getSaveFileNameAndFilter static method

    :param parent: The parent for modal mode
    :type parent: object
    :param caption:
    :type caption: str
    :param basedir: the path of the folder to display
    :type basedir: str
    :param filters: the filter to apply to the dialog
    :type filters: str
    :param selectedfilter:
    :type selectedfilter: str
    :param options: the mode to use for the dialog
    :type options: int
    :return: filename & selectedfilter; empty if dialog is canceled
    :rtype: tuple
    """
    return QFileDialog.getSaveFileName(
        parent, caption, basedir, filters, selectedfilter, options
    )


def get_existing_directory(
    parent=None, caption="", basedir="", options=QFileDialog.ShowDirsOnly
):
    """Wrapper around QtGui.QFileDialog.getExistingDirectory static method
    Compatible with PyQt >=v4.4 (API #1 and #2)"""
    # Calling QFileDialog static method
    _temp1, _temp2 = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = None, None
    try:
        result = QFileDialog.getExistingDirectory(parent, caption, basedir, options)
    except Exception:
        result = None
    finally:
        # On Windows platforms: restore standard outputs
        sys.stdout, sys.stderr = _temp1, _temp2
    return result
