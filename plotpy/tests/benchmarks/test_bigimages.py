# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test showing 10 big images"""

# guitest: show

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context

from plotpy.builder import make


def imshow():
    win = make.dialog(
        toolbar=True, title="Displaying 10 big images test", size=(800, 600)
    )
    plot = win.manager.get_plot()
    for i in range(10):
        plot.add_item(make.image(compute_image(i)))
    win.show()
    return win


def compute_image(i, N=7500, M=1750):
    if i % 2 == 0:
        N, M = M, N
    return (np.random.rand(N, M) * 65536).astype(np.int16)


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_bigimages():
    """Test Bigimages"""
    with qt_app_context(exec_loop=True):
        _persist_obj = imshow()


if __name__ == "__main__":
    test_bigimages()
