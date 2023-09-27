# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Contours
========

This module provides functions and classes to create contour curves.

.. autoclass:: ContourLine
   :members:

.. autofunction:: compute_contours

.. autoclass:: ContourItem
   :members:

.. autofunction:: create_contour_items
"""

from __future__ import annotations

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import dataitems as gdi
from guidata.dataset import datatypes as gdt
from guidata.utils.misc import assert_interfaces_valid

from plotpy.config import _
from plotpy.contour2d import contour_2d_grid, contour_2d_ortho
from plotpy.items.shapes.polygon import PolygonShape
from plotpy.styles import ShapeParam


class ContourLine(gdt.DataSet):
    """A contour line"""

    vertices = gdi.FloatArrayItem(_("Vertices"), help=_("Vertices of the line"))
    level = gdi.FloatItem(_("Level"), help=_("Level of the line"))


def compute_contours(
    Z: np.ndarray,
    levels: float | np.ndarray,
    X: np.ndarray | None = None,
    Y: np.ndarray | None = None,
) -> list[ContourLine]:
    """Create contour curves

    Args:
        Z: The height values over which the contour is drawn.
        levels : Determines the number and positions of the contour lines/regions.
         If a float, draw contour lines at this specified levels
         If array-like, draw contour lines at the specified levels.
         The values must be in increasing order.
        X: The coordinates of the values in *Z*.
         *X* must be 2-D with the same shape as *Z* (e.g. created via
         ``numpy.meshgrid``), or it must both be 1-D such that ``len(X) == M``
         is the number of columns in *Z*.
         If none, they are assumed to be integer indices, i.e. ``X = range(M)``.
        Y: The coordinates of the values in *Z*.
         *Y* must be 2-D with the same shape as *Z* (e.g. created via
         ``numpy.meshgrid``), or it must both be 1-D such that ``len(Y) == N``
         is the number of rows in *Z*.
         If none, they are assumed to be integer indices, i.e. ``Y = range(N)``.

    Returns:
        A list of :py:class:`ContourLine` instances.
    """
    z = np.asarray(Z, dtype=np.float64)
    if z.ndim != 2:
        raise TypeError("Input z must be a 2D array.")
    elif z.shape[0] < 2 or z.shape[1] < 2:
        raise TypeError("Input z must be at least a 2x2 array.")
    else:
        Ny, Nx = z.shape

    if X is None:
        X = np.arange(Nx)
    if Y is None:
        Y = np.arange(Ny)

    x = np.asarray(X, dtype=np.float64)
    y = np.asarray(Y, dtype=np.float64)

    if x.ndim != y.ndim:
        raise TypeError("Number of dimensions of x and y should match.")
    if x.ndim == 1:
        (nx,) = x.shape
        (ny,) = y.shape
        if nx != Nx:
            raise TypeError("Length of x must be number of columns in z.")
        if ny != Ny:
            raise TypeError("Length of y must be number of rows in z.")
    elif x.ndim == 2:
        if x.shape != z.shape:
            raise TypeError(
                "Shape of x does not match that of z: found "
                "{0} instead of {1}.".format(x.shape, z.shape)
            )
        if y.shape != z.shape:
            raise TypeError(
                "Shape of y does not match that of z: found "
                "{0} instead of {1}.".format(y.shape, z.shape)
            )
    else:
        raise TypeError("Inputs x and y must be 1D or 2D.")

    if isinstance(levels, np.ndarray):
        levels = np.asarray(levels, dtype=np.float64)
    else:
        levels = np.asarray([levels], dtype=np.float64)

    if x.ndim == 2:
        func = contour_2d_grid
    else:
        func = contour_2d_ortho

    lines = []
    points, offsets = func(z, x, y, levels)
    start = 0
    v = 0
    for v, index in offsets:
        if index - start >= 2:
            cline = ContourLine.create(vertices=points[start:index], level=levels[v])
            lines.append(cline)
        start = index
    last_points = points[start:]
    if len(last_points) >= 2:
        cline = ContourLine.create(vertices=last_points, level=levels[v])
        lines.append(cline)
    return lines


class ContourItem(PolygonShape):
    """Contour shape"""

    _readonly = True
    _can_select = True
    _can_resize = False
    _can_rotate = False
    _can_move = False

    def __init__(self, points=None, shapeparam=None):
        super().__init__(points, closed=True, shapeparam=shapeparam)
        self.setIcon(get_icon("contour.png"))


assert_interfaces_valid(ContourItem)


def create_contour_items(
    Z: np.ndarray,
    levels: float | np.ndarray,
    X: np.ndarray | None = None,
    Y: np.ndarray | None = None,
) -> list[ContourItem]:
    """Create contour items

    Args:
        Z: The height values over which the contour is drawn.
        levels : Determines the number and positions of the contour lines/regions.
         If a float, draw contour lines at this specified levels
         If array-like, draw contour lines at the specified levels.
         The values must be in increasing order.
        X: The coordinates of the values in *Z*.
         *X* must be 2-D with the same shape as *Z* (e.g. created via
         ``numpy.meshgrid``), or it must both be 1-D such that ``len(X) == M``
         is the number of columns in *Z*.
         If none, they are assumed to be integer indices, i.e. ``X = range(M)``.
        Y: The coordinates of the values in *Z*.
         *Y* must be 2-D with the same shape as *Z* (e.g. created via
         ``numpy.meshgrid``), or it must both be 1-D such that ``len(Y) == N``
         is the number of rows in *Z*.
         If none, they are assumed to be integer indices, i.e. ``Y = range(N)``.

    Returns:
        A list of :py:class:`.ContourItem` instances.
    """
    items = []
    lines = compute_contours(Z, levels, X, Y)
    for line in lines:
        param = ShapeParam("Contour", icon="contour.png")
        item = ContourItem(points=line.vertices, shapeparam=param)
        item.set_style("plot", "shape/contour")
        item.setTitle(_("Contour") + f"[Z={line.level}]")
        items.append(item)
    return items
