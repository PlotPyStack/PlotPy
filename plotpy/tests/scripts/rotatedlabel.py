# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
RotatedLabel test

RotatedLabel is derived from QLabel: it provides rotated text display.
"""

import sys

from qtpy import QtWidgets as QW
from qtpy.QtCore import Qt

from plotpy.widgets.labels import RotatedLabel

SHOW = True  # Show test in GUI-based test launcher


class Frame(QW.QFrame):
    def __init__(self, parent=None):
        QW.QFrame.__init__(self, parent)
        layout = QW.QGridLayout()
        self.setLayout(layout)
        angle = 0
        for row in range(7):
            for column in range(7):
                layout.addWidget(
                    RotatedLabel(
                        "Label %03d°" % angle, angle=angle, color=Qt.blue, bold=True
                    ),
                    row,
                    column,
                    Qt.AlignCenter,
                )
                angle += 10


if __name__ == "__main__":
    app = QW.QApplication([])
    frame = Frame()
    frame.show()
    sys.exit(app.exec_())
