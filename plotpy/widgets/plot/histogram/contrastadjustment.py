# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103

"""
plotpy.gui.widgets.histogram
----------------------------

The `histogram` module provides histogram related objects:
    * :py:class:`.histogram.common.HistogramItem`: an histogram plot item
    * :py:class:`.histogram.contrastadjustment.ContrastAdjustment`: the `contrast
      adjustment panel`
    * :py:class:`.histogram.common.LevelsHistogram`: a curve plotting widget
      used by the `contrast adjustment panel` to compute, manipulate and
      display the image levels histogram

``HistogramItem`` objects are plot items (derived from QwtPlotItem) that may
be displayed on a 2D plotting widget like :py:class:`.baseplot.BasePlot`.

Example
~~~~~~~

Simple histogram plotting example:

.. literalinclude:: ../../../tests/gui/histogram.py

Reference
~~~~~~~~~

.. autoclass:: ContrastAdjustment
   :members:
   :inherited-members:
"""

from guidata.configtools import get_icon, get_image_layout
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.gui import assert_interfaces_valid
from plotpy.utils.misc_from_gui import add_actions, create_action
from plotpy.widgets.interfaces.common import IVoiImageItemType
from plotpy.widgets.interfaces.panel import IPanel
from plotpy.widgets.panels import ID_CONTRAST, PanelWidget
from plotpy.widgets.plot.histogram.base import EliminateOutliersParam, LevelsHistogram
from plotpy.widgets.plot.manager import PlotManager
from plotpy.widgets.tools.curve import AntiAliasingTool, SelectPointTool
from plotpy.widgets.tools.plot import BasePlotMenuTool
from plotpy.widgets.tools.selection import SelectTool


class ContrastAdjustment(PanelWidget):
    """Contrast adjustment tool"""

    __implements__ = (IPanel,)
    PANEL_ID = ID_CONTRAST
    PANEL_TITLE = _("Contrast adjustment tool")
    PANEL_ICON = "contrast.png"

    def __init__(self, parent=None):
        super(ContrastAdjustment, self).__init__(parent)

        self.local_manager = None  # local manager for the histogram plot
        self.manager = None  # manager for the associated image plot

        # Storing min/max markers for each active image
        self.min_markers = {}
        self.max_markers = {}

        # Select point tools
        self.min_select_tool = None
        self.max_select_tool = None

        style = "<span style='color: #444444'><b>{}</b></span>"
        layout, _label = get_image_layout(
            self.PANEL_ICON, style.format(self.PANEL_TITLE), alignment=QC.Qt.AlignCenter
        )
        layout.setAlignment(QC.Qt.AlignCenter)
        vlayout = QW.QVBoxLayout()
        vlayout.addLayout(layout)
        self.local_manager = PlotManager(self)
        self.histogram = LevelsHistogram(parent)
        vlayout.addWidget(self.histogram)
        self.local_manager.add_plot(self.histogram)
        hlayout = QW.QHBoxLayout()
        self.setLayout(hlayout)
        hlayout.addLayout(vlayout)

        self.toolbar = toolbar = QW.QToolBar(self)
        toolbar.setOrientation(QC.Qt.Vertical)
        #        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        hlayout.addWidget(toolbar)

        # Add standard plot-related tools to the local manager
        lman = self.local_manager
        lman.add_tool(SelectTool)
        lman.add_tool(BasePlotMenuTool, "item")
        lman.add_tool(BasePlotMenuTool, "axes")
        lman.add_tool(BasePlotMenuTool, "grid")
        lman.add_tool(AntiAliasingTool)
        lman.get_default_tool().activate()

        self.outliers_param = EliminateOutliersParam(self.PANEL_TITLE)

    def register_panel(self, manager):
        """Register panel to plot manager"""
        self.manager = manager
        default_toolbar = self.manager.get_default_toolbar()
        self.manager.add_toolbar(self.toolbar, "contrast")
        self.manager.set_default_toolbar(default_toolbar)
        self.setup_actions()
        for plot in manager.get_plots():
            self.histogram.connect_plot(plot)

    def configure_panel(self):
        """Configure panel"""
        self.min_select_tool = self.manager.add_tool(
            SelectPointTool,
            title=_("Minimum level"),
            on_active_item=True,
            mode="create",
            tip=_("Select minimum level on image"),
            toolbar_id="contrast",
            end_callback=self.apply_min_selection,
        )
        self.max_select_tool = self.manager.add_tool(
            SelectPointTool,
            title=_("Maximum level"),
            on_active_item=True,
            mode="create",
            tip=_("Select maximum level on image"),
            toolbar_id="contrast",
            end_callback=self.apply_max_selection,
        )

    def get_plot(self):
        """

        :return:
        """
        return self.manager.get_active_plot()

    def closeEvent(self, event):
        """

        :param event:
        """
        self.hide()
        event.ignore()

    def setup_actions(self):
        """ """
        fullrange_ac = create_action(
            self,
            _("Full range"),
            icon=get_icon("full_range.png"),
            triggered=self.histogram.set_full_range,
            tip=_("Scale the image's display range " "according to data range"),
        )
        autorange_ac = create_action(
            self,
            _("Eliminate outliers"),
            icon=get_icon("eliminate_outliers.png"),
            triggered=self.eliminate_outliers,
            tip=_(
                "Eliminate levels histogram "
                "outliers and scale the image's "
                "display range accordingly"
            ),
        )
        add_actions(self.toolbar, [fullrange_ac, autorange_ac])

    def eliminate_outliers(self):
        """ """

        def apply(param):
            """

            :param param:
            """
            self.histogram.eliminate_outliers(param.percent)

        if self.outliers_param.edit(self, apply=apply):
            apply(self.outliers_param)

    def apply_min_selection(self, tool):
        """

        :param tool:
        """
        item = self.get_plot().get_last_active_item(IVoiImageItemType)
        point = self.min_select_tool.get_coordinates()
        z = item.get_data(*point)
        self.histogram.set_min(z)

    def apply_max_selection(self, tool):
        """

        :param tool:
        """
        item = self.get_plot().get_last_active_item(IVoiImageItemType)
        point = self.max_select_tool.get_coordinates()
        z = item.get_data(*point)
        self.histogram.set_max(z)

    def set_range(self, _min, _max):
        """Set contrast panel's histogram range"""
        self.histogram.set_range(_min, _max)
        # Update the levels histogram in case active item data has changed:
        self.histogram.selection_changed(self.get_plot())


assert_interfaces_valid(ContrastAdjustment)
