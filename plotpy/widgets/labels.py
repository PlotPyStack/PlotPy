# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
plotpy.gui.widgets.labels
-------------------------

The ``plotpy.gui.widgets.labels`` module provides ready-to-use or generic widgets
for developing easily Qt-based graphical user interfaces.
"""

from math import cos, pi, sin

from guidata.configtools import get_family
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW


class RotatedLabel(QW.QLabel):
    """
    Rotated QLabel
    (rich text is not supported)

    Arguments:
        * parent: parent widget
        * angle=270 (int): rotation angle in degrees
        * family (string): font family
        * bold (bool): font weight
        * italic (bool): font italic style
        * color (QColor): font color
    """

    def __init__(
        self,
        text,
        parent=None,
        angle=270,
        family=None,
        bold=False,
        italic=False,
        color=None,
    ):
        QW.QLabel.__init__(self, text, parent)
        font = self.font()
        if family is not None:
            font.setFamily(get_family(family))
        font.setBold(bold)
        font.setItalic(italic)
        self.setFont(font)
        self.color = color
        self.angle = angle
        self.setAlignment(QC.Qt.AlignCenter)

    def paintEvent(self, evt):
        """

        :param evt:
        """
        painter = QG.QPainter(self)
        if self.color is not None:
            painter.setPen(QG.QPen(self.color))
        painter.rotate(self.angle)
        transform = painter.transform().inverted()[0]
        rct = transform.mapRect(self.rect())
        painter.drawText(rct, self.alignment(), self.text())

    def sizeHint(self):
        """

        :return:
        """
        hint = QW.QLabel.sizeHint(self)
        width, height = hint.width(), hint.height()
        angle = self.angle * pi / 180
        rotated_width = int(abs(width * cos(angle)) + abs(height * sin(angle)))
        rotated_height = int(abs(width * sin(angle)) + abs(height * cos(angle)))
        return QC.QSize(rotated_width, rotated_height)

    def minimumSizeHint(self):
        """

        :return:
        """
        return self.sizeHint()
