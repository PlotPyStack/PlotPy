# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotDialog test"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import PlotDialog, PlotType


def plot(*items):
    win = PlotDialog(
        edit=False,
        toolbar=True,
        auto_tools=False,
        wintitle="PlotDialog test (no auto tools)",
        options=dict(
            title="Title", xlabel="xlabel", ylabel="ylabel", type=PlotType.CURVE
        ),
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
