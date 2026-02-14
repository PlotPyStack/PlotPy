# -*- coding: utf-8

from __future__ import annotations

import abc
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from guidata.configtools import get_icon
from guidata.qthelpers import is_qobject_valid, win32_fix_title_bar_background
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QWidget  # only to help intersphinx find QWidget

from plotpy.config import _
from plotpy.constants import X_BOTTOM, Y_LEFT, PlotType
from plotpy.plot.base import BasePlot, BasePlotOptions
from plotpy.plot.manager import PlotManager

if TYPE_CHECKING:
    from plotpy.panels.base import PanelWidget


def configure_plot_splitter(qsplit: QW.QSplitter, decreasing_size: bool = True) -> None:
    """Configure a QSplitter for plot widgets

    Args:
        qsplit: QSplitter instance
        decreasing_size: Specify if child widgets can be resized down
         to size 0 by the user. Defaults to True.
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


@dataclass
class PlotOptions(BasePlotOptions):
    """Plot options

    Args:
        title: The plot title
        xlabel: (bottom axis title, top axis title) or bottom axis title only
        ylabel: (left axis title, right axis title) or left axis title only
        zlabel: The Z-axis label
        xunit: (bottom axis unit, top axis unit) or bottom axis unit only
        yunit: (left axis unit, right axis unit) or left axis unit only
        zunit: The Z-axis unit
        yreverse: If True, the Y-axis is reversed
        aspect_ratio: The plot aspect ratio
        lock_aspect_ratio: If True, the aspect ratio is locked
        curve_antialiasing: If True, the curve antialiasing is enabled
        gridparam: The grid parameters
        section: The plot configuration section name ("plot", by default)
        type: The plot type ("auto", "manual", "curve" or "image")
        axes_synchronised: If True, the axes are synchronised
        force_colorbar_enabled: If True, the colorbar is always enabled
        no_image_analysis_widgets: If True, the image analysis widgets are not added
        show_contrast: If True, the contrast adjustment panel is visible
        show_itemlist: If True, the itemlist panel is visible
        show_xsection: If True, the X-axis cross section panel is visible
        show_ysection: If True, the Y-axis cross section panel is visible
        xsection_pos: The X-axis cross section panel position ("top" or "bottom")
        ysection_pos: The Y-axis cross section panel position ("left" or "right")
    """

    no_image_analysis_widgets: bool = False
    show_contrast: bool = False
    show_itemlist: bool = False
    show_xsection: bool = False
    show_ysection: bool = False
    xsection_pos: str = "top"
    ysection_pos: str = "right"

    def __post_init__(self) -> None:
        """Check arguments"""
        super().__post_init__()
        # Check xsection_pos and ysection_pos
        if self.xsection_pos not in ["top", "bottom"]:
            raise ValueError("xsection_pos must be 'top' or 'bottom'")
        if self.ysection_pos not in ["left", "right"]:
            raise ValueError("ysection_pos must be 'left' or 'right'")
        # Show warning if no image analysis widgets is True and type is not manual
        if self.no_image_analysis_widgets and self.type != "manual":
            warnings.warn(
                "no_image_analysis_widgets is True but type is not 'manual' "
                "(option ignored)",
                RuntimeWarning,
            )


class BasePlotWidget(QW.QSplitter):
    """Base class for plot widgets

    This widget is a ``QSplitter`` that contains a plot, several panels and a toolbar.
    It also includes tools (as in the :py:mod:`.tools` module) for manipulating the
    plot, its items and its panels. All these elements are managed by a
    :py:class:`.PlotManager` object. The plot manager is accessible through the
    :py:attr:`.PlotWidget.manager` attribute.

    Args:
        parent: The parent widget
        options: Plot options
    """

    def __init__(
        self,
        parent: QWidget = None,
        options: PlotOptions | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)
        self.manager: PlotManager | None = None
        if isinstance(options, dict):
            options = PlotOptions(**options)
        self.options = options = options if options is not None else PlotOptions()
        self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)
        self.plot = self.create_plot()

        # Avoid circular import
        # pylint: disable=import-outside-toplevel
        from plotpy.panels.itemlist import PlotItemList

        self.itemlist = PlotItemList(self)
        self.itemlist.setVisible(options.show_itemlist)

        # For CURVE plots, or MANUAL plots with the ``no_image_analysis_widgets``
        # option, don't add splitters and widgets dedicated to images since
        # they make the widget more "laggy" when resized.
        if options.type == PlotType.CURVE or (
            options.type == PlotType.MANUAL and options.no_image_analysis_widgets
        ):
            self.__set_curve_layout()
        else:
            self.__set_image_layout()

        configure_plot_splitter(self)

    # ---- Private API -----------------------------------------------------------------
    def __set_curve_layout(self) -> None:
        """Set the layout for curve only plots"""
        self.setOrientation(QC.Qt.Orientation.Horizontal)
        self.addWidget(self.plot)
        self.addWidget(self.itemlist)

        self.xcsw = None
        self.ycsw = None
        self.contrast = None

    def __set_image_layout(self) -> None:
        """Set the layout for image only plots"""
        self.setOrientation(QC.Qt.Orientation.Vertical)
        self.sub_splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal, self)

        # Avoid circular import
        # pylint: disable=import-outside-toplevel
        from plotpy.panels.csection.cswidget import XCrossSection, YCrossSection

        self.ycsw = YCrossSection(
            self,
            position=self.options.ysection_pos,
            xsection_pos=self.options.xsection_pos,
        )
        self.ycsw.setVisible(self.options.show_ysection)

        self.xcsw = XCrossSection(self)
        self.xcsw.setVisible(self.options.show_xsection)

        self.xcsw.SIG_VISIBILITY_CHANGED.connect(self.__xcsw_is_visible)
        self.xcsw.SIG_RESIZED.connect(self.__adjust_ycsw_height)

        self.xcsw_splitter = QW.QSplitter(QC.Qt.Orientation.Vertical, self)
        if self.options.xsection_pos == "top":
            self.xcsw_splitter.addWidget(self.xcsw)
            self.xcsw_splitter.addWidget(self.plot)
        else:
            self.xcsw_splitter.addWidget(self.plot)
            self.xcsw_splitter.addWidget(self.xcsw)

        self.ycsw_splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal, self)
        if self.options.ysection_pos == "left":
            self.ycsw_splitter.addWidget(self.ycsw)
            self.ycsw_splitter.addWidget(self.xcsw_splitter)
        else:
            self.ycsw_splitter.addWidget(self.xcsw_splitter)
            self.ycsw_splitter.addWidget(self.ycsw)

        configure_plot_splitter(
            self.xcsw_splitter, decreasing_size=self.options.xsection_pos == "bottom"
        )
        configure_plot_splitter(
            self.ycsw_splitter, decreasing_size=self.options.ysection_pos == "right"
        )

        self.sub_splitter.addWidget(self.ycsw_splitter)
        self.sub_splitter.addWidget(self.itemlist)

        # Contrast adjustment (Levels histogram)
        # Avoid circular import
        # pylint: disable=import-outside-toplevel
        from plotpy.panels.contrastadjustment import ContrastAdjustment

        self.contrast = ContrastAdjustment(self)
        self.contrast.setVisible(self.options.show_contrast)
        self.addWidget(self.contrast)

        configure_plot_splitter(self.sub_splitter)

    def __adjust_ycsw_height(self, height: int | None = None) -> None:
        """Adjust the Y-axis cross section panel height

        Args:
            height: The height (in pixels) to set. If None, the height is adjusted
             to the current height of the widget.
        """
        if height is None:
            height = self.xcsw.height() - self.ycsw.toolbar.height()
        self.ycsw.adjust_height(height)

    def __xcsw_is_visible(self, state: bool) -> None:
        """Callback when the X-axis cross section panel visibility changes

        Args:
            state: The new visibility state of the X-axis cross section panel
        """
        if state:
            self.__adjust_ycsw_height()
        else:
            self.__adjust_ycsw_height(0)

    # ---- Public API ------------------------------------------------------------------
    def create_plot(self) -> BasePlot:
        """Create the plot, which is the main widget of the base plot widget.
        In subclasses, this method can be overriden to create a custom plot object,
        as for example multiple plots in a grid layout."""
        return BasePlot(parent=self, options=self.options)

    def add_panels_to_manager(self) -> None:
        """Add the panels to the plot manager

        Raises:
            RuntimeError: If the plot manager is not defined
        """
        if self.manager is None:
            raise RuntimeError("Plot manager is not defined")
        self.manager.add_panel(self.itemlist)
        if self.xcsw is not None:
            self.manager.add_panel(self.xcsw)
        if self.ycsw is not None:
            self.manager.add_panel(self.ycsw)
        if self.contrast is not None:
            self.manager.add_panel(self.contrast)

    def register_tools(self) -> None:
        """Register the plotting tools according to the plot type

        Raises:
            RuntimeError: If the plot manager is not defined
        """
        if self.manager is None:
            raise RuntimeError("Plot manager is not defined")
        if self.options.type == PlotType.CURVE:
            self.manager.register_all_curve_tools()
        elif self.options.type == PlotType.IMAGE:
            self.manager.register_all_image_tools()
        elif self.options.type == PlotType.AUTO:
            self.manager.register_all_tools()

    def register_annotation_tools(self) -> None:
        """Register the annotation tools according to the plot type

        Raises:
            RuntimeError: If the plot manager is not defined
        """
        if self.manager is None:
            raise RuntimeError("Plot manager is not defined")
        if self.options.type == PlotType.CURVE:
            self.manager.register_curve_annotation_tools()
        elif self.options.type == PlotType.IMAGE:
            self.manager.register_image_annotation_tools()
        elif self.options.type == PlotType.AUTO:
            self.manager.register_all_annotation_tools()


class PlotWidget(BasePlotWidget):
    """Plot widget with integrated plot manager, toolbar, tools and panels

    Args:
        parent: Parent widget
        toolbar: Show/hide toolbar
        options: Plot options
        panels: Additionnal panels
        auto_tools: If True, the plot tools are automatically registered.
         If False, the user must register the tools manually.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        options: PlotOptions | dict[str, Any] | None = None,
        panels: tuple[PanelWidget] | None = None,
        auto_tools: bool = True,
    ) -> None:
        super().__init__(parent, options)
        self.manager = PlotManager(self)
        self.toolbar: QW.QToolBar | None = None
        self.configure_manager(panels, toolbar)
        if auto_tools:
            self.register_tools()

    # ---- Public API ------------------------------------------------------------------
    def get_plot(self) -> BasePlot:
        """Return the plot object

        Returns:
            BasePlot: The plot object
        """
        return self.plot

    def get_toolbar(self) -> QW.QToolBar:
        """Return main toolbar

        Returns:
            The plot widget main toolbar
        """
        return self.toolbar

    def get_manager(self) -> PlotManager:
        """Return the plot manager

        Returns:
            The plot widget manager
        """
        return self.manager

    def configure_manager(
        self,
        panels: tuple[PanelWidget] | None = None,
        toolbar: bool = True,
    ) -> None:
        """Configure the plot manager

        Args:
            panels: additionnal panels (list, tuple). Defaults to None.
            toolbar: [description]. Defaults to True.
        """
        self.manager.add_plot(self.get_plot())
        self.add_panels_to_manager()
        if panels is not None:
            for panel in panels:
                self.manager.add_panel(panel)
        self.toolbar = QW.QToolBar(_("Tools"))
        if toolbar:
            self.manager.add_toolbar(self.toolbar, "default")
        else:
            self.toolbar.hide()


def set_widget_title_icon(
    widget: QWidget, title: str, icon: QG.QIcon, size: tuple[int, int] | None = None
) -> None:
    """Setups the widget title and icon

    Args:
        title: The window title
        icon: The window icon
        size: The window size (width, height). Defaults to None (no resize)
    """
    win32_fix_title_bar_background(widget)
    widget.setWindowTitle(title)
    if isinstance(icon, str):
        icon = get_icon(icon)
    if icon is not None:
        widget.setWindowIcon(icon)
    widget.setMinimumSize(320, 240)
    if size is not None:
        widget.resize(*size)


def add_widget_to_grid_layout(
    layout: QW.QGridLayout,
    widget: QWidget,
    row: int | None = None,
    column: int | None = None,
    rowspan: int | None = None,
    columnspan: int | None = None,
) -> None:
    """Add widget to the grid layout

    Args:
        layout: The layout
        widget: The widget to add
        row: The row index
        column: The column index
        rowspan: The row span
        columnspan: The column span

    If row, column, rowspan and columnspan are None, the widget is added to the grid
    layout after the previous one (i.e. same as the method addWidget without options).

    If row is not None, column must be not None and the widget is added to the grid
    layout at the specified row and column. If rowspan is not None, the widget is
    added to the grid layout with the specified row span. If columnspan is not None,
    the widget is added to the grid layout with the specified column span.
    """
    if row is None and column is None and rowspan is None and columnspan is None:
        layout.addWidget(widget)
    else:
        if row is None or column is None:
            raise ValueError("row and column must be specified")
        if rowspan is None and columnspan is None:
            layout.addWidget(widget, row, column)
        elif rowspan is None:
            layout.addWidget(widget, row, column, 1, columnspan)
        elif columnspan is None:
            layout.addWidget(widget, row, column, rowspan, 1)
        else:
            layout.addWidget(widget, row, column, rowspan, columnspan)


class AbstractPlotDialogWindow(abc.ABC):
    """Abstract base class for plot dialog and plot window"""

    @abc.abstractmethod
    def get_plot(self) -> BasePlot | None:
        """Return the plot object

        Returns:
            BasePlot: The plot object
        """

    @abc.abstractmethod
    def get_toolbar(self) -> QW.QToolBar:
        """Return main toolbar

        Returns:
            The plot widget main toolbar
        """

    @abc.abstractmethod
    def get_manager(self) -> PlotManager:
        """Return the plot manager

        Returns:
            The plot widget manager
        """

    @abc.abstractmethod
    def setup_widget(
        self,
        toolbar: bool = False,
        options: PlotOptions | dict[str, Any] | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = False,
    ) -> None:
        """Setup the widget

        Args:
            toolbar: If True, the plot toolbar is displayed
            options: Plot options
            panels: The panels to add to the plot
            auto_tools: If True, the plot tools are automatically registered.
             If False, the user must register the tools manually.
        """

    @abc.abstractmethod
    def add_widget(
        self,
        widget: QWidget,
        row: int | None = None,
        column: int | None = None,
        rowspan: int | None = None,
        columnspan: int | None = None,
    ) -> None:
        """Add widget to the widget main layout

        Args:
            widget: The widget to add
            row: The row index
            column: The column index
            rowspan: The row span
            columnspan: The column span
        """

    @abc.abstractmethod
    def populate_plot_layout(self) -> None:
        """Populate the plot layout"""

    @abc.abstractmethod
    def setup_layout(self) -> None:
        """Setup the widget layout"""

    @abc.abstractmethod
    def register_tools(self):
        """
        Register the plotting tools: the base implementation of this method
        register tools according to the plot type (curve, image, etc.)

        This method may be overriden to provide a fully customized set of tools
        """

    @abc.abstractmethod
    def register_annotation_tools(self):
        """
        Register the annotation tools: the base implementation of this method
        register tools according to the plot type (curve, image, etc.)

        This method may be overriden to provide a fully customized set of tools
        """


class PlotDialogMeta(type(QW.QDialog), abc.ABCMeta):
    """Mixed metaclass to avoid conflicts"""


class PlotDialog(QW.QDialog, AbstractPlotDialogWindow, metaclass=PlotDialogMeta):
    """Plotting dialog box with integrated plot manager

    Args:
        parent: parent widget
        toolbar: show/hide toolbar
        options: plot options
        panels: additionnal panels
        auto_tools: If True, the plot tools are automatically registered.
         If False, the user must register the tools manually.
        title: The window title
        icon: The window icon
        edit: If True, the plot is editable
        size: The window size (width, height). Defaults to None (no resize)
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        options: PlotOptions | dict[str, Any] | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = True,
        title: str = "PlotPy",
        icon: str = "plotpy.svg",
        edit: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(parent)
        set_widget_title_icon(self, title, icon, size)
        self.edit = edit
        self.button_box = None
        self.button_layout = None
        self.plot_layout = QW.QGridLayout()
        self.plot_widget: PlotWidget = None
        self.manager: PlotManager = None
        self.setup_widget(toolbar, options, panels, auto_tools)
        self.setWindowFlags(QC.Qt.Window)

    def get_plot(self) -> BasePlot | None:
        """Return the plot object

        Returns:
            BasePlot: The plot object
        """
        if self.plot_widget is not None:
            return self.plot_widget.get_plot()
        return None

    def get_toolbar(self) -> QW.QToolBar:
        """Return main toolbar

        Returns:
            The plot widget main toolbar
        """
        if self.plot_widget is not None:
            return self.plot_widget.get_toolbar()
        return None

    def get_manager(self) -> PlotManager:
        """Return the plot manager

        Returns:
            The plot widget manager
        """
        if self.plot_widget is not None:
            return self.plot_widget.get_manager()
        return None

    def setup_widget(
        self,
        toolbar: bool = False,
        options: PlotOptions | dict[str, Any] | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = False,
    ) -> None:
        """Setup the widget

        Args:
            toolbar: If True, the plot toolbar is displayed
            options: Plot options
            panels: The panels to add to the plot
            auto_tools: If True, the plot tools are automatically registered.
             If False, the user must register the tools manually.
        """
        self.plot_widget = PlotWidget(self, toolbar, options, panels, auto_tools=False)
        self.manager = self.plot_widget.manager
        self.populate_plot_layout()
        self.setup_layout()
        if auto_tools:
            self.register_tools()

    def add_widget(
        self,
        widget: QWidget,
        row: int | None = None,
        column: int | None = None,
        rowspan: int | None = None,
        columnspan: int | None = None,
    ) -> None:
        """Add widget to the widget main layout

        Args:
            widget: The widget to add
            row: The row index
            column: The column index
            rowspan: The row span
            columnspan: The column span
        """
        add_widget_to_grid_layout(
            self.plot_layout, widget, row, column, rowspan, columnspan
        )

    def populate_plot_layout(self) -> None:
        """Populate the plot layout"""
        self.add_widget(self.plot_widget)

    def setup_layout(self) -> None:
        """Setup the widget layout"""
        vlayout = QW.QVBoxLayout(self)
        vlayout.addWidget(self.plot_widget.toolbar)
        vlayout.addLayout(self.plot_layout)
        self.setLayout(vlayout)
        if self.edit:
            self.button_layout = QW.QHBoxLayout()
            self.install_button_layout()
            vlayout.addLayout(self.button_layout)

    def install_button_layout(self) -> None:
        """Install standard buttons (OK, Cancel) in dialog button box layout

        This method may be overriden to customize the button box
        """
        bbox = QW.QDialogButtonBox(QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.button_layout.addWidget(bbox)
        self.button_box = bbox

    def register_tools(self):
        """Register the plotting tools: the base implementation of this method
        register tools according to the plot type (curve, image, etc.)

        This method may be overriden to provide a fully customized set of tools
        """
        self.plot_widget.register_tools()

    def register_annotation_tools(self):
        """Register the annotation tools: the base implementation of this method
        register tools according to the plot type (curve, image, etc.)

        This method may be overriden to provide a fully customized set of tools
        """
        self.plot_widget.register_annotation_tools()


class PlotWindowMeta(type(QW.QMainWindow), abc.ABCMeta):
    """Mixed metaclass to avoid conflicts"""


class PlotWindow(QW.QMainWindow, AbstractPlotDialogWindow, metaclass=PlotWindowMeta):
    """Plotting window with integrated plot manager

    Args:
        parent: parent widget
        toolbar: show/hide toolbar
        options: plot options
        panels: additionnal panels
        auto_tools: If True, the plot tools are automatically registered.
         If False, the user must register the tools manually.
        title: The window title
        icon: The window icon
        size: The window size (width, height). Defaults to None (no resize)
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        options: PlotOptions | dict[str, Any] | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = True,
        title: str = "PlotPy",
        icon: str = "plotpy.svg",
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(parent)
        set_widget_title_icon(self, title, icon, size)
        self.plot_layout = QW.QGridLayout()
        self.plot_widget: PlotWidget = None
        self.manager: PlotManager = None
        self.setup_widget(toolbar, options, panels, auto_tools)

    def get_plot(self) -> BasePlot | None:
        """Return the plot object

        Returns:
            BasePlot: The plot object
        """
        if self.plot_widget is not None:
            return self.plot_widget.get_plot()
        return None

    def get_toolbar(self) -> QW.QToolBar:
        """Return main toolbar

        Returns:
            The plot widget main toolbar
        """
        if self.plot_widget is not None:
            return self.plot_widget.get_toolbar()
        return None

    def get_manager(self) -> PlotManager:
        """Return the plot manager

        Returns:
            The plot widget manager
        """
        if self.plot_widget is not None:
            return self.plot_widget.get_manager()
        return None

    def setup_widget(
        self,
        toolbar: bool = False,
        options: PlotOptions | dict[str, Any] | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = False,
    ) -> None:
        """Setup the widget

        Args:
            toolbar: If True, the plot toolbar is displayed
            options: Plot options
            panels: The panels to add to the plot
            auto_tools: If True, the plot tools are automatically registered.
             If False, the user must register the tools manually.
        """
        self.plot_widget = PlotWidget(self, toolbar, options, panels, auto_tools=False)
        self.manager = self.plot_widget.manager
        self.populate_plot_layout()
        self.setup_layout()
        if auto_tools:
            self.register_tools()

    def add_widget(
        self,
        widget: QWidget,
        row: int | None = None,
        column: int | None = None,
        rowspan: int | None = None,
        columnspan: int | None = None,
    ) -> None:
        """Add widget to the widget main layout

        Args:
            widget: The widget to add
            row: The row index
            column: The column index
            rowspan: The row span
            columnspan: The column span
        """
        add_widget_to_grid_layout(
            self.plot_layout, widget, row, column, rowspan, columnspan
        )

    def populate_plot_layout(self) -> None:
        """Populate the plot layout"""
        self.add_widget(self.plot_widget)

    def setup_layout(self) -> None:
        """Setup the widget layout"""
        self.addToolBar(self.plot_widget.toolbar)
        widget = QWidget()
        widget.setLayout(self.plot_layout)
        self.setCentralWidget(widget)

    def register_tools(self):
        """
        Register the plotting tools: the base implementation of this method
        register tools according to the plot type (curve, image, etc.)

        This method may be overriden to provide a fully customized set of tools
        """
        self.plot_widget.register_tools()

    def register_annotation_tools(self):
        """Register the annotation tools: the base implementation of this method
        register tools according to the plot type (curve, image, etc.)

        This method may be overriden to provide a fully customized set of tools
        """
        self.plot_widget.register_annotation_tools()

    def closeEvent(self, event) -> None:
        """Reimplement the close event to close all panels

        Args:
            event: The close event
        """
        # Closing panels (necessary if at least one of these panels has no
        # parent widget: otherwise, this panel will stay open after the main
        # window has been closed which is not the expected behavior)
        for panel in self.manager.panels:
            panel_widget = self.manager.get_panel(panel)
            if is_qobject_valid(panel_widget):
                panel_widget.close()
        QW.QMainWindow.closeEvent(self, event)


class SubplotWidget(BasePlotWidget):
    """Construct a Widget that helps managing several plots
    together handled by the same manager

    Since the plots must be added to the manager before the panels
    the add_itemlist method can be called after having declared
    all the subplots

    Args:
        manager: The plot manager
        parent: The parent widget
        options: Plot options
    """

    def __init__(
        self,
        manager: PlotManager,
        parent: QWidget | None = None,
        options: PlotOptions | dict[str, Any] | None = None,
    ) -> None:
        self.plotlayout: QW.QGridLayout | None = None
        super().__init__(parent, options=options)
        self.manager = manager
        self.plots: list[BasePlot] = []

    def create_plot(self) -> QWidget:
        """Create the plot, which is the main widget of the plot widget"""
        main = QWidget()
        self.plotlayout = QW.QGridLayout()
        main.setLayout(self.plotlayout)
        return main

    def get_plots(self) -> list[BasePlot]:
        """Return the plots

        Returns:
            list[BasePlot]: The plots
        """
        return self.plots

    def add_plot(
        self, plot: BasePlot, i: int = 0, j: int = 0, plot_id: str | None = None
    ) -> None:
        """Add a plot to the grid of plots

        Args:
            plot: The plot to add
            i: The row index
            j: The column index
            plot_id: The plot id
        """
        self.plotlayout.addWidget(plot, i, j)
        self.plots.append(plot)
        if plot_id is None:
            plot_id = id(plot)
        self.manager.add_plot(plot, plot_id)


class BaseSyncPlot:
    """Base class for synchronized plot windows and dialogs"""

    def __init__(
        self,
        toolbar: bool = True,
        options: PlotOptions | dict[str, Any] | None = None,
        auto_tools: bool = True,
        title: str = "PlotPy",
        icon: str = "plotpy.svg",
        size: tuple[int, int] | None = None,
    ) -> None:
        self.manager = PlotManager(None)
        self.manager.set_main(self)
        # Note: parent is not set here and widget operations on `self` are
        # deferred to _finalize_init() because PySide6 requires the subclass's
        # __init__ to have fully completed before widget methods can be called.
        self.subplotwidget = SubplotWidget(self.manager, parent=None, options=options)
        self._toolbar_visible = toolbar
        self.auto_tools = auto_tools
        self._rescale_timer: QC.QTimer | None = None
        self._init_title = title
        self._init_icon = icon
        self._init_size = size

    def _finalize_init(self) -> None:
        """Finalize initialization after Qt widget __init__ has completed.

        This is called by subclasses in their __init__ after calling both
        QMainWindow/QDialog.__init__ and BaseSyncPlot.__init__.
        """
        self.toolbar = QW.QToolBar(_("Tools"), self)
        self.toolbar.setVisible(self._toolbar_visible)
        self.manager.add_toolbar(self.toolbar, "default")
        self.toolbar.setMovable(True)
        self.toolbar.setFloatable(True)
        set_widget_title_icon(self, self._init_title, self._init_icon, self._init_size)
        # Note: setup_layout() is called by subclasses after _finalize_init()

    def setup_layout(self) -> None:
        """Setup the layout - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement `setup_layout` method")

    def get_toolbar(self) -> QW.QToolBar:
        """Return main toolbar

        Returns:
            The plot widget main toolbar
        """
        return self.toolbar

    def get_manager(self) -> PlotManager:
        """Return the plot manager

        Returns:
            The plot widget manager
        """
        return self.manager

    def finalize_configuration(self) -> None:
        """Configure plot manager and register all tools"""
        self.subplotwidget.add_panels_to_manager()
        if self.auto_tools:
            self.subplotwidget.register_tools()

    def rescale_plots(self) -> None:
        """Rescale all plots

        Note: This method is called via QTimer.singleShot, so it may be invoked
        even after the widget starts closing. We check if rescaling is still needed.
        """
        # Don't rescale if timer was already stopped (widget is closing)
        if self._rescale_timer is None or not self._rescale_timer.isActive():
            return

        QW.QApplication.instance().processEvents()
        for plot in self.subplotwidget.plots:
            plot.do_autoscale()

    def handle_show_event(self) -> None:
        """Handle the show event to trigger plot rescaling"""
        # Use a QTimer instance so we can stop it if the widget is closed quickly
        if self._rescale_timer is None:
            self._rescale_timer = QC.QTimer(self)
            self._rescale_timer.setSingleShot(True)
            self._rescale_timer.timeout.connect(self.rescale_plots)
        self._rescale_timer.start(0)

    def handle_close_event(self) -> None:
        """Handle the close event to stop pending timer"""
        if self._rescale_timer is not None and self._rescale_timer.isActive():
            self._rescale_timer.stop()

    def add_plot(
        self,
        row: int,
        col: int,
        plot: BasePlot,
        sync: bool = False,
        plot_id: str | None = None,
    ) -> None:
        """Add plot to window

        Args:
            row: The row index
            col: The column index
            plot: The plot to add
            sync: If True, the axes are synchronized
            plot_id: The plot id
        """
        if plot_id is None:
            plot_id = str(len(self.subplotwidget.plots) + 1)
        self.subplotwidget.add_plot(plot, row, col, plot_id)
        if sync and len(self.subplotwidget.plots) > 1:
            self._synchronize_with_existing_plots(plot_id)

    def _synchronize_with_existing_plots(self, plot_id: str) -> None:
        """Synchronize the new plot with existing plots"""
        syncaxis = self.manager.synchronize_axis
        for i_plot in range(len(self.subplotwidget.plots) - 1):
            existing_plot_id = f"{i_plot + 1}"
            syncaxis(X_BOTTOM, [plot_id, existing_plot_id])
            syncaxis(Y_LEFT, [plot_id, existing_plot_id])

    def get_plots(self) -> list[BasePlot]:
        """Return the plots

        Returns:
            list[BasePlot]: The plots
        """
        return self.subplotwidget.get_plots()


class SyncPlotWindow(QW.QMainWindow, BaseSyncPlot):
    """Window for showing plots, optionally synchronized

    Args:
        parent: parent widget
        toolbar: show/hide toolbar
        options: plot options
        panels: additionnal panels
        auto_tools: If True, the plot tools are automatically registered.
         If False, the user must register the tools manually.
        title: The window title
        icon: The window icon
        size: The window size (width, height). Defaults to None (no resize)

    Usage: first, create a window, then add plots to it, then call the
    :py:meth:`.SyncPlotWindow.finalize_configuration` method to add panels and
    eventually register tools.

    Example::

        from plotpy.plot import BasePlot, SyncPlotWindow
        win = SyncPlotWindow(title="My window")
        plot = BasePlot()
        win.add_plot(plot)
        win.finalize_configuration()
        win.show()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        toolbar: bool = True,
        options: PlotOptions | dict[str, Any] | None = None,
        auto_tools: bool = True,
        title: str = "PlotPy",
        icon: str = "plotpy.svg",
        size: tuple[int, int] | None = None,
    ) -> None:
        self.subplotwidget: SubplotWidget
        self.toolbar: QW.QToolBar
        BaseSyncPlot.__init__(self, toolbar, options, auto_tools, title, icon, size)
        QW.QMainWindow.__init__(self, parent)
        self._finalize_init()
        self.setup_layout()

    def showEvent(self, event):  # pylint: disable=C0103
        """Reimplement Qt method"""
        super().showEvent(event)
        self.handle_show_event()

    def closeEvent(self, event):  # pylint: disable=C0103
        """Reimplement Qt method to stop pending timer before closing"""
        self.handle_close_event()
        super().closeEvent(event)

    def setup_layout(self) -> None:
        """Setup the main window layout"""
        self.setCentralWidget(self.subplotwidget)
        self.addToolBar(self.toolbar)


class SyncPlotDialog(QW.QDialog, BaseSyncPlot):
    """Dialog for showing plots, optionally synchronized

    Args:
        parent: parent widget
        toolbar: show/hide toolbar
        options: plot options
        auto_tools: If True, the plot tools are automatically registered.
         If False, the user must register the tools manually.
        title: The window title
        icon: The window icon
        size: The window size (width, height). Defaults to None (no resize)

    Usage: first, create a dialog, then add plots to it, then call the
    :py:meth:`.SyncPlotDialog.finalize_configuration` method to add panels and
    eventually register tools.

    Example::

        from plotpy.plot import BasePlot, SyncPlotDialog
        dlg = SyncPlotDialog(title="My dialog")
        plot = BasePlot()
        dlg.add_plot(plot)
        dlg.finalize_configuration()
        dlg.exec()
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        toolbar: bool = True,
        options: PlotOptions | dict[str, Any] | None = None,
        auto_tools: bool = True,
        title: str = "PlotPy",
        icon: str = "plotpy.svg",
        size: tuple[int, int] | None = None,
    ) -> None:
        self.subplotwidget: SubplotWidget
        self.toolbar: QW.QToolBar
        BaseSyncPlot.__init__(self, toolbar, options, auto_tools, title, icon, size)
        QW.QDialog.__init__(self, parent)
        self._finalize_init()
        self.setup_layout()
        self.setWindowFlags(QC.Qt.Window)

    def showEvent(self, event):  # pylint: disable=C0103
        """Reimplement Qt method"""
        super().showEvent(event)
        self.handle_show_event()

    def closeEvent(self, event):  # pylint: disable=C0103
        """Reimplement Qt method to stop pending timer before closing"""
        self.handle_close_event()
        super().closeEvent(event)

    def setup_layout(self) -> None:
        """Setup the dialog layout"""
        self.plot_layout = QW.QGridLayout()
        self.plot_layout.addWidget(self.subplotwidget)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(self.plot_layout)
        self.setLayout(layout)
