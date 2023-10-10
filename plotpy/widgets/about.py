# -*- coding: utf-8 -*-
"""
about
=====

"""

from __future__ import annotations

import guidata
import qwt
from guidata.widgets import about as guidata_about
from qtpy.QtWidgets import QMessageBox, QWidget

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
    shortdesc = (
        f"PlotPy {plotpy.__version__}\n\n"
        f"PlotPy is a set of tools for curve and image plotting.\n"
        f"Created by Pierre Raybaut."
    )
    addinfos = f"guidata {guidata.__version__}, PythonQwt {qwt.__version__}"
    desc = guidata_about.get_general_infos(addinfos)
    if not copyright_only:
        desc = f"{shortdesc}\n\n{desc}"
    if html:
        desc = desc.replace("\n", "<br />")
    return desc


def show_about_dialog(parent: QWidget) -> None:
    """Show ``plotpy`` about dialog

    Args:
        parent (QWidget): parent widget
    """
    QMessageBox.about(parent, _("About") + " PlotPy", about(html=True))
