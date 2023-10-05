# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Tests around image transforms: rotation, translation, ..."""

# guitest: show

import os

import numpy as np
import pytest
from guidata.env import execenv
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy import io
from plotpy.builder import LUTAlpha, make
from plotpy.items import TrImageItem, assemble_imageitems
from plotpy.tests import vistools as ptv
from plotpy.tests.data import gen_image4

DEFAULT_CHARS = "".join([chr(c) for c in range(32, 256)])


def get_font_array(sz: int, chars: str = DEFAULT_CHARS) -> np.ndarray | None:
    """Return array of font characters

    Args:
        sz: Font size
        chars: Characters to include (default: all printable characters)

    Returns:
        Array of font characters
    """
    font = QG.QFont()
    font.setFixedPitch(True)
    font.setPixelSize(sz)
    font.setStyleStrategy(QG.QFont.NoAntialias)
    dummy = QG.QImage(10, 10, QG.QImage.Format_ARGB32)
    pnt = QG.QPainter(dummy)
    pnt.setFont(font)
    metric = pnt.fontMetrics()
    rct = metric.boundingRect(chars)
    pnt.end()
    h = rct.height()
    w = rct.width()
    img = QG.QImage(w, h, QG.QImage.Format_ARGB32)
    paint = QG.QPainter()
    paint.begin(img)
    paint.setFont(font)
    paint.setBrush(QG.QColor(255, 255, 255))
    paint.setPen(QG.QColor(255, 255, 255))
    paint.drawRect(0, 0, w + 1, h + 1)
    paint.setPen(QG.QColor(0, 0, 0))
    paint.setBrush(QG.QColor(0, 0, 0))
    paint.drawText(0, paint.fontMetrics().ascent(), chars)
    paint.end()
    try:
        try:
            data = img.bits().asstring(img.numBytes())
        except AttributeError:
            # PyQt5
            data = img.bits().asstring(img.byteCount())
    except SystemError:
        # Python 3
        return
    npy = np.frombuffer(data, np.uint8)
    npy.shape = img.height(), img.bytesPerLine() // 4, 4
    return npy[:, :, 0]


def write_text_on_array(
    data: np.ndarray,
    x: int,
    y: int,
    sz: int,
    txt: str,
    range: tuple[int, int] | None = None,
) -> None:
    """Write text in image (in-place)

    Args:
        data: Image data
        x: X-coordinate of top-left corner
        y: Y-coordinate of top-left corner
        sz: Font size
        txt: Text to write
        range: Range of values to map to 0-255 (default: None)
    """
    arr = get_font_array(sz, txt)
    if arr is None:
        return
    if range is None:
        m, M = data.min(), data.max()
    else:
        m, M = range
    z = (float(M) - float(m)) * np.array(arr, float) / 255.0 + m
    arr = np.array(z, data.dtype)
    dy, dx = arr.shape
    data[y : y + dy, x : x + dx] = arr


def make_items(N: int) -> list[TrImageItem]:
    """Make test TrImageItem items

    Args:
        N: Image size (N x N)

    Returns:
        List of image items
    """
    data = gen_image4(N, N)
    m = data.min()
    M = data.max()
    items = [make.trimage(data, alpha_function=LUTAlpha.LINEAR, colormap="jet")]
    for dtype in (np.uint8, np.uint16, np.int8, np.int16):
        info = np.iinfo(dtype().dtype)  # pylint: disable=no-value-for-parameter
        s = float((info.max - info.min))
        a1 = s * (data - m) / (M - m)
        img = np.array(a1 + info.min, dtype)
        write_text_on_array(img, 0, 0, int(N / 15.0), str(dtype))
        items.append(make.trimage(img, colormap="jet"))
    nc = int(np.sqrt(len(items)) + 1.0)
    maxy, x, y = 0, 0, 0
    w = None
    for index, item in enumerate(items):
        h = item.boundingRect().height()
        if index % nc == 0:
            x = 0
            y += maxy
            maxy = h
        else:
            x += w
            maxy = max(maxy, h)
        w = item.boundingRect().width()
        item.set_transform(x, y, 0.0)
    return items


def save_image(name: str, data: np.ndarray) -> None:
    """Save image to file

    Args:
        name: Base name of file
        data: Image data
    """
    for fname in (name + ".u16.tif", name + ".u8.png"):
        if os.path.exists(fname):
            os.remove(fname)
    size = int(data.nbytes / 1024.0)
    print(f"Saving image: {data.shape[0]} x {data.shape[1]} ({size} KB):")
    print(" --> uint16")
    io.imwrite(name + ".u16.tif", data, dtype=np.uint16, max_range=True)
    print(" --> uint8")
    io.imwrite(name + ".u8.png", data, dtype=np.uint8, max_range=True)


def get_bbox(items: list[TrImageItem]) -> QC.QRectF:
    """Get bounding box of items

    Args:
        items: List of image items

    Returns:
        Bounding box of items
    """
    rectf = QC.QRectF()
    for item in items:
        rectf = rectf.united(item.boundingRect())
    return rectf


def build_image(items: list[TrImageItem]) -> None:
    """Build image from items

    Args:
        items: List of image items
    """
    r = get_bbox(items)
    _x, _y, w, h = r.getRect()
    print("-" * 80)
    print(f"Assemble test1: {int(w)} x {int(h)}")
    dest = assemble_imageitems(items, r, w, h)
    if not execenv.unattended:
        save_image("test1", dest)
    print("-" * 80)
    print(f"Assemble test1: {int(w/4)} x {int(h/4)}")
    dest = assemble_imageitems(items, r, w / 4, h / 4)
    if not execenv.unattended:
        save_image("test2", dest)
    print("-" * 80)


@pytest.mark.parametrize("assemble_images", [False, True])
def test_transform(N: int = 500, assemble_images: bool = False) -> None:
    """Test image transforms

    Args:
        N: Image size (N x N)
        assemble_images: If True, assemble images (default: False)
    """
    with qt_app_context(exec_loop=True):
        items = make_items(N)
        _win = ptv.show_items(
            items,
            wintitle="Transform test ({}x{} images)".format(N, N),
            plot_type="image",
            show_itemlist=False,
        )
    if assemble_images:
        build_image(items)


if __name__ == "__main__":
    test_transform(assemble_images=True)
