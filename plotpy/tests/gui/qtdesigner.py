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

from qtpy.QtWidgets import QApplication

from plotpy.widgets.builder import make
from plotpy.widgets.qtdesigner import loadui

SHOW = True  # Show test in GUI-based test launcher
FormClass = loadui(os.path.splitext(__file__)[0] + ".ui")


class TestWindow(FormClass):
    def __init__(self, image_data):
        super(TestWindow, self).__init__()
        plot = self.imagewidget.plot
        plot.add_item(make.image(image_data))
        self.setWindowTitle("QtDesigner plugins example")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from tests.gui.image import compute_image
    except ImportError:
        from plotpy.tests.gui.image import compute_image

    form = TestWindow(compute_image())
    form.show()
    sys.exit(app.exec_())
