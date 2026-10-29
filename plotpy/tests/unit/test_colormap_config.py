# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Custom colormaps location tests

Custom colormaps are saved in the configuration directory of the application set with
``CONF.set_application``, and copied from legacy directories the first time.
"""

from __future__ import annotations

import json
import os
import os.path as osp

import pytest
import qtpy.QtCore as QC
import qtpy.QtGui as QG

from plotpy.config import CONF
from plotpy.mathutils import colormap as cmapmod
from plotpy.widgets.colormap.widget import EditableColormap

RAW_CMAP = [[0.0, "#0000ff"], [1.0, "#ffff00"]]
CUSTOM_BASENAME = "colormaps_custom.json"


def write_json(path: str, data: dict) -> None:
    """Write data to a json file, creating its directory"""
    os.makedirs(osp.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fdesc:
        json.dump(data, fdesc)


def read_json(path: str) -> dict:
    """Read a json file"""
    with open(path, encoding="utf-8") as fdesc:
        return json.load(fdesc)


def app_path(config_dir: str, app_name: str) -> str:
    """Return the expected custom colormaps path of an application"""
    return osp.normpath(osp.join(config_dir, f".{app_name}", CUSTOM_BASENAME))


def test_default_application_name() -> None:
    """PlotPy's configuration has its own name by default"""
    assert CONF.name == "plotpy"


def test_no_directory_created_on_lookup(isolated_config_dir) -> None:
    """Looking up configuration paths does not create any directory"""
    config_dir = str(isolated_config_dir)
    CONF.set_application("MyApp_v1/plotpy", None, load=False)
    cmapmod.get_custom_colormaps_path()
    CONF.filename()
    assert os.listdir(config_dir) == []


def test_custom_colormaps_follow_application(isolated_config_dir) -> None:
    """Custom colormaps are saved to, and reloaded from, the application directory"""
    config_dir = str(isolated_config_dir)
    all_cmaps, custom_cmaps = cmapmod.ALL_COLORMAPS, cmapmod.CUSTOM_COLORMAPS
    name = "Issue 70 colormap"
    cmap = EditableColormap(
        [QG.QColor(QC.Qt.GlobalColor.blue), QG.QColor(QC.Qt.GlobalColor.yellow)],
        name=name,
    )

    CONF.set_application("MyApp_v1/plotpy", None, load=False)
    path = app_path(config_dir, "MyApp_v1/plotpy")
    assert osp.normpath(cmapmod.get_custom_colormaps_path()) == path
    assert cmapmod.CUSTOM_COLORMAPS_PATH == cmapmod.get_custom_colormaps_path()
    cmapmod.add_cmap(cmap)
    assert list(read_json(path)) == [name]
    assert os.listdir(config_dir) == [".MyApp_v1"]

    CONF.set_application("OtherApp/plotpy", None, load=False)
    assert not cmapmod.cmap_exists(name)
    assert cmapmod.cmap_exists("jet")

    CONF.set_application("MyApp_v1/plotpy", None, load=False)
    assert cmapmod.cmap_exists(name)
    assert cmapmod.cmap_exists(name, cmapmod.CUSTOM_COLORMAPS)
    # Dictionaries imported by other modules are updated in place:
    assert cmapmod.ALL_COLORMAPS is all_cmaps
    assert cmapmod.CUSTOM_COLORMAPS is custom_cmaps

    cmapmod.delete_cmap(cmapmod.get_cmap(name))
    assert read_json(path) == {}


@pytest.mark.parametrize(
    "app_name, legacy_dirs",
    [
        ("MyApp_v1/plotpy", (".none", ".plotpy")),
        ("plotpy", (".none",)),
    ],
)
def test_legacy_custom_colormaps_migration(
    isolated_config_dir, app_name: str, legacy_dirs: tuple[str, ...]
) -> None:
    """Custom colormaps saved in legacy directories are copied the first time"""
    config_dir = str(isolated_config_dir)
    legacy_files = {}
    for dirname in legacy_dirs:
        legacy_path = osp.join(config_dir, dirname, CUSTOM_BASENAME)
        legacy_files[legacy_path] = {f"From {dirname}": RAW_CMAP}
        write_json(legacy_path, legacy_files[legacy_path])

    CONF.set_application(app_name, None, load=False)
    names = sorted(f"From {dirname}" for dirname in legacy_dirs)
    assert sorted(read_json(app_path(config_dir, app_name))) == names
    for name in names:
        assert cmapmod.cmap_exists(name, cmapmod.CUSTOM_COLORMAPS)
    for legacy_path, data in legacy_files.items():
        assert read_json(legacy_path) == data

    # Once the application has its own file, legacy files are ignored:
    write_json(osp.join(config_dir, ".none", CUSTOM_BASENAME), {"Later": RAW_CMAP})
    CONF.set_application(app_name, None, load=False)
    assert not cmapmod.cmap_exists("Later")
