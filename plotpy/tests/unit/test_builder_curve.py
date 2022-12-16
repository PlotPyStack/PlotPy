# -*- coding: utf-8 -*-
#
# Copyright © 2018 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Test PlotItemBuilder.curve parameters"""

import numpy as np
import pytest

from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.builder import make
from plotpy.gui.widgets.ext_gui_lib import Qt, QwtPlotCurve
from plotpy.gui.widgets.plot import PlotDialog


def plot_qtbot_curve(qtbot, curve):
    """Plot *curve* in a dialog managed by *qtbot*"""
    win = PlotDialog(options={"type": PlotType.CURVE})
    plot = win.get_plot()
    plot.add_item(curve)
    qtbot.addWidget(win)
    win.show()
    qtbot.keyClick(win, Qt.Key_Enter)


_COLOR_TO_HEX = {"red": "#ff0000", "blue": "#0000ff"}


@pytest.mark.parametrize("shade", [0, 0.4, 1.0])
@pytest.mark.parametrize("curvestyle", ["Lines", "Sticks", "Steps", "Dots", "NoCurve"])
@pytest.mark.parametrize("baseline", [0.0, 1.0])
def test_builder_curve_curve_params(qtbot, shade, curvestyle, baseline):
    """Test curve parameters of curve() method"""

    x = np.linspace(-10, 10, 200)
    y = np.sin(x)
    curve = make.curve(x, y, shade=shade, curvestyle=curvestyle, baseline=baseline)

    assert curve.baseline() == baseline
    brush = curve.brush()
    assert brush.color().alphaF() == pytest.approx(shade)
    assert curve.style() == getattr(QwtPlotCurve, curvestyle)
    plot_qtbot_curve(qtbot, curve)


@pytest.mark.parametrize("color", ["red", "blue"])
@pytest.mark.parametrize(
    "linestyle",
    ["SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine", "NoPen"],
)
@pytest.mark.parametrize("linewidth", [1, 2])
def test_builder_curve_line_params(qtbot, color, linestyle, linewidth):
    """Test line parameters of curve() method"""

    x = np.linspace(-10, 10, 200)
    y = np.sin(x)
    curve = make.curve(x, y, color=color, linestyle=linestyle, linewidth=linewidth)

    pen = curve.pen()
    assert pen.color().name() == _COLOR_TO_HEX[color]
    assert pen.style() == getattr(Qt, linestyle)
    assert pen.width() == linewidth
    plot_qtbot_curve(qtbot, curve)


@pytest.mark.parametrize(
    "marker",
    [
        "Cross",
        "Ellipse",
        "Star1",
        "XCross",
        "Rect",
        "Diamond",
        "UTriangle",
        "DTriangle",
        "RTriangle",
        "LTriangle",
        "Star2",
        "NoSymbol",
    ],
)
@pytest.mark.parametrize("markersize", [1, 5, 10])
@pytest.mark.parametrize("markerfacecolor", ["red", "blue"])
@pytest.mark.parametrize("markeredgecolor", ["red", "blue"])
def test_builder_curve_marker_params(
    qtbot, marker, markersize, markerfacecolor, markeredgecolor
):
    """Test marker parameters of curve() methodg"""

    x = np.linspace(-10, 10, 200)
    y = np.sin(x)
    curve = make.curve(
        x,
        y,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
    )

    symbol = curve.symbol()
    assert symbol.style() == getattr(type(symbol), marker)
    assert symbol.size().width() == markersize
    assert symbol.size().height() == markersize
    assert symbol.brush().color().name() == _COLOR_TO_HEX[markerfacecolor]
    assert symbol.pen().color().name() == _COLOR_TO_HEX[markeredgecolor]
    plot_qtbot_curve(qtbot, curve)
