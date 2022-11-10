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

SHOW = True  # Show test in GUI-based test launcher

import sys, os.path as osp

from plotpy.gui.widgets.ext_gui_lib import QApplication
from plotpy.gui.widgets.qtdesigner import loadui
from plotpy.gui.widgets.builder import make

FormClass = loadui(osp.splitext(__file__)[0] + ".ui")


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
