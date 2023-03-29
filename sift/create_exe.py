#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Setup script for distributing SIFT as a stand-alone executable
# SIFT is the Signal and Image Filtering Tool
# Simple signal and image processing application based on plotpy
# (see plotpy/tests/sift.py)

"""Create a stand-alone executable"""

import os
import pathlib
import sys

from plotpy.utils.packaging_helpers import Distribution

# Importing modules to be bundled
from sift import app

sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))


def create_executable():
    """Build executable using ``packaging.Distribution``"""

    dir_path = pathlib.Path(__file__).parent
    icon_path = str(dir_path / "sift.ico")
    script_path = os.path.join(dir_path, "run.pyw")
    dist = Distribution()
    dist.setup(
        name="Sift",
        version=app.VERSION,
        description="Signal and Image Filtering Tool",
        script=script_path,
        target_name="sift.exe",
        target_dir="{}-{}".format("Sift", app.VERSION),
        icon=icon_path,
    )
    dist.add_modules("plotpy", "tests", "scipy")
    dist.excludes += ["IPython", "tkinter", "scipy.spatial.cKDTree"]
    dist.excludes.remove("email")

    # Building executable
    dist.build("cx_Freeze", create_archive="move")


if __name__ == "__main__":
    create_executable()
