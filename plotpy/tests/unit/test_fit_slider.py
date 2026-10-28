# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve fitting parameter sliders: values outside the slider range, non-finite
values and invalid inputs keep the fit dialog usable."""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context

from plotpy.widgets.fit import FitDialog, FitParam, FitParamDataSet


def _param(
    value: float = 0.5, vmin: float = 0.0, vmax: float = 1.0, logscale: bool = False
) -> FitParam:
    """Return a fit parameter with its widgets, updated for the given value"""
    param = FitParam("p", 0.5, 0.0, 1.0, logscale=logscale)
    param.create_widgets(None, lambda: None)
    param.min, param.max, param.value = vmin, vmax, value
    param.update()
    return param


def _has_range_warning(param: FitParam) -> bool:
    """Return True if the parameter shows the out-of-range warning"""
    return param.range_warning.isVisible() and bool(param.lineedit.toolTip())


@pytest.mark.parametrize("logscale", [False, True])
@pytest.mark.parametrize("value", [1e15, 2.0, -1.0, -1e15])
def test_value_outside_range_clamps_slider(value: float, logscale: bool):
    """The slider stays at the nearest end and a warning is shown."""
    with qt_app_context(exec_loop=False):
        param = _param(value, logscale=logscale)
        expected = param.steps - 1 if value > param.max else 0
        assert param.slider.value() == expected
        assert not param.slider.signalsBlocked()
        assert param.value == value
        assert _has_range_warning(param)
        param.value = 0.5
        param.update()
        assert not _has_range_warning(param)


@pytest.mark.parametrize(
    "value, vmin, vmax",
    [
        (np.nan, 0.0, 1.0),
        (np.inf, 0.0, 1.0),
        (-np.inf, 0.0, 1.0),
        (2.0, 1.0, 1.0),
        (np.float64(2.0), 1.0, 1.0),
        (1e308, -1e308, 1e308),
    ],
)
def test_undefined_slider_position(value: float, vmin: float, vmax: float):
    """Non-finite values and empty ranges leave the slider position unchanged."""
    with qt_app_context(exec_loop=False):
        param = _param(0.5)
        position = param.slider.value()
        param.min, param.max, param.value = vmin, vmax, value
        param.update()
        assert param.slider.value() == position
        assert not param.slider.signalsBlocked()


@pytest.mark.parametrize("logscale", [False, True])
def test_slider_mapping_round_trip(logscale: bool):
    """Slider position -> value -> slider position gives the same position."""
    with qt_app_context(exec_loop=False):
        param = _param(0.5, 0.0, 10.0, logscale)
        last = param.steps - 1
        for position in (0, 1, 1234, last - 1, last):
            param.slider_value_changed(position)
            param.update_slider_value()
            assert param.slider.value() == position
        param.value = param.min
        param.update_slider_value()
        assert param.slider.value() == 0
        param.value = param.max
        param.update_slider_value()
        assert param.slider.value() == last


def test_autofit_with_value_far_outside_range():
    """All parameters are updated when the fit leaves a slider range."""
    x = np.linspace(0.0, 1.0, 50)
    y = 1e6 * x + 3.0

    def fitfunc(x: np.ndarray, params: list[float]) -> np.ndarray:
        a, b = params
        return a * x + b

    with qt_app_context(exec_loop=False):
        # The fitted slope is 1e6 times the slider range width: its slider position
        # used to exceed the 32-bit integer range accepted by `QSlider.setValue`
        params = [FitParam("a", 0.5, 0.0, 1.0), FitParam("b", 0.0, -5.0, 5.0)]
        dialog = FitDialog(edit=True, auto_fit=True)
        dialog.set_data(x, y, fitfunc, params)
        dialog.autofit()
        a, b = params
        assert a.value == pytest.approx(1e6)
        assert b.value == pytest.approx(3.0)
        for param in params:
            assert param.lineedit.text() == param.format % param.value
            assert not param.slider.signalsBlocked()
        assert a.slider.value() == a.steps - 1
        assert _has_range_warning(a)
        assert not _has_range_warning(b)
        dialog.close()


@pytest.mark.parametrize("text", ["nan", "inf", "-inf", "abc", ""])
def test_line_edit_rejects_invalid_values(text: str):
    """Typing a non-numeric or non-finite value restores the previous value."""
    with qt_app_context(exec_loop=False):
        param = _param(0.5)
        param.lineedit.setText(text)
        param.line_editing_finished()
        assert param.value == 0.5
        assert param.lineedit.text() == param.format % 0.5


def test_line_edit_accepts_large_values():
    """A large finite value is accepted, with the slider at its end."""
    with qt_app_context(exec_loop=False):
        param = _param(0.5)
        param.lineedit.setText("1e300")
        param.line_editing_finished()
        assert param.value == 1e300
        assert param.slider.value() == param.steps - 1
        assert _has_range_warning(param)


def test_steps_minimum():
    """The parameter properties dialog requires at least two slider steps."""
    assert not FitParamDataSet.steps.check_value(1)
    assert FitParamDataSet.steps.check_value(2)
