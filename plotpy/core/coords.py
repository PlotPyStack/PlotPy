# -*- coding: utf-8 -*-

"""
plotpy.core.coords
------------------

The `coords` module provides functions to convert between coordinate systems.

Reference
~~~~~~~~~

.. autofunction:: canvas_to_axes
.. autofunction:: axes_to_canvas
"""


def canvas_to_axes(item, pos):
    """Convert (x,y) from canvas coordinates system to axes coordinates"""
    if item is None:
        return
    plot, ax, ay = item.plot(), item.xAxis(), item.yAxis()
    return plot.invTransform(ax, pos.x()), plot.invTransform(ay, pos.y())


def axes_to_canvas(item, x, y):
    """Convert (x,y) from axes coordinates to canvas coordinates system"""
    if item is None:
        return
    plot, ax, ay = item.plot(), item.xAxis(), item.yAxis()
    return plot.transform(ax, x), plot.transform(ay, y)
