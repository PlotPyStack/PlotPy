# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
ColorMapEditor test

This plotpy widget can be used to edit and visualize a colormap. This test is used
to verify the consistancy of the colormap editor widget and some of the
CustomQwtLinearColormap features like initialization from a list of tuples or
modifications.
"""

# guitest: show

import qtpy.QtCore as QC
import qtpy.QtGui as QG
from guidata.qthelpers import qt_app_context

from plotpy.widgets.colormap.editor import ColorMapEditor
from plotpy.widgets.colormap.widget import CustomQwtLinearColormap


def test_colormap_manager() -> None:
    """Test the colormap editor widget and the CustomQwtLinearColormap class
    by using multiple methods to initialize and export the colormap.
    """
    with qt_app_context(exec_loop=True):
        print("Initialization of a default colormap editor widget")
        editor = ColorMapEditor(None)
        red = QG.QColor(QC.Qt.GlobalColor.red)
        green = QG.QColor(QC.Qt.GlobalColor.green)
        editor.colormap_widget.add_handle_at_relative_pos(0.5, red)
        editor.show()

        cmap_tuples = editor.get_colormap().to_tuples()
        print(
            "Initialization of a new colormap editor with the previous colormap: ",
            cmap_tuples,
        )
        new_cmap = CustomQwtLinearColormap.from_iterable(cmap_tuples)
        print(f"{new_cmap.to_tuples()}")
        editor = ColorMapEditor(None, colormap=new_cmap)
        editor.show()

        cmap_tuples = editor.get_colormap().to_tuples()
        print(
            "Initialization of a new default colormap editor, "
            "modified post-initialization with the previous colormap: ",
            cmap_tuples,
        )
        new_cmap = CustomQwtLinearColormap.from_iterable(cmap_tuples)
        editor = ColorMapEditor(None)
        editor.set_colormap(new_cmap)
        editor.show()

        cmap_tuples = editor.get_colormap().to_tuples()
        cmap_tuples = tuple((int(val * 255 + 1), color) for val, color in cmap_tuples)
        print(
            "Initialization of a new default colormap editor, "
            "modified post-initialization with the previous colormap with stops scaled by "
            "255 + 1: ",
            cmap_tuples,
        )
        new_cmap = CustomQwtLinearColormap.from_iterable(cmap_tuples)
        editor = ColorMapEditor(None)
        editor.set_colormap(new_cmap)
        editor.show()

        print(
            "Initialization of a new default colormap editor, "
            "modified post-initialization with the previous colormap where the red stop is "
            "replaced with a green stop: ",
            cmap_tuples,
        )

        editor = ColorMapEditor(None)
        editor.set_colormap(new_cmap)
        editor.colormap_widget.edit_color_stop(1, None, green)
        editor.show()


if __name__ == "__main__":
    test_colormap_manager()
