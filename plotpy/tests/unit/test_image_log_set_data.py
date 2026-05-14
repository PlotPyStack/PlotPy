# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Regression tests for cached log10 data refresh in ``ImageItem.set_data``.

When the Z-axis is in logarithmic scale, ``ImageItem`` keeps a cached
``_log_data`` array. Prior to the fix, calling ``set_data`` did not refresh
that cache, so the displayed image kept reflecting the previous values until
the user toggled the log scale off and on again.
"""

from __future__ import annotations

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make


def _make_item(data: np.ndarray):
    """Return an ``ImageItem`` ready for log-scale tests."""
    return make.image(data, interpolation="nearest")


def test_set_data_refreshes_log_data_when_log_scale_enabled() -> None:
    """``set_data`` must recompute ``_log_data`` when log scale is active."""
    with qt_app_context(exec_loop=False):
        first = np.array([[1.0, 10.0], [100.0, 1000.0]])
        item = _make_item(first)
        item.set_zaxis_log_state(True)
        np.testing.assert_array_almost_equal(item._log_data, np.log10(first.clip(1)))

        second = np.array([[10.0, 100.0], [1000.0, 10000.0]])
        item.set_data(second)

        # The cache must reflect the new data, not the previous one.
        np.testing.assert_array_almost_equal(item._log_data, np.log10(second.clip(1)))
        # And the LUT range must be derived from the refreshed log data.
        lut_min, lut_max = item.get_lut_range()
        assert lut_min == np.log10(second.clip(1)).min()
        assert lut_max == np.log10(second.clip(1)).max()


def test_set_data_keeps_lut_range_in_log_mode() -> None:
    """``keep_lut_range`` must be honored even when log scale is active."""
    with qt_app_context(exec_loop=False):
        first = np.array([[1.0, 10.0], [100.0, 1000.0]])
        item = _make_item(first)
        item.set_zaxis_log_state(True)
        item.set_lut_range((0.5, 2.5))
        item.param.keep_lut_range = True

        second = np.array([[10.0, 100.0], [1000.0, 10000.0]])
        item.set_data(second)

        # Cache must still be refreshed (display correctness)…
        np.testing.assert_array_almost_equal(item._log_data, np.log10(second.clip(1)))
        # …but the LUT range must remain frozen as requested by the user.
        assert item.get_lut_range() == (0.5, 2.5)


def test_set_data_does_not_create_log_data_when_log_scale_disabled() -> None:
    """When log scale is off, ``set_data`` must not create ``_log_data``."""
    with qt_app_context(exec_loop=False):
        item = _make_item(np.array([[1.0, 2.0], [3.0, 4.0]]))
        assert item._log_data is None
        item.set_data(np.array([[5.0, 6.0], [7.0, 8.0]]))
        assert item._log_data is None
