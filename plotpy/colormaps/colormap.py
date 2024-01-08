# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Colormap functions
------------------

Overview
^^^^^^^^

The :py:mod:`.colormap` module contains definition of common colormaps and tools
to manipulate and create them.

The following functions are available:

* :py:func:`.get_cmap`: get a colormap from its name
* :py:func:`.get_cmap_name`: get a colormap's name
* :py:func:`.get_colormap_list`: get the list of available colormaps
* :py:func:`.build_icon_from_cmap`: build an icon representing the colormap
* :py:func:`.build_icon_from_cmap_name`: build an icon representing the colormap
  from its name
* :py:func:`.register_extra_colormap`: register a custom colormap

Reference
^^^^^^^^^

.. autofunction:: get_cmap
.. autofunction:: get_cmap_name
.. autofunction:: get_colormap_list
.. autofunction:: build_icon_from_cmap
.. autofunction:: build_icon_from_cmap_name
.. autofunction:: register_extra_colormap
"""

from __future__ import annotations

from numpy import array, linspace, newaxis, uint8, zeros
from qtpy import QtGui as QG
from qwt import QwtInterval, toQImage

from plotpy.colormaps import _cm
from plotpy.mathutils.colormaps import (
    DEFAULT_COLORMAPS,
    DEFAULT_COLORMAPS_PATH,
    save_colormaps,
)
from plotpy.widgets.colormap_widget import (
    CustomQwtLinearColormap,  # Reuse matplotlib data
)

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


def _setup_colormap(cmap: CustomQwtLinearColormap, cmdata):
    """Setup a CustomQwtLinearColorMap according to
    matplotlib's data
    """
    red = array(cmdata["red"])
    green = array(cmdata["green"])
    blue = array(cmdata["blue"])
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


def get_cmap(name: str) -> CustomQwtLinearColormap:
    """Get a colormap from its name

    Args:
        name: colormap name

    Returns:
        Return a QwtColormap based on matplotlib's colormap of the same name
        We avoid rebuilding the cmap by keeping it in cache
    """
    if name in COLORMAPS:
        return COLORMAPS[name]

    colormap = CustomQwtLinearColormap()
    COLORMAPS[name] = colormap
    COLORMAPS[colormap] = name
    data = getattr(_cm, "_" + name + "_data")
    _setup_colormap(colormap, data)
    return colormap


def get_cmap_name(cmap: CustomQwtLinearColormap) -> str:
    """Return colormap's name

    Args:
        cmap: colormap

    Returns:
        colormap's name
    """
    return COLORMAPS.get(cmap, None)


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


def build_icon_from_cmap(
    cmap: CustomQwtLinearColormap, width: int = 24, height: int = 24
) -> QG.QIcon:
    """Builds an icon representing the colormap

    Args:
        cmap: colormap
        width: icon width
        height: icon height
    """
    data = zeros((width, height), uint8)
    line = linspace(0, 255, width)
    data[:, :] = line[:, newaxis]
    img = toQImage(data)
    img.setColorTable(cmap.colorTable(FULLRANGE))
    return QG.QIcon(QG.QPixmap.fromImage(img))


def build_icon_from_cmap_name(cmap_name: str) -> QG.QIcon:
    """Builds an icon representing the colormap from its name

    Args:
        cmap_name: colormap name

    Returns:
        icon representing the colormap
    """
    if cmap_name in ICON_CACHE:
        return ICON_CACHE[cmap_name]
    icon = build_icon_from_cmap(get_cmap(cmap_name))
    ICON_CACHE[cmap_name] = icon
    return icon


def register_extra_colormap(name: str, colormap: CustomQwtLinearColormap) -> None:
    """Add a custom colormap to the list of known colormaps
    must be done early in the import process because
    datasets will use get_color_map list at import time

    Args:
        name: colormap name
        colormap: QwtColorMap object
    """
    COLORMAPS[name] = colormap
    COLORMAPS[colormap] = name
    EXTRA_COLORMAPS.append(name)


if __name__ == "__main__":
    for cmap in get_colormap_list():
        DEFAULT_COLORMAPS[cmap] = get_cmap(cmap)
    save_colormaps(DEFAULT_COLORMAPS_PATH, DEFAULT_COLORMAPS)
