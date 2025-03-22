# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Dot array example
=================

Example showing how to create a custom item (drawing dots of variable size)
and integrate the associated `guidata` dataset (GUI-based form) to edit its
parameters (directly into the same window as the plot itself, *and* within
the custom item parameters: right-click on the selectable item to open the
associated dialog box).
"""

# guitest: show

from __future__ import annotations

from typing import TYPE_CHECKING

import guidata.dataset as gds
import guidata.dataset.qtwidgets as gdq
import numpy as np
from guidata.configtools import get_image_file_path
from guidata.qthelpers import qt_app_context
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

import plotpy.config  # Loading icons  # noqa: F401
from plotpy.interfaces import IImageItemType
from plotpy.items import RawImageItem
from plotpy.items.curve.errorbar import vmap
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.styles import RawImageParam
from plotpy.tools import CopyToClipboardTool, HelpTool, PrintTool, SaveAsTool

if TYPE_CHECKING:
    from plotpy.interfaces import IItemType


class DotArrayParam(gds.DataSet):
    """Dot array"""

    def _update_cb(self, *args):
        """Update callback, to be overriden"""
        pass

    g1 = gds.BeginGroup("Size of the area")
    dim_h = gds.FloatItem("Width", default=20, min=0, unit="mm")
    dim_v = gds.FloatItem("Height", default=20, min=0, unit="mm")
    _g1 = gds.EndGroup("Size of the area")

    g2 = gds.BeginGroup("Grid pattern properties")
    step_x = gds.FloatItem("Step in X-axis", default=1, min=1, unit="mm")
    step_y = gds.FloatItem("Step in Y-axis", default=1, min=1, unit="mm")
    size = gds.FloatItem("Dot size", default=0.2, min=0, max=2, slider=True, unit="mm")
    color = gds.ColorItem("Dot color", default="red")
    _g2 = gds.EndGroup("Grid pattern properties")

    def update_item(self, obj):
        """Update item from parameters"""
        self._update_cb()

    def update_param(self, obj):
        """Update parameters from object"""
        pass


class DotArrayRawImageParam(RawImageParam, DotArrayParam):
    pass


class DotArrayItem(RawImageItem):
    """Dot array item"""

    def __init__(self, param=None):
        super().__init__(np.zeros((1, 1)), param)
        self.update_border()

    def boundingRect(self):
        """Reimplemented to return the bounding rectangle of the item"""
        param = self.param
        if param is not None:
            return QC.QRectF(
                QC.QPointF(-0.5 * param.size, -0.5 * param.size),
                QC.QPointF(
                    param.dim_h + 0.5 * param.size, param.dim_v + 0.5 * param.size
                ),
            )

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IImageItemType,)

    def draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap):
        """Draw image"""
        if self.warn_if_non_linear_scale(painter, canvasRect):
            return
        painter.setRenderHint(QG.QPainter.Antialiasing, True)
        param = self.param
        xcoords = vmap(xMap, np.arange(0, param.dim_h + 1, param.step_x))
        ycoords = vmap(yMap, np.arange(0, param.dim_v + 1, param.step_y))
        rx = 0.5 * param.size * xMap.pDist() / xMap.sDist()
        ry = 0.5 * param.size * yMap.pDist() / yMap.sDist()
        color = QG.QColor(param.color)
        painter.setPen(QG.QPen(color))
        painter.setBrush(QG.QBrush(color))
        for xc in xcoords:
            for yc in ycoords:
                painter.drawEllipse(QC.QPointF(xc, yc), rx, ry)


class CustomHelpTool(HelpTool):
    """Custom help tool"""

    def activate_command(self, plot, checked):
        """Activate command"""
        QW.QMessageBox.information(
            plot,
            "Help",
            """**to be customized**
Keyboard/mouse shortcuts:
  - single left-click: item (curve, image, ...) selection
  - single right-click: context-menu relative to selected item
  - shift: on-active-curve (or image) cursor
  - alt: free cursor
  - left-click + mouse move: move item (when available)
  - middle-click + mouse move: pan
  - right-click + mouse move: zoom""",
        )


class DotArrayDialog(PlotDialog):
    """Dot array dialog"""

    def __init__(self):
        self.item = None
        self.stamp_gbox = None
        super().__init__(
            title="Dot array example",
            options=PlotOptions(title="Main plot", type="image"),
            toolbar=True,
            edit=True,
        )
        self.resize(900, 600)

    def register_tools(self):
        """Register tools"""
        manager = self.plot_widget.manager
        manager.register_standard_tools()
        manager.add_separator_tool()
        manager.add_tool(SaveAsTool)
        manager.add_tool(CopyToClipboardTool)
        manager.add_tool(PrintTool)
        manager.add_tool(CustomHelpTool)
        manager.activate_default_tool()
        plot = manager.get_plot()
        plot.enableAxis(plot.yRight, False)
        plot.set_aspect_ratio(lock=True)

    def populate_plot_layout(self):
        """Populate the plot layout

        Reimplements the method from PlotDialog"""
        self.add_widget(self.plot_widget, row=0, column=0, rowspan=3, columnspan=1)
        logo_path = get_image_file_path("plotpy.svg")
        logo = QW.QLabel()
        logo.setPixmap(QG.QPixmap(logo_path))
        logo.setAlignment(QC.Qt.AlignCenter)
        self.add_widget(logo, 1, 1)
        logo_txt = QW.QLabel("Powered by <b>plotpy</b>")
        logo_txt.setAlignment(QC.Qt.AlignHCenter | QC.Qt.AlignTop)
        self.add_widget(logo_txt, 2, 1)
        self.stamp_gbox = gdq.DataSetEditGroupBox("Dots", DotArrayParam)
        self.stamp_gbox.SIG_APPLY_BUTTON_CLICKED.connect(self.apply_params)
        self.add_widget(self.stamp_gbox, 0, 1)

    def show_data(self, param):
        """Show data"""
        plot = self.plot_widget.plot
        if self.item is None:
            itemparam = DotArrayRawImageParam()
            gds.update_dataset(itemparam, param)
            param._update_cb = lambda: self.stamp_gbox.get()
            self.item = DotArrayItem(itemparam)
            plot.add_item(self.item)
        else:
            gds.update_dataset(self.item.param, param)
            self.item.update_border()
        plot.do_autoscale()

    def apply_params(self):
        """Apply parameters"""
        param = self.stamp_gbox.dataset
        self.show_data(param)


def test_dot_array():
    """Test dot array dialog"""
    with qt_app_context(exec_loop=True):
        dlg = DotArrayDialog()
        dlg.apply_params()
        dlg.show()


if __name__ == "__main__":
    test_dot_array()
