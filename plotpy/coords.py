# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Plot coordinates
----------------

The :mod:`plotpy.coords` module provides functions to convert coordinates
between canvas and axes coordinates systems.

Reference
~~~~~~~~~

.. autofunction:: canvas_to_axes
.. autofunction:: axes_to_canvas
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qtpy.QtCore import QPointF
    from qwt import QwtPlot, QwtPlotItem


def canvas_to_axes(item: QwtPlotItem, pos: QPointF) -> tuple[float, float] | None:
    """Convert position from canvas coordinates system to axes coordinates

    Args:
        item: Plot item
        pos: Position in canvas coordinates system

    Returns:
        Position in axes coordinates system or None if item is None
    """
    if item is None:
        return None
    plot: QwtPlot = item.plot()
    ax, ay = item.xAxis(), item.yAxis()
    return plot.invTransform(ax, pos.x()), plot.invTransform(ay, pos.y())


def axes_to_canvas(item: QwtPlotItem, x: float, y: float) -> tuple[float, float] | None:
    """Convert (x,y) from axes coordinates to canvas coordinates system

    Args:
        item: Plot item
        x: X position in axes coordinates system
        y: Y position in axes coordinates system

    Returns:
        Position in canvas coordinates system or None if item is None
    """
    if item is None:
        return None
    plot: QwtPlot = item.plot()
    ax, ay = item.xAxis(), item.yAxis()
    return plot.transform(ax, x), plot.transform(ay, y)
