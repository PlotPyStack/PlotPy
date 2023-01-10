# -*- coding: utf-8
from guidata.configtools import get_icon
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.widgets.itemlist import PlotItemList
from plotpy.widgets.plot.base import BasePlot, PlotType
from plotpy.widgets.plot.manager import PlotManager


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


class BasePlotWidget(QW.QSplitter):
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

        # for curves only plots, or MANUAL plots with the no_image_analysis_widgets option,
        # don't add splitters and widgets dedicated to images since
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

            from plotpy.widgets.plot.cross_section.cswidget import YCrossSection

            self.ycsw = YCrossSection(
                self, position=ysection_pos, xsection_pos=xsection_pos
            )
            self.ycsw.setVisible(show_ysection)

            from plotpy.widgets.plot.cross_section.cswidget import XCrossSection

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
            from plotpy.widgets.plot.histogram import ContrastAdjustment

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
            QW.QApplication.processEvents()

    def xcsw_is_visible(self, state):
        """

        :param state:
        """
        if state:
            QW.QApplication.processEvents()
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

        self.plot_layout = QW.QGridLayout()

        if options is None:
            options = {}
        self.plot_widget = None
        self.create_plot(options)

        if panels is not None:
            for panel in panels:
                self.add_panel(panel)

        self.toolbar = QW.QToolBar(_("Tools"))
        if not toolbar:
            self.toolbar.hide()

        # Configuring widget layout
        self.setup_widget_properties(wintitle=wintitle, icon=icon)
        self.setup_widget_layout()

        # Configuring plot manager
        self.setup_plot_manager(auto_tools)

    def setup_widget_layout(self):
        """ """
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


class PlotDialog(QW.QDialog, PlotWidgetMixin):
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
        self.setWindowFlags(QC.Qt.WindowType.Window)

    def setup_widget_layout(self):
        """ """
        vlayout = QW.QVBoxLayout(self)
        vlayout.addWidget(self.toolbar)
        vlayout.addLayout(self.plot_layout)
        self.setLayout(vlayout)
        if self.edit:
            self.button_layout = QW.QHBoxLayout()
            self.install_button_layout()
            vlayout.addLayout(self.button_layout)

    def install_button_layout(self):
        """
        Install standard buttons (OK, Cancel) in dialog button box layout
        (:py:attr:`.plot.PlotDialog.button_layout`)

        This method may be overriden to customize the button box
        """
        bbox = QW.QDialogButtonBox(QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.button_layout.addWidget(bbox)
        self.button_box = bbox


class SubplotWidget(QW.QSplitter):
    """Construct a Widget that helps managing several plots
    together handled by the same manager

    Since the plots must be added to the manager before the panels
    the add_itemlist method can be called after having declared
    all the subplots
    """

    def __init__(self, manager, parent=None, **kwargs):
        super(SubplotWidget, self).__init__(parent, **kwargs)
        self.setOrientation(QC.Qt.Orientation.Horizontal)
        self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)
        self.manager = manager
        self.plots = []
        self.itemlist = None
        main = QW.QWidget()
        self.plotlayout = QW.QGridLayout()
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


class PlotWindow(QW.QMainWindow, PlotWidgetMixin):
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
        """ """
        self.addToolBar(self.toolbar)
        widget = QW.QWidget()
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
        QW.QMainWindow.closeEvent(self, event)


class PlotWidget(QW.QWidget, PlotWidgetMixin):
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
        """ """
        vlayout = QW.QVBoxLayout(self)
        vlayout.addLayout(self.plot_layout)
        self.setLayout(vlayout)

    def setup_plot_manager(self, auto_tools):
        """

        :param auto_tools:
        """
        # don't do anything here for PlotWidget. The toolbar and tools registration
        # are done manually for this class, see simple_window.py example.
        pass
