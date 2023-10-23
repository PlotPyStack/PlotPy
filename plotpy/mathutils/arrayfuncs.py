# -*- coding: utf-8 -*-

"""
Array functions
---------------

Overview
^^^^^^^^

The :py:mod:`.arrayfuncs` module provides miscellaneous array functions.

The following functions are available:

* :py:func:`.get_nan_min`
* :py:func:`.get_nan_max`
* :py:func:`.get_nan_range`

Reference
^^^^^^^^^

.. autofunction:: get_nan_min
.. autofunction:: get_nan_max
.. autofunction:: get_nan_range
"""

from __future__ import annotations

import numpy as np


def get_nan_min(data: np.ndarray | np.ma.MaskedArray) -> float:
    """Return minimum value of data, ignoring NaNs

    Args:
        data: Data array (or masked array)

    Returns:
        float: Minimum value of data, ignoring NaNs
    """
    if isinstance(data, np.ma.MaskedArray):
        data = data.data
    if data.dtype.name in ("float32", "float64", "float128"):
        return np.nanmin(data)
    else:
        return data.min()


def get_nan_max(data: np.ndarray | np.ma.MaskedArray) -> float:
    """Return maximum value of data, ignoring NaNs

    Args:
        data: Data array (or masked array)

    Returns:
        float: Maximum value of data, ignoring NaNs
    """
    if isinstance(data, np.ma.MaskedArray):
        data = data.data
    if data.dtype.name in ("float32", "float64", "float128"):
        return np.nanmax(data)
    else:
        return data.max()


def get_nan_range(data: np.ndarray | np.ma.MaskedArray) -> tuple[float, float]:
    """Return range of data, i.e. (min, max), ignoring NaNs

    Args:
        data: Data array (or masked array)

    Returns:
        tuple: Minimum and maximum value of data, ignoring NaNs
    """
    return get_nan_min(data), get_nan_max(data)
