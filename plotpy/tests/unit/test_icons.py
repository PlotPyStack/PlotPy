# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Icon tests

PlotPy icons are SVG files: the icons referenced in PlotPy's code must exist, and
the former PNG names of the icons must still be resolved (to the SVG files).
"""

from __future__ import annotations

import os
import os.path as osp
import re

import pytest
from guidata import configtools

import plotpy
import plotpy.config  # noqa: F401  (registers PlotPy's icon path)

# Icons referenced in PlotPy's code although they have never been provided
# (the "not found" icon is shown instead)
MISSING_ICONS = {"rotate.svg"}


def _referenced_icon_names() -> set[str]:
    """Return the SVG image names referenced as string literals in PlotPy's code
    (tests excluded)"""
    names = set()
    pattern = re.compile(r"[\"']([\w\-]+\.svg)[\"']")
    root = osp.dirname(plotpy.__file__)
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath == root:
            dirnames.remove("tests")
        for filename in filenames:
            if filename.endswith(".py"):
                with open(osp.join(dirpath, filename), encoding="utf-8") as fdesc:
                    names.update(pattern.findall(fdesc.read()))
    return names


def test_no_png_icons() -> None:
    """Test that PlotPy icons are provided as SVG files only"""
    root = configtools.get_module_data_path("plotpy", "data/icons")
    pngs = [
        osp.join(dirpath, filename)
        for dirpath, _dirnames, filenames in os.walk(root)
        for filename in filenames
        if filename.lower().endswith(".png")
    ]
    assert not pngs


def test_referenced_icons_exist() -> None:
    """Test that the icons referenced in PlotPy's code exist"""
    names = _referenced_icon_names()
    assert "curve.svg" in names
    missing = set()
    for name in names:
        try:
            configtools.get_image_file_path(name, default=None)
        except RuntimeError:
            missing.add(name)
    assert missing == MISSING_ICONS


@pytest.mark.parametrize("name", ["curve.png", "dense1pattern.png", "csection.png"])
def test_png_name_fallback(name: str) -> None:
    """Test that the former PNG names of the icons are resolved to SVG files"""
    path = configtools.get_image_file_path(name, default=None)
    assert osp.basename(path) == name.replace(".png", ".svg")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
