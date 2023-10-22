# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
plotpy test package
===================
"""

import os.path as osp

from guidata.configtools import get_module_data_path

import plotpy

TESTDATAPATH = get_module_data_path("plotpy", osp.join("tests", "data"))


def get_path(filename: str) -> str:
    """Return absolute path of test file"""
    return osp.join(TESTDATAPATH, filename)


def run() -> None:
    """Run plotpy test launcher"""
    from guidata.guitest import run_testlauncher

    import plotpy.config  # load icons

    run_testlauncher(plotpy)


if __name__ == "__main__":
    run()
