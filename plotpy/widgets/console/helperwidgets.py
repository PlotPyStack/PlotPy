# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Helper widgets.
"""


from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.utils.icons import get_std_icon


class HelperToolButton(QW.QToolButton):
    """Subclasses QToolButton, to provide a simple tooltip on mousedown."""

    def __init__(self):
        QW.QToolButton.__init__(self)
        self.setIcon(get_std_icon("MessageBoxInformation"))
        style = """
            QToolButton {
              border: 1px solid grey;
              padding:0px;
              border-radius: 2px;
              background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                  stop: 0 #f6f7fa, stop: 1 #dadbde);
            }
            """
        self.setStyleSheet(style)

    def setToolTip(self, text):
        """

        :param text:
        """
        self._tip_text = text

    def toolTip(self):
        """

        :return:
        """
        return self._tip_text

    def mousePressEvent(self, event):
        """

        :param event:
        """
        QW.QToolTip.hideText()

    def mouseReleaseEvent(self, event):
        """

        :param event:
        """
        QW.QToolTip.showText(
            self.mapToGlobal(QC.QPoint(0, self.height())), self._tip_text
        )
