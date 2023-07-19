# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# -*- coding: utf-8 -*-
"""
Testing plotpy QtDesigner plugins

These plugins provide PlotWidget objects
embedding in GUI layouts directly from QtDesigner.
"""

# guitest: show

import os

from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.tests.gui.test_image import compute_image
from plotpy.widgets.qtdesigner import loadui

FormClass = loadui(os.path.splitext(__file__)[0] + ".ui")


class WindowTest(FormClass):
    def __init__(self, image_data):
        super(WindowTest, self).__init__()
        plot = self.imagewidget.plot
        plot.add_item(make.image(image_data))
        self.setWindowTitle("QtDesigner plugins example")


def test_qtdesigner():
    with qt_app_context(exec_loop=True):
        form = WindowTest(compute_image())
        form.show()


if __name__ == "__main__":
    test_qtdesigner()
