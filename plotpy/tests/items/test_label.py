# -*- coding: utf-8 -*-

"""Label and legend item tests."""

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make


def test_legend_click_inside_out_of_range_row() -> None:
    """Clicking outside a legend row must not index the curve list negatively."""
    with qt_app_context(exec_loop=False):
        window = make.dialog(edit=False, type="curve", size=(640, 480))
        plot = window.manager.get_plot()
        plot.add_item(make.curve(np.arange(3), np.arange(3), title="Signal"))
        legend = make.legend("TR")
        plot.add_item(legend)
        legend.get_text_rect()

        result = legend.click_inside(6.0, -100.0)

        assert result == (2.0, 1, True, None)
        window.close()


def test_empty_legend_click_inside_does_not_crash() -> None:
    """Clicking an empty legend must not index an empty curve list."""
    with qt_app_context(exec_loop=False):
        window = make.dialog(edit=False, type="curve", size=(640, 480))
        plot = window.manager.get_plot()
        legend = make.legend("TR")
        plot.add_item(legend)
        legend.get_text_rect()

        result = legend.click_inside(6.0, -100.0)

        assert result == (2.0, 1, True, None)
        window.close()
