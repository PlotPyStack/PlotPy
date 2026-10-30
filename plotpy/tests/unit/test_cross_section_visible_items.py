# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Cross section panels keep curves for visible images only, and compute the
curves of images added or shown again; unchanged axis styles do not lay out the
plot again."""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtWidgets as QW

from plotpy.builder import make


def _window():
    # In unattended mode, leaving a `qt_app_context` schedules the closing of all
    # top-level widgets: process it now, so that it does not close this window
    QW.QApplication.processEvents()
    win = make.dialog(type="image", show_xsection=True, show_ysection=True)
    win.show()
    return win


def _cs_plots(win):
    """Return the X and Y cross section plots of the window"""
    return win.manager.get_xcs_panel().cs_plot, win.manager.get_ycs_panel().cs_plot


def _add_marker(win, x: float, y: float):
    """Add a marker to the plot and register it for the cross sections"""
    plot = win.manager.get_plot()
    marker = make.marker(position=(x, y))
    plot.add_item(marker)
    for cs_plot in _cs_plots(win):
        cs_plot.register_shape(plot, marker)
    return marker


def _assert_sections(win, image, x: float, y: float) -> None:
    """Assert that the cross section curves of the image are the sections at
    (x, y)"""
    xcs, ycs = _cs_plots(win)
    xcurve, ycurve = xcs.known_items[image], ycs.known_items[image]
    assert xcurve.dataSize() > 0 and ycurve.dataSize() > 0
    # The Y cross section curve is vertical: section values are its X data
    assert np.array_equal(xcurve.get_data()[1], image.get_xsection(y)[1])
    assert np.array_equal(ycurve.get_data()[0], image.get_ysection(x)[1])


def test_cross_section_curves_follow_visible_images():
    """Hidden images have no cross section curve, until they are shown again."""
    with qt_app_context(exec_loop=False):
        win = _window()
        plot = win.manager.get_plot()
        xcs = win.manager.get_xcs_panel().cs_plot
        ycs = win.manager.get_ycs_panel().cs_plot
        data = np.random.default_rng(0).random((16, 16))
        images = []
        for _index in range(20):
            if images:
                plot.set_item_visible(images[-1], False, notify=False, replot=False)
            image = make.image(data.copy())
            plot.add_item(image)
            images.append(image)
            QW.QApplication.processEvents()
        assert list(xcs.known_items) == [images[-1]]
        assert list(ycs.known_items) == [images[-1]]
        plot.set_item_visible(images[-1], False)
        assert not xcs.known_items
        plot.set_item_visible(images[0], True)
        assert list(xcs.known_items) == [images[0]]
        assert xcs.known_items[images[0]].isVisible()
        plot.del_item(images[0])
        assert not xcs.known_items and not ycs.known_items
        win.close()


def test_cross_section_computed_when_image_shown_again():
    """The cross sections of an image shown again are those at the marker
    position, even if the marker was moved while the image was hidden."""
    with qt_app_context(exec_loop=False):
        win = _window()
        plot = win.manager.get_plot()
        image1 = make.image(np.arange(16 * 16, dtype=float).reshape(16, 16))
        image2 = make.image(np.full((16, 16), 42.0))
        plot.add_item(image1)
        plot.add_item(image2)
        marker = _add_marker(win, 5, 5)
        _assert_sections(win, image1, 5, 5)
        plot.set_item_visible(image1, False)
        marker.set_pos(10, 12)
        plot.set_item_visible(image1, True)
        _assert_sections(win, image1, 10, 12)
        _assert_sections(win, image2, 10, 12)
        win.close()


def test_cross_section_computed_for_added_image():
    """The cross sections of an image added to the plot are computed at once."""
    with qt_app_context(exec_loop=False):
        win = _window()
        plot = win.manager.get_plot()
        plot.add_item(make.image(np.full((16, 16), 42.0)))
        _add_marker(win, 5, 7)
        image = make.image(np.arange(16 * 16, dtype=float).reshape(16, 16))
        plot.add_item(image)
        _assert_sections(win, image, 5, 7)
        win.close()


def test_cross_section_of_shown_image_follows_autorefresh_mode():
    """With the auto-refresh mode disabled, the cross section curves of an image
    shown again are computed on the next refresh only."""
    with qt_app_context(exec_loop=False):
        win = _window()
        plot = win.manager.get_plot()
        xcs, _ycs = _cs_plots(win)
        image = make.image(np.arange(16 * 16, dtype=float).reshape(16, 16))
        plot.add_item(image)
        _add_marker(win, 5, 5)
        xcs.toggle_autorefresh(False)
        plot.set_item_visible(image, False)
        plot.set_item_visible(image, True)
        assert xcs.known_items[image].dataSize() == 0
        xcs.update_plot()
        assert xcs.known_items[image].dataSize() == 16
        win.close()


def test_cross_section_shade_counts_visible_images_only():
    """The shade of the cross section curves ignores hidden images."""
    with qt_app_context(exec_loop=False):
        win = _window()
        plot = win.manager.get_plot()
        xcs, _ycs = _cs_plots(win)
        images = []
        for _index in range(4):
            if images:
                plot.set_item_visible(images[-1], False)
            image = make.image(np.ones((16, 16)))
            plot.add_item(image)
            images.append(image)
        assert xcs.param.shade == pytest.approx(xcs.SHADE)
        brush_color = xcs.known_items[images[-1]].brush().color()
        assert brush_color.alphaF() == pytest.approx(xcs.SHADE, abs=1e-2)
        win.close()


def test_unchanged_axis_style_does_not_relayout():
    """Setting the same titles again neither lays out the plot nor notifies."""
    with qt_app_context(exec_loop=False):
        win = _window()
        plot = win.manager.get_plot()
        plot.set_titles(title="T", xlabel="x", ylabel="y", xunit="mm", yunit="mm")
        layouts, notifications = [], []
        update_layout = plot.updateLayout
        plot.updateLayout = lambda: (layouts.append(1), update_layout())
        plot.SIG_PLOT_LABELS_CHANGED.connect(notifications.append)
        plot.set_titles(title="T", xlabel="x", ylabel="y", xunit="mm", yunit="mm")
        assert not layouts and not notifications
        plot.set_titles(xlabel="x2")
        assert plot.get_axis_title("bottom") == "x2"
        assert plot.axisTitle(plot.get_axis_id("bottom")).text() == "x2 (mm)"
        assert layouts and notifications
        win.close()


if __name__ == "__main__":
    test_cross_section_curves_follow_visible_images()
    test_cross_section_computed_when_image_shown_again()
    test_cross_section_computed_for_added_image()
    test_cross_section_of_shown_image_follows_autorefresh_mode()
    test_cross_section_shade_counts_visible_images_only()
    test_unchanged_axis_style_does_not_relayout()
