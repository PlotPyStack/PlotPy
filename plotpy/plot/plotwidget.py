# -*- coding: utf-8

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from guidata.configtools import get_icon
from guidata.qthelpers import win32_fix_title_bar_background
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QWidget  # only to help intersphinx find QWidget

from plotpy.config import _
from plotpy.constants import PlotType
from plotpy.panels.contrastadjustment import ContrastAdjustment
from plotpy.panels.csection.cswidget import XCrossSection, YCrossSection
from plotpy.panels.itemlist import PlotItemList
from plotpy.plot.base import BasePlot
from plotpy.plot.manager import PlotManager

if TYPE_CHECKING:
    from plotpy.panels.base import PanelWidget
    from plotpy.styles import GridParam


def configure_plot_splitter(qsplit: QW.QSplitter, decreasing_size: bool = True) -> None:
    """_summary_

    Args:
        qsplit (QSplitter): QSplitter instance
        decreasing_size (bool | None): Specify if child widgets can be resized down
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


class BasePlotWidget(QW.QSplitter):
    """
    Construct a BasePlotWidget object, which includes:
        * A plot (:py:class:`.BasePlot`)
        * An `item list` panel (:py:class:`.PlotItemList`)
        * A `contrast adjustment` panel (:py:class:`.ContrastAdjustment`)
        * An `X-axis cross section` panel (:py:class:`.XCrossSection`)
        * An `Y-axis cross section` panel (:py:class:`.YCrossSection`)

    This object does nothing in itself because plot and panels are not
    connected to each other.
    See class :py:class:`.PlotWidget`
    """

    def __init__(
        self,
        parent: QWidget = None,
        title: str = "",
        xlabel: tuple[str, str] = ("", ""),
        ylabel: tuple[str, str] = ("", ""),
        zlabel: tuple[str, str] | None = None,
        xunit: tuple[str, str] = ("", ""),
        yunit: tuple[str, str] = ("", ""),
        zunit: tuple[str, str] | None = None,
        yreverse: bool | None = None,
        aspect_ratio: float = 1.0,
        lock_aspect_ratio: bool | None = None,
        show_contrast: bool = False,
        show_itemlist: bool = False,
        show_xsection: bool = False,
        show_ysection: bool = False,
        xsection_pos: str = "top",
        ysection_pos: str = "right",
        gridparam: GridParam = None,
        curve_antialiasing: bool | None = None,
        section: str = "plot",
        type: int = PlotType.AUTO,
        no_image_analysis_widgets: bool = False,
        force_colorbar_enabled: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)

        self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)

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

        # for curves only plots, or MANUAL plots with the no_image_analysis_widgets
        # option, don't add splitters and widgets dedicated to images since
        # they make the widget more "laggy" when resized.
        if type == PlotType.CURVE or (
            type == PlotType.MANUAL and no_image_analysis_widgets is True
        ):
            self.setOrientation(QC.Qt.Orientation.Horizontal)
            self.addWidget(self.plot)
            self.addWidget(self.itemlist)

            self.xcsw = None
            self.ycsw = None
            self.contrast = None
        else:
            self.setOrientation(QC.Qt.Orientation.Vertical)
            self.sub_splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal, self)

            self.ycsw = YCrossSection(
                self, position=ysection_pos, xsection_pos=xsection_pos
            )
            self.ycsw.setVisible(show_ysection)

            self.xcsw = XCrossSection(self)
            self.xcsw.setVisible(show_xsection)

            self.xcsw.SIG_VISIBILITY_CHANGED.connect(self.xcsw_is_visible)

            self.xcsw_splitter = QW.QSplitter(QC.Qt.Orientation.Vertical, self)
            if xsection_pos == "top":
                self.xcsw_splitter.addWidget(self.xcsw)
                self.xcsw_splitter.addWidget(self.plot)
            else:
                self.xcsw_splitter.addWidget(self.plot)
                self.xcsw_splitter.addWidget(self.xcsw)
            self.xcsw_splitter.splitterMoved.connect(
                lambda pos, index: self.adjust_ycsw_height()
            )

            self.ycsw_splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal, self)
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

            self.contrast = ContrastAdjustment(self)
            self.contrast.setVisible(show_contrast)
            self.addWidget(self.contrast)

            configure_plot_splitter(self.sub_splitter)

        configure_plot_splitter(self)

    def get_plot(self) -> BasePlot:
        """Return the plot object

        Returns:
            BasePlot: The plot object
        """
        return self.plot

    def adjust_ycsw_height(self, height: int | None = None) -> None:
        """

        :param height:
        """
        if height is None:
            height = self.xcsw.height() - self.ycsw.toolbar.height()
        self.ycsw.adjust_height(height)

    def xcsw_is_visible(self, state: bool) -> None:
        """

        :param state:
        """
        if state:
            self.adjust_ycsw_height()
        else:
            self.adjust_ycsw_height(0)


class PlotWidget(BasePlotWidget):
    """
    Construct a PlotWidget object: plotting widget with integrated
    plot manager

    Args:
        parent (QWidget): parent widget
        toolbar (bool): show/hide toolbar
        options (dict): options sent to the :py:class:`.BasePlot` object (dictionary)
        panels (list, tuple): additionnal panels
        auto_tools (bool): automatically register tools
    """

    def __init__(
        self,
        parent: QWidget,
        toolbar: bool = False,
        options: dict = {},
        panels: tuple[PanelWidget] | None = None,
        auto_tools: bool = True,
    ) -> None:
        super().__init__(parent, **options)
        self.manager = PlotManager(self)
        self.configure_manager(panels, toolbar)
        if auto_tools:
            self.register_tools()

    def configure_manager(
        self,
        panels: tuple[PanelWidget] | None = None,
        toolbar: bool = True,
    ) -> None:
        """Configure the plot manager

        Args:
            panels (tuple[PanelWidget] | None): additionnal panels (list, tuple). Defaults to None.
            toolbar (bool | None): [description]. Defaults to True.
        """
        self.manager.add_plot(self.plot)
        self.manager.add_panel(self.itemlist)
        if self.xcsw is not None:
            self.manager.add_panel(self.xcsw)
        if self.ycsw is not None:
            self.manager.add_panel(self.ycsw)
        if self.contrast is not None:
            self.manager.add_panel(self.contrast)
        if panels is not None:
            for panel in panels:
                self.manager.add_panel(panel)
        self.toolbar = QW.QToolBar(_("Tools"))
        if toolbar:
            self.manager.add_toolbar(self.toolbar, "default")
        else:
            self.toolbar.hide()

    def register_tools(self) -> None:
        """Register the plotting tools according to the plot type"""
        if self.plot.type == PlotType.CURVE:
            self.manager.register_all_curve_tools()
        elif self.plot.type == PlotType.IMAGE:
            self.manager.register_all_image_tools()
        elif self.plot.type == PlotType.AUTO:
            self.manager.register_all_tools()


def set_widget_title_icon(widget: QWidget, wintitle: str, icon: QG.QIcon) -> None:
    """Setups the widget title and icon

    Args:
        wintitle (str): The window title
        icon (QIcon): The window icon
    """
    win32_fix_title_bar_background(widget)
    widget.setWindowTitle(wintitle)
    if isinstance(icon, str):
        icon = get_icon(icon)
    if icon is not None:
        widget.setWindowIcon(icon)
    widget.setMinimumSize(320, 240)
    widget.resize(640, 480)


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
        layout (QGridLayout): The layout
        widget (QWidget): The widget to add
        row (int): The row index
        column (int): The column index
        rowspan (int | None): The row span
        columnspan (int | None): The column span

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
    def setup_widget(
        self,
        toolbar: bool = False,
        options: dict | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = False,
    ) -> None:
        """Setup the widget

        Args:
            toolbar (bool): If True, the plot toolbar is displayed
            options (dict): Plot options
            panels (tuple[PanelWidget]): The panels to add to the plot
            auto_tools (bool): If True, the plot tools are automatically registered.
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
            widget (QWidget): The widget to add
            row (int | None): The row index
            column (int | None): The column index
            rowspan (int | None): The row span
            columnspan (int | None): The column span
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


class PlotDialogMeta(type(QW.QDialog), abc.ABCMeta):
    """Mixed metaclass to avoid conflicts"""


class PlotDialog(QW.QDialog, AbstractPlotDialogWindow, metaclass=PlotDialogMeta):
    """
    Construct a PlotDialog object: plotting dialog box with integrated
    plot manager

    Args:
        wintitle (str): The window title
        icon (QIcon): The window icon
        edit (bool): If True, the plot is editable
        toolbar (bool): If True, the plot toolbar is displayed
        options (dict): Plot options
        parent (QWidget): The parent widget
        panels (tuple[PanelWidget]): The panels to add to the plot
        auto_tools (bool): If True, the plot tools are automatically registered.
            If False, the user must register the tools manually.
    """

    def __init__(
        self,
        wintitle: str = "plotpy plot",
        icon: str = "plotpy.svg",
        edit: bool = False,
        toolbar: bool = False,
        options: dict = {},
        parent: QWidget | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = True,
    ) -> None:
        super().__init__(parent)
        set_widget_title_icon(self, wintitle, icon)
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

    def setup_widget(
        self,
        toolbar: bool = False,
        options: dict | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = False,
    ) -> None:
        """Setup the widget

        Args:
            toolbar (bool): If True, the plot toolbar is displayed
            options (dict): Plot options
            panels (tuple[PanelWidget]): The panels to add to the plot
            auto_tools (bool): If True, the plot tools are automatically registered.
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
            widget (QWidget): The widget to add
            row (int | None): The row index
            column (int | None): The column index
            rowspan (int | None): The row span
            columnspan (int | None): The column span
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


class PlotWindowMeta(type(QW.QMainWindow), abc.ABCMeta):
    """Mixed metaclass to avoid conflicts"""


class PlotWindow(QW.QMainWindow, AbstractPlotDialogWindow, metaclass=PlotWindowMeta):
    """
    Construct a PlotWindow object: plotting window with integrated plot
    manager

    Args:
        wintitle (str): The window title
        icon (QIcon): The window icon
        toolbar (bool): If True, the plot toolbar is displayed
        options (dict): Plot options
        parent (QWidget): The parent widget
        panels (tuple[PanelWidget]): The panels to add to the plot
        auto_tools (bool): If True, the plot tools are automatically registered.
            If False, the user must register the tools manually.
    """

    def __init__(
        self,
        wintitle: str = "plotpy plot",
        icon: str = "plotpy.svg",
        toolbar: bool = False,
        options: dict = {},
        parent: QWidget | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = True,
    ) -> None:
        super().__init__(parent)
        set_widget_title_icon(self, wintitle, icon)
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

    def setup_widget(
        self,
        toolbar: bool = False,
        options: dict | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = False,
    ) -> None:
        """Setup the widget

        Args:
            toolbar (bool): If True, the plot toolbar is displayed
            options (dict): Plot options
            panels (tuple[PanelWidget]): The panels to add to the plot
            auto_tools (bool): If True, the plot tools are automatically registered.
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
            widget (QWidget): The widget to add
            row (int | None): The row index
            column (int | None): The column index
            rowspan (int | None): The row span
            columnspan (int | None): The column span
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

    def closeEvent(self, event) -> None:
        """Reimplement the close event to close all panels

        Args:
            event (QCloseEvent): The close event
        """
        # Closing panels (necessary if at least one of these panels has no
        # parent widget: otherwise, this panel will stay open after the main
        # window has been closed which is not the expected behavior)
        for panel in self.manager.panels:
            self.manager.get_panel(panel).close()
        QW.QMainWindow.closeEvent(self, event)


class SubplotWidget(QW.QSplitter):
    """Construct a Widget that helps managing several plots
    together handled by the same manager

    Since the plots must be added to the manager before the panels
    the add_itemlist method can be called after having declared
    all the subplots

    Args:
        manager (PlotManager): The plot manager
        parent (QWidget): The parent widget
        kwargs: Extra arguments passed to the QSplitter constructor
    """

    def __init__(
        self, manager: PlotManager, parent: QWidget | None = None, **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self.setOrientation(QC.Qt.Orientation.Horizontal)
        self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)
        self.manager = manager
        self.plots = []
        self.itemlist = None
        main = QWidget()
        self.plotlayout = QW.QGridLayout()
        main.setLayout(self.plotlayout)
        self.addWidget(main)

    def add_itemlist(self, show_itemlist: bool = False) -> None:
        """Add the itemlist to the widget

        Args:
            show_itemlist (bool): If True, the itemlist is visible
        """
        self.itemlist = PlotItemList(self)
        self.itemlist.setVisible(show_itemlist)
        self.addWidget(self.itemlist)
        configure_plot_splitter(self)
        self.manager.add_panel(self.itemlist)

    def add_subplot(
        self, plot: BasePlot, i: int = 0, j: int = 0, plot_id: str | None = None
    ) -> None:
        """Add a plot to the grid of plots

        Args:
            plot (BasePlot): The plot to add
            i (int): The row index
            j (int): The column index
            plot_id (str): The plot id
        """
        self.plotlayout.addWidget(plot, i, j)
        self.plots.append(plot)
        if plot_id is None:
            plot_id = id(plot)
        self.manager.add_plot(plot, plot_id)


# TODO: Migrate DataLab's SyncPlotWindow right here
