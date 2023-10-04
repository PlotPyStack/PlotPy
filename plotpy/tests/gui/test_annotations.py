# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""PlotDialog test"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def plot(*items, plot_type="auto"):
    title = "All annotation tools"
    if plot_type in ("curve", "image"):
        title = f"{plot_type.capitalize()} specialized plot annotation tools"
    win = ptv.show_items(items, plot_type=plot_type, wintitle=title, title=title)
    win.register_annotation_tools()
    return win


def test_annotation():
    """Test annotation"""
    x = linspace(-10, 10, 200)
    y = sin(sin(sin(x)))
    persist = []
    with qt_app_context(exec_loop=True):
        persist.append(plot(make.curve(x, y, color="b"), plot_type="curve"))
        persist.append(plot(make.image(ptd.gen_image1()), plot_type="image"))
        persist.append(plot(make.curve(x, y, color="b"), make.image(ptd.gen_image1())))


if __name__ == "__main__":
    test_annotation()
