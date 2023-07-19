# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
plotpy test package
===================
"""


def run():
    """Run plotpy test launcher"""
    from guidata.guitest import run_testlauncher

    import plotpy
    import plotpy.config  # Loading icons

    run_testlauncher(plotpy)


if __name__ == "__main__":
    run()
