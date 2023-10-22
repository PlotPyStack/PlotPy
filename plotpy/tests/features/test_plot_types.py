# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""PlotTypes test"""

# guitest: show

from guidata.qthelpers import qt_app_context
from numpy import linspace, sin

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def test_plot_types():
    """Test plot types"""
    _persist = []
    with qt_app_context(exec_loop=True):
        x = linspace(-10, 10, 200)
        y = sin(sin(sin(x)))
        for plot_type in ("curve", "image", "auto", "manual"):
            for reverse in (True, False):
                revtxt = f"{'image' if reverse else 'curve'} added first"
                items = [
                    make.curve(x, y, color="b"),
                    make.image(ptd.gen_image1()),
                ]
                _persist.append(
                    ptv.show_items(
                        reversed(items) if reverse else items,
                        plot_type=plot_type,
                        wintitle=f"Plot type: '{plot_type}' ({revtxt})",
                    )
                )


if __name__ == "__main__":
    test_plot_types()
