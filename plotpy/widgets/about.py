# -*- coding: utf-8 -*-
"""
about
=====

"""

import platform
import sys

from qtpy import QtCore as QC
from qwt import QWT_VERSION_STR

import plotpy


def about(html=True, copyright_only=False):
    """Return text about this package"""
    python_version = "{} {}".format(
        platform.python_version(), "64 bits" if sys.maxsize > 2**32 else "32 bits"
    )
    shortdesc = (
        f"Plotpy {plotpy.__version__}\n\n"
        f"Plotpy is a set of tools for curve and image plotting.\n"
        f"Created by Pierre Raybaut."
    )
    desc = (
        f"Copyright © 2023 CEA\n\nPython {python_version}, "
        f"Qt {QC.__version__}, PythonQwt {QWT_VERSION_STR} on {platform.system()}"
    )
    if not copyright_only:
        desc = f"{shortdesc}\n\n{desc}"
    if html:
        desc = desc.replace("\n", "<br />")
    return desc
