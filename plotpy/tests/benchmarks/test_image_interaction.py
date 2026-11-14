# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
PlotPy image interaction benchmark
----------------------------------

This script measures the time needed to refresh an image plot during mouse
interactions, for several image item types and interpolation methods:

* Moving a shape over the image (the image itself does not change)
* Panning the image (the image must be rendered again)

Each mouse move event is followed by the repaint of the plot, as on screen.
The display scaling may be set with the ``QT_SCALE_FACTOR`` environment variable
(e.g. ``QT_SCALE_FACTOR=2`` for a 200% scaling).

Results obtained with PlotPy v2.12.1 on Windows 11 with a i5-1335U CPU, Qt 5.15.2
(1100x775 canvas at 100% scaling, 2048x2048 image), time per mouse move (ms),
before and after reusing image renderings when only overlays change:

.. code-block:: none

    Item           | Interpolation | Interaction | 100% scaling  | 200% scaling
    -----------------------------------------------------------------------------
    maskedxyimage  | nearest       | move shape  |  12.7 →   4.7 |  33.4 →  12.7
    maskedxyimage  | nearest       | pan         |  15.1 →  12.4 |  31.5 →  25.6
    maskedxyimage  | antialiasing  | move shape  |  67.6 →   4.7 | 175.3 →  10.2
    maskedxyimage  | antialiasing  | pan         |  70.5 →  63.1 | 183.2 → 169.8
    image          | nearest       | move shape  |   7.3 →   4.4 |  16.6 →  11.8
    image          | antialiasing  | move shape  |  41.8 →   4.0 | 108.8 →  10.0
    image          | antialiasing  | pan         |  43.0 →  42.7 | 111.5 → 115.9
"""

from __future__ import annotations

import time

import numpy as np
import pytest
from guidata.env import execenv
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.items.image.base import BaseImageItem
from plotpy.plot import PlotOptions, PlotWindow
from plotpy.tests.unit.utils import mouse_event_at_relative_plot_pos
from plotpy.widgets.about import get_python_libs_info

SIZE = 2048  # Image size
MOVES = 40  # Number of mouse move events per interaction


def make_image_item(kind: str, interpolation: str) -> BaseImageItem:
    """Make an image item of the given kind"""
    data = (np.random.default_rng(0).random((SIZE, SIZE)) * 4000).astype(np.uint16)
    if kind == "image":
        return make.image(data, interpolation=interpolation)
    x = np.arange(SIZE, dtype=float)
    # Masked XY image, as shown by DataLab
    return make.maskedxyimage(
        x, x, data, None, interpolation=interpolation, show_mask=True
    )


def measure(
    win: PlotWindow, item: BaseImageItem, shape, interaction: str
) -> tuple[float, float]:
    """Return the median time per mouse move (ms) and the number of image
    renderings per mouse move for the given interaction"""
    plot = win.manager.get_plot()
    canvas = plot.canvas()
    renders = []
    original_draw_image = item.draw_image

    def draw_image(*args):
        renders.append(None)
        return original_draw_image(*args)

    item.draw_image = draw_image
    times = []
    # Relative canvas position of the shape center
    x0, y0, x1, y1 = shape.get_rect()
    cx = plot.transform(item.xAxis(), (x0 + x1) / 2) / canvas.width()
    cy = plot.transform(item.yAxis(), (y0 + y1) / 2) / canvas.height()
    path = np.linspace(0.0, 0.2, MOVES)
    if interaction == "move shape":
        xs, ys = cx + path, cy + path
        btn = QC.Qt.MouseButton.LeftButton
    else:
        xs, ys = 0.4 + path, np.full_like(path, 0.5)
        btn = QC.Qt.MouseButton.MiddleButton
    rect_before = shape.get_rect()
    limits_before = plot.get_axis_limits(item.xAxis())
    try:
        event_types = QC.QEvent.Type
        send = mouse_event_at_relative_plot_pos
        send(win, (xs[0], ys[0]), (event_types.MouseButtonPress,), btn=btn)
        QW.QApplication.processEvents()
        for x, y in zip(xs, ys):
            # Each mouse move event is followed by the repaint of the plot
            t0 = time.perf_counter()
            send(win, (x, y), (event_types.MouseMove,), btn=btn)
            QW.QApplication.processEvents()
            times.append(time.perf_counter() - t0)
        send(win, (xs[-1], ys[-1]), (event_types.MouseButtonRelease,), btn=btn)
        QW.QApplication.processEvents()
    finally:
        del item.draw_image
    if interaction == "move shape":
        assert shape.get_rect() != rect_before, "The shape was not moved"
    else:
        assert plot.get_axis_limits(item.xAxis()) != limits_before, "No panning"
    plot.do_autoscale()
    QW.QApplication.processEvents()
    return 1000 * float(np.median(times[1:])), len(renders) / MOVES


def run_benchmark() -> None:
    """Run the benchmark and print the results"""
    execenv.print(f"PlotPy image interaction benchmark [{get_python_libs_info()}]")
    with qt_app_context(exec_loop=False):
        win = PlotWindow(toolbar=True, options=PlotOptions(type="image"))
        win.resize(1200, 850)
        win.show()
        QW.QApplication.processEvents()
        plot = win.manager.get_plot()
        ratio = plot.canvas().devicePixelRatioF()
        canvas = plot.canvas()
        execenv.print(
            f"Display scaling: {ratio:.0%}, canvas: {canvas.width()}x"
            f"{canvas.height()} pixels, image: {SIZE}x{SIZE} pixels"
        )
        execenv.print()
        header = (
            f"{'Item':<14} | {'Interpolation':<13} | {'Interaction':<11} | "
            f"{'∆t (ms)':>7} | {'Renders/move':>12}"
        )
        execenv.print(header)
        execenv.print("-" * len(header))
        for kind in ("maskedxyimage", "image"):
            for interpolation in ("nearest", "linear", "antialiasing"):
                item = make_image_item(kind, interpolation)
                shape = make.rectangle(SIZE * 0.4, SIZE * 0.4, SIZE * 0.5, SIZE * 0.5)
                plot.add_item(item)
                plot.add_item(shape)
                plot.do_autoscale()
                plot.select_item(shape)
                QW.QApplication.processEvents()
                for interaction in ("move shape", "pan"):
                    dt, renders = measure(win, item, shape, interaction)
                    execenv.print(
                        f"{kind:<14} | {interpolation:<13} | {interaction:<11} | "
                        f"{dt:7.1f} | {renders:12.2f}"
                    )
                plot.del_items([item, shape])
        win.close()


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_image_interaction_benchmark():
    """Run the image interaction benchmark"""
    run_benchmark()


if __name__ == "__main__":
    run_benchmark()
