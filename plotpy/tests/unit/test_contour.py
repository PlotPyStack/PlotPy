import unittest

import numpy as np

from plotpy.widgets.contour import contour


class ContourTest(unittest.TestCase):
    """
    Test case for contour() function

    Test data are borrowed from https://matplotlib.org/gallery/images_contours_and_fields/contour_demo.html#sphx-glr-gallery-images-contours-and-fields-contour-demo-py

    """

    def setUp(self):
        delta = 0.025
        self.x = np.arange(-3.0, 3.0, delta)
        self.y = np.arange(-2.0, 2.0, delta)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        Z1 = np.exp(-self.X**2 - self.Y**2)
        Z2 = np.exp(-((self.X - 1) ** 2) - (self.Y - 1) ** 2)
        self.Z = (Z1 - Z2) * 2

    def test_contour_level_1(self):
        """Test that contour() returns one closed line when level is 1.0"""
        # Ortho coord
        lines = contour(self.x, self.y, self.Z, 1.0)
        assert len(lines) == 1
        assert np.all(np.equal(lines[0].vertices[0], lines[0].vertices[-1]))
        assert lines[0].level == 1.0

        # Grid coord
        lines = contour(self.X, self.Y, self.Z, 1.0)
        assert len(lines) == 1
        assert np.all(np.equal(lines[0].vertices[0], lines[0].vertices[-1]))
        assert lines[0].level == 1.0

    def test_contour_level_diag_0(self):
        """Test that contour() returns opened lines (diagonal) when level is 0.0"""
        lines = contour(self.X, self.Y, self.Z, 0.0)
        assert len(lines) == 1
        assert np.all(lines[0].vertices[0] != lines[0].vertices[-1])
        assert lines[0].level == 0.0

    def test_contour_level_opened_neg_0_5(self):
        """Test that contour() returns opened lines when level is -0.5"""
        lines = contour(self.X, self.Y, self.Z, -0.5)
        assert len(lines) == 1
        assert np.all(lines[0].vertices[0] != lines[0].vertices[-1])
        assert lines[0].level == -0.5

    def test_contour_abs_level_1(self):
        """Test that contour() returns two closed lines when level is 1.0
        and data are absolute.
        """
        lines = contour(self.x, self.y, np.abs(self.Z), 1.0)
        assert len(lines) == 2
        for line in lines:
            assert np.all(np.equal(line.vertices[0], line.vertices[-1]))
            assert line.level == 1.0
