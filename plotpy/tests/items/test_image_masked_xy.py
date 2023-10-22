# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Masked Image test, creating the MaskedXYImageItem object via make.maskedxyimage

Masked image XY items are constructed using a masked array item. Masked data is
ignored in computations, like the average cross sections.
"""

# guitest: show

from __future__ import annotations

from plotpy import io
from plotpy.builder import make
from plotpy.tests.items.test_image_masked import MaskedImageTest


class XYMaskedImageTest(MaskedImageTest):
    """XYMaskedImageItem test class"""

    def build_items(self) -> list:
        """Build items"""
        data = io.imread(self.IMAGE_FN, to_grayscale=True)
        x = [0]
        delta = 1
        for x_val in range(data.shape[0] - 1):
            delta = delta + 0.1
            x.append(x[-1] + delta)
        y = [0]
        for y_val in range(data.shape[1] - 1):
            delta = delta + 0.1
            y.append(y[-1] + delta)
        image = make.maskedimage(data=data, colormap="gray", show_mask=True, x=x, y=y)
        return [image]


def test_image_masked_xy():
    """Test MaskedImageItem"""
    test = XYMaskedImageTest("MaskedImageItem test")
    test.run()


if __name__ == "__main__":
    test_image_masked_xy()
