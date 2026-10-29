# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test curve downsampling methods (min/max and stride)"""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.items.curve.base import minmax_downsampling_indices


def _spiky_signal(size: int = 10_000, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Return a noisy signal with a few narrow peaks"""
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, size)
    y = 0.1 * rng.standard_normal(size)
    for index, height in ((1234, 5.0), (5001, -4.0), (8888, 3.0)):
        if index < size:
            y[index] = height
    return x, y


@pytest.mark.parametrize("factor", [2, 5, 10, 50, 333])
def test_minmax_indices(factor: int) -> None:
    """Min/max downsampling keeps extrema, first and last points"""
    _x, y = _spiky_signal()
    indices = minmax_downsampling_indices(y, factor)
    assert np.all(np.diff(indices) > 0)
    assert indices[0] == 0 and indices[-1] == y.size - 1
    assert indices.size <= 2 * -(-y.size // (2 * factor)) + 2
    for peak in (1234, 5001, 8888):
        assert peak in indices
    # Each group of 2 * factor points keeps its minimum and its maximum:
    for start in range(0, y.size, 2 * factor):
        group = y[start : start + 2 * factor]
        kept = y[indices[(indices >= start) & (indices < start + 2 * factor)]]
        assert kept.min() == group.min() and kept.max() == group.max()


def test_minmax_indices_special_cases() -> None:
    """Min/max downsampling of short, constant and NaN data"""
    assert np.array_equal(minmax_downsampling_indices(np.arange(5.0), 1), np.arange(5))
    assert np.array_equal(minmax_downsampling_indices(np.arange(2.0), 10), [0, 1])
    assert minmax_downsampling_indices(np.array([]), 10).size == 0
    constant = minmax_downsampling_indices(np.ones(100), 10)
    assert constant[0] == 0 and constant[-1] == 99
    y = np.arange(100.0)
    y[20:40] = np.nan  # A whole group of NaN values
    y[45] = np.nan  # A NaN value in a group of finite values
    indices = minmax_downsampling_indices(y, 10)
    assert np.count_nonzero(np.isnan(y[indices])) == 1  # The curve is interrupted
    assert 45 not in indices
    assert {40, 59} <= set(indices)


def test_curve_downsampling_methods() -> None:
    """Curve downsampling with the min/max (default) and stride methods"""
    with qt_app_context(exec_loop=False):
        x, y = _spiky_signal()
        curve = make.curve(x, y, dsamp_factor=50, use_dsamp=True)
        assert curve.param.dsamp_method == "minmax"
        indices = curve.get_dsamp_indices()
        assert np.array_equal(indices, minmax_downsampling_indices(y, 50))
        assert curve.dataSize() == indices.size
        assert curve.sample(int(np.searchsorted(indices, 1234))).y() == 5.0

        curve.param.dsamp_method = "stride"
        curve.update_params()
        assert np.array_equal(curve.get_dsamp_indices(), np.arange(0, y.size, 50))
        assert curve.dataSize() == y[::50].size

        curve.param.use_dsamp = False
        curve.update_params()
        assert curve.get_dsamp_indices() is None
        assert curve.dataSize() == y.size
        assert np.array_equal(curve.dsamp(y), y)


def test_errorbar_downsampling() -> None:
    """Error bars are downsampled like the curve data"""
    with qt_app_context(exec_loop=False):
        x, y = _spiky_signal(2000)
        dy = np.linspace(0.1, 0.2, x.size)
        item = make.error(x, y, None, dy, dsamp_factor=10, use_dsamp=True)
        indices = item.get_dsamp_indices()
        assert indices is not None and indices.size == item.dataSize()
        assert np.array_equal(item.dsamp(dy), dy[indices])
        assert item.dsamp(None) is None
        _xmin, _xmax, ymin, ymax = item.get_minmax_arrays()
        assert np.allclose(ymin, y[indices] - dy[indices])
        assert np.allclose(ymax, y[indices] + dy[indices])


def test_frozen_downsampling() -> None:
    """Points kept by downsampling may be frozen while the data is updated"""
    with qt_app_context(exec_loop=False):
        x, y = _spiky_signal(2000)
        curve = make.curve(x, y, dsamp_factor=10, use_dsamp=True)
        indices = curve.get_dsamp_indices().copy()
        y2 = y.copy()
        y2[1234] = 0.0  # The peak is no longer a maximum of its group
        with curve.frozen_downsampling():
            curve.set_data(x, y2)
            assert np.array_equal(curve.get_dsamp_indices(), indices)
            # The number of points changes: the kept points are computed again
            curve.set_data(x[:-1], y2[:-1])
            assert curve.get_dsamp_indices()[-1] == x.size - 2
        curve.set_data(x, y2)
        assert 1234 not in curve.get_dsamp_indices()


def test_hit_test_and_move_point() -> None:
    """Handles of downsampled curves are indices of the points kept"""
    with qt_app_context(exec_loop=False):
        x, y = _spiky_signal(2000)
        curve = make.curve(x, y, dsamp_factor=10, use_dsamp=True)
        curve.immutable = False
        win = make.dialog(type="curve")
        plot = win.manager.get_plot()
        plot.add_item(curve)
        win.resize(800, 600)
        win.show()
        QW.QApplication.processEvents()
        plot.replot()
        indices = curve.get_dsamp_indices()
        handle = int(np.searchsorted(indices, 1234))
        ax, ay = curve.xAxis(), curve.yAxis()
        # Slightly beside the peak (`hit_test` ignores positions exactly on points)
        pos = QC.QPointF(
            plot.transform(ax, x[1234]) + 0.3, plot.transform(ay, y[1234]) + 0.3
        )
        _distance, attach, _inside, _other = curve.hit_test(pos)
        assert attach in (handle - 1, handle)
        # Moving the handle moves the corresponding point of the curve data:
        new_pos = QC.QPointF(pos.x(), plot.transform(ay, 1.0))
        curve.move_local_point_to(handle, new_pos)
        _x, new_y = curve.get_data()
        assert new_y[1234] == pytest.approx(1.0, abs=0.05)
        assert curve.sample(handle).y() == new_y[1234]  # Still drawn
        win.close()
