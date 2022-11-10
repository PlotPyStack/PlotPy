# -*- coding: utf-8 -*-
#
# Copyright © 2016 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
Dot array example
=================

Example showing how to create a custom item (drawing dots of variable size)
and integrate the associated `plotpy.gui` dataset (GUI-based form) to edit its
parameters (directly into the same window as the plot itself, *and* within
the custom item parameters: right-click on the selectable item to open the
associated dialog box).
"""

SHOW = True  # Show test in GUI-based test launcher

import numpy as np

from plotpy.gui.widgets.baseplot import PlotType
import plotpy.core.config.misc as configtools
import plotpy.core.dataset.datatypes as gdt
import plotpy.core.dataset.dataitems as gdi
import plotpy.gui.dataset.qtwidgets as gdq
import plotpy.gui.widgets.plot as gqp
import plotpy.gui.widgets.items.curve as gqc
import plotpy.gui.widgets.items.image as gqi
import plotpy.gui.widgets.tools as gqt
from plotpy.gui.widgets import ext_gui_lib


class DotArrayParam(gdt.DataSet):
    """Dot array"""

    g1 = gdt.BeginGroup("Size of the area")
    dim_h = gdi.FloatItem("Width", default=20, min=0, unit="mm")
    dim_v = gdi.FloatItem("Height", default=20, min=0, unit="mm")
    _g1 = gdt.EndGroup("Size of the area")

    g2 = gdt.BeginGroup("Grid pattern properties")
    step_x = gdi.FloatItem("Step in X-axis", default=1, min=1, unit="mm")
    step_y = gdi.FloatItem("Step in Y-axis", default=1, min=1, unit="mm")
    size = gdi.FloatItem("Dot size", default=0.2, min=0, max=2, slider=True, unit="mm")
    color = gdi.ColorItem("Dot color", default="red")
    _g2 = gdt.EndGroup("Grid pattern properties")

    def update_item(self, obj):
        self._update_cb()

    def update_param(self, obj):
        pass


class DotArrayItem(gqi.RawImageItem):
    def __init__(self, imageparam=None):
        super(DotArrayItem, self).__init__(np.zeros((1, 1)), imageparam)
        self.update_border()

    def boundingRect(self):
        param = self.param
        if param is not None:
            return ext_gui_lib.QRectF(
                ext_gui_lib.QPointF(-0.5 * param.size, -0.5 * param.size),
                ext_gui_lib.QPointF(
                    param.dim_h + 0.5 * param.size, param.dim_v + 0.5 * param.size
                ),
            )

    def types(self):
        return (gqi.IImageItemType,)

    def draw_image(self, painter, canvasRect, srcRect, dstRect, xMap, yMap):
        painter.setRenderHint(ext_gui_lib.QPainter.Antialiasing, True)
        param = self.param
        xcoords = gqc.vmap(xMap, np.arange(0, param.dim_h + 1, param.step_x))
        ycoords = gqc.vmap(yMap, np.arange(0, param.dim_v + 1, param.step_y))
        rx = 0.5 * param.size * xMap.pDist() / xMap.sDist()
        ry = 0.5 * param.size * yMap.pDist() / yMap.sDist()
        color = ext_gui_lib.QColor(param.color)
        painter.setPen(ext_gui_lib.QPen(color))
        painter.setBrush(ext_gui_lib.QBrush(color))
        for xc in xcoords:
            for yc in ycoords:
                painter.drawEllipse(ext_gui_lib.QPointF(xc, yc), rx, ry)


class CustomHelpTool(gqt.HelpTool):
    def activate_command(self, plot, checked):
        ext_gui_lib.QMessageBox.information(
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


class DotArrayDialog(gqp.PlotDialog):
    def __init__(self):
        self.item = None
        self.stamp_gbox = None
        super(DotArrayDialog, self).__init__(
            wintitle="Dot array example",
            #            icon="path/to/your_icon.png",
            toolbar=True,
            edit=True,
        )
        self.resize(900, 600)

    def register_tools(self):
        self.register_standard_tools()
        self.add_separator_tool()
        self.add_tool(gqt.SaveAsTool)
        self.add_tool(gqt.CopyToClipboardTool)
        self.add_tool(gqt.PrintTool)
        self.add_tool(CustomHelpTool)
        self.activate_default_tool()
        plot = self.get_plot()
        plot.enableAxis(plot.yRight, False)
        plot.set_aspect_ratio(lock=True)

    def create_plot(self, options):
        logo_path = configtools.get_image_file_path("plotpy.svg")
        logo = ext_gui_lib.QLabel()
        logo.setPixmap(ext_gui_lib.QPixmap(logo_path))
        logo.setAlignment(ext_gui_lib.Qt.AlignCenter)
        self.plot_layout.addWidget(logo, 1, 1)
        logo_txt = ext_gui_lib.QLabel("Powered by <b>plotpy</b>")
        logo_txt.setAlignment(ext_gui_lib.Qt.AlignHCenter | ext_gui_lib.Qt.AlignTop)
        self.plot_layout.addWidget(logo_txt, 2, 1)
        self.stamp_gbox = gdq.DataSetEditGroupBox("Dots", DotArrayParam)
        self.stamp_gbox.SIG_APPLY_BUTTON_CLICKED.connect(self.apply_params)
        self.plot_layout.addWidget(self.stamp_gbox, 0, 1)
        options = dict(title="Main plot", type=PlotType.IMAGE)
        gqp.PlotDialog.create_plot(self, options, 0, 0, 3, 1)

    def show_data(self, param):
        plot = self.get_plot()
        if self.item is None:
            param._update_cb = lambda: self.stamp_gbox.get()
            self.item = DotArrayItem(param)
            plot.add_item(self.item)
        else:
            self.item.update_border()
        plot.do_autoscale()

    def apply_params(self):
        param = self.stamp_gbox.dataset
        self.show_data(param)


if __name__ == "__main__":
    import plotpy.core.config.config  # Loading icons

    # -- Create QApplication
    import plotpy.gui

    _app = plotpy.gui.qapplication()

    dlg = DotArrayDialog()
    dlg.apply_params()
    dlg.exec_()
