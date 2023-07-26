# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Plot Image unit tests"""
import contextlib

import numpy as np
import pytest
from pytest import approx
from qtpy.QtCore import Qt

from plotpy.core.builder import make
from plotpy.core.plot.plotwidget import BasePlot, PlotDialog, PlotType
from plotpy.core.tools.image import ColormapTool


def compute_image():
    """Return a test image as numpy array"""
    N = 2000
    x = np.array(np.linspace(-5, 5, N), np.float32)
    img = np.zeros((N, N), np.float32)
    x.shape = (1, N)
    img += x**2
    return img


@contextlib.contextmanager
def plot_image(qtbot, item):
    win = PlotDialog(
        toolbar=True,
        wintitle="PlotDialog image test",
        options=dict(type=PlotType.IMAGE),
    )
    plot = win.manager.get_plot()
    assert isinstance(plot, BasePlot)
    plot.add_item(item)
    assert item in plot.items
    assert item.plot() is plot
    win.show()
    qtbot.addWidget(win)
    yield plot
    qtbot.keyClick(win, Qt.Key_Enter)


def test_plot_image(qtbot):
    """Test plotting of an Image"""
    item = make.image(compute_image())
    with plot_image(qtbot, item) as plot:
        pass


def compute_image_xy():
    N = 2000
    T = np.float32
    x = np.array(np.linspace(-5, 5, N), T)
    img = np.zeros((N, N), T)
    x.shape = (1, N)
    img += x**2
    x.shape = (N, 1)
    img += x**2
    x.shape = (N,)
    return x, (x + 5) ** 0.6, img


def test_plot_image_xy(qtbot):
    """Test plotting of an Image with custom XY coordinates"""
    item = make.xyimage(*compute_image_xy())
    with plot_image(qtbot, item) as plot:
        ...


def test_plot_quad_image(qtbot):
    """Test plotting of an Image with custom quad coordinates"""
    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z = X * Y
    item = make.quadgrid(X, Y, Z)
    with plot_image(qtbot, item) as plot:
        ...


def test_plot_tr_image(qtbot):
    """Test plotting of a TrImageItem"""
    img = compute_image()
    item = make.trimage(img)
    with plot_image(qtbot, item) as plot:
        # translate the image and check the new bounds
        bounds1 = item.bounds
        item.set_transform(50, 25, 0)
        bounds2 = item.bounds
        assert bounds1.width() == bounds2.width()
        assert bounds1.height() == bounds2.height()
        assert bounds2.left() == bounds1.left() + 50
        assert bounds2.top() == bounds1.top() + 25

        # rescale the image
        item.set_transform(0, 0, 0, 2.0, 3.0)
        plot.do_autoscale()
        bounds3 = item.bounds
        assert bounds3.width() == bounds2.width() * 2.0
        assert bounds3.height() == bounds2.height() * 3.0


@pytest.mark.parametrize("ratio", [1.0, 0.75, 1.5, 2.0, 3.0])
def test_set_aspect_ratio(qtbot, ratio):
    """Test BasePlot.set_aspect_ratio method()

    It ensures that the new height is correctly set."""
    win = PlotDialog(options=dict(type=PlotType.IMAGE))
    item = make.image(compute_image())
    plot = win.manager.get_plot()
    plot.add_item(item, autoscale=False)
    win.show()
    qtbot.addWidget(win)

    x0, x1, y0, y1 = plot.get_plot_limits()
    original_width = abs(x1 - x0)
    original_height = abs(y1 - y0)

    plot.set_aspect_ratio(ratio, True)
    assert plot.get_aspect_ratio() == ratio
    x0, x1, y0, y1 = plot.get_plot_limits()
    width = abs(x1 - x0)
    height = abs(y1 - y0)
    # XXX: This is tested with gui, it depends on x/y image ration
    # assert original_width != width
    # assert original_height / height == pytest.approx(ratio)
    #    assert original_height == height
    #    assert width / original_width == pytest.approx(ratio)

    qtbot.keyClick(win, Qt.Key_Enter)


def test_colormap_tool(qtbot):
    """Test ColorMapTool on an image"""
    win = PlotDialog(toolbar=True, options={"type": PlotType.IMAGE})
    item = make.image(compute_image())
    plot = win.manager.get_plot()
    plot.add_item(item)
    win.show()
    qtbot.addWidget(win)

    # default color map should be "jet"
    color_map_tool = win.manager.get_tool(ColormapTool)
    assert item.get_color_map_name() == "jet"
    jet_img = plot.grab().toImage()

    # change the colormap
    plot.select_item(item)
    action = color_map_tool.menu.actions()[0]
    color_map_tool.activate_cmap(action)
    assert item.get_color_map_name() == "Accent"
    accent_img = plot.grab().toImage()
    assert jet_img != accent_img
    # TODO: Check colormap of accent_img

    qtbot.keyClick(win, Qt.Key_Enter)
