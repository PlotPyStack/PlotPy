# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Unit tests for io module
"""

import numpy as np
import pytest
from guidata.configtools import get_image_file_path
from qtpy.QtGui import QImage

from plotpy.tests import get_path

try:
    import pydicom  # type:ignore
except ImportError:
    pydicom = None

from plotpy.io import imread, imwrite


def compute_image(N=1000, M=1000):
    """Compute a random image"""
    return (np.random.rand(N, M) * 65536).astype(np.uint8)


def test_imwrite_png(tmpdir):
    """Test writing of a png file"""

    # write a random image
    dest = tmpdir / "out.png"
    data = compute_image(1000, 500)
    imwrite(dest, data)
    assert dest.exists()

    # check image with Qt
    img = QImage()
    img.load(str(dest))
    assert img.height() == 1000
    assert img.width() == 500


def test_imwrite_txt(tmpdir):
    """Test writing of image in txt format"""
    # write a random image
    dest = tmpdir / "out.txt"
    data = compute_image(1000, 500)
    imwrite(dest, data)
    assert dest.exists()

    text = dest.read_text("ascii")
    lines = text.splitlines()
    assert len(lines) == 1000
    for line in lines:
        values = line.split(" ")
        assert len(values) == 500
        assert all(0 <= int(v) <= 255 for v in values)


def test_imwrite_csv(tmpdir):
    """Test writing of image in csv format"""
    # write a random image
    dest = tmpdir / "out.csv"
    data = compute_image(20, 30)
    imwrite(dest, data)
    assert dest.exists()

    text = dest.read_text("ascii")
    lines = text.splitlines()
    assert len(lines) == 20
    for line in lines:
        values = line.split(",")
        assert len(values) == 30
        assert all(0 <= int(v) <= 255 for v in values)


def test_imread_brain_png():
    """Test reading of brain png file"""
    brain_path = get_path("brain.png")
    data = imread(brain_path)
    assert data.shape == (256, 256)


def test_imread_python_icon():
    """Test reading of python icon which is a colored PNG with alpha."""
    path = get_image_file_path("python.png")
    data = imread(path)
    assert data.shape == (16, 16, 4)


def test_imread_python_icon_grayscale():
    """Test reading of python icon which is a colored PNG with alpha,
    data should be converted to grayscale."""
    path = get_image_file_path("python.png")
    data = imread(path, to_grayscale=True)
    assert data.shape == (16, 16)


@pytest.mark.skipif(pydicom is None, reason="pydicom not installed")
def test_imread_dcm():
    """Test reading of dcm file"""
    brain_path = get_path("mr-brain.dcm")
    data = imread(brain_path)
    assert data.shape == (512, 512)


def test_imread_txt(tmpdir):
    """Test reading of txt file"""

    img = tmpdir / "img.txt"
    content = "\n".join(" ".join(f"{n:d}" for n in range(255)) for _ in range(50))
    img.write_text(content, "ascii")

    data = imread(img)
    assert data.shape == (50, 255)
    assert data[0, 25] == 25


if __name__ == "__main__":
    test_imread_python_icon()
    test_imread_python_icon_grayscale()
