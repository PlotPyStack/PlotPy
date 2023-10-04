# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Tests around image transforms: rotation, translation, ..."""

# guitest: show

import os

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy import io
from plotpy.builder import LUTAlpha, make
from plotpy.items import assemble_imageitems
from plotpy.tests.data import gen_image4

DEFAULT_CHARS = "".join([chr(c) for c in range(32, 256)])


def get_font_array(sz, chars=DEFAULT_CHARS):
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


def txtwrite(data, x, y, sz, txt, range=None):
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


def get_bbox(items):
    r = QC.QRectF()
    for it in items:
        r = r.united(it.boundingRect())
    return r


def save_image(name, data):
    for fname in (name + ".u16.tif", name + ".u8.png"):
        if os.path.exists(fname):
            os.remove(fname)
    print(
        "Saving image: {} x {} ({} KB):".format(
            data.shape[0], data.shape[1], data.nbytes / 1024.0
        )
    )
    print(" --> uint16")
    io.imwrite(name + ".u16.tif", data, dtype=np.uint16, max_range=True)
    print(" --> uint8")
    io.imwrite(name + ".u8.png", data, dtype=np.uint8, max_range=True)


def build_image(items):
    r = get_bbox(items)
    x, y, w, h = r.getRect()
    print("-" * 80)
    print("Assemble test1:", w, "x", h)
    dest = assemble_imageitems(items, r, w, h)
    if not execenv.unattended:
        save_image("test1", dest)
    print("-" * 80)
    print("Assemble test2:", w / 4, "x", h / 4)
    dest = assemble_imageitems(items, r, w / 4, h / 4)
    if not execenv.unattended:
        save_image("test2", dest)
    print("-" * 80)


def test_transform():
    """Test"""
    N = 500
    data = gen_image4(N, N)
    m = data.min()
    M = data.max()
    with qt_app_context(exec_loop=True):
        items = [make.trimage(data, alpha_function=LUTAlpha.LINEAR, colormap="jet")]
        for dtype in (np.uint8, np.uint16, np.int8, np.int16):
            info = np.iinfo(dtype().dtype)  # pylint: disable=no-value-for-parameter
            s = float((info.max - info.min))
            a1 = s * (data - m) / (M - m)
            img = np.array(a1 + info.min, dtype)
            txtwrite(img, 0, 0, int(N / 15.0), str(dtype))
            items.append(make.trimage(img, colormap="jet"))
        gridparam = make.gridparam(
            background="black",
            minor_enabled=(False, False),
            major_style=(".", "gray", 1),
        )
        win = make.dialog(
            edit=False,
            toolbar=True,
            wintitle="Transform test ({}x{} images)".format(N, N),
            gridparam=gridparam,
            type="image",
        )
        nc = int(np.sqrt(len(items)) + 1.0)
        maxy, x, y = 0, 0, 0
        w = None
        plot = win.manager.get_plot()
        for i, item in enumerate(items):
            h = item.boundingRect().height()
            if i % nc == 0:
                x = 0
                y += maxy
                maxy = h
            else:
                x += w
                maxy = max(maxy, h)
            w = item.boundingRect().width()
            item.set_transform(x, y, 0.0)
            plot.add_item(item)
        win.show()
    return items


def test_build_image():
    items = test_transform()
    build_image(items)


if __name__ == "__main__":
    test_build_image()
