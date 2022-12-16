# -*- coding: utf-8 -*-
#
# Copyright © 2009-2019 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103


# ==============================================================================
# Utilities for plot items
# ==============================================================================


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
