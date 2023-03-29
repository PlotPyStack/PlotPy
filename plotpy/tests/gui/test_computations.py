# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Plot computations test"""


from numpy import linspace, sin, trapz

from plotpy.widgets.builder import make
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.qthelpers_guidata import qt_app_context

SHOW = True  # Show test in GUI-based test launcher


def plot(*items):
    win = PlotDialog(edit=False, toolbar=True, options={"type": PlotType.CURVE})
    plot = win.manager.get_plot()
    for item in items:
        plot.add_item(item)
    win.show()
    return win


def test_computations():
    """Test computations"""

    x = linspace(-10, 10, 1000)
    y = sin(sin(sin(x)))
    with qt_app_context(exec_loop=True):
        curve = make.curve(x, y, "ab", "b")
        range = make.range(-2, 2)
        disp0 = make.range_info_label(
            range, "BR", "x = %.1f ± %.1f cm", title="Range infos"
        )

        disp1 = make.computation(
            range, "BL", "trapz=%g", curve, lambda x, y: trapz(y, x)
        )

        disp2 = make.computations(
            range,
            "TL",
            [
                (curve, "min=%.5f", lambda x, y: y.min()),
                (curve, "max=%.5f", lambda x, y: y.max()),
                (curve, "avg=%.5f", lambda x, y: y.mean()),
            ],
        )
        legend = make.legend("TR")
        _persist_obj = plot(curve, range, disp0, disp1, disp2, legend)


if __name__ == "__main__":
    test_computations()
