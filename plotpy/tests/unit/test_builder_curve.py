# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test PlotBuilder.curve parameters"""

import numpy as np
import pytest
from qtpy.QtCore import Qt
from qwt import QwtPlotCurve

from plotpy.builder import make


def show_item(qtbot, item, type="curve"):
    """Plot curve in a dialog"""
    win = make.dialog(type=type)
    plot = win.manager.get_plot()
    plot.add_item(item)
    win.show()
    qtbot.keyClick(win, Qt.Key_Enter)


_COLOR_TO_HEX = {"red": "#ff0000", "blue": "#0000ff"}


def _make_curve_style(shade, curvestyle, baseline):
    """Make curve with curve style parameters"""
    x = np.linspace(-10, 10, 200)
    y = np.sin(x)
    curve = make.curve(x, y, shade=shade, curvestyle=curvestyle, baseline=baseline)
    assert curve.baseline() == baseline
    brush = curve.brush()
    assert brush.color().alphaF() == pytest.approx(shade)
    assert curve.style() == getattr(QwtPlotCurve, curvestyle)
    return curve


@pytest.mark.parametrize("shade", [0])
@pytest.mark.parametrize("curvestyle", ["Lines", "Sticks", "Steps", "Dots", "NoCurve"])
@pytest.mark.parametrize("baseline", [0.0])
def test_builder_curve_curve_style(qtbot, shade, curvestyle, baseline):
    """Test curve parameters of curve() method"""
    curve = _make_curve_style(shade, curvestyle, baseline)
    show_item(qtbot, curve, "curve")


@pytest.mark.parametrize("shade", [0, 0.4, 1.0])
@pytest.mark.parametrize("curvestyle", ["Lines"])
@pytest.mark.parametrize("baseline", [0.0, 1.0])
def test_builder_curve_curve_shade_baseline(qtbot, shade, curvestyle, baseline):
    """Test curve parameters of curve() method"""
    curve = _make_curve_style(shade, curvestyle, baseline)
    show_item(qtbot, curve, "curve")


def _make_curve_linestyle(color, linestyle, linewidth):
    """Make curve with line parameters"""
    x = np.linspace(-10, 10, 200)
    y = np.sin(x)
    curve = make.curve(x, y, color=color, linestyle=linestyle, linewidth=linewidth)
    pen = curve.pen()
    assert pen.color().name() == _COLOR_TO_HEX[color]
    assert pen.style() == getattr(Qt, linestyle)
    assert pen.width() == linewidth
    return curve


@pytest.mark.parametrize("color", ["red"])
@pytest.mark.parametrize(
    "linestyle",
    ["SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine", "NoPen"],
)
@pytest.mark.parametrize("linewidth", [1, 2])
def test_builder_curve_line_style(qtbot, color, linestyle, linewidth):
    """Test line parameters of curve() method"""
    curve = _make_curve_linestyle(color, linestyle, linewidth)
    show_item(qtbot, curve, "curve")


@pytest.mark.parametrize("color", ["red", "blue"])
@pytest.mark.parametrize("linestyle", ["SolidLine"])
@pytest.mark.parametrize("linewidth", [1, 2])
def test_builder_curve_line_color(qtbot, color, linestyle, linewidth):
    """Test line parameters of curve() method"""
    curve = _make_curve_linestyle(color, linestyle, linewidth)
    show_item(qtbot, curve, "curve")


def _make_curve_marker(marker, markersize, markerfacecolor, markeredgecolor):
    """Make curve with marker parameters"""
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
    return curve


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
@pytest.mark.parametrize("markersize", [5])
@pytest.mark.parametrize("markerfacecolor", ["red"])
@pytest.mark.parametrize("markeredgecolor", ["blue"])
def test_builder_curve_marker_params_symbol(
    qtbot, marker, markersize, markerfacecolor, markeredgecolor
):
    """Test marker parameters of curve() methodg"""
    curve = _make_curve_marker(marker, markersize, markerfacecolor, markeredgecolor)
    show_item(qtbot, curve, "curve")


@pytest.mark.parametrize("marker", ["Cross"])
@pytest.mark.parametrize("markersize", [1, 5, 10])
@pytest.mark.parametrize("markerfacecolor", ["red", "blue"])
@pytest.mark.parametrize("markeredgecolor", ["red", "blue"])
def test_builder_curve_marker_size_color(
    qtbot, marker, markersize, markerfacecolor, markeredgecolor
):
    """Test marker parameters of curve() methodg"""
    curve = _make_curve_marker(marker, markersize, markerfacecolor, markeredgecolor)
    show_item(qtbot, curve, "curve")
