# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Histogram test"""


from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType

SHOW = True  # Show test in GUI-based test launcher


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
    plot = win.manager.get_plot()
    plot.add_item(make.histogram(data))
    win.show()
    win.exec_()


if __name__ == "__main__":
    # Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()

    test()
