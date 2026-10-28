# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Cross section panels keep curves for visible images only; unchanged axis
styles do not lay out the plot again."""

from __future__ import annotations

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtWidgets as QW

from plotpy.builder import make


def _window():
    win = make.dialog(type="image", show_xsection=True, show_ysection=True)
    win.show()
    return win


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
    test_unchanged_axis_style_does_not_relayout()
