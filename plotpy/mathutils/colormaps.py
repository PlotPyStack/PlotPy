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
from typing import Sequence

import numpy as np
import qtpy.QtGui as QG
from guidata.configtools import get_module_data_path
from qwt import QwtInterval, toQImage

from plotpy.config import CONF
from plotpy.widgets.colormap.widget import EditableColormap

# from guidata.dataset.datatypes import NoDefault
FULLRANGE = QwtInterval(0.0, 1.0)
DEFAULT = EditableColormap(name="default")


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


def load_qwt_colormaps_from_json(json_path: str) -> dict[str, EditableColormap]:
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


def save_colormaps(json_filename: str, colormaps: dict[str, EditableColormap]):
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
    cmap: EditableColormap, width: int = 16, height: int = 16
) -> QG.QIcon:
    """Builds an icon representing the colormap

    Args:
        cmap: colormap
        width: icon width
        height: icon height
    """
    data = np.zeros((width, height), np.uint8)
    line = np.linspace(0, 255, width)
    data[:, :] = line[:, np.newaxis]
    img = toQImage(data)
    img.setColorTable(cmap.colorTable(FULLRANGE))
    return QG.QIcon(QG.QPixmap.fromImage(img))


def build_icon_from_cmap_name(cmap_name: str) -> QG.QIcon:
    """Builds an QIcon representing the colormap from the colormap name found in
    ALL_COLORMAPS global variable.

    Args:
        cmap_name: colormap name to search in ALL_COLORMAPS

    Returns:
        QIcon representing the colormap
    """
    return build_icon_from_cmap(get_cmap(cmap_name.lower()))


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
    return ALL_COLORMAPS.get(cmap_name.lower(), DEFAULT)


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
DEFAULT_COLORMAPS = load_qwt_colormaps_from_json(DEFAULT_COLORMAPS_PATH)
CUSTOM_COLORMAPS = load_qwt_colormaps_from_json(CUSTOM_COLORMAPS_PATH)

# Merge default and custom colormaps into a single dictionnary to simplify access
ALL_COLORMAPS = {**DEFAULT_COLORMAPS, **CUSTOM_COLORMAPS}
