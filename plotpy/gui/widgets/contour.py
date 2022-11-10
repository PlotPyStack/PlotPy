# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.gui.widgets.contour
==========================

This module provides the :py:func:`.contour` function that computes contour lines.

.. autoclass:: ContourLine

.. autofunction:: contour
"""

import numpy as np

from plotpy.contour2d import contour_2d_grid, contour_2d_ortho


class ContourLine:
    """Class that contains line data

    .. py:attribute:: vertices

        Array of points

    .. py:attribute:: level

        lLevel used to generate this line
    """

    def __init__(self, vertices, level):
        self.vertices = vertices
        self.level = level


def contour(X, Y, Z, levels):
    """Compute a list of contour lines (:py:class:`.ContourLine`)

    Parameters

    X, Y : array-like, optional
        The coordinates of the values in *Z*.

        *X* and *Y* must both be 2-D with the same shape as *Z* (e.g.
        created via `numpy.meshgrid`), or they must both be 1-D such
        that ``len(X) == M`` is the number of columns in *Z* and
        ``len(Y) == N`` is the number of rows in *Z*.

        If none, they are assumed to be integer indices, i.e.
        ``X = range(M)``, ``Y = range(N)``.

    Z : array-like(N, M)
        The height values over which the contour is drawn.

    levels : float or array-like
        Determines the number and positions of the contour lines / regions.

        If a float, draw contour lines at this specified levels
        If array-like, draw contour lines at the specified levels.
        The values must be in increasing order.

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
        nx, = x.shape
        ny, = y.shape

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
            lines.append(ContourLine(points[start:index], levels[v]))
        start = index
    last_points = points[start:]
    if len(last_points) >= 2:
        lines.append(ContourLine(last_points, levels[v]))
    return lines
