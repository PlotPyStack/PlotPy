# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PlotDialog test"""

SHOW = True  # Show test in GUI-based test launcher

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make


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
    plot = win.get_plot()
    for item in items:
        plot.add_item(item)
    win.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    win.exec_()


def test():
    """Test"""
    # -- Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()
    # --
    from numpy import linspace, sin

    x = linspace(-10, 10, 200)
    y = sin(sin(sin(x)))
    plot(make.curve(x, y, color="b"))


if __name__ == "__main__":
    test()
