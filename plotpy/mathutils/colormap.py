# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Colormap functions
------------------

Overview
^^^^^^^^

The :py:mod:`plotpy.mathutils.colormap` module contains definition of common colormaps
and tools to manipulate and create them.

The following functions are available:

* :py:func:`.get_cmap`: get a colormap from its name
* :py:func:`.cmap_exists`: check if a colormap exists
* :py:func:`.add_cmap`: add a colormap to the list of available colormaps
* :py:func:`.get_custom_colormaps_path`: get the path of the custom colormaps file
* :py:func:`.reload_custom_colormaps`: reload custom colormaps from this file
* :py:func:`.build_icon_from_cmap`: build an icon representing the colormap
* :py:func:`.build_icon_from_cmap_name`: build an icon representing the colormap
  from its name

The :py:class:`.LogScaleColorMap` class maps values to colors on a base-10
logarithmic scale (e.g. for the color bar of images shown with a logarithmic
Z-axis).

Custom colormaps (e.g. created with the colormap manager) are saved in the
configuration directory of PlotPy: ``.plotpy`` by default, in the user's configuration
directory (``~/.config`` on Linux, the user's home directory otherwise). Applications
may save them in their own configuration directory by setting the application name of
PlotPy's configuration, e.g. ``plotpy.config.CONF.set_application("MyApp/plotpy",
"1.0.0")``: custom colormaps are then reloaded from this directory. The first time,
custom colormaps saved by previous versions of PlotPy (in the ``.none`` or ``.plotpy``
directory) are copied there.

Reference
^^^^^^^^^

.. autofunction:: get_cmap
.. autofunction:: cmap_exists
.. autofunction:: add_cmap
.. autofunction:: get_custom_colormaps_path
.. autofunction:: reload_custom_colormaps
.. autofunction:: build_icon_from_cmap
.. autofunction:: build_icon_from_cmap_name
.. autoclass:: LogScaleColorMap
   :members:
"""

from __future__ import annotations

import json
import math
import os
import os.path as osp
import warnings
from typing import Any, Dict, Literal, Sequence

import numpy as np
import qtpy.QtCore as QC
import qtpy.QtGui as QG
from guidata.configtools import get_module_data_path
from guidata.userconfig import get_config_basedir
from qwt import QwtInterval, toQImage
from qwt.color_map import QwtColorMap

from plotpy.config import CONF
from plotpy.widgets.colormap.widget import EditableColormap

FULLRANGE = QwtInterval(0.0, 1.0)
SMALL_ICON_WIDTH, SMALL_ICON_HEIGHT, SMALL_ICON_ORIENTATION = 16, 7, "h"
LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, LARGE_ICON_ORIENTATION = 80, 16, "h"

CmapDictType = Dict[str, EditableColormap]


def load_raw_colormaps_from_json(
    json_path: str,
) -> dict[str, Sequence[tuple[float, str]]]:
    """Tries to load raw colormaps from a json file. A raw colormap is a list of tuple
    sequence of tuples that contains a position value and a hex color string.

    Args:
        json_path: absolute path to the json to open. If file is not found, returns an
         empty dictionary

    Returns:
        Dictionnary of colormaps names -> raw colormap sequences
    """
    if isinstance(json_path, str) and os.path.isfile(json_path):
        with open(json_path, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(e)
                return {}
    return {}


def load_qwt_colormaps_from_json(json_path: str) -> CmapDictType:
    """Same as function load_raw_colormaps_from_json but transforms the raw colormaps
    into CustomQwtLinearColormap objects that are used by plotpy.

    Args:
        json_path: absolute path to the json to open. If file is not found, returns an
        empty dictionary

    Returns:
        Dictionnary of colormpas names -> CustomQwtLinearColormap
    """
    return {
        name.lower(): EditableColormap.from_iterable(iterable, name=name)
        for name, iterable in load_raw_colormaps_from_json(json_path).items()
    }


def get_cmap_path(config_path: str):
    """Takes a file path (i.e. from the CONF global variable) and tries to find it in
    this order:
        1. in Plotpy's data directory
        2. in user's plotpy configuration directory
        3. anywhere else using the path as an absolute path
    If the file is not found, the absolute filepath returned will point to user's plotpy
    configuration folder.

    Args:
        config_path: file path/name to check in the order listed above.
    """
    try:
        data_config_path = os.path.join(
            get_module_data_path("plotpy", "data"), config_path
        )
        if os.path.isfile(data_config_path):
            return data_config_path
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(e)

    user_config_path = CONF.get_path(config_path)
    if os.path.isfile(user_config_path):
        return user_config_path

    if os.path.isfile(config_path):
        return config_path

    return user_config_path


def _save_raw_colormaps(json_path: str, raw_colormaps: dict[str, Any]) -> None:
    """Saves raw colormaps into the given json file, creating its directory if needed.

    Args:
        json_path: absolute path of the json file in which to save the colormaps
        raw_colormaps: Dictionnary of colormaps names -> raw colormap sequences
    """
    os.makedirs(osp.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_colormaps, f, indent=4)


def save_colormaps(json_filename: str, colormaps: CmapDictType):
    """Saves colormaps into the given json file. Refer ton function get_cmap_path to
    know what json_filename can be used.

    Args:
        json_filename: json file name/path in which to save the colormaps
        colormaps: Dictionnary of colormpas names -> CustomQwtLinearColormap
    """
    raw_colormaps = {cmap.name: cmap.to_tuples() for cmap in colormaps.values()}
    _save_raw_colormaps(CONF.get_path(json_filename), raw_colormaps)


#: Configuration directories in which previous versions of PlotPy saved the custom
#: colormaps of all applications (``.none`` when PlotPy's configuration had no
#: application name, ``.plotpy`` when the host application named it "plotpy")
LEGACY_CUSTOM_COLORMAPS_DIRS = (".none", ".plotpy")


def _get_custom_colormaps_filename() -> str:
    """Returns the "colormaps/custom" option of PlotPy's configuration"""
    return CONF.get(
        "colormaps",
        "colormaps/custom",
        default="colormaps_custom.json",  # type: ignore
    )


def get_custom_colormaps_path() -> str:
    """Returns the path of the json file in which custom colormaps are saved.

    This file is located in the configuration directory of the application set with
    ``plotpy.config.CONF.set_application`` (``.plotpy`` by default, in the user's
    configuration directory), unless the "colormaps/custom" option of the "colormaps"
    configuration section is an absolute path.

    Returns:
        Absolute path of the custom colormaps json file (which may not exist yet)
    """
    return CONF.get_path(_get_custom_colormaps_filename())


def load_custom_colormaps() -> CmapDictType:
    """Loads the custom colormaps of the current application (see function
    get_custom_colormaps_path).

    If the custom colormaps file of the application does not exist yet, the custom
    colormaps saved by previous versions of PlotPy (see LEGACY_CUSTOM_COLORMAPS_DIRS)
    are first copied into it. The legacy files are left untouched.

    Returns:
        Dictionnary of colormaps names -> CustomQwtLinearColormap
    """
    filename = _get_custom_colormaps_filename()
    json_path = CONF.get_path(filename)
    if not osp.isfile(json_path) and not osp.isabs(filename):
        raw_colormaps: dict[str, Any] = {}
        for dirname in LEGACY_CUSTOM_COLORMAPS_DIRS:
            legacy_path = osp.join(get_config_basedir(), dirname, filename)
            raw_colormaps.update(load_raw_colormaps_from_json(legacy_path))
        if raw_colormaps:
            try:
                _save_raw_colormaps(json_path, raw_colormaps)
            except OSError as exc:
                warnings.warn(f"Unable to copy custom colormaps to {json_path}: {exc}")
    return load_qwt_colormaps_from_json(json_path)


# Load default colormaps path from the config file
DEFAULT_COLORMAPS_PATH = get_cmap_path(
    CONF.get(
        "colormaps",
        "colormaps/default",
        default="colormaps_default.json",  # type: ignore
    )
)

# Load default and custom colormaps from json files
DEFAULT_COLORMAPS: CmapDictType = load_qwt_colormaps_from_json(DEFAULT_COLORMAPS_PATH)
CUSTOM_COLORMAPS: CmapDictType = load_custom_colormaps()

# Merge default and custom colormaps into a single dictionnary to simplify access
ALL_COLORMAPS: CmapDictType = {**DEFAULT_COLORMAPS, **CUSTOM_COLORMAPS}

# Default colormap to use if a colormap is not found
DEFAULT = ALL_COLORMAPS["jet"]


def reload_custom_colormaps() -> None:
    """Reloads the custom colormaps of the current application (see function
    load_custom_colormaps).

    This function is called each time the application name of PlotPy's configuration
    is set with ``plotpy.config.CONF.set_application``. The CUSTOM_COLORMAPS and
    ALL_COLORMAPS global variables are updated in place.
    """
    custom_colormaps = load_custom_colormaps()
    CUSTOM_COLORMAPS.clear()
    CUSTOM_COLORMAPS.update(custom_colormaps)
    ALL_COLORMAPS.clear()
    ALL_COLORMAPS.update(DEFAULT_COLORMAPS)
    ALL_COLORMAPS.update(custom_colormaps)


CONF.register_application_callback(reload_custom_colormaps)


def __getattr__(name: str) -> Any:
    """Returns module attributes computed on demand"""
    if name == "CUSTOM_COLORMAPS_PATH":
        # Kept for backward compatibility: this path depends on the application name
        return get_custom_colormaps_path()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def build_icon_from_cmap(
    cmap: EditableColormap,
    width: int = SMALL_ICON_WIDTH,
    height: int = SMALL_ICON_HEIGHT,
    orientation: Literal["h", "v"] = SMALL_ICON_ORIENTATION,
    margin: int = 0,
) -> QG.QIcon:
    """Builds an icon representing the colormap

    Args:
        cmap: colormap
        width: icon width
        height: icon height
        orientation: orientation of the colormap in the icon. Can be "h" for horizontal
         or "v" for vertical
        margin: margin around the colormap in the icon. Beware that the margin is
         included in the given icon size. For example, if margin is 1 and width is 16,
         the actual colormap width will be 14 (16 - 2 * 1). This was done to prevent
         interpolation on display.
    """
    padded_width = width - 2 * margin
    padded_height = height - 2 * margin

    data = np.zeros((padded_height, padded_width), np.uint8)

    if orientation == "h":
        line = np.linspace(0, 255, padded_width)
        data[:, :] = line[:]
    else:
        line = np.linspace(0, 255, padded_height)
        data[:, :] = line[:, np.newaxis]

    img = toQImage(data)
    img.setColorTable(cmap.colorTable(FULLRANGE))
    cm_pxmap = QG.QPixmap.fromImage(img)

    if margin == 0:
        return QG.QIcon(cm_pxmap)

    padded_pixmap = QG.QPixmap(width, height)
    padded_pixmap.fill(QC.Qt.GlobalColor.transparent)

    # Create a painter to draw onto the new pixmap
    painter = QG.QPainter(padded_pixmap)
    painter.drawPixmap(margin, margin, cm_pxmap)
    painter.end()

    icon = QG.QIcon(padded_pixmap)

    return icon


def build_icon_from_cmap_name(
    cmap_name: str,
    width: int = SMALL_ICON_WIDTH,
    height: int = SMALL_ICON_HEIGHT,
    orientation: Literal["h", "v"] = SMALL_ICON_ORIENTATION,
    margin: int = 0,
) -> QG.QIcon:
    """Builds an QIcon representing the colormap from the colormap name found in
    ALL_COLORMAPS global variable.

    Args:
        cmap_name: colormap name to search in ALL_COLORMAPS
        width: icon width
        height: icon height
        orientation: orientation of the colormap in the icon. Can be "h" for horizontal
         or "v" for vertical
        margin: margin around the colormap in the icon. Beware that the margin is
         included in the given icon size. For example, if margin is 1 and width is 16,
         the actual colormap width will be 14 (16 - 2 * 1). This was done to prevent
         interpolation on display.

    Returns:
        QIcon representing the colormap
    """
    return build_icon_from_cmap(
        get_cmap(cmap_name.lower()), width, height, orientation, margin
    )


def get_cmap(cmap_name: str) -> EditableColormap:
    """Returns the colormap with the given name from the ALL_COLORMAPS global variable.
    If the colormap is not found, returns the DEFAULT colormap.

    Args:
        cmap_name: colormap name to search in ALL_COLORMAPS. All keys in ALL_COLORMAPS
         are lower case, so the given name is also lowered.

    Returns:
        A CustomQwtLinearColormap instance corresponding to the given name, if no
        colormap is found, returns the DEFAULT colormap.
    """
    global ALL_COLORMAPS
    return ALL_COLORMAPS.get(cmap_name.lower(), DEFAULT)


def cmap_exists(cmap_name: str, cmap_dict: CmapDictType | None = None) -> bool:
    """Returns True if the colormap with the given name exists in the given colormap
    dictionary, False otherwise. If no dictionary is given, the ALL_COLORMAPS global
    variable is used.

    Args:
        cmap_name: colormap name to search in given colormap dictionnary. All keys in
         the dictionary are lower case, so the given name is also lowered.
        cmap_dict: colormap dictionnary to search in. If None, ALL_COLORMAPS is used.

    Returns:
        True if the colormap exists, False otherwise.
    """
    if cmap_dict is None:
        cmap_dict = ALL_COLORMAPS
    return cmap_name.lower() in cmap_dict


def add_cmap(cmap: EditableColormap) -> None:
    """Adds the given colormap to both ALL_COLORMAPS and CUSTOM_COLORMAPS global
    variables.

    Args:
        cmap: colormap to add
    """
    global ALL_COLORMAPS, CUSTOM_COLORMAPS
    ALL_COLORMAPS[cmap.name.lower()] = cmap
    CUSTOM_COLORMAPS[cmap.name.lower()] = cmap
    save_colormaps(get_custom_colormaps_path(), CUSTOM_COLORMAPS)


def delete_cmap(cmap: EditableColormap) -> None:
    """Deletes the given colormap from both ALL_COLORMAPS and CUSTOM_COLORMAPS global"""
    global ALL_COLORMAPS, CUSTOM_COLORMAPS
    if CUSTOM_COLORMAPS.pop(cmap.name.lower(), None) is not None:
        del ALL_COLORMAPS[cmap.name.lower()]
        save_colormaps(get_custom_colormaps_path(), CUSTOM_COLORMAPS)


class LogScaleColorMap(QwtColorMap):
    """Color map applying another color map on a base-10 logarithmic scale

    The value interval and the values are given in data units: the wrapped color
    map is applied to their base-10 logarithm. Values lower than or equal to zero
    get the color of the lower bound of the interval.

    This is used to draw the color bar of images shown with a logarithmic Z-axis,
    so that the colors of the color bar match those of the image.

    Args:
        colormap: Wrapped color map
    """

    def __init__(self, colormap: QwtColorMap) -> None:
        super().__init__(colormap.format())
        self.colormap = colormap

    @staticmethod
    def _to_log(interval: QwtInterval, value: float) -> tuple[QwtInterval, float]:
        """Convert interval and value to base-10 logarithmic scale

        Args:
            interval: Value interval, in data units
            value: Value, in data units

        Returns:
            Interval and value, on logarithmic scale (unchanged if the interval
            is not strictly positive)
        """
        vmin, vmax = interval.minValue(), interval.maxValue()
        if not (vmin > 0 and vmax > 0):
            return interval, value
        lmin = math.log10(vmin)
        lvalue = math.log10(value) if value > 0 else lmin
        return QwtInterval(lmin, math.log10(vmax)), lvalue

    def rgb(self, interval: QwtInterval, value: float) -> int:
        """Return the color of a value

        Args:
            interval: Value interval, in data units
            value: Value, in data units

        Returns:
            RGB value of the color
        """
        return self.colormap.rgb(*self._to_log(interval, value))

    def colorIndex(self, interval: QwtInterval, value: float) -> int:
        """Return the color index of a value

        Args:
            interval: Value interval, in data units
            value: Value, in data units

        Returns:
            Index of the color in the color table
        """
        return self.colormap.colorIndex(*self._to_log(interval, value))
