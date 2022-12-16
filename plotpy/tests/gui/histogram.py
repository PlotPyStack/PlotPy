# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Histogram test"""

SHOW = True  # Show test in GUI-based test launcher

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make


def test():
    """Test"""
    from numpy.random import normal

    data = normal(0, 1, (2000,))
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="Histogram test",
        options={"type": PlotType.CURVE},
    )
    plot = win.get_plot()
    plot.add_item(make.histogram(data))
    win.show()
    win.exec_()


if __name__ == "__main__":
    # Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()

    test()
