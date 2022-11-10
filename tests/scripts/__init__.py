# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy test package
====================
"""

import plotpy.core

try:
    from tests.gui.guitest import run_testlauncher
except ImportError:
    from plotpy.tests.gui.guitest import run_testlauncher


def run():
    """Run plotpy.core test launcher"""

    run_testlauncher(plotpy.core, "tests.scripts")


if __name__ == "__main__":
    run()
