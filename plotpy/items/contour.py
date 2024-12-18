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

import guidata.dataset as gds
import numpy as np
from guidata.configtools import get_icon
from guidata.utils.misc import assert_interfaces_valid
from skimage import measure

from plotpy.config import _
from plotpy.items.shape.polygon import PolygonShape
from plotpy.styles import ShapeParam


class ContourLine(gds.DataSet):
    """A contour line"""

    vertices = gds.FloatArrayItem(_("Vertices"), help=_("Vertices of the line"))
    level = gds.FloatItem(_("Level"), help=_("Level of the line"))


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

    if isinstance(levels, np.ndarray):
        levels = np.asarray(levels, dtype=np.float64)
    else:
        levels = np.asarray([levels], dtype=np.float64)

    if X is None:
        delta_x, x_origin = 1.0, 0.0
    else:
        delta_x, x_origin = X[0, 1] - X[0, 0], X[0, 0]
    if Y is None:
        delta_y, y_origin = 1.0, 0.0
    else:
        delta_y, y_origin = Y[1, 0] - Y[0, 0], Y[0, 0]

    # Find contours in the binary image for each level
    clines = []
    for level in levels:
        for contour in measure.find_contours(Z, level):
            contour = contour.squeeze()
            if len(contour) > 1:  # Avoid single points
                line = np.zeros_like(contour, dtype=np.float32)
                line[:, 0] = contour[:, 1] * delta_x + x_origin
                line[:, 1] = contour[:, 0] * delta_y + y_origin
                cline = ContourLine.create(vertices=line, level=level)
                clines.append(cline)
    return clines


class ContourItem(PolygonShape):
    """Contour shape"""

    _readonly = True
    _can_select = True
    _can_resize = False
    _can_rotate = False
    _can_move = False
    _icon_name = "contour.png"

    def __init__(self, points=None, shapeparam=None):
        super().__init__(points, closed=True, shapeparam=shapeparam)


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

    contours = compute_contours(Z, levels, X, Y)
    for cline in contours:
        param = ShapeParam("Contour", icon="contour.png")
        item = ContourItem(points=cline.vertices, shapeparam=param)
        item.set_style("plot", "shape/contour")
        item.setTitle(_("Contour") + f"[Z={cline.level}]")
        items.append(item)
    return items
