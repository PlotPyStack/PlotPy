# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
ColorMapManager test

This plotpy widget can be used to manage colormaps (visualize, edit, create ans save).
"""

# guitest: show

import pytest
import qtpy.QtCore as QC
import qtpy.QtGui as QG
from guidata.env import execenv
from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.mathutils.colormap import ALL_COLORMAPS, delete_cmap, get_cmap
from plotpy.widgets.colormap.manager import ColorMapManager
from plotpy.widgets.colormap.widget import EditableColormap


@pytest.fixture
def test_cmap(cmap_name="Kinda Viridis"):
    cmap = EditableColormap(
        [QG.QColor(QC.Qt.GlobalColor.blue), QG.QColor(QC.Qt.GlobalColor.yellow)],
        name=cmap_name,
    )
    yield cmap

    delete_cmap(get_cmap(cmap_name))


def test_colormap_manager(test_cmap: EditableColormap) -> None:
    """Test the colormap manager widget."""
    with qt_app_context(exec_loop=False):
        red = QG.QColor(QC.Qt.GlobalColor.red)
        cmap_editor = ColorMapManager(None, active_colormap="YlGn")
        cmap_editor.show()

        with execenv.context(accept_dialogs=True):
            cmap_editor.save_colormap(test_cmap)
        cmap_editor.colormap_editor.colormap_widget.add_handle_at_relative_pos(0.5, red)
        cmap_editor.get_colormap()
        cmap_editor.colormap_editor.update_colormap_widget()
        cmap_editor.colormap_editor.update_current_dataset()

        # set the colormap to last one
        with execenv.context(accept_dialogs=True):
            cmap_editor.remove_colormap()

        result = exec_dialog(cmap_editor)
        execenv.print("Dialog result:", result)
        cmap = cmap_editor.get_colormap()
        execenv.print("Selected colormap:", None if cmap is None else cmap.name)
        delete_cmap(test_cmap)


if __name__ == "__main__":
    test_name = "Kinda Viridis"
    new_colormap = EditableColormap(
        [QG.QColor(QC.Qt.GlobalColor.blue), QG.QColor(QC.Qt.GlobalColor.yellow)],
        name=test_name,
    )
    test_colormap_manager(new_colormap)
    delete_cmap(get_cmap(test_name))
