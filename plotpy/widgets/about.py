# -*- coding: utf-8 -*-
"""
about
=====

"""

from __future__ import annotations

import guidata
import qwt
from guidata.configtools import get_icon
from guidata.widgets import about as guidata_about
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow, QMessageBox

import plotpy
from plotpy.config import _


def get_python_libs_infos(addinfos: str = "") -> str:
    """Get Python and libraries information

    Args:
        addinfos: additional information to be displayed

    Returns:
        str: Python and libraries information
    """
    if addinfos:
        addinfos = ", " + addinfos
    addinfos = f"PlotPy {plotpy.__version__}{addinfos}"
    return guidata_about.get_python_libs_infos(addinfos)


def about(html: bool = True, copyright_only: bool = False) -> str:
    """Return text about this package

    Args:
        html: return html text. Defaults to True.
        copyright_only: if True, return only copyright

    Returns:
        str: text about this package
    """
    info = guidata_about.AboutInfo(
        name="PlotPy",
        version=plotpy.__version__,
        description=_("Set of tools for curve and image plotting."),
        author="Pierre Raybaut",
        year=2016,
        organization="PlotPyStack",
    )
    addinfos = f"guidata {guidata.__version__}, PythonQwt {qwt.__version__}"
    return info.about(html=html, copyright_only=copyright_only, addinfos=addinfos)


def show_about_dialog() -> None:
    """Show ``plotpy`` about dialog"""
    win = QMainWindow(None)
    win.setAttribute(Qt.WA_DeleteOnClose)
    win.hide()
    win.setWindowIcon(get_icon("plotpy.svg"))
    QMessageBox.about(win, _("About") + " PlotPy", about(html=True))
    win.close()
