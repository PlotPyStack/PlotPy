# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Builder tests"""

# guitest: show

import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW

from plotpy.widgets.colormap_editor import ColorMapEditor
from plotpy.widgets.colormap_widget import CustomQwtLinearColormap

if __name__ == "__main__":
    print("Initialization of a default colormap editor widget")
    app = QW.QApplication([])
    editor = ColorMapEditor(None)
    red = QG.QColor(QC.Qt.GlobalColor.red)
    editor.colormap_widget.add_handle_at_relative_pos(0.5, red)
    editor.show()
    app.exec_()

    cmap_tuples = editor.getColormap().to_tuples()
    print(
        "Initialization of a new colormap editor with the previous colormap: ",
        cmap_tuples,
    )
    new_cmap = CustomQwtLinearColormap.from_iterable(cmap_tuples)
    print(f"{new_cmap.to_tuples()}")
    editor = ColorMapEditor(None, colormap=new_cmap)
    editor.show()
    app.exec_()

    cmap_tuples = editor.getColormap().to_tuples()
    print(
        "Initialization of a new default colormap editor, "
        "modified post-initialization with the previous colormap: ",
        cmap_tuples,
    )
    new_cmap = CustomQwtLinearColormap.from_iterable(cmap_tuples)
    editor = ColorMapEditor(None)
    editor.setColormap(new_cmap)
    editor.show()
    app.exec_()

    cmap_tuples = editor.getColormap().to_tuples()
    cmap_tuples = tuple((int(val * 255 + 1), color) for val, color in cmap_tuples)
    print(
        "Initialization of a new default colormap editor, "
        "modified post-initialization with the previous colormap with stops scaled by * 255 + 1: ",
        cmap_tuples,
    )
    new_cmap = CustomQwtLinearColormap.from_iterable(cmap_tuples)
    editor = ColorMapEditor(None)
    editor.setColormap(new_cmap)
    editor.show()
    app.exec_()
