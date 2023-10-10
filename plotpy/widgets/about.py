# -*- coding: utf-8 -*-
"""
about
=====

"""

from __future__ import annotations

import guidata
import qwt
from guidata.widgets.about import get_general_infos
from qtpy.QtWidgets import QMessageBox, QWidget

import plotpy
from plotpy.config import _


def about(html: bool = True, copyright_only: bool = False) -> str:
    """Return text about this package

    Args:
        html: return html text. Defaults to True.
        copyright_only: if True, return only copyright

    Returns:
        str: text about this package
    """
    shortdesc = (
        f"Plotpy {plotpy.__version__}\n\n"
        f"Plotpy is a set of tools for curve and image plotting.\n"
        f"Created by Pierre Raybaut."
    )
    addinfos = f"guidata {guidata.__version__}, PythonQwt {qwt.__version__}"
    desc = get_general_infos(addinfos)
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
    QMessageBox.about(parent, _("About") + " plotpy", about(html=True))
