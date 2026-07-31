# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Contour builder test"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.items import ContourItem
from plotpy.tests import vistools as ptv


def create_two_gaussians() -> np.ndarray:
    """Create two nearby 2D Gaussians with different shapes."""
    axis = np.linspace(-5.0, 5.0, 300)
    x, y = np.meshgrid(axis, axis)
    wide = np.exp(-((x + 0.9) ** 2 + (y + 0.2) ** 2) / (2.0 * 1.2**2))
    narrow = 0.65 * np.exp(-((x - 1.0) ** 2 + (y - 0.4) ** 2) / (2.0 * 0.6**2))
    return wide + narrow


def test_contours():
    """Contour plotting on two nearby 2D Gaussians"""
    with qt_app_context(exec_loop=True):
        image = create_two_gaussians()
        contour_items = make.contours(image, np.linspace(0.2, 1.0, 5))

        assert contour_items
        assert all(isinstance(item, ContourItem) for item in contour_items)

        _win = ptv.show_items(
            [make.image(image, colormap="cool")] + contour_items,
            wintitle=test_contours.__doc__,
            curve_antialiasing=False,
            lock_aspect_ratio=True,
        )


if __name__ == "__main__":
    test_contours()
