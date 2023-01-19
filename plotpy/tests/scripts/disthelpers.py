# -*- coding: utf-8 -*-
#
# Copyright © 2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.core.disthelpers demo

How to create an executable with py2exe or cx_Freeze with less efforts than
writing a complete setup script.

This test must be run from plotpy sources (the file packaging.py must be
present). CxFreeze or py2exe must be installed.
"""


import os

SHOW = True  # Show test in GUI-based test launcher

if os.name == "nt":
    try:
        from plotpy.utils.packaging_helpers import Distribution
    except ImportError:
        print(
            "disthelpers test is not shown because packaging.py, "
            "cx_freeze or py2exe are not available."
        )
        SHOW = False
else:
    SHOW = False


if __name__ == "__main__":
    dist = Distribution()
    dist.setup(
        name="Application demo",
        version="1.0.0",
        description="Application demo based on editgroupbox.py",
        script=os.path.join(os.path.dirname(__file__), "editgroupbox.py"),
        target_name="demo.exe",
    )
    dist.add_modules("plotpy")
    dist.build("cx_Freeze")
