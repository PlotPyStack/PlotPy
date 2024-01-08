# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)


import json
import os
from typing import Sequence

import numpy as np
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW
from guidata.configtools import get_module_data_path
from qwt import QwtInterval, toQImage

from plotpy.config import CONF
from plotpy.widgets.colormap_widget import CustomQwtLinearColormap

# from guidata.dataset.datatypes import NoDefault
FULLRANGE = QwtInterval(0.0, 1.0)
DEFAULT = CustomQwtLinearColormap(name="default")


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
        with open(json_path) as f:
            try:
                return json.load(f)
            except BaseException as e:
                print(e)
                return {}
    return {}


def load_qwt_colormaps_from_json(json_path: str) -> dict[str, CustomQwtLinearColormap]:
    """Same as function load_raw_colormaps_from_json but transforms the raw colormaps
    into CustomQwtLinearColormap objects that are used by plotpy.

    Args:
        json_path: absolute path to the json to open. If file is not found, returns an
        empty dictionary

    Returns:
        Dictionnary of colormpas names -> CustomQwtLinearColormap
    """
    return {
        name: CustomQwtLinearColormap.from_iterable(iterable, name=name)
        for name, iterable in load_raw_colormaps_from_json(json_path).items()
    }


def save_colormaps(json_filename: str, colormaps: dict[str, CustomQwtLinearColormap]):
    """Saves colormaps into the given json file. Refer ton function get_cmap_path to
    know what json_filename can be used.

    Args:
        json_filename: json file name/path in which to save the colormaps
        colormaps: Dictionnary of colormpas names -> CustomQwtLinearColormap
    """
    raw_colormaps = {name: cmap.to_tuples() for name, cmap in colormaps.items()}
    json_abs_path = CONF.get_path(json_filename)
    with open(json_abs_path, "w") as f:
        json.dump(raw_colormaps, f, indent=4)


def build_icon_from_cmap(
    cmap: CustomQwtLinearColormap, width: int = 24, height: int = 24
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
    return build_icon_from_cmap(get_cmap(cmap_name))


def get_cmap(cmap_name: str) -> CustomQwtLinearColormap:
    return ALL_COLORMAPS.get(cmap_name, DEFAULT)


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
    except BaseException as e:
        print(e)

    user_config_path = CONF.get_path(config_path)
    if os.path.isfile(user_config_path):
        return user_config_path

    if os.path.isfile(config_path):
        return config_path

    return user_config_path


DEFAULT_COLORMAPS_PATH = get_cmap_path(
    CONF.get("colormaps", "colormaps/default", default="colormaps_default.json")  # type: ignore
)
CUSTOM_COLORMAPS_PATH = get_cmap_path(
    CONF.get("colormaps", "colormaps/custom", default="colormaps_custom.json")  # type: ignore
)

DEFAULT_COLORMAPS = load_qwt_colormaps_from_json(DEFAULT_COLORMAPS_PATH)
CUSTOM_COLORMAPS = load_qwt_colormaps_from_json(CUSTOM_COLORMAPS_PATH)

ALL_COLORMAPS = {**DEFAULT_COLORMAPS, **CUSTOM_COLORMAPS}

if __name__ == "__main__":
    CUSTOM_COLORMAPS["glow_hot"] = CustomQwtLinearColormap.from_iterable(
        ((0, "#0000ff"), (0.5, "#ff0000"), (1.0, "#ffff00"))
    )
    # print(f"Saving custom_colormaps at {CONF.get_path(CUSTOM_COLORMAPS_PATH)}")
    save_colormaps(CUSTOM_COLORMAPS_PATH, CUSTOM_COLORMAPS)
    print(CUSTOM_COLORMAPS)
