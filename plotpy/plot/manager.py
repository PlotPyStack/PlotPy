# -*- coding: utf-8 -*-

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any

from guidata.qthelpers import create_action
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.constants import ID_CONTRAST, ID_ITEMLIST, ID_XCS, ID_YCS
from plotpy.interfaces import IPlotManager
from plotpy.plot import BasePlot
from plotpy.tools import (
    AboutTool,
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
    AntiAliasingTool,
    AspectRatioTool,
    AverageCrossSectionTool,
    AxisScaleTool,
    BasePlotMenuTool,
    ColormapTool,
    ContrastPanelTool,
    CopyToClipboardTool,
    CrossSectionTool,
    CurveStatsTool,
    DeleteItemTool,
    DisplayCoordsTool,
    DoAutoscaleTool,
    DownSamplingTool,
    DummySeparatorTool,
    EditItemDataTool,
    ExportItemDataTool,
    HelpTool,
    ImageStatsTool,
    ItemCenterTool,
    ItemListPanelTool,
    LabelTool,
    PrintTool,
    RectangularSelectionTool,
    RectZoomTool,
    ReverseYAxisTool,
    SaveAsTool,
    SelectTool,
    SnapshotTool,
    XCSPanelTool,
    YCSPanelTool,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable

    from qwt import QwtPlotCanvas, QwtScaleDiv

    from plotpy.panels import ContrastAdjustment, PanelWidget, PlotItemList


class DefaultPlotID:
    pass


class PlotManager:
    """
    Construct a PlotManager object, a 'controller' that organizes relations
    between plots (:py:class:`.BasePlot`), panels, tools and toolbars

    Args:
        main (QWidget): The main parent widget
    """

    __implements__ = (IPlotManager,)

    def __init__(self, main: QW.QWidget) -> None:
        self.main = main  # The main parent widget
        self.plots = {}  # maps ids to instances of BasePlot
        self.panels = {}  # Qt widgets that need to know about the plots
        self.tools = []
        self.toolbars = {}
        self.active_tool = None
        self.default_tool = None
        self.default_plot = None
        self.default_toolbar = None
        self.synchronized_plots = {}
        self.groups = {}  # Action groups for grouping QActions
        # Keep track of the registration sequence (plots, panels, tools):
        self._first_tool_flag = True

    def add_plot(self, plot: BasePlot, plot_id: Any = DefaultPlotID) -> None:
        """
        Register a plot to the plot manager:
            * plot: :py:class:`.BasePlot`
            * plot_id (default id is the plot object's id: ``id(plot)``):
              unique ID identifying the plot (any Python object),
              this ID will be asked by the manager to access this plot later.

        Plot manager's registration sequence is the following:
            1. add plots
            2. add panels
            3. add tools
        """
        if plot_id is DefaultPlotID:
            plot_id = id(plot)
        assert plot_id not in self.plots
        assert isinstance(plot, BasePlot)
        assert not self.tools, "tools must be added after plots"
        assert not self.panels, "panels must be added after plots"
        self.plots[plot_id] = plot
        if len(self.plots) == 1:
            self.default_plot = plot
        plot.set_manager(self, plot_id)
        # Connecting signals
        plot.SIG_ITEMS_CHANGED.connect(self.update_tools_status)
        plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.update_tools_status)
        plot.SIG_PLOT_AXIS_CHANGED.connect(self.plot_axis_changed)

    def set_default_plot(self, plot: BasePlot) -> None:
        """
        Set default plot

        The default plot is the plot on which tools and panels will act.
        """
        self.default_plot = plot

    def get_default_plot(self) -> BasePlot:
        """
        Return default plot

        The default plot is the plot on which tools and panels will act.
        """
        return self.default_plot

    def add_panel(self, panel: PanelWidget) -> None:
        """
        Register a panel to the plot manager

        Plot manager's registration sequence is the following:
            1. add plots
            2. add panels
            3. add tools
        """
        assert panel.PANEL_ID not in self.panels
        assert not self.tools, "tools must be added after panels"
        self.panels[panel.PANEL_ID] = panel
        panel.register_panel(self)

    def configure_panels(self) -> None:
        """
        Call all the registred panels 'configure_panel' methods to finalize the
        object construction (this allows to use tools registered to the same
        plot manager as the panel itself with breaking the registration
        sequence: "add plots, then panels, then tools")
        """
        for panel_id in self.panels:
            panel = self.get_panel(panel_id)
            panel.configure_panel()

    def add_toolbar(self, toolbar: QW.QToolBar, toolbar_id: str = "default") -> None:
        """
        Add toolbar to the plot manager
            toolbar: a QToolBar object
            toolbar_id: toolbar's id (default id is string "default")
        """
        assert toolbar_id not in self.toolbars
        self.toolbars[toolbar_id] = toolbar
        if self.default_toolbar is None:
            self.default_toolbar = toolbar

    def set_default_toolbar(self, toolbar: QW.QToolBar) -> None:
        """
        Set default toolbar
        """
        self.default_toolbar = toolbar

    def get_default_toolbar(self) -> QW.QToolBar:
        """
        Return default toolbar
        """
        return self.default_toolbar

    def add_tool(self, ToolKlass: type[GuiToolT], *args, **kwargs) -> GuiToolT:
        """
        Register a tool to the manager
            * ToolKlass: tool's class (see :ref:`tools`)
            * args: arguments sent to the tool's class
            * kwargs: keyword arguments sent to the tool's class

        Plot manager's registration sequence is the following:
            1. add plots
            2. add panels
            3. add tools
        """
        if self._first_tool_flag:
            # This is the very first tool to be added to this manager
            self._first_tool_flag = False
            self.configure_panels()
        tool = ToolKlass(self, *args, **kwargs)
        self.tools.append(tool)
        for plot in list(self.plots.values()):
            tool.register_plot(plot)
        if len(self.tools) == 1 or self.default_tool is None:
            self.default_tool = tool
        return tool

    def get_tool(self, ToolKlass: type[GuiToolT]) -> GuiToolT | None:
        """Return tool instance from its class

        Args:
            ToolKlass: tool's class (see :ref:`tools`)

        Returns:
            GuiTool: tool instance
        """
        for tool in self.tools:
            if isinstance(tool, ToolKlass):
                return tool

    def add_separator_tool(self, toolbar_id: str | None = None) -> None:
        """
        Register a separator tool to the plot manager: the separator tool is
        just a tool which insert a separator in the plot context menu

        Args:
            toolbar_id: toolbar's id (default to None)
        """
        if toolbar_id is None:
            for _id, toolbar in list(self.toolbars.items()):
                if toolbar is self.get_default_toolbar():
                    toolbar_id = _id
                    break
        self.add_tool(DummySeparatorTool, toolbar_id)

    def set_default_tool(self, tool: GuiTool) -> None:
        """
        Set default tool

        Args:
            tool: tool instance
        """
        self.default_tool = tool

    def get_default_tool(self) -> GuiTool:
        """
        Get default tool

        Returns:
            GuiTool: tool instance
        """
        return self.default_tool

    def activate_default_tool(self) -> None:
        """
        Activate default tool
        """
        self.get_default_tool().activate()

    def get_active_tool(self) -> GuiTool:
        """
        Return active tool

        Returns:
            GuiTool: tool instance
        """
        return self.active_tool

    def set_active_tool(self, tool: GuiTool | None = None) -> None:
        """
        Set active tool (if tool argument is None, the active tool will be
        the default tool)

        Args:
            tool: tool instance or None
        """
        self.active_tool = tool

    def get_plot(self, plot_id: Any = DefaultPlotID) -> BasePlot:
        """
        Return plot associated to `plot_id` (if method is called without
        specifying the `plot_id` parameter, return the default plot)

        Args:
            plot_id: plot's id (optional, default to DefaultPlotID)
        """
        if plot_id is DefaultPlotID:
            return self.default_plot
        return self.plots[plot_id]

    def get_plots(self) -> list[BasePlot]:
        """
        Return all registered plots

        Returns:
            list[BasePlot]: list of plots
        """
        return list(self.plots.values())

    def get_active_plot(self) -> BasePlot:
        """
        Return the active plot

        The active plot is the plot whose canvas has the focus
        otherwise it's the "default" plot

        Returns:
            BasePlot: plot instance
        """
        for plot in list(self.plots.values()):
            canvas: QwtPlotCanvas = plot.canvas()
            if canvas.hasFocus():
                return plot
        return self.default_plot

    def get_tool_group(self, groupname: str) -> QW.QActionGroup:
        """
        Return the QActionGroup associated to `groupname`

        Args:
            groupname: group's name

        Returns:
            QActionGroup: action group
        """
        group = self.groups.get(groupname, None)
        if group is None:
            group = QW.QActionGroup(self.main)
            self.groups[groupname] = weakref.ref(group)
            return group
        else:
            return group()

    def get_main(self) -> QW.QWidget:
        """
        Return the main (parent) widget

        Note that for py:class:`.plot.PlotWidget` objects, this method will
        return the widget itself because the plot manager is integrated to it.

        Returns:
            QWidget: main widget
        """
        return self.main

    def set_main(self, main: QW.QWidget) -> None:
        """
        Set the main (parent) widget

        Args:
            main: main widget
        """
        self.main = main

    def get_panel(self, panel_id: str) -> PanelWidget:
        """
        Return panel from its ID
        Panel IDs are listed in module plotpy.panels

        Args:
            panel_id: panel's id

        Returns:
            PanelWidget: panel widget
        """
        return self.panels.get(panel_id, None)

    def get_itemlist_panel(self) -> PlotItemList:
        """
        Convenience function to get the `item list panel`

        Return None if the item list panel has not been added to this manager

        Returns:
            PlotItemList: item list panel
        """
        return self.get_panel(ID_ITEMLIST)

    def get_contrast_panel(self) -> ContrastAdjustment:
        """
        Convenience function to get the `contrast adjustment panel`

        Return None if the contrast adjustment panel has not been added
        to this manager
        """
        return self.get_panel(ID_CONTRAST)

    def set_contrast_range(self, zmin: float, zmax: float) -> None:
        """
        Convenience function to set the `contrast adjustment panel` range

        This is strictly equivalent to the following::

            # Here, *widget* is for example a PlotWidget instance
            # (the same apply for PlotWidget or any
            #  class deriving from PlotManager)
            widget.get_contrast_panel().set_range(zmin, zmax)

        Args:
            zmin: minimum value
            zmax: maximum value
        """
        self.get_contrast_panel().set_range(zmin, zmax)

    def get_xcs_panel(self) -> XCrossSection:
        """
        Convenience function to get the `X-axis cross section panel`

        Return None if the X-axis cross section panel has not been added
        to this manager

        Returns:
            XCrossSection: X-axis cross section panel
        """
        return self.get_panel(ID_XCS)

    def get_ycs_panel(self) -> YCrossSection:
        """
        Convenience function to get the `Y-axis cross section panel`

        Return None if the Y-axis cross section panel has not been added
        to this manager

        Returns:
            YCrossSection: Y-axis cross section panel
        """
        return self.get_panel(ID_YCS)

    def update_cross_sections(self) -> None:
        """
        Convenience function to update the `cross section panels` at once

        This is strictly equivalent to the following::

            # Here, *widget* is for example a PlotWidget instance
            # (the same apply for any other class deriving from PlotManager)
            widget.get_xcs_panel().update_plot()
            widget.get_ycs_panel().update_plot()
        """
        self.get_xcs_panel().update_plot()
        self.get_ycs_panel().update_plot()

    def get_toolbar(self, toolbar_id: str = "default") -> QW.QToolBar:
        """
        Return toolbar from its ID

        Args:
            toolbar_id: toolbar's id (default id is string "default")

        Returns:
            QToolBar: toolbar
        """
        return self.toolbars.get(toolbar_id, None)

    def get_context_menu(self, plot: BasePlot | None = None) -> QW.QMenu:
        """
        Return widget context menu -- built using active tools

        Args:
            plot: plot instance (default to None)

        Returns:
            QMenu: context menu
        """
        if plot is None:
            plot = self.get_plot()
        menu = QW.QMenu(plot)
        self.update_tools_status(plot)
        for tool in self.tools:
            tool.setup_context_menu(menu, plot)
        return menu

    def update_tools_status(self, plot: BasePlot | None = None) -> None:
        """
        Update tools for current plot

        Args:
            plot: plot instance (default to None)
        """
        if plot is None:
            plot = self.get_plot()
        for tool in self.tools:
            tool.update_status(plot)

    def create_action(
        self,
        title: str,
        triggered: Callable | None = None,
        toggled: Callable | None = None,
        shortcut: QG.QKeySequence | None = None,
        icon: QG.QIcon | None = None,
        tip: str | None = None,
        checkable: bool | None = None,
        context: QC.Qt.ShortcutContext = QC.Qt.ShortcutContext.WindowShortcut,
        enabled: bool | None = None,
    ):
        """
        Create a new QAction

        Args:
            parent (QWidget or None): Parent widget
            title (str): Action title
            triggered (Callable or None): Triggered callback
            toggled (Callable or None): Toggled callback
            shortcut (QKeySequence or None): Shortcut
            icon (QIcon or None): Icon
            tip (str or None): Tooltip
            checkable (bool or None): Checkable
            context (Qt.ShortcutContext): Shortcut context
            enabled (bool or None): Enabled

        Returns:
            QAction: New action
        """
        return create_action(
            self.main,
            title,
            triggered=triggered,
            toggled=toggled,
            shortcut=shortcut,
            icon=icon,
            tip=tip,
            checkable=checkable,
            context=context,
            enabled=enabled,
        )

    # The following methods provide some sets of tools that
    # are often registered together
    def register_standard_tools(self) -> None:
        """
        Registering basic tools for standard plot dialog
        --> top of the context-menu
        """
        t = self.add_tool(SelectTool)
        self.set_default_tool(t)
        self.add_tool(RectangularSelectionTool, intersect=False)
        self.add_tool(RectZoomTool)
        self.add_tool(DoAutoscaleTool)
        self.add_tool(BasePlotMenuTool, "item")
        self.add_tool(ExportItemDataTool)
        self.add_tool(EditItemDataTool)
        self.add_tool(ItemCenterTool)
        self.add_tool(DeleteItemTool)
        self.add_separator_tool()
        self.add_tool(BasePlotMenuTool, "grid")
        self.add_tool(BasePlotMenuTool, "axes")
        self.add_tool(DisplayCoordsTool)
        if self.get_itemlist_panel():
            self.add_tool(ItemListPanelTool)

    def register_curve_tools(self) -> None:
        """
        Register only curve-related tools

        .. seealso::

            :py:meth:`.plot.manager.PlotManager.add_tool`

            :py:meth:`.plot.manager.PlotManager.register_standard_tools`

            :py:meth:`.plot.manager.PlotManager.register_other_tools`

            :py:meth:`.plot.manager.PlotManager.register_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_tools`
        """
        self.add_tool(CurveStatsTool)
        self.add_tool(AntiAliasingTool)
        self.add_tool(AxisScaleTool)
        self.add_tool(DownSamplingTool)

    def register_image_tools(self) -> None:
        """
        Register only image-related tools

        .. seealso::

            :py:meth:`.plot.manager.PlotManager.add_tool`

            :py:meth:`.plot.manager.PlotManager.register_standard_tools`

            :py:meth:`.plot.manager.PlotManager.register_other_tools`

            :py:meth:`.plot.manager.PlotManager.register_curve_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_tools`
        """
        self.add_tool(ColormapTool)
        self.add_tool(ReverseYAxisTool)
        self.add_tool(AspectRatioTool)
        if self.get_contrast_panel():
            self.add_tool(ContrastPanelTool)
        self.add_tool(SnapshotTool)
        self.add_tool(ImageStatsTool)
        if self.get_xcs_panel() and self.get_ycs_panel():
            self.add_tool(XCSPanelTool)
            self.add_tool(YCSPanelTool)
            self.add_tool(CrossSectionTool)
            self.add_tool(AverageCrossSectionTool)

    def register_other_tools(self) -> None:
        """
        Register other common tools

        .. seealso::

            :py:meth:`.plot.manager.PlotManager.add_tool`

            :py:meth:`.plot.manager.PlotManager.register_standard_tools`

            :py:meth:`.plot.manager.PlotManager.register_curve_tools`

            :py:meth:`.plot.manager.PlotManager.register_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_tools`
        """
        self.add_tool(SaveAsTool)
        self.add_tool(CopyToClipboardTool)
        self.add_tool(PrintTool)
        self.add_tool(HelpTool)
        self.add_tool(AboutTool)

    def register_all_curve_tools(self) -> None:
        """
        Register standard, curve-related and other tools

        .. seealso::

            :py:meth:`.plot.manager.PlotManager.add_tool`

            :py:meth:`.plot.manager.PlotManager.register_standard_tools`

            :py:meth:`.plot.manager.PlotManager.register_other_tools`

            :py:meth:`.plot.manager.PlotManager.register_curve_tools`

            :py:meth:`.plot.manager.PlotManager.register_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_tools`
        """
        self.register_standard_tools()
        self.add_separator_tool()
        self.register_curve_tools()
        self.add_separator_tool()
        self.register_other_tools()
        self.add_separator_tool()
        self.update_tools_status()
        self.get_default_tool().activate()

    def register_all_image_tools(self) -> None:
        """
        Register standard, image-related and other tools

        .. seealso::

            :py:meth:`.plot.manager.PlotManager.add_tool`

            :py:meth:`.plot.manager.PlotManager.register_standard_tools`

            :py:meth:`.plot.manager.PlotManager.register_other_tools`

            :py:meth:`.plot.manager.PlotManager.register_curve_tools`

            :py:meth:`.plot.manager.PlotManager.register_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_curve_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_tools`
        """
        self.register_standard_tools()
        self.add_separator_tool()
        self.register_image_tools()
        self.add_separator_tool()
        self.register_other_tools()
        self.add_separator_tool()
        self.update_tools_status()
        self.get_default_tool().activate()

    def register_all_tools(self) -> None:
        """
        Register standard, curve and image-related and other tools

        .. seealso::

            :py:meth:`.plot.manager.PlotManager.add_tool`

            :py:meth:`.plot.manager.PlotManager.register_standard_tools`

            :py:meth:`.plot.manager.PlotManager.register_other_tools`

            :py:meth:`.plot.manager.PlotManager.register_curve_tools`

            :py:meth:`.plot.manager.PlotManager.register_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_image_tools`

            :py:meth:`.plot.manager.PlotManager.register_all_curve_tools`
        """
        self.register_standard_tools()
        self.add_separator_tool()
        self.register_curve_tools()
        self.add_separator_tool()
        self.register_image_tools()
        self.add_separator_tool()
        self.register_other_tools()
        self.add_separator_tool()
        self.update_tools_status()
        self.get_default_tool().activate()

    def register_all_annotation_tools(self) -> None:
        """
        Register all annotation tools for the plot
        """
        self.add_separator_tool()
        self.add_tool(AnnotatedPointTool)
        self.add_tool(AnnotatedSegmentTool)
        self.add_tool(AnnotatedRectangleTool)
        self.add_tool(AnnotatedObliqueRectangleTool)
        self.add_tool(AnnotatedCircleTool)
        self.add_tool(AnnotatedEllipseTool)
        self.add_tool(LabelTool)

    def register_curve_annotation_tools(self) -> None:
        """
        Register all curve friendly annotation tools for the plot
        """
        self.add_separator_tool()
        self.add_tool(AnnotatedPointTool)
        self.add_tool(AnnotatedSegmentTool)
        self.add_tool(LabelTool)

    def register_image_annotation_tools(self) -> None:
        """
        Register all image friendly annotation tools for the plot
        """
        # No curve-specific annotation tool, so this is equivalent to the
        # register_all_annotation_tools function for now
        self.register_all_annotation_tools()

    def synchronize_axis(self, axis_id: int, plot_ids: list[str]) -> None:
        """
        Synchronize axis of plots

        Args:
            axis_id: axis id
            plot_ids: list of plot ids
        """
        for plot_id in plot_ids:
            synclist = self.synchronized_plots.setdefault(plot_id, [])
            for plot2_id in plot_ids:
                if plot_id == plot2_id:
                    continue
                item = (axis_id, plot2_id)
                if item not in synclist:
                    synclist.append(item)

    def plot_axis_changed(self, plot: BasePlot) -> None:
        """
        Plot axis changed, update other synchronized plots (if any)

        Args:
            plot: plot instance
        """
        plot_id = plot.plot_id
        if plot_id not in self.synchronized_plots:
            return
        for axis_id, other_plot_id in self.synchronized_plots[plot_id]:
            scalediv: QwtScaleDiv = plot.axisScaleDiv(axis_id)
            other_plot = self.get_plot(other_plot_id)
            lb = scalediv.lowerBound()
            ub = scalediv.upperBound()
            other_plot.setAxisScale(axis_id, lb, ub)
            other_plot.replot()


assert_interfaces_valid(PlotManager)
