# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Test for MaskedImageItem dtype changes

This test verifies that changing the data type of a masked image from float to
integer types (like float64 to uint8) doesn't raise RuntimeWarnings when the
filling_value is NaN or None.
"""

from __future__ import annotations

import numpy as np
import pytest

from plotpy.builder import make


def test_masked_image_dtype_change_from_float_to_uint8():
    """Test changing masked image dtype from float64 to uint8 with NaN filling_value"""
    # Create a float64 masked array with NaN as fill value (the default)
    data = np.random.rand(10, 10).astype(np.float64)
    mask = np.zeros_like(data, dtype=bool)
    mask[3:5, 3:5] = True
    masked_data = np.ma.masked_array(data, mask=mask)

    # Create masked image item
    item = make.maskedimage(masked_data, colormap="viridis", show_mask=True)

    # Verify initial state
    assert item.data.dtype == np.float64

    # Set filling_value to NaN (typical for float images)
    item.param.filling_value = np.nan

    # Change data dtype to uint8
    new_data = (masked_data * 255).astype(np.uint8)
    item.set_data(new_data)

    # This should not raise a RuntimeWarning
    with pytest.warns(None) as warning_list:
        item.update_mask()

    # Check that no RuntimeWarning was raised
    runtime_warnings = [
        w for w in warning_list if issubclass(w.category, RuntimeWarning)
    ]
    assert len(runtime_warnings) == 0, "RuntimeWarning should not be raised"

    # Verify the data type changed
    assert item.data.dtype == np.uint8


def test_masked_image_dtype_change_with_none_filling_value():
    """Test changing masked image dtype with None filling_value"""
    # Create a float64 masked array
    data = np.random.rand(10, 10).astype(np.float64)
    mask = np.zeros_like(data, dtype=bool)
    mask[3:5, 3:5] = True
    masked_data = np.ma.masked_array(data, mask=mask)

    # Create masked image item
    item = make.maskedimage(masked_data, colormap="viridis", show_mask=True)

    # Set filling_value to None
    item.param.filling_value = None

    # Change data dtype to uint8
    new_data = (masked_data * 255).astype(np.uint8)
    item.set_data(new_data)

    # This should not raise a RuntimeWarning
    with pytest.warns(None) as warning_list:
        item.update_mask()

    # Check that no RuntimeWarning was raised
    runtime_warnings = [
        w for w in warning_list if issubclass(w.category, RuntimeWarning)
    ]
    assert len(runtime_warnings) == 0, "RuntimeWarning should not be raised"


def test_masked_image_filling_value_defaults():
    """Test that filling_value defaults are appropriate for different dtypes"""
    test_dtypes = [np.uint8, np.uint16, np.int16, np.float32, np.float64]

    for dtype in test_dtypes:
        data = np.random.rand(5, 5)
        if np.issubdtype(dtype, np.integer):
            data = (data * 100).astype(dtype)
        else:
            data = data.astype(dtype)

        mask = np.zeros_like(data, dtype=bool)
        mask[2:3, 2:3] = True
        masked_data = np.ma.masked_array(data, mask=mask)

        item = make.maskedimage(masked_data, colormap="viridis", show_mask=True)

        # Set filling_value to NaN (typical initial state for float images)
        item.param.filling_value = np.nan

        # This should handle the conversion gracefully
        with pytest.warns(None) as warning_list:
            item.update_mask()

        # Check that no RuntimeWarning was raised
        runtime_warnings = [
            w for w in warning_list if issubclass(w.category, RuntimeWarning)
        ]
        assert len(runtime_warnings) == 0, f"RuntimeWarning for dtype {dtype}"


if __name__ == "__main__":
    test_masked_image_dtype_change_from_float_to_uint8()
    test_masked_image_dtype_change_with_none_filling_value()
    test_masked_image_filling_value_defaults()
    print("All tests passed!")
