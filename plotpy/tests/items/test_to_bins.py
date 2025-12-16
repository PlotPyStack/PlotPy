# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test for to_bins function used in XYImageItem"""

import numpy as np

from plotpy.items.image.filter import to_bins


def test_to_bins_single_element():
    """Test to_bins with a single-element array.

    This is a regression test for the bug where loading an image with only
    1 row (e.g., SIF files with shape (1, N)) caused an IndexError because
    to_bins assumed at least 2 elements to compute bin edges.
    """
    x = np.array([5.0])
    result = to_bins(x)

    # Should return 2 bin edges, centered around the single point
    assert len(result) == 2
    assert result[0] == 4.5  # x[0] - 0.5
    assert result[1] == 5.5  # x[0] + 0.5


def test_to_bins_two_elements():
    """Test to_bins with a two-element array."""
    x = np.array([1.0, 3.0])
    result = to_bins(x)

    # Should return 3 bin edges
    assert len(result) == 3
    np.testing.assert_allclose(result, [0.0, 2.0, 4.0])


def test_to_bins_multiple_elements():
    """Test to_bins with multiple elements (uniform spacing)."""
    x = np.array([1.0, 2.0, 3.0, 4.0])
    result = to_bins(x)

    # Should return 5 bin edges
    assert len(result) == 5
    np.testing.assert_allclose(result, [0.5, 1.5, 2.5, 3.5, 4.5])


def test_to_bins_non_uniform_spacing():
    """Test to_bins with non-uniform spacing."""
    x = np.array([0.0, 1.0, 4.0])
    result = to_bins(x)

    # Should return 4 bin edges
    # First edge: 0.0 - (1.0 - 0.0) / 2 = -0.5
    # Middle: (0.0 + 1.0) / 2 = 0.5, (1.0 + 4.0) / 2 = 2.5
    # Last edge: 4.0 + (4.0 - 1.0) / 2 = 5.5
    assert len(result) == 4
    np.testing.assert_allclose(result, [-0.5, 0.5, 2.5, 5.5])


if __name__ == "__main__":
    test_to_bins_single_element()
    test_to_bins_two_elements()
    test_to_bins_multiple_elements()
    test_to_bins_non_uniform_spacing()
    print("All tests passed!")
