# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing `auto_tools` plot option"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.builder import make


def plot(*items):
    win = make.dialog(
        toolbar=True,
        auto_tools=False,
        wintitle="Plot test (no auto tools)",
    )
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    win.manager.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    return win


def test_no_auto_tools():
    """Test no auto tools"""

    x = linspace(-10, 10, 200)
    y = sin(sin(sin(x)))
    with qt_app_context(exec_loop=True):
        _persist_plot = plot(make.curve(x, y, color="b"))


if __name__ == "__main__":
    test_no_auto_tools()
