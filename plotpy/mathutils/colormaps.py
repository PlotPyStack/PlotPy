# -*- coding: utf-8 -*-
"""This module provides utilities to interact with colormap. It provides functions
to load/save colormaps from/to json files and to build icons representing the
colormaps.
"""
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)
from __future__ import annotations

import json
import os
from typing import Dict, Literal, Sequence

import numpy as np
import qtpy.QtCore as QC
import qtpy.QtGui as QG
from guidata.configtools import get_module_data_path
from qwt import QwtInterval, toQImage

from plotpy.config import CONF
from plotpy.widgets.colormap.widget import EditableColormap

# from guidata.dataset.datatypes import NoDefault
FULLRANGE = QwtInterval(0.0, 1.0)
DEFAULT = EditableColormap(name="jet")
SQUARE_ICON_SIZE = 16
RECT_ICON_SIZE_W, RECT_ICON_SIZE_H = 80, 16

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


def save_colormaps(json_filename: str, colormaps: CmapDictType):
    """Saves colormaps into the given json file. Refer ton function get_cmap_path to
    know what json_filename can be used.

    Args:
        json_filename: json file name/path in which to save the colormaps
        colormaps: Dictionnary of colormpas names -> CustomQwtLinearColormap
    """
    raw_colormaps = {name: cmap.to_tuples() for name, cmap in colormaps.items()}
    json_abs_path = CONF.get_path(json_filename)
    with open(json_abs_path, "w", encoding="utf-8") as f:
        json.dump(raw_colormaps, f, indent=4)


def build_icon_from_cmap(
    cmap: EditableColormap,
    width: int = SQUARE_ICON_SIZE,
    height: int = SQUARE_ICON_SIZE,
    orientation: Literal["h", "v"] = "v",
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
    width: int = SQUARE_ICON_SIZE,
    height: int = SQUARE_ICON_SIZE,
    orientation: Literal["h", "v"] = "v",
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
    save_colormaps(CUSTOM_COLORMAPS_PATH, CUSTOM_COLORMAPS)


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


# Load default colormaps path from the config file
DEFAULT_COLORMAPS_PATH = get_cmap_path(
    CONF.get(
        "colormaps",
        "colormaps/default",
        default="colormaps_default.json",  # type: ignore
    )
)
# Load custom colormaps path from the config file
CUSTOM_COLORMAPS_PATH = get_cmap_path(
    CONF.get(
        "colormaps", "colormaps/custom", default="colormaps_custom.json"  # type: ignore
    )
)

# Load default and custom colormaps from json files
DEFAULT_COLORMAPS: CmapDictType = load_qwt_colormaps_from_json(DEFAULT_COLORMAPS_PATH)
CUSTOM_COLORMAPS: CmapDictType = load_qwt_colormaps_from_json(CUSTOM_COLORMAPS_PATH)

# Merge default and custom colormaps into a single dictionnary to simplify access
ALL_COLORMAPS: CmapDictType = {**DEFAULT_COLORMAPS, **CUSTOM_COLORMAPS}
