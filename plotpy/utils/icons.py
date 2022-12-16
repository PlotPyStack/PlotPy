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
plotpy.gui.utils.icons
----------------------

The ``plotpy.gui.utils.icons`` module provides helper functions for developing
easily Qt-based graphical user interfaces.
"""
import sys

from qtpy import QtGui as QG
from qtpy import QtWidgets as QW


def get_std_icon(name, size=None):
    """
    Get standard platform icon
    Call "show_std_icons()" for details
    """
    if not name.startswith("SP_"):
        name = "SP_" + name
    icon = QW.QWidget().style().standardIcon(getattr(QW.QStyle, name))
    if size is None:
        return icon
    else:
        return QG.QIcon(icon.pixmap(size, size))


def show_std_icons():
    """
    Show all standard Icons
    """
    app = QW.QApplication(sys.argv)
    dialog = ShowStdIcons(None)
    dialog.show()
    sys.exit(app.exec_())


class ShowStdIcons(QW.QWidget):
    """
    Dialog showing standard icons
    """

    def __init__(self, parent):
        QW.QWidget.__init__(self, parent)
        layout = QW.QHBoxLayout()
        row_nb = 14
        cindex = 0
        for child in dir(QW.QStyle):
            if child.startswith("SP_"):
                if cindex == 0:
                    col_layout = QW.QVBoxLayout()
                icon_layout = QW.QHBoxLayout()
                icon = get_std_icon(child)
                label = QW.QLabel()
                label.setPixmap(icon.pixmap(32, 32))
                icon_layout.addWidget(label)
                icon_layout.addWidget(QW.QLineEdit(child.replace("SP_", "")))
                col_layout.addLayout(icon_layout)
                cindex = (cindex + 1) % row_nb
                if cindex == 0:
                    layout.addLayout(col_layout)
        self.setLayout(layout)
        self.setWindowTitle("Standard Platform Icons")
        self.setWindowIcon(get_std_icon("TitleBarMenuButton"))
