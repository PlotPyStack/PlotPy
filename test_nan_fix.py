#!/usr/bin/env python3
"""
Test script to verify the NaN handling fix in ErrorBarCurveItem
"""

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make


def test_nan_errorbar_fix():
    """Test that ErrorBarCurveItem handles all-NaN data gracefully"""
    print("Testing ErrorBar curve with all-NaN data...")

    with qt_app_context():
        # Create data with all NaN values (this was causing the error)
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0]) * np.nan
        dx = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        dy = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])

        # Create errorbar curve
        curve = make.merror(x, y, dx, dy, title="Test curve with NaN")

        # Test that boundingRect doesn't crash (this was the original issue)
        try:
            bbox = curve.boundingRect()
            print(f"✓ boundingRect() succeeded: {bbox}")
        except Exception as e:
            print(f"✗ boundingRect() failed: {e}")
            return False

        # Test that get_minmax_arrays works
        try:
            _ = curve.get_minmax_arrays()
            print("✓ get_minmax_arrays() succeeded")
        except Exception as e:
            print(f"✗ get_minmax_arrays() failed: {e}")
            return False

        print("✓ All tests passed! NaN handling fix is working correctly.")
        return True


if __name__ == "__main__":
    test_nan_errorbar_fix()
