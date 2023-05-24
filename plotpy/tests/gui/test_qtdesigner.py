# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# -*- coding: utf-8 -*-
"""
Testing plotpy QtDesigner plugins

These plugins provide PlotWidget objects
embedding in GUI layouts directly from QtDesigner.
"""


import os
import sys

import guidata
import pytest
from qtpy import QtWidgets as QW

from plotpy.core.builder import make
from plotpy.tests.gui.test_image import compute_image
from plotpy.widgets.qtdesigner import loadui

SHOW = True  # Show test in GUI-based test launcher
FormClass = loadui(os.path.splitext(__file__)[0] + ".ui")


class WindowTest(FormClass):
    def __init__(self, image_data):
        super(WindowTest, self).__init__()
        plot = self.imagewidget.plot
        plot.add_item(make.image(image_data))
        self.setWindowTitle("QtDesigner plugins example")


def test_qtdesigner():
    _app = guidata.qapplication()

    form = WindowTest(compute_image())
    form.show()
    # sys.exit(app.exec())


if __name__ == "__main__":
    pytest.main()
