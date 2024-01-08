# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Builder tests"""

# guitest: show

import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW

from plotpy.widgets.colormap_manager import ColorMapManager

# from plotpy.widgets.colormap_widget import CustomQwtLinearColormap

if __name__ == "__main__":
    print("Initialization of a default colormap editor widget")
    app = QW.QApplication([])
    editor = ColorMapManager(None)
    red = QG.QColor(QC.Qt.GlobalColor.red)
    editor.show()
    app.exec_()
