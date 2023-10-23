# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing `auto_tools` plot option"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_no_auto_tools():
    """Test no auto tools"""
    x = linspace(-10, 10, 200)
    y = sin(sin(sin(x)))
    with qt_app_context(exec_loop=True):
        _win = ptv.show_items(
            [make.curve(x, y, color="b")],
            auto_tools=False,
            wintitle=test_no_auto_tools.__doc__,
        )


if __name__ == "__main__":
    test_no_auto_tools()
