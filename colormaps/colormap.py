# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Colormap utilities
------------------

"""

from __future__ import annotations

import _cm
import numpy as np
from qtpy import QtGui as QG
from qwt import QwtInterval

from plotpy.mathutils.colormaps import (
    DEFAULT_COLORMAPS,
    DEFAULT_COLORMAPS_PATH,
    save_colormaps,
)
from plotpy.widgets.colormap.widget import EditableColormap  # Reuse matplotlib data

# usefull to obtain a full color map
FULLRANGE = QwtInterval(0.0, 1.0)

COLORMAPS = {}
EXTRA_COLORMAPS = []  # custom build colormaps
ICON_CACHE = {}


def _interpolate(val, vmin, vmax):
    """Interpolate a color component between to values as provided
    by matplotlib colormaps
    """
    interp = (val - vmin[0]) / (vmax[0] - vmin[0])
    return (1 - interp) * vmin[1] + interp * vmax[2]


def _setup_colormap(cmap: EditableColormap, cmdata):
    """Setup a CustomQwtLinearColorMap according to
    matplotlib's data
    """
    red = np.array(cmdata["red"])
    green = np.array(cmdata["green"])
    blue = np.array(cmdata["blue"])
    qmin = QG.QColor()
    qmin.setRgbF(red[0, 2], green[0, 2], blue[0, 2])
    qmax = QG.QColor()
    qmax.setRgbF(red[-1, 2], green[-1, 2], blue[-1, 2])
    cmap.setColorInterval(qmin, qmax)
    indices = sorted(set(red[:, 0]) | set(green[:, 0]) | set(blue[:, 0]))
    for i in indices[1:-1]:
        idxr = red[:, 0].searchsorted(i)
        idxg = green[:, 0].searchsorted(i)
        idxb = blue[:, 0].searchsorted(i)
        compr = _interpolate(i, red[idxr - 1], red[idxr])
        compg = _interpolate(i, green[idxg - 1], green[idxg])
        compb = _interpolate(i, blue[idxb - 1], blue[idxb])
        col = QG.QColor()
        col.setRgbF(compr, compg, compb)
        cmap.addColorStop(i, col)


def get_cmap(name: str) -> EditableColormap:
    """Get a colormap from its name

    Args:
        name: colormap name

    Returns:
        Return a QwtColormap based on matplotlib's colormap of the same name
        We avoid rebuilding the cmap by keeping it in cache
    """
    if name in COLORMAPS:
        return COLORMAPS[name]

    colormap = EditableColormap()
    COLORMAPS[name] = colormap
    COLORMAPS[colormap] = name
    data = getattr(_cm, "_" + name + "_data")
    _setup_colormap(colormap, data)
    return colormap


def get_colormap_list() -> list[str]:
    """Builds a list of available colormaps by introspection of the _cm module

    Returns:
        list of colormap names
    """
    cmlist = []
    cmlist += EXTRA_COLORMAPS
    for name in dir(_cm):
        if name.endswith("_data"):
            obj = getattr(_cm, name)
            if isinstance(obj, dict):
                cmlist.append(name[1:-5])
    return cmlist


if __name__ == "__main__":
    for cmap in get_colormap_list():
        DEFAULT_COLORMAPS[cmap] = get_cmap(cmap)
    save_colormaps(DEFAULT_COLORMAPS_PATH, DEFAULT_COLORMAPS)
