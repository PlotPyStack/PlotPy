import unittest

import numpy as np

from plotpy.items.contour import compute_contours
from plotpy.tests.data import gen_xyz_data


class ContourTest(unittest.TestCase):
    """
    Test case for contour() function

    Test data are borrowed from https://matplotlib.org/gallery/images_contours_and_fields/contour_demo.html#sphx-glr-gallery-images-contours-and-fields-contour-demo-py

    """

    def setUp(self):
        self.X, self.Y, self.Z = gen_xyz_data()

    def test_contour_level_1(self):
        """Test that contour() returns one closed line when level is 1.0"""
        # Ortho coord
        lines = compute_contours(self.Z, 1.0, self.X, self.Y)
        assert len(lines) == 1
        assert np.all(np.equal(lines[0].vertices[0], lines[0].vertices[-1]))
        assert lines[0].level == 1.0

        # Grid coord
        lines = compute_contours(self.Z, 1.0, self.X, self.Y)
        assert len(lines) == 1
        assert np.all(np.equal(lines[0].vertices[0], lines[0].vertices[-1]))
        assert lines[0].level == 1.0

    def test_contour_level_diag_0(self):
        """Test that contour() returns opened lines (diagonal) when level is 0.0"""
        lines = compute_contours(self.Z, 0.0, self.X, self.Y)
        assert len(lines) == 1
        assert np.any(lines[0].vertices[0] != lines[0].vertices[-1])
        assert lines[0].level == 0.0

    def test_contour_level_opened_neg_0_5(self):
        """Test that contour() returns opened lines when level is -0.5"""
        lines = compute_contours(self.Z, -0.5, self.X, self.Y)
        assert len(lines) == 1
        assert np.any(lines[0].vertices[0] != lines[0].vertices[-1])
        assert lines[0].level == -0.5

    def test_contour_abs_level_1(self):
        """Test that contour() returns two closed lines when level is 1.0
        and data are absolute.
        """
        lines = compute_contours(np.abs(self.Z), 1.0, self.X, self.Y)
        assert len(lines) == 2
        for line in lines:
            assert np.all(np.equal(line.vertices[0], line.vertices[-1]))
            assert line.level == 1.0
