# -*- coding: utf-8 -*-
from guidata.configtools import get_icon
from guidata.qthelpers import add_actions, create_action
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.interfaces.panel import IPanel
from plotpy.panels.base import ID_OCS, ID_XCS, ID_YCS, PanelWidget
from plotpy.panels.csection.csplot import (
    CrossSectionPlot,
    ObliqueCrossSectionPlot,
    XCrossSectionPlot,
    YCrossSectionPlot,
)
from plotpy.plot.manager import PlotManager
from plotpy.tools import ExportItemDataTool


class CrossSectionWidget(PanelWidget):
    """ """

    PANEL_ID = None
    PANEL_TITLE = _("Cross section tool")
    PANEL_ICON = "csection.png"
    CrossSectionPlotKlass = CrossSectionPlot  # to be overridden in subclasses

    __implements__ = (IPanel,)

    def __init__(self, parent=None):
        super(CrossSectionWidget, self).__init__(parent)

        self.export_ac = None
        self.autoscale_ac = None
        self.refresh_ac = None
        self.autorefresh_ac = None
        self.lockscales_ac = None

        self.manager = None  # manager for the associated image plot

        self.local_manager = PlotManager(self)
        self.cs_plot = self.CrossSectionPlotKlass(parent)
        self.cs_plot.SIG_CS_CURVE_CHANGED.connect(self.cs_curve_has_changed)
        self.export_tool = None
        self.setup_plot()

        self.toolbar = QW.QToolBar(self)
        self.toolbar.setOrientation(QC.Qt.Orientation.Vertical)

        self.setup_widget()

    def set_options(self, autoscale=None, autorefresh=None, lockscales=None):
        """

        :param autoscale:
        :param autorefresh:
        :param lockscales:
        """
        assert self.manager is not None, (
            "Panel '%s' must be registered to plot manager before changing options"
            % self.PANEL_ID
        )
        if autoscale is not None:
            self.autoscale_ac.setChecked(autoscale)
        if autorefresh is not None:
            self.autorefresh_ac.setChecked(autorefresh)
        if lockscales is not None:
            self.lockscales_ac.setChecked(lockscales)

    def setup_plot(self):
        """ """
        # Configure the local manager
        lman = self.local_manager
        lman.add_plot(self.cs_plot)
        lman.register_all_curve_tools()
        self.export_tool = lman.get_tool(ExportItemDataTool)

    def setup_widget(self):
        """ """
        layout = QW.QHBoxLayout()
        layout.addWidget(self.cs_plot)
        layout.addWidget(self.toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def cs_curve_has_changed(self, curve):
        """Cross section curve has just changed"""
        # Do something with curve's data for example
        pass

    def register_panel(self, manager):
        """Register panel to plot manager"""
        self.manager = manager
        for plot in manager.get_plots():
            self.cs_plot.connect_plot(plot)
        self.setup_actions()
        self.add_actions_to_toolbar()

    def configure_panel(self):
        """Configure panel"""
        pass

    def get_plot(self):
        """

        :return:
        """
        return self.manager.get_active_plot()

    def setup_actions(self):
        """ """
        self.export_ac = self.export_tool.action
        self.lockscales_ac = create_action(
            self,
            _("Lock scales"),
            icon=get_icon("axes.png"),
            toggled=self.cs_plot.toggle_lockscales,
            tip=_("Lock scales to main plot axes"),
        )
        self.lockscales_ac.setChecked(self.cs_plot.lockscales)
        self.autoscale_ac = create_action(
            self,
            _("Auto-scale"),
            icon=get_icon("csautoscale.png"),
            toggled=self.cs_plot.toggle_autoscale,
        )
        self.autoscale_ac.toggled.connect(self.lockscales_ac.setDisabled)
        self.autoscale_ac.setChecked(self.cs_plot.autoscale_mode)
        self.refresh_ac = create_action(
            self,
            _("Refresh"),
            icon=get_icon("refresh.png"),
            triggered=lambda: self.cs_plot.update_plot(),
        )
        self.autorefresh_ac = create_action(
            self,
            _("Auto-refresh"),
            icon=get_icon("autorefresh.png"),
            toggled=self.cs_plot.toggle_autorefresh,
        )
        self.autorefresh_ac.setChecked(self.cs_plot.autorefresh_mode)

    def add_actions_to_toolbar(self):
        """ """
        add_actions(
            self.toolbar,
            (
                self.export_ac,
                None,
                self.autoscale_ac,
                self.lockscales_ac,
                None,
                self.refresh_ac,
                self.autorefresh_ac,
            ),
        )

    def register_shape(self, shape, final, refresh=True):
        """

        :param shape:
        :param final:
        :param refresh:
        """
        plot = self.get_plot()
        self.cs_plot.register_shape(plot, shape, final, refresh)

    def unregister_shape(self, shape):
        """

        :param shape:
        """
        self.cs_plot.unregister_shape(shape)

    def update_plot(self, obj=None):
        """
        Update cross section curve(s) associated to object *obj*

        *obj* may be a marker or a rectangular shape
        (see :py:class:`.tools.CrossSectionTool`
        and :py:class:`.tools.AverageCrossSectionTool`)

        If obj is None, update the cross sections of the last active object
        """
        self.cs_plot.update_plot(obj)


assert_interfaces_valid(CrossSectionWidget)


class XCrossSection(CrossSectionWidget):
    """X-axis cross section widget"""

    PANEL_ID = ID_XCS
    OTHER_PANEL_ID = ID_YCS
    CrossSectionPlotKlass = XCrossSectionPlot

    def __init__(self, parent=None):
        super(XCrossSection, self).__init__(parent)
        self.peritem_ac = None
        self.applylut_ac = None

    def set_options(
        self,
        autoscale=None,
        autorefresh=None,
        peritem=None,
        applylut=None,
        lockscales=None,
    ):
        """

        :param autoscale:
        :param autorefresh:
        :param peritem:
        :param applylut:
        :param lockscales:
        """
        assert self.manager is not None, (
            f"Panel '{self.PANEL_ID}' must be "
            "registered to plot manager before changing options"
        )

        if autoscale is not None:
            self.autoscale_ac.setChecked(autoscale)
        if autorefresh is not None:
            self.autorefresh_ac.setChecked(autorefresh)
        if lockscales is not None:
            self.lockscales_ac.setChecked(lockscales)
        if peritem is not None:
            self.peritem_ac.setChecked(peritem)
        if applylut is not None:
            self.applylut_ac.setChecked(applylut)

    def add_actions_to_toolbar(self):
        """ """
        other = self.manager.get_panel(self.OTHER_PANEL_ID)
        if other is None:
            add_actions(
                self.toolbar,
                (
                    self.peritem_ac,
                    self.applylut_ac,
                    None,
                    self.export_ac,
                    None,
                    self.autoscale_ac,
                    self.lockscales_ac,
                    None,
                    self.refresh_ac,
                    self.autorefresh_ac,
                ),
            )
        else:
            add_actions(
                self.toolbar,
                (
                    other.peritem_ac,
                    other.applylut_ac,
                    None,
                    self.export_ac,
                    None,
                    other.autoscale_ac,
                    other.lockscales_ac,
                    None,
                    other.refresh_ac,
                    other.autorefresh_ac,
                ),
            )
            other.peritem_ac.toggled.connect(self.cs_plot.toggle_perimage_mode)
            other.applylut_ac.toggled.connect(self.cs_plot.toggle_apply_lut)
            other.autoscale_ac.toggled.connect(self.cs_plot.toggle_autoscale)
            other.refresh_ac.triggered.connect(lambda: self.cs_plot.update_plot())
            other.autorefresh_ac.toggled.connect(self.cs_plot.toggle_autorefresh)
            other.lockscales_ac.toggled.connect(self.cs_plot.toggle_lockscales)

    def closeEvent(self, event):
        """

        :param event:
        """
        self.hide()
        event.ignore()

    def setup_actions(self):
        """ """
        CrossSectionWidget.setup_actions(self)
        self.peritem_ac = create_action(
            self,
            _("Per image cross-section"),
            icon=get_icon("csperimage.png"),
            toggled=self.cs_plot.toggle_perimage_mode,
            tip=_(
                "Enable the per-image cross-section mode, "
                "which works directly on image rows/columns.\n"
                "That is the fastest method to compute "
                "cross-section curves but it ignores "
                "image transformations (e.g. rotation)"
            ),
        )
        self.applylut_ac = create_action(
            self,
            _("Apply LUT\n(contrast settings)"),
            icon=get_icon("csapplylut.png"),
            toggled=self.cs_plot.toggle_apply_lut,
            tip=_(
                "Apply LUT (Look-Up Table) contrast settings.\n"
                "This is the easiest way to compare images "
                "which have slightly different level ranges.\n\n"
                "Note: LUT is coded over 1024 levels (0...1023)"
            ),
        )
        self.peritem_ac.setChecked(True)
        self.applylut_ac.setChecked(False)


class YCrossSection(XCrossSection):
    """
    Y-axis cross section widget
    parent (QWidget): parent widget
    position (string): "left" or "right"
    """

    PANEL_ID = ID_YCS
    OTHER_PANEL_ID = ID_XCS
    CrossSectionPlotKlass = YCrossSectionPlot

    def __init__(self, parent=None, position="right", xsection_pos="top"):
        self.xsection_pos = xsection_pos
        self.spacer = QW.QSpacerItem(0, 0)
        super(YCrossSection, self).__init__(parent)
        self.cs_plot.set_axis_direction("bottom", reverse=position == "left")

    def setup_widget(self):
        """ """
        toolbar = self.toolbar
        toolbar.setOrientation(QC.Qt.Orientation.Horizontal)
        layout = QW.QVBoxLayout()
        if self.xsection_pos == "top":
            layout.addSpacerItem(self.spacer)
        layout.addWidget(toolbar)
        layout.addWidget(self.cs_plot)
        if self.xsection_pos == "bottom":
            layout.addSpacerItem(self.spacer)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def adjust_height(self, height):
        """

        :param height:
        """
        self.spacer.changeSize(0, height, QW.QSizePolicy.Fixed, QW.QSizePolicy.Fixed)
        self.layout().invalidate()


# Oblique cross section panel
class ObliqueCrossSection(CrossSectionWidget):
    """Oblique averaged cross section widget"""

    PANEL_ID = ID_OCS
    CrossSectionPlotKlass = ObliqueCrossSectionPlot
    PANEL_ICON = "csection_oblique.png"

    def setup_actions(self):
        """ """
        super(ObliqueCrossSection, self).setup_actions()
        self.lockscales_ac.setChecked(False)
        self.autoscale_ac.setChecked(True)
