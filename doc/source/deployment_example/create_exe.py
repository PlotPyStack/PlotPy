#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deployment example
==================

Deployment script using `plotpy.core.disthelpers` (py2exe or cx_Freeze)
"""

from guidata.disthelpers import Distribution

from plotpy.utils.packaging_helpers import add_plotpy


def create_exe():
    dist = Distribution()
    dist.setup(
        "example",
        "1.0",
        "plotpy app example",
        "simpledialog.pyw",
        excludes=["IPython", "tkinter", "scipy"],
    )
    if "plotpy" not in dist.module_import_func_dict.keys():
        dist.module_import_func_dict["plotpy"] = add_plotpy
    dist.add_modules("plotpy")
    dist.build_cx_freeze()  # use `build_py2exe` to use py2exe instead


if __name__ == "__main__":
    create_exe()
