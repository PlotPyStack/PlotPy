# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Plot computations test"""

import numpy
import pytest
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.constants import PlotType
from plotpy.plot import PlotDialog

list_offsets = [1e3, 1e6, 1e9, 1e12]


@pytest.mark.parametrize("offset", list_offsets)
def test_xyimagebug(offset):
    data = numpy.random.rand(100, 100)
    x = numpy.arange(100) + offset
    y = numpy.arange(100)
    with qt_app_context(exec_loop=True):
        image = make.xyimage(x, y, data=data)
        win = PlotDialog(options={"type": PlotType.IMAGE})
        plot = win.manager.get_plot()
        plot.add_item(image)
        plot.select_item(image)  # this helps in seeing where the image should be


if __name__ == "__main__":
    test_xyimagebug(1e9)
