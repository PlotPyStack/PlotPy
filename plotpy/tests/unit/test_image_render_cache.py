# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test the reuse of image renderings when only overlays change"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy._scaler import INTERP_NEAREST
from plotpy.builder import make
from plotpy.items import RawImageItem
from plotpy.items.image.base import BaseImageItem
from plotpy.plot import PlotOptions, PlotWidget
from plotpy.tests.unit.utils import mouse_event_at_relative_plot_pos

RNG = np.random.default_rng(0)
DATA = RNG.random((60, 80)).astype(np.float32)
MASK = np.zeros(DATA.shape, bool)
MASK[10:30, 20:50] = True
X = np.cumsum(RNG.random(80) + 0.5)
Y = np.cumsum(RNG.random(60) + 0.5)

#: Image items whose rendering is reused when only overlays change
REUSABLE_ITEMS: dict[str, Callable[[], BaseImageItem]] = {
    "image": lambda: make.image(DATA),
    "image_aa": lambda: make.image(DATA, interpolation="antialiasing"),
    "xyimage": lambda: make.xyimage(X, Y, DATA),
    "maskedimage": lambda: make.maskedimage(DATA, MASK, show_mask=True),
    "maskedxyimage": lambda: make.maskedxyimage(X, Y, DATA, MASK, show_mask=True),
    "rgbimage": lambda: make.rgbimage((RNG.random((60, 80, 3)) * 255).astype("u1")),
    "histogram2d": lambda: make.histogram2D(RNG.normal(size=500), RNG.normal(size=500)),
    "rawimage": lambda: RawImageItem(DATA),
}


class CustomImageItem(RawImageItem):
    """Image item drawing something else in its ``draw_image`` method"""

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """Draw image"""
        painter.fillRect(canvasRect, QC.Qt.red)


#: Image items whose rendering is not reused
OTHER_ITEMS: dict[str, Callable[[], BaseImageItem]] = {
    "trimage": lambda: make.trimage(DATA),
    "quadgrid": lambda: make.quadgrid(
        *np.meshgrid(X[:20], Y[:15]), DATA[:15, :20].astype(float)
    ),
    "custom": lambda: CustomImageItem(DATA),
}


class Window:
    """Plot widget showing an image item and a rectangle shape, counting the
    renderings of the image item"""

    def __init__(self, item: BaseImageItem) -> None:
        self.widget = PlotWidget(options=PlotOptions(type="image"))
        self.plot = self.widget.get_plot()
        self.item = item
        self.shape = make.rectangle(10, 10, 30, 30)
        self.plot.add_item(item)
        self.plot.add_item(self.shape)
        self.widget.resize(400, 300)
        self.widget.show()
        self.plot.do_autoscale()
        self.renders = 0
        draw_image = item.draw_image

        def counting_draw_image(*args):
            self.renders += 1
            draw_image(*args)

        item.draw_image = counting_draw_image
        self.grab()
        self.renders = 0

    def grab(self) -> QG.QImage:
        """Repaint the plot and return its image"""
        QW.QApplication.processEvents()
        return self.widget.grab().toImage()

    def move_shape(self) -> None:
        """Move the shape over the image"""
        self.shape.move_shape((10, 10), (20, 15))

    def close(self) -> None:
        """Close the widget"""
        self.widget.close()
        self.widget.deleteLater()


@pytest.mark.parametrize("name", list(REUSABLE_ITEMS))
def test_overlays_replot_reuses_rendering(name: str) -> None:
    """When only overlays change, the previous rendering of the image is drawn
    again, which looks the same as a new rendering"""
    with qt_app_context(exec_loop=False):
        win = Window(REUSABLE_ITEMS[name]())
        win.move_shape()
        win.plot.replot_overlays()
        overlays_image = win.grab()
        assert win.renders == 0
        win.plot.replot()
        image = win.grab()
        assert win.renders == 1
        assert overlays_image == image
        win.close()


@pytest.mark.parametrize("name", list(OTHER_ITEMS))
def test_overlays_replot_other_items(name: str) -> None:
    """Image items which may not reuse their rendering are rendered again"""
    with qt_app_context(exec_loop=False):
        win = Window(OTHER_ITEMS[name]())
        win.move_shape()
        win.plot.replot_overlays()
        win.grab()
        assert win.renders >= 1
        win.close()


def test_image_changes_render_again() -> None:
    """Images are rendered again when they change, even with an overlays replot"""
    with qt_app_context(exec_loop=False):
        win = Window(make.image(DATA))
        # Replot and invalidate
        for refresh in (win.plot.replot, win.plot.invalidate):
            win.renders = 0
            refresh()
            win.grab()
            assert win.renders == 1
        # Data, contrast, colormap and interpolation, without any replot
        changes = (
            lambda: win.item.set_data(DATA * 2),
            lambda: win.item.set_lut_range([0.2, 0.5]),
            lambda: win.item.set_color_map("gray"),
            lambda: win.item.set_interpolation(INTERP_NEAREST),
            # Image position (e.g. image moved together with a selected shape)
            lambda: win.item.move_with_selection(5, 5),
        )
        for index, change in enumerate(changes):
            win.renders = 0
            change()
            win.plot.replot_overlays()
            win.grab()
            assert win.renders == 1, f"Change #{index} not rendered"
        # Plot axes
        win.renders = 0
        limits = win.plot.get_axis_limits("bottom")
        win.plot.set_plot_limits(10, 50, 10, 40)
        assert win.plot.get_axis_limits("bottom") != limits
        win.grab()
        assert win.renders == 1
        win.close()


def test_mask_overlay() -> None:
    """The mask overlay is only rendered when visible"""
    with qt_app_context(exec_loop=False):
        win = Window(make.maskedimage(DATA, MASK, show_mask=True))
        assert len(win.item._offscreen_draws) == 2  # Image and mask overlay
        win.item.unmask_all()
        win.plot.replot()
        win.grab()
        assert len(win.item._offscreen_draws) == 1  # Transparent mask overlay
        win.item.param.alpha_unmasked = 0.5
        win.plot.replot()
        win.grab()
        assert len(win.item._offscreen_draws) == 2  # Unmasked area overlay
        win.close()


def test_moving_shape_with_mouse() -> None:
    """Moving a shape with the mouse does not render the image again"""
    with qt_app_context(exec_loop=False):
        win = Window(make.image(DATA))
        win.plot.select_item(win.shape)
        canvas = win.plot.canvas()
        x0, y0, x1, y1 = win.shape.get_rect()
        cx = win.plot.transform(win.item.xAxis(), (x0 + x1) / 2) / canvas.width()
        cy = win.plot.transform(win.item.yAxis(), (y0 + y1) / 2) / canvas.height()
        event = QC.QEvent.Type
        btn = QC.Qt.MouseButton.LeftButton
        mouse_event_at_relative_plot_pos(
            win.widget, (cx, cy), (event.MouseButtonPress,), btn=btn
        )
        win.grab()
        win.renders = 0
        for delta in np.linspace(0.01, 0.1, 10):
            pos = (cx + delta, cy + delta)
            mouse_event_at_relative_plot_pos(
                win.widget, pos, (event.MouseMove,), btn=btn
            )
            win.grab()
            assert win.renders == 0
        mouse_event_at_relative_plot_pos(
            win.widget, pos, (event.MouseButtonRelease,), btn=btn
        )
        assert win.shape.get_rect() != (x0, y0, x1, y1)
        win.close()
