# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing per-axis autoscale strategy."""

# guitest: skip

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.constants import AXIS_IDS, X_BOTTOM, Y_LEFT
from plotpy.tests import vistools as ptv


def _make_plot():
    """Create a plot widget with a single curve item."""
    x = np.linspace(0.0, 10.0, 11)
    y = np.linspace(-5.0, 5.0, 11)
    items = [make.curve(x, y, color="b")]
    win = ptv.show_items(items, wintitle="autoscale-strategy-test", auto_tools=False)
    return win, win.get_plot()


def test_default_strategy_is_auto():
    """All axes default to the 'auto' strategy."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        for axis_id in AXIS_IDS:
            assert plot.get_axis_autoscale_strategy(axis_id) == ("auto", None, None)


def test_set_get_strategy_round_trip():
    """`set_axis_autoscale_strategy` round-trips through the getter."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        plot.set_axis_autoscale_strategy(X_BOTTOM, "fixed", vmin=1.5, vmax=8.5)
        assert plot.get_axis_autoscale_strategy(X_BOTTOM) == ("fixed", 1.5, 8.5)
        plot.set_axis_autoscale_strategy(Y_LEFT, "none")
        assert plot.get_axis_autoscale_strategy(Y_LEFT) == ("none", None, None)


def test_invalid_strategy_raises():
    """Unknown strategies are rejected."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        with pytest.raises(ValueError):
            plot.set_axis_autoscale_strategy(X_BOTTOM, "bogus")


def test_strategy_none_keeps_limits():
    """An axis with strategy 'none' is left untouched by `do_autoscale`."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        plot.set_axis_limits(X_BOTTOM, -42.0, 42.0)
        plot.set_axis_autoscale_strategy(X_BOTTOM, "none")
        plot.do_autoscale(replot=False)
        vmin, vmax = plot.get_axis_limits(X_BOTTOM)
        assert vmin == -42.0
        assert vmax == 42.0


def test_strategy_fixed_applies_bounds():
    """An axis with strategy 'fixed' is set to the configured vmin/vmax."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        plot.set_axis_autoscale_strategy(Y_LEFT, "fixed", vmin=-100.0, vmax=100.0)
        plot.do_autoscale(replot=False)
        vmin, vmax = plot.get_axis_limits(Y_LEFT)
        assert vmin == -100.0
        assert vmax == 100.0


def test_strategy_auto_uses_item_bounds():
    """An axis with strategy 'auto' covers the items' bounding rect."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        plot.do_autoscale(replot=False)
        vmin, vmax = plot.get_axis_limits(X_BOTTOM)
        # Curve x-range is [0, 10]; auto strategy adds a margin so bounds are wider.
        assert vmin <= 0.0
        assert vmax >= 10.0


def test_explicit_axis_id_honors_none():
    """`do_autoscale(axis_id=...)` honors the 'none' strategy."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        plot.set_axis_limits(X_BOTTOM, -7.0, 7.0)
        plot.set_axis_autoscale_strategy(X_BOTTOM, "none")
        plot.do_autoscale(replot=False, axis_id=X_BOTTOM)
        vmin, vmax = plot.get_axis_limits(X_BOTTOM)
        assert vmin == -7.0
        assert vmax == 7.0


def test_disabled_axis_is_inert():
    """A disabled axis is ignored even when its strategy is 'fixed'."""
    with qt_app_context(exec_loop=False):
        _win, plot = _make_plot()
        from plotpy.constants import X_TOP

        assert not plot.axisEnabled(X_TOP)
        plot.set_axis_autoscale_strategy(X_TOP, "fixed", vmin=-1.0, vmax=1.0)
        # Should not raise nor mutate the disabled axis state.
        plot.do_autoscale(replot=False)
        plot.do_autoscale(replot=False, axis_id=X_TOP)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
