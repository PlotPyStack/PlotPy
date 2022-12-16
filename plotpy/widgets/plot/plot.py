# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.gui.widgets.plot
-----------------------

The `plot` module provides the following features:
    * :py:class:`.plot.PlotManager`: the `plot manager` is an object to
      link `plots`, `panels` and `tools` together for designing highly
      versatile graphical user interfaces
    * :py:class:`.plot.PlotWidget`: a ready-to-use widget for curve/image
      displaying with an integrated and preconfigured `plot manager` providing
      the `item list panel` and curve/image-related `tools`
    * :py:class:`.plot.PlotDialog`: a ready-to-use dialog box for
      curve/image displaying with an integrated and preconfigured `plot manager`
      providing the `item list panel` and curve/image-related `tools`

.. seealso::

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

    Module :py:mod:`.tools`
        Module providing the `plot tools`

    Module :py:mod:`.panels`
        Module providing the `plot panels` IDs

    Module :py:mod:`.baseplot`
        Module providing the `plotpy` plotting widget base class


Class diagrams
~~~~~~~~~~~~~~

Curve-related widgets with integrated plot manager:

.. image:: /images/curve_widgets.png

Image-related widgets with integrated plot manager:

.. image:: /images/image_widgets.png

Building your own plot manager:

.. image:: /images/my_plot_manager.png


Examples
~~~~~~~~

Simple example *without* the `plot manager`:

.. literalinclude:: ../../../tests/gui/filtertest1.py
   :start-after: SHOW

Simple example *with* the `plot manager`:
even if this simple example does not justify the use of the `plot manager`
(this is an unnecessary complication here), it shows how to use it. In more
complex applications, using the `plot manager` allows to design highly versatile
graphical user interfaces.

.. literalinclude:: ../../../tests/gui/filtertest2.py
   :start-after: SHOW

Reference
~~~~~~~~~

.. autoclass:: PlotManager
   :members:
   :inherited-members:
.. autoclass:: BasePlotWidget
   :members:
.. autoclass:: PlotWidget
   :members:
.. autoclass:: PlotWidgetMixin
   :members:
.. autoclass:: PlotDialog
   :members:
.. autoclass:: PlotWindow
   :members:

"""

import weakref

from plotpy.gui.config.misc import get_icon
from plotpy.gui.utils.gui import assert_interfaces_valid
from plotpy.gui.utils.misc import create_action
from plotpy.gui.widgets.baseplot import BasePlot, PlotItemList, PlotType
from plotpy.gui.widgets.config import _
from plotpy.gui.widgets.ext_gui_lib import (
    QActionGroup,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QSplitter,
    Qt,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from plotpy.gui.widgets.interfaces import IPlotManager
from plotpy.gui.widgets.tools import (
    AboutTool,
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
    AntiAliasingTool,
    AspectRatioTool,
    DoAutoscaleTool,
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


class DefaultPlotID(object):
    pass


class PlotManager(object):
    """
    Construct a PlotManager object, a 'controller' that organizes relations
    between plots (i.e. :py:class:`.baseplot.BasePlot`, panels,
    tools (see :py:mod:`.tools`) and toolbars
    """

    __implements__ = (IPlotManager,)

    def __init__(self, main):
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

    def add_plot(self, plot, plot_id=DefaultPlotID):
        """
        Register a plot to the plot manager:
            * plot: :py:class:`.baseplot.BasePlot`
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

    def set_default_plot(self, plot):
        """
        Set default plot

        The default plot is the plot on which tools and panels will act.
        """
        self.default_plot = plot

    def get_default_plot(self):
        """
        Return default plot

        The default plot is the plot on which tools and panels will act.
        """
        return self.default_plot

    def add_panel(self, panel):
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

    def configure_panels(self):
        """
        Call all the registred panels 'configure_panel' methods to finalize the
        object construction (this allows to use tools registered to the same
        plot manager as the panel itself with breaking the registration
        sequence: "add plots, then panels, then tools")
        """
        for panel_id in self.panels:
            panel = self.get_panel(panel_id)
            panel.configure_panel()

    def add_toolbar(self, toolbar, toolbar_id="default"):
        """
        Add toolbar to the plot manager
            toolbar: a QToolBar object
            toolbar_id: toolbar's id (default id is string "default")
        """
        assert toolbar_id not in self.toolbars
        self.toolbars[toolbar_id] = toolbar
        if self.default_toolbar is None:
            self.default_toolbar = toolbar

    def set_default_toolbar(self, toolbar):
        """
        Set default toolbar
        """
        self.default_toolbar = toolbar

    def get_default_toolbar(self):
        """
        Return default toolbar
        """
        return self.default_toolbar

    def add_tool(self, ToolKlass, *args, **kwargs):
        """
        Register a tool to the manager
            * ToolKlass: tool's class (`plotpy` builtin tools are defined in
              module :py:mod:`.tools`)
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
        if len(self.tools) == 1:
            self.default_tool = tool
        return tool

    def get_tool(self, ToolKlass):
        """Return tool instance from its class"""
        for tool in self.tools:
            if isinstance(tool, ToolKlass):
                return tool

    def add_separator_tool(self, toolbar_id=None):
        """
        Register a separator tool to the plot manager: the separator tool is
        just a tool which insert a separator in the plot context menu
        """
        if toolbar_id is None:
            for _id, toolbar in list(self.toolbars.items()):
                if toolbar is self.get_default_toolbar():
                    toolbar_id = _id
                    break
        self.add_tool(DummySeparatorTool, toolbar_id)

    def set_default_tool(self, tool):
        """
        Set default tool
        """
        self.default_tool = tool

    def get_default_tool(self):
        """
        Get default tool
        """
        return self.default_tool

    def activate_default_tool(self):
        """
        Activate default tool
        """
        self.get_default_tool().activate()

    def get_active_tool(self):
        """
        Return active tool
        """
        return self.active_tool

    def set_active_tool(self, tool=None):
        """
        Set active tool (if tool argument is None, the active tool will be
        the default tool)
        """
        self.active_tool = tool

    def get_plot(self, plot_id=DefaultPlotID):
        """
        Return plot associated to `plot_id` (if method is called without
        specifying the `plot_id` parameter, return the default plot)
        """
        if plot_id is DefaultPlotID:
            return self.default_plot
        return self.plots[plot_id]

    def get_plots(self):
        """
        Return all registered plots
        """
        return list(self.plots.values())

    def get_active_plot(self):
        """
        Return the active plot

        The active plot is the plot whose canvas has the focus
        otherwise it's the "default" plot
        """
        for plot in list(self.plots.values()):
            canvas = plot.canvas()
            if canvas.hasFocus():
                return plot
        return self.default_plot

    def get_tool_group(self, groupname):
        """

        :param groupname:
        :return:
        """
        group = self.groups.get(groupname, None)
        if group is None:
            group = QActionGroup(self.main)
            self.groups[groupname] = weakref.ref(group)
            return group
        else:
            return group()

    def get_main(self):
        """
        Return the main (parent) widget

        Note that for py:class:`.plot.PlotWidget` objects, this method will
        return the widget itself because the plot manager is integrated to it.
        """
        return self.main

    def set_main(self, main):
        """

        :param main:
        """
        self.main = main

    def get_panel(self, panel_id):
        """
        Return panel from its ID
        Panel IDs are listed in module plotpy.gui.widgets.panels
        """
        return self.panels.get(panel_id, None)

    def get_itemlist_panel(self):
        """
        Convenience function to get the `item list panel`

        Return None if the item list panel has not been added to this manager
        """
        from plotpy.gui.widgets import panels

        return self.get_panel(panels.ID_ITEMLIST)

    def get_contrast_panel(self):
        """
        Convenience function to get the `contrast adjustment panel`

        Return None if the contrast adjustment panel has not been added
        to this manager
        """
        from plotpy.gui.widgets import panels

        return self.get_panel(panels.ID_CONTRAST)

    def set_contrast_range(self, zmin, zmax):
        """
        Convenience function to set the `contrast adjustment panel` range

        This is strictly equivalent to the following::

            # Here, *widget* is for example a PlotWidget instance
            # (the same apply for PlotWidget or any
            #  class deriving from PlotManager)
            widget.get_contrast_panel().set_range(zmin, zmax)
        """
        self.get_contrast_panel().set_range(zmin, zmax)

    def get_xcs_panel(self):
        """
        Convenience function to get the `X-axis cross section panel`

        Return None if the X-axis cross section panel has not been added
        to this manager
        """
        from plotpy.gui.widgets import panels

        return self.get_panel(panels.ID_XCS)

    def get_ycs_panel(self):
        """
        Convenience function to get the `Y-axis cross section panel`

        Return None if the Y-axis cross section panel has not been added
        to this manager
        """
        from plotpy.gui.widgets import panels

        return self.get_panel(panels.ID_YCS)

    def update_cross_sections(self):
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

    def get_toolbar(self, toolbar_id="default"):
        """
        Return toolbar from its ID
            toolbar_id: toolbar's id (default id is string "default")
        """
        return self.toolbars.get(toolbar_id, None)

    def get_context_menu(self, plot=None):
        """
        Return widget context menu -- built using active tools
        """
        if plot is None:
            plot = self.get_plot()
        menu = QMenu(plot)
        self.update_tools_status(plot)
        for tool in self.tools:
            tool.setup_context_menu(menu, plot)
        return menu

    def update_tools_status(self, plot=None):
        """
        Update tools for current plot
        """
        if plot is None:
            plot = self.get_plot()
        for tool in self.tools:
            tool.update_status(plot)

    def create_action(
        self,
        title,
        triggered=None,
        toggled=None,
        shortcut=None,
        icon=None,
        tip=None,
        checkable=None,
        context=Qt.WindowShortcut,
        enabled=None,
    ):
        """
        Create a new QAction
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
    def register_standard_tools(self):
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
        try:
            import plotpy.gui.widgets.variableexplorer.objecteditor  # analysis:ignore
            self.add_tool(EditItemDataTool)
        except ImportError:
            pass
        self.add_tool(ItemCenterTool)
        self.add_tool(DeleteItemTool)
        self.add_separator_tool()
        self.add_tool(BasePlotMenuTool, "grid")
        self.add_tool(BasePlotMenuTool, "axes")
        self.add_tool(DisplayCoordsTool)
        if self.get_itemlist_panel():
            self.add_tool(ItemListPanelTool)

    def register_curve_tools(self):
        """
        Register only curve-related tools

        .. seealso::

            :py:meth:`.plot.PlotManager.add_tool`

            :py:meth:`.plot.PlotManager.register_standard_tools`

            :py:meth:`.plot.PlotManager.register_other_tools`

            :py:meth:`.plot.PlotManager.register_image_tools`

            :py:meth:`.plot.PlotManager.register_all_tools`
        """
        self.add_tool(CurveStatsTool)
        self.add_tool(AntiAliasingTool)
        self.add_tool(AxisScaleTool)

    def register_image_tools(self):
        """
        Register only image-related tools

        .. seealso::

            :py:meth:`.plot.PlotManager.add_tool`

            :py:meth:`.plot.PlotManager.register_standard_tools`

            :py:meth:`.plot.PlotManager.register_other_tools`

            :py:meth:`.plot.PlotManager.register_curve_tools`

            :py:meth:`.plot.PlotManager.register_all_tools`
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

    def register_other_tools(self):
        """
        Register other common tools

        .. seealso::

            :py:meth:`.plot.PlotManager.add_tool`

            :py:meth:`.plot.PlotManager.register_standard_tools`

            :py:meth:`.plot.PlotManager.register_curve_tools`

            :py:meth:`.plot.PlotManager.register_image_tools`

            :py:meth:`.plot.PlotManager.register_all_tools`
        """
        self.add_tool(SaveAsTool)
        self.add_tool(CopyToClipboardTool)
        self.add_tool(PrintTool)
        self.add_tool(HelpTool)
        self.add_tool(AboutTool)

    def register_all_curve_tools(self):
        """
        Register standard, curve-related and other tools

        .. seealso::

            :py:meth:`.plot.PlotManager.add_tool`

            :py:meth:`.plot.PlotManager.register_standard_tools`

            :py:meth:`.plot.PlotManager.register_other_tools`

            :py:meth:`.plot.PlotManager.register_curve_tools`

            :py:meth:`.plot.PlotManager.register_image_tools`

            :py:meth:`.plot.PlotManager.register_all_image_tools`

            :py:meth:`.plot.PlotManager.register_all_tools`
        """
        self.register_standard_tools()
        self.add_separator_tool()
        self.register_curve_tools()
        self.add_separator_tool()
        self.register_other_tools()
        self.add_separator_tool()
        self.update_tools_status()
        self.get_default_tool().activate()

    def register_all_image_tools(self):
        """
        Register standard, image-related and other tools

        .. seealso::

            :py:meth:`.plot.PlotManager.add_tool`

            :py:meth:`.plot.PlotManager.register_standard_tools`

            :py:meth:`.plot.PlotManager.register_other_tools`

            :py:meth:`.plot.PlotManager.register_curve_tools`

            :py:meth:`.plot.PlotManager.register_image_tools`

            :py:meth:`.plot.PlotManager.register_all_curve_tools`

            :py:meth:`.plot.PlotManager.register_all_tools`
        """
        self.register_standard_tools()
        self.add_separator_tool()
        self.register_image_tools()
        self.add_separator_tool()
        self.register_other_tools()
        self.add_separator_tool()
        self.update_tools_status()
        self.get_default_tool().activate()

    def register_all_tools(self):
        """
        Register standard, curve and image-related and other tools

        .. seealso::

            :py:meth:`.plot.PlotManager.add_tool`

            :py:meth:`.plot.PlotManager.register_standard_tools`

            :py:meth:`.plot.PlotManager.register_other_tools`

            :py:meth:`.plot.PlotManager.register_curve_tools`

            :py:meth:`.plot.PlotManager.register_image_tools`

            :py:meth:`.plot.PlotManager.register_all_image_tools`

            :py:meth:`.plot.PlotManager.register_all_curve_tools`
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

    def register_all_annotation_tools(self):
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

    def register_curve_annotation_tools(self):
        """
        Register all curve friendly annotation tools for the plot
        """
        self.add_separator_tool()

        self.add_tool(AnnotatedPointTool)
        self.add_tool(AnnotatedSegmentTool)

        self.add_tool(LabelTool)

    def register_image_annotation_tools(self):
        """
        Register all image friendly annotation tools for the plot
        """

        # No curve-specific annotation tool, so this is equivalent to the
        # register_all_annotation_tools function for now
        self.register_all_annotation_tools()

    def synchronize_axis(self, axis, plots):
        """

        :param axis:
        :param plots:
        """
        for plot_id in plots:
            synclist = self.synchronized_plots.setdefault(plot_id, [])
            for plot2_id in plots:
                if plot_id == plot2_id:
                    continue
                item = (axis, plot2_id)
                if item not in synclist:
                    synclist.append(item)

    def plot_axis_changed(self, plot):
        """

        :param plot:
        :return:
        """
        plot_id = plot.plot_id
        if plot_id not in self.synchronized_plots:
            return
        for (axis, other_plot_id) in self.synchronized_plots[plot_id]:
            scalediv = plot.axisScaleDiv(axis)
            map = plot.canvasMap(axis)
            other = self.get_plot(other_plot_id)
            lb = scalediv.lowerBound()
            ub = scalediv.upperBound()
            other.setAxisScale(axis, lb, ub)
            other.replot()


assert_interfaces_valid(PlotManager)


# ===============================================================================
# Curve Plot Widget/Dialog with integrated Item list widget
# ===============================================================================
def configure_plot_splitter(qsplit, decreasing_size=True):
    """

    :param qsplit:
    :param decreasing_size:
    """
    qsplit.setChildrenCollapsible(False)
    qsplit.setHandleWidth(4)
    if decreasing_size:
        qsplit.setStretchFactor(0, 1)
        qsplit.setStretchFactor(1, 0)
        qsplit.setSizes([2, 1])
    else:
        qsplit.setStretchFactor(0, 0)
        qsplit.setStretchFactor(1, 1)
        qsplit.setSizes([1, 2])


class SubplotWidget(QSplitter):
    """Construct a Widget that helps managing several plots
    together handled by the same manager

    Since the plots must be added to the manager before the panels
    the add_itemlist method can be called after having declared
    all the subplots
    """

    def __init__(self, manager, parent=None, **kwargs):
        super(SubplotWidget, self).__init__(parent, **kwargs)
        self.setOrientation(Qt.Horizontal)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.manager = manager
        self.plots = []
        self.itemlist = None
        main = QWidget()
        self.plotlayout = QGridLayout()
        main.setLayout(self.plotlayout)
        self.addWidget(main)

    def add_itemlist(self, show_itemlist=False):
        """

        :param show_itemlist:
        """
        self.itemlist = PlotItemList(self)
        self.itemlist.setVisible(show_itemlist)
        self.addWidget(self.itemlist)
        configure_plot_splitter(self)
        self.manager.add_panel(self.itemlist)

    def add_subplot(self, plot, i=0, j=0, plot_id=None):
        """Add a plot to the grid of plots"""
        self.plotlayout.addWidget(plot, i, j)
        self.plots.append(plot)
        if plot_id is None:
            plot_id = id(plot)
        self.manager.add_plot(plot, plot_id)


class BasePlotWidget(QSplitter):
    """
    Construct a BasePlotWidget object, which includes:
        * A plot (:py:class:`.baseplot.BasePlot`)
        * An `item list` panel (:py:class:`.baseplot.PlotItemList`)
        * A `contrast adjustment` panel
          (:py:class:`.histogram.ContrastAdjustment`)
        * An `X-axis cross section` panel
          (:py:class:`.cross_section.XCrossSection`)
        * An `Y-axis cross section` panel
          (:py:class:`.cross_section.YCrossSection`)

    This object does nothing in itself because plot and panels are not
    connected to each other.
    See class :py:class:`.plot.PlotWidget`
    """

    def __init__(
        self,
        parent=None,
        title="",
        xlabel=("", ""),
        ylabel=("", ""),
        zlabel=None,
        xunit=("", ""),
        yunit=("", ""),
        zunit=None,
        yreverse=None,
        colormap="jet",
        aspect_ratio=1.0,
        lock_aspect_ratio=None,
        show_contrast=False,
        show_itemlist=False,
        show_xsection=False,
        show_ysection=False,
        xsection_pos="top",
        ysection_pos="right",
        gridparam=None,
        curve_antialiasing=None,
        section="plot",
        type=PlotType.AUTO,
        no_image_analysis_widgets=False,
        force_colorbar_enabled=False,
        **kwargs
    ):
        super(BasePlotWidget, self).__init__(parent, **kwargs)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.plot = BasePlot(
            parent=self,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            zlabel=zlabel,
            xunit=xunit,
            yunit=yunit,
            zunit=zunit,
            yreverse=yreverse,
            aspect_ratio=aspect_ratio,
            lock_aspect_ratio=lock_aspect_ratio,
            gridparam=gridparam,
            section=section,
            type=type,
            force_colorbar_enabled=force_colorbar_enabled,
        )
        if curve_antialiasing is not None:
            self.plot.set_antialiasing(curve_antialiasing)

        self.itemlist = PlotItemList(self)
        self.itemlist.setVisible(show_itemlist)

        # for curves only plots, or MANUAL plots with the no_image_analysis_widgets option,
        # don't add splitters and widgets dedicated to images since
        # they make the widget more "laggy" when resized.
        if type == PlotType.CURVE or (
            type == PlotType.MANUAL and no_image_analysis_widgets is True
        ):

            self.setOrientation(Qt.Horizontal)
            self.addWidget(self.plot)
            self.addWidget(self.itemlist)

            self.xcsw = None
            self.ycsw = None
            self.contrast = None
        else:
            self.setOrientation(Qt.Vertical)
            self.sub_splitter = QSplitter(Qt.Horizontal, self)

            from plotpy.gui.widgets.cross_section import YCrossSection

            self.ycsw = YCrossSection(
                self, position=ysection_pos, xsection_pos=xsection_pos
            )
            self.ycsw.setVisible(show_ysection)

            from plotpy.gui.widgets.cross_section import XCrossSection

            self.xcsw = XCrossSection(self)
            self.xcsw.setVisible(show_xsection)

            self.xcsw.SIG_VISIBILITY_CHANGED.connect(self.xcsw_is_visible)

            self.xcsw_splitter = QSplitter(Qt.Vertical, self)
            if xsection_pos == "top":
                self.xcsw_splitter.addWidget(self.xcsw)
                self.xcsw_splitter.addWidget(self.plot)
            else:
                self.xcsw_splitter.addWidget(self.plot)
                self.xcsw_splitter.addWidget(self.xcsw)
            self.xcsw_splitter.splitterMoved.connect(
                lambda pos, index: self.adjust_ycsw_height()
            )

            self.ycsw_splitter = QSplitter(Qt.Horizontal, self)
            if ysection_pos == "left":
                self.ycsw_splitter.addWidget(self.ycsw)
                self.ycsw_splitter.addWidget(self.xcsw_splitter)
            else:
                self.ycsw_splitter.addWidget(self.xcsw_splitter)
                self.ycsw_splitter.addWidget(self.ycsw)

            configure_plot_splitter(
                self.xcsw_splitter, decreasing_size=xsection_pos == "bottom"
            )
            configure_plot_splitter(
                self.ycsw_splitter, decreasing_size=ysection_pos == "right"
            )

            self.sub_splitter.addWidget(self.ycsw_splitter)
            self.sub_splitter.addWidget(self.itemlist)

            # Contrast adjustment (Levels histogram)
            from plotpy.gui.widgets.histogram import ContrastAdjustment

            self.contrast = ContrastAdjustment(self)
            self.contrast.setVisible(show_contrast)
            self.addWidget(self.contrast)

            configure_plot_splitter(self.sub_splitter)

        configure_plot_splitter(self)

    def adjust_ycsw_height(self, height=None):
        """

        :param height:
        """
        if height is None:
            height = self.xcsw.height() - self.ycsw.toolbar.height()
        self.ycsw.adjust_height(height)
        if height:
            QApplication.processEvents()

    def xcsw_is_visible(self, state):
        """

        :param state:
        """
        if state:
            QApplication.processEvents()
            self.adjust_ycsw_height()
        else:
            self.adjust_ycsw_height(0)


class PlotWidgetMixin(PlotManager):
    """Mixin used by PlotWidget, PlotDialog and PlotWindow

    .. py:attribute:: plot_layout

        a `QGridLayout`
    """

    def __init__(
        self,
        wintitle="plotpy plot",
        icon="plotpy.svg",
        toolbar=False,
        auto_tools=True,
        options=None,
        panels=None,
    ):
        PlotManager.__init__(self, main=self)

        self.plot_layout = QGridLayout()

        if options is None:
            options = {}
        self.plot_widget = None
        self.create_plot(options)

        if panels is not None:
            for panel in panels:
                self.add_panel(panel)

        self.toolbar = QToolBar(_("Tools"))
        if not toolbar:
            self.toolbar.hide()

        # Configuring widget layout
        self.setup_widget_properties(wintitle=wintitle, icon=icon)
        self.setup_widget_layout()

        # Configuring plot manager
        self.setup_plot_manager(auto_tools)

    def setup_widget_layout(self):
        """

        """
        raise NotImplementedError

    def setup_plot_manager(self, auto_tools=True):
        """

        :param auto_tools:
        """
        self.add_toolbar(self.toolbar, "default")
        if auto_tools is True:
            self.register_tools()

    def setup_widget_properties(self, wintitle, icon):
        """

        :param wintitle:
        :param icon:
        """
        self.setWindowTitle(wintitle)
        if isinstance(icon, str):
            icon = get_icon(icon)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setMinimumSize(320, 240)
        self.resize(640, 480)

    def register_tools(self):
        """
        Register the plotting dialog box tools: the base implementation
        provides standard, curve and/or image-related and other tools, depending on the plot type

        This method may be overriden to provide a fully customized set of tools
        """
        plot_type = self.plot_widget.plot.type
        if plot_type == PlotType.CURVE:
            self.register_all_curve_tools()
        elif plot_type == PlotType.IMAGE:
            self.register_all_image_tools()
        elif plot_type == PlotType.AUTO:
            self.register_all_tools()

    def create_plot(self, options, row=0, column=0, rowspan=1, columnspan=1):
        """
        Create the plotting widget (which is an instance of class
        :py:class:`.plot.BasePlotWidget`), add it to the dialog box
        main layout (:py:attr:`.PlotWidgetMixin.plot_layout`) and
        then add the `item list` panel

        May be overriden to customize the plot layout
        (:py:attr:`.PlotWidgetMixin.plot_layout`)
        """
        self.plot_widget = BasePlotWidget(self, **options)
        self.plot_layout.addWidget(self.plot_widget, row, column, rowspan, columnspan)

        # Configuring plot manager
        self.add_plot(self.plot_widget.plot)
        self.add_panel(self.plot_widget.itemlist)
        if self.plot_widget.xcsw is not None:
            self.add_panel(self.plot_widget.xcsw)
        if self.plot_widget.ycsw is not None:
            self.add_panel(self.plot_widget.ycsw)
        if self.plot_widget.contrast is not None:
            self.add_panel(self.plot_widget.contrast)


class PlotDialog(QDialog, PlotWidgetMixin):
    """
    Construct a PlotDialog object: plotting dialog box with integrated
    plot manager

        * wintitle: window title
        * icon: window icon
        * edit: editable state
        * toolbar: show/hide toolbar
        * options: options sent to the :py:class:`.baseplot.BasePlot` object
          (dictionary)
        * parent: parent widget
        * panels (optional): additionnal panels (list, tuple)

    .. py:attribute:: button_layout

        Container for standard buttons (OK, Cancel)
    """

    def __init__(
        self,
        wintitle="plotpy plot",
        icon="plotpy.svg",
        edit=False,
        toolbar=False,
        auto_tools=True,
        options=None,
        parent=None,
        panels=None,
    ):
        self.edit = edit
        self.button_box = None
        self.button_layout = None
        super(PlotDialog, self).__init__(
            parent,
            wintitle=wintitle,
            icon=icon,
            toolbar=toolbar,
            auto_tools=auto_tools,
            options=options,
            panels=panels,
        )
        self.setWindowFlags(Qt.Window)

    def setup_widget_layout(self):
        """

        """
        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.toolbar)
        vlayout.addLayout(self.plot_layout)
        self.setLayout(vlayout)
        if self.edit:
            self.button_layout = QHBoxLayout()
            self.install_button_layout()
            vlayout.addLayout(self.button_layout)

    def install_button_layout(self):
        """
        Install standard buttons (OK, Cancel) in dialog button box layout
        (:py:attr:`.plot.PlotDialog.button_layout`)

        This method may be overriden to customize the button box
        """
        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.button_layout.addWidget(bbox)
        self.button_box = bbox


class PlotWindow(QMainWindow, PlotWidgetMixin):
    """
    Construct a PlotWindow object: plotting window with integrated plot
    manager

        * wintitle: window title
        * icon: window icon
        * toolbar: show/hide toolbar
        * options: options sent to the :py:class:`.baseplot.BasePlot` object
          (dictionary)
        * parent: parent widget
        * panels (optional): additionnal panels (list, tuple)
    """

    def __init__(
        self,
        wintitle="plotpy plot",
        icon="plotpy.svg",
        toolbar=False,
        auto_tools=True,
        options=None,
        parent=None,
        panels=None,
    ):
        super(PlotWindow, self).__init__(
            parent,
            wintitle=wintitle,
            icon=icon,
            toolbar=toolbar,
            auto_tools=auto_tools,
            options=options,
            panels=panels,
        )

    def setup_widget_layout(self):
        """

        """
        self.addToolBar(self.toolbar)
        widget = QWidget()
        widget.setLayout(self.plot_layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        """

        :param event:
        """
        # Closing panels (necessary if at least one of these panels has no
        # parent widget: otherwise, this panel will stay open after the main
        # window has been closed which is not the expected behavior)
        for panel in self.panels:
            self.get_panel(panel).close()
        QMainWindow.closeEvent(self, event)


class PlotWidget(QWidget, PlotWidgetMixin):
    """
    Construct a PlotWidget object: plotting widget with integrated
    plot manager

        * parent: parent widget
        * options: options sent to the :py:class:`.baseplot.BasePlot` object
          (dictionary)
        * panels (optional): additionnal panels (list, tuple)
    """

    def __init__(self, parent=None, options=None, panels=None):
        super(PlotWidget, self).__init__(parent=parent, options=options, panels=panels)

        # to limit the API change of the old ImageWidget and PlotWidget classes and avoid
        # calls to plotwidget.plot_widget.plot instead of plotwidget.plot
        self.plot = self.plot_widget.plot

    def setup_widget_layout(self):
        """

        """
        vlayout = QVBoxLayout(self)
        vlayout.addLayout(self.plot_layout)
        self.setLayout(vlayout)

    def setup_plot_manager(self, auto_tools):
        """

        :param auto_tools:
        """
        # don't do anything here for PlotWidget. The toolbar and tools registration
        # are done manually for this class, see simple_window.py example.
        pass
