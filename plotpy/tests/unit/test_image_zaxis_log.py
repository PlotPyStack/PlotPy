# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Z-axis logarithmic scale of image items (Issue #63).

With the Z-axis logarithmic scale, the colors are mapped to the base-10 logarithm
of the data, whereas the LUT range, the color bar, the contrast adjustment panel
and the cursor values remain in data units.
"""

from __future__ import annotations

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qwt import QwtInterval

from plotpy.builder import make
from plotpy.constants import LUT_MAX
from plotpy.items import assemble_imageitems
from plotpy.lutrange import lut_range_threshold
from plotpy.mathutils.colormap import LogScaleColorMap, get_cmap
from plotpy.tools import ZAxisLogTool

#: Data ranging from 1 to 10000, on a logarithmic scale
DATA = np.logspace(0, 4, 6 * 8).reshape(6, 8)

SUPPORTED_KINDS = ("image", "xyimage", "trimage", "maskedimage", "maskedxyimage")


def _make_item(kind: str, data: np.ndarray = DATA):
    """Return an image item of the given kind, without interpolation"""
    ny, nx = data.shape
    x, y = np.arange(nx, dtype=float), np.arange(ny, dtype=float)
    mask = np.zeros(data.shape, dtype=bool)
    builders = {
        "image": lambda: make.image(data, interpolation="nearest"),
        "xyimage": lambda: make.xyimage(x, y, data, interpolation="nearest"),
        "trimage": lambda: make.trimage(data, interpolation="nearest"),
        "maskedimage": lambda: make.maskedimage(data, mask, interpolation="nearest"),
        "maskedxyimage": lambda: make.maskedxyimage(
            x, y, data, mask, interpolation="nearest"
        ),
    }
    return builders[kind]()


def _expected_lut_values(item, values: np.ndarray) -> np.ndarray:
    """Return the LUT indexes expected for data values with the log scale"""
    lmin, lmax = np.log10(item.get_lut_range())
    lvalues = np.log10(np.maximum(values, item._log_floor))
    return (LUT_MAX * (lvalues - lmin) / (lmax - lmin)).clip(0, LUT_MAX)


@pytest.mark.parametrize("kind", SUPPORTED_KINDS)
def test_toggle_keeps_lut_range_in_data_units(kind: str) -> None:
    """Enabling the log scale sets the full positive range, in data units, and
    disabling it restores the previous LUT range"""
    with qt_app_context(exec_loop=False):
        item = _make_item(kind)
        assert item.supports_zaxis_log()
        item.set_lut_range((100.0, 5000.0))
        item.set_zaxis_log_state(True)
        assert item.get_zaxis_log_state()
        assert item.get_lut_range() == pytest.approx((1.0, 10000.0))
        assert item.get_lut_range_full() == pytest.approx((1.0, 10000.0))
        # Enabling it twice must not overwrite the saved linear range
        item.set_zaxis_log_state(True)
        item.set_zaxis_log_state(False)
        assert not item.get_zaxis_log_state()
        assert item.get_lut_range() == (100.0, 5000.0)


@pytest.mark.parametrize("kind", SUPPORTED_KINDS)
def test_cross_sections_apply_log_lut(kind: str) -> None:
    """Cross sections with `apply_lut=True` use the log color mapping"""
    with qt_app_context(exec_loop=False):
        item = _make_item(kind)
        item.set_zaxis_log_state(True)
        item.set_lut_range((2.0, 9000.0))
        iy = 3
        _x, raw = item.get_xsection(iy)
        _x, ydata = item.get_xsection(iy, apply_lut=True)
        np.testing.assert_allclose(ydata, _expected_lut_values(item, raw))
        assert len(np.unique(ydata)) > 1
        item.set_zaxis_log_state(False)
        _x, ydata = item.get_xsection(iy, apply_lut=True)
        a, b, _bg, _cmap = item.lut
        np.testing.assert_allclose(ydata, (raw * a + b).clip(0, LUT_MAX))


@pytest.mark.parametrize("kind", ("image", "maskedimage", "trimage"))
def test_export_roi_applies_log_lut(kind: str) -> None:
    """Exporting an image area with `apply_lut=True` uses the log color mapping"""
    with qt_app_context(exec_loop=False):
        item = _make_item(kind)
        item.set_zaxis_log_state(True)
        ny, nx = DATA.shape
        rect = QC.QRectF(0, 0, nx, ny)
        raw = assemble_imageitems([item], rect, nx, ny)
        output = assemble_imageitems([item], rect, nx, ny, apply_lut=True)
        inside = raw > 0  # Pixels outside the image are not exported
        assert np.count_nonzero(inside) > nx
        a, b, _bg, _cmap = item.lut
        np.testing.assert_allclose(
            output[inside], a * np.log10(raw[inside]) + b, rtol=1e-5, atol=1e-3
        )


def test_non_positive_values() -> None:
    """Values lower than or equal to zero get the lowest color, and the LUT range
    is clamped to the smallest positive value"""
    with qt_app_context(exec_loop=False):
        data = np.array([[-5.0, 0.0, np.nan], [0.5, 5.0, 50.0]])
        item = make.image(data, interpolation="nearest")
        item.set_zaxis_log_state(True)
        assert item.get_lut_range() == (0.5, 50.0)
        np.testing.assert_allclose(
            item._log_data,
            [[np.log10(0.5), np.log10(0.5), np.nan], np.log10([0.5, 5.0, 50.0])],
        )
        item.set_lut_range((-1.0, 5.0))
        assert item.get_lut_range() == (0.5, 5.0)
        item.set_lut_range((-2.0, -1.0))
        assert item.get_lut_range() == (0.5, 0.5)
        _x, ydata = item.get_xsection(0, apply_lut=True)
        assert ydata[0] == ydata[1]


def test_data_between_zero_and_one() -> None:
    """Data lower than 1 is no longer shown with a single color"""
    with qt_app_context(exec_loop=False):
        data = np.linspace(0.0, 1.0, 101).reshape(1, 101)
        item = make.image(data, interpolation="nearest")
        item.set_zaxis_log_state(True)
        assert item.get_lut_range() == (0.01, 1.0)
        _x, ydata = item.get_xsection(0, apply_lut=True)
        assert ydata[0] == ydata[1] == 0
        assert ydata[-1] == LUT_MAX
        assert np.all(np.diff(ydata[1:]) > 0)


def test_contrast_functions_in_data_units() -> None:
    """Full range and outliers elimination give LUT ranges in data units"""
    with qt_app_context(exec_loop=False):
        item = make.image(DATA, interpolation="nearest")
        item.set_zaxis_log_state(True)
        vmin, vmax = lut_range_threshold(item, 256, 1.0)
        assert 1.0 <= vmin < vmax <= 10000.0
        item.set_lut_threshold(1.0)
        assert item.get_lut_range() == pytest.approx((vmin, vmax))
        item.set_lut_range(item.get_lut_range_full())
        assert item.get_lut_range() == pytest.approx((1.0, 10000.0))


@pytest.mark.parametrize("kind", ("image", "maskedxyimage"))
def test_set_data_in_log_mode(kind: str) -> None:
    """`set_data` LUT ranges are in data units with the log scale"""
    with qt_app_context(exec_loop=False):
        item = _make_item(kind)
        item.set_zaxis_log_state(True)
        item.set_data(DATA * 10.0, lut_range=(50.0, 500.0))
        assert item.get_lut_range() == (50.0, 500.0)
        item.set_data(DATA * 10.0)
        assert item.get_lut_range() == pytest.approx((10.0, 100000.0))
        # Disabling the log scale gives the range that the data would have had
        item.set_zaxis_log_state(False)
        assert item.get_lut_range() == pytest.approx((10.0, 100000.0))


def test_anti_aliasing_kernel_follows_displayed_data() -> None:
    """The anti-aliasing kernel has the data type of the data drawn"""
    with qt_app_context(exec_loop=False):
        item = make.image(DATA.astype(np.uint16), interpolation="nearest")
        item.set_zaxis_log_state(True)
        item.set_interpolation(2, 3)  # INTERP_AA
        assert item.interpolate[1].dtype == np.float64
        item.set_zaxis_log_state(False)
        assert item.interpolate[1].dtype == np.uint16


def test_colorbar_in_data_units() -> None:
    """The color bar uses a log scale in data units, with the colors of the image"""
    with qt_app_context(exec_loop=False):
        win = make.dialog(type="image", toolbar=True)
        plot = win.manager.get_plot()
        item = make.image(DATA, colormap="jet", interpolation="nearest")
        plot.add_item(item)
        zaxis = plot.colormap_axis
        item.set_zaxis_log_state(True)
        assert plot.get_axis_scale(zaxis) == "log"
        scalediv = plot.axisScaleDiv(zaxis)
        assert (scalediv.lowerBound(), scalediv.upperBound()) == pytest.approx(
            (1.0, 10000.0)
        )
        widget = plot.axisWidget(zaxis)
        colormap = widget.colorMap()
        assert isinstance(colormap, LogScaleColorMap)
        assert colormap.colormap is item.get_color_map()
        interval = widget.colorBarInterval()
        assert (interval.minValue(), interval.maxValue()) == pytest.approx(
            (1.0, 10000.0)
        )
        # Switching to another item without log scale restores a linear color bar
        other = make.image(DATA, interpolation="nearest")
        plot.add_item(other)
        plot.set_active_item(other)
        assert plot.get_axis_scale(zaxis) == "lin"
        assert widget.colorMap() is other.get_color_map()
        plot.set_active_item(item)
        assert plot.get_axis_scale(zaxis) == "log"
        item.set_zaxis_log_state(False)
        assert plot.get_axis_scale(zaxis) == "lin"
        assert widget.colorMap() is item.get_color_map()
        win.close()


@pytest.mark.parametrize("invert", (False, True))
def test_log_scale_colormap_colors(invert: bool) -> None:
    """`LogScaleColorMap` applies the wrapped colormap to the log of values"""
    with qt_app_context(exec_loop=False):
        cmap = get_cmap("jet")
        old_invert = cmap.invert
        cmap.invert = invert
        try:
            logcmap = LogScaleColorMap(cmap)
            assert logcmap.format() == cmap.format()
            interval = QwtInterval(1.0, 10000.0)
            loginterval = QwtInterval(0.0, 4.0)
            for exponent in range(5):
                value = 10.0**exponent
                assert logcmap.rgb(interval, value) == cmap.rgb(loginterval, exponent)
                assert logcmap.colorIndex(interval, value) == cmap.colorIndex(
                    loginterval, exponent
                )
            assert logcmap.rgb(interval, 0.0) == cmap.rgb(loginterval, 0.0)
            assert logcmap.rgb(interval, -1.0) == cmap.rgb(loginterval, 0.0)
            # Not strictly positive intervals are left unchanged
            interval = QwtInterval(-1.0, 1.0)
            assert logcmap.rgb(interval, 0.5) == cmap.rgb(interval, 0.5)
        finally:
            cmap.invert = old_invert


def test_unsupported_items() -> None:
    """Items without log color mapping are ignored by the Z-axis log tool"""
    with qt_app_context(exec_loop=False):
        win = make.dialog(type="image", toolbar=True)
        plot = win.manager.get_plot()
        tool = win.manager.get_tool(ZAxisLogTool)
        rgb = make.rgbimage(np.zeros((6, 8, 3), dtype=np.uint8))
        rng = np.random.default_rng(0)
        hist2d = make.histogram2D(rng.normal(size=100), rng.normal(size=100), 8, 8)
        for item in (rgb, hist2d):
            assert not item.supports_zaxis_log()
            plot.add_item(item)
            item.set_zaxis_log_state(True)
            assert not item.get_zaxis_log_state()
        tool.update_status(plot)
        assert not tool.get_supported_items(plot)
        assert not tool.action.isEnabled()
        image = make.image(DATA)
        plot.add_item(image)
        tool.update_status(plot)
        assert tool.get_supported_items(plot) == [image]
        assert tool.action.isEnabled()
        win.close()


def test_tool_notifies_lut_change() -> None:
    """Toggling the Z-axis log scale updates the contrast panel range"""
    with qt_app_context(exec_loop=False):
        win = make.dialog(type="image", toolbar=True, show_contrast=True)
        plot = win.manager.get_plot()
        contrast = win.manager.get_contrast_panel()
        item = make.image(DATA, interpolation="nearest")
        plot.add_item(item)
        plot.set_active_item(item)
        plot.select_item(item)
        item.set_lut_range((100.0, 5000.0))
        emitted = []
        plot.SIG_LUT_CHANGED.connect(lambda _plot: emitted.append(True))
        tool = win.manager.get_tool(ZAxisLogTool)
        tool.activate()
        assert item.get_zaxis_log_state()
        assert emitted
        assert contrast.histogram.range.get_range() == pytest.approx((1.0, 10000.0))
        tool.activate()
        assert not item.get_zaxis_log_state()
        assert contrast.histogram.range.get_range() == pytest.approx((100.0, 5000.0))
        win.close()
