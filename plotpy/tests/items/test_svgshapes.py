# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test showing SVG shapes"""

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.tests import vistools as ptv


def test_svg():
    """Test showing SVG shapes"""
    with qt_app_context(exec_loop=True):
        path1, path2 = get_path("svg_tool.svg"), get_path("svg_target.svg")
        csvg = make.svg("circle", path2, 0, 0, 100, 100, "Circle")
        rsvg = make.svg("rectangle", path1, 150, 0, 200, 100, "Rect")
        ssvg = make.svg("square", path1, 0, 150, 100, 250, "Square")
        items = [csvg, rsvg, ssvg]
        _win = ptv.show_items(items, wintitle=test_svg.__doc__, lock_aspect_ratio=True)


if __name__ == "__main__":
    test_svg()
