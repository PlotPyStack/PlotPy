# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
ColorMapManager test

This plotpy widget can be used to manage colormaps (visualize, edit, create ans save).
"""

# guitest: show

import qtpy.QtCore as QC
import qtpy.QtGui as QG
from guidata.qthelpers import qt_app_context

from plotpy.mathutils.colormaps import ALL_COLORMAPS
from plotpy.widgets.colormap_manager import ColorMapManager
from plotpy.widgets.colormap_widget import CustomQwtLinearColormap


def test_colormap_manager() -> None:
    """Test the colormap manager widget."""
    with qt_app_context(exec_loop=True):
        red = QG.QColor(QC.Qt.GlobalColor.red)
        blue = QG.QColor(QC.Qt.GlobalColor.blue)
        yellow = QG.QColor(QC.Qt.GlobalColor.yellow)
        cmap = CustomQwtLinearColormap(blue, yellow, name="kinda_viridis")
        ALL_COLORMAPS["kinda_viridis"] = cmap
        editor = ColorMapManager(None, active_colormap="YlGn")
        editor.colormap_editor.colormap_widget.add_handle_at_relative_pos(0.5, red)
        editor.get_colormap()
        editor.colormap_editor.update_colormap_widget()
        editor.colormap_editor.update_current_dataset()
        editor.show()


if __name__ == "__main__":
    test_colormap_manager()
