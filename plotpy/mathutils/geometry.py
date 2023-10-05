# -*- coding: utf-8 -*-

"""
Basic geometry functions
------------------------

Overview
^^^^^^^^

The :py:mod:`.geometry` module provides basic geometry functions for
computing 2D transformations and distances.

The following functions are available:

* :py:func:`.translate`
* :py:func:`.scale`
* :py:func:`.rotate`
* :py:func:`.colvector`
* :py:func:`.vector_norm`
* :py:func:`.vector_projection`
* :py:func:`.vector_angle`
* :py:func:`.compute_center`
* :py:func:`.compute_rect_size`
* :py:func:`.compute_distance`
* :py:func:`.compute_angle`

Reference
^^^^^^^^^

.. autofunction:: translate
.. autofunction:: scale
.. autofunction:: rotate
.. autofunction:: colvector
.. autofunction:: vector_norm
.. autofunction:: vector_projection
.. autofunction:: vector_angle
.. autofunction:: compute_center
.. autofunction:: compute_rect_size
.. autofunction:: compute_distance
.. autofunction:: compute_angle
"""

# pylint: disable=C0103

from __future__ import annotations

import numpy as np

# ===============================================================================
# Transform matrix functions
# ===============================================================================


def translate(tx: float, ty: float) -> np.matrix:
    """Return translation matrix (NumPy matrix object)

    Args:
        tx: Translation along X-axis
        ty: Translation along Y-axis

    Returns:
        Translation matrix
    """
    return np.matrix([[1, 0, tx], [0, 1, ty], [0, 0, 1]], float)


def scale(sx: float, sy: float) -> np.matrix:
    """Return scale matrix (NumPy matrix object)

    Args:
        sx: Scale along X-axis
        sy: Scale along Y-axis

    Returns:
        Scale matrix
    """
    return np.matrix([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], float)


def rotate(alpha: float) -> np.matrix:
    """Return rotation matrix (NumPy matrix object)

    Args:
        alpha: Rotation angle (in radians)

    Returns:
        Rotation matrix
    """
    return np.matrix(
        [
            [np.cos(alpha), -np.sin(alpha), 0],
            [np.sin(alpha), np.cos(alpha), 0],
            [0, 0, 1],
        ],
        float,
    )


def colvector(x: float, y: float) -> np.matrix:
    """Return vector (NumPy matrix object) from coordinates

    Args:
        x: x-coordinate
        y: y-coordinate

    Returns:
        Vector (NumPy matrix object)
    """
    return np.matrix([x, y, 1]).T


# ===============================================================================
# Operations on vectors (from coordinates)
# ===============================================================================


def vector_norm(xa: float, ya: float, xb: float, yb: float) -> float:
    """Return vector norm

    Args:
        xa: x-coordinate of first point
        ya: y-coordinate of first point
        xb: x-coordinate of second point
        yb: y-coordinate of second point

    Returns:
        Norm of vector (xa, xb)-->(ya, yb)
    """
    return np.linalg.norm(np.array((xb - xa, yb - ya)))


def vector_projection(dv: np.ndarray, xa: float, ya: float, xb: float, yb: float):
    """Return vector projection

    Args:
        dv: vector to project
        xa: x-coordinate of first point
        ya: y-coordinate of first point
        xb: x-coordinate of second point
        yb: y-coordinate of second point

    Returns:
        Projection of *dv* on vector (xa, xb)-->(ya, yb)
    """
    assert dv.shape == (2,)
    v_ab = np.array((xb - xa, yb - ya))
    u_ab = v_ab / np.linalg.norm(v_ab)
    return np.vdot(u_ab, dv) * u_ab + np.array((xb, yb))


def vector_rotation(theta: float, dx: float, dy: float) -> tuple[float, float]:
    """Compute theta-rotation on vector

    Args:
        theta: Rotation angle
        dx: x-coordinate of vector
        dy: y-coordinate of vector

    Returns:
        Tuple of (x, y) coordinates of rotated vector
    """
    return np.array(rotate(theta) * colvector(dx, dy)).ravel()[:2]


def vector_angle(dx: float, dy: float) -> float:
    """Return vector angle with X-axis

    Args:
        dx: x-coordinate of vector
        dy: y-coordinate of vector

    Returns:
        Angle between vector and X-axis (in radians)
    """
    # sign(dy) ==  1 --> return Arccos()
    # sign(dy) ==  0 --> return  0 if sign(dx) ==  1
    # sign(dy) ==  0 --> return pi if sign(dx) == -1
    # sign(dy) == -1 --> return 2pi-Arccos()
    if dx == 0 and dy == 0:
        return 0.0
    else:
        sx, sy = np.sign(dx), np.sign(dy)
        acos = np.arccos(dx / np.sqrt(dx**2 + dy**2))
        return sy * (np.pi * (sy - 1) + acos) + np.pi * (1 - sy**2) * (1 - sx) * 0.5


# ===============================================================================
# Misc.
# ===============================================================================


def compute_center(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
    """Compute center of rectangle

    Args:
        x1: x-coordinate of top-left corner
        y1: y-coordinate of top-left corner
        x2: x-coordinate of bottom-right corner
        y2: y-coordinate of bottom-right corner

    Returns:
        Tuple of (x, y) coordinates of center
    """
    return 0.5 * (x1 + x2), 0.5 * (y1 + y2)


def compute_rect_size(
    x1: float, y1: float, x2: float, y2: float
) -> tuple[float, float]:
    """Compute rectangle size

    Args:
        x1: x-coordinate of top-left corner
        y1: y-coordinate of top-left corner
        x2: x-coordinate of bottom-right corner
        y2: y-coordinate of bottom-right corner

    Returns:
        Tuple of (width, height)
    """
    return x2 - x1, np.fabs(y2 - y1)


def compute_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Compute distance between two points

    Args:
        x1: x-coordinate of first point
        y1: y-coordinate of first point
        x2: x-coordinate of second point
        y2: y-coordinate of second point

    Returns:
        Distance between points
    """
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def compute_angle(
    x1: float, y1: float, x2: float, y2: float, reverse: bool = False
) -> float:
    """Compute angle between two points

    Args:
        x1: x-coordinate of first point
        y1: y-coordinate of first point
        x2: x-coordinate of second point
        y2: y-coordinate of second point
        reverse: If True, return the angle in the opposite direction

    Returns:
        Angle between points (in degrees)
    """
    sign = -1 if reverse else 1
    if x2 == x1:
        return 0.0
    else:
        return np.arctan(-sign * (y2 - y1) / (x2 - x1)) * 180.0 / np.pi
