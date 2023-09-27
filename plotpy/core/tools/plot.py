# -*- coding: utf-8 -*-
from guidata.configtools import get_icon
from guidata.qthelpers import add_actions, add_separator
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.core.constants import PARAMETERS_TITLE_ICON
from plotpy.core.events import ZoomRectHandler, setup_standard_tool_filter
from plotpy.core.interfaces.common import IImageItemType, IShapeItemType
from plotpy.core.items import RectangleShape, get_items_in_rectangle
from plotpy.core.tools.base import (
    CommandTool,
    DefaultToolbarID,
    GuiTool,
    InteractiveTool,
    RectangularActionTool,
)


class DoAutoscaleTool(CommandTool):
    """
    A tool to perfrom autoscale for associated plot
    """

    def __init__(
        self,
        manager,
        title=_("AutoScale"),
        icon="autoscale.png",
        tip=None,
        toolbar_id=DefaultToolbarID,
    ):
        super(DoAutoscaleTool, self).__init__(
            manager, title=title, icon=icon, tip=tip, toolbar_id=toolbar_id
        )

    def setup_context_menu(self, menu, plot):
        """re-implement"""
        pass

    def activate_command(self, plot, checked):
        """Activate tool"""
        if checked:
            plot.do_autoscale()


class BasePlotMenuTool(CommandTool):
    """
    A tool that gather parameter panels from the BasePlot
    and proposes to edit them and set them back
    """

    def __init__(
        self, manager, key, title=None, icon=None, tip=None, toolbar_id=DefaultToolbarID
    ):
        default_title, default_icon = PARAMETERS_TITLE_ICON[key]
        if title is None:
            title = default_title
        if icon is None:
            icon = default_icon
        super(BasePlotMenuTool, self).__init__(manager, title, icon, tip, toolbar_id)
        # Warning: icon (str) --(Base class constructor)--> self.icon (QIcon)
        self.key = key

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.edit_plot_parameters(self.key)

    def update_status(self, plot):
        """

        :param plot:
        """
        status = plot.get_plot_parameters_status(self.key)
        self.action.setEnabled(status)


class DisplayCoordsTool(CommandTool):
    """ """

    def __init__(self, manager):
        super(DisplayCoordsTool, self).__init__(
            manager,
            _("Markers"),
            icon=get_icon("on_curve.png"),
            tip=None,
            toolbar_id=None,
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
        menu = QW.QMenu()
        self.canvas_act = manager.create_action(
            _("Free"), toggled=self.activate_canvas_pointer
        )
        self.curve_act = manager.create_action(
            _("Bound to active item"), toggled=self.activate_curve_pointer
        )
        add_actions(menu, (self.canvas_act, self.curve_act))
        return menu

    def activate_canvas_pointer(self, enable):
        """

        :param enable:
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_pointer("canvas" if enable else None)

    def activate_curve_pointer(self, enable):
        """

        :param enable:
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_pointer("curve" if enable else None)

    def update_status(self, plot):
        """

        :param plot:
        """
        self.canvas_act.setChecked(plot.canvas_pointer)
        self.curve_act.setChecked(plot.curve_pointer)


class RectZoomTool(InteractiveTool):
    TITLE = _("Rectangle zoom")
    ICON = "magnifier.png"

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        handler = ZoomRectHandler(
            filter, QC.Qt.MouseButton.LeftButton, start_state=start_state
        )
        shape, h0, h1 = self.get_shape()
        handler.set_shape(shape, h0, h1)
        return setup_standard_tool_filter(filter, start_state)

    def get_shape(self):
        """

        :return:
        """
        shape = RectangleShape(0, 0, 1, 1)
        shape.set_style("plot", "shape/rectzoom")
        return shape, 0, 2


class DummySeparatorTool(GuiTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(DummySeparatorTool, self).__init__(manager, toolbar_id)

    def setup_toolbar(self, toolbar):
        """Setup tool's toolbar"""
        add_separator(toolbar)

    def setup_context_menu(self, menu, plot):
        """

        :param menu:
        :param plot:
        """
        add_separator(menu)


class RectangularSelectionTool(RectangularActionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Rectangular selection tool")
    ICON = "rectangular_select.png"

    def __init__(self, manager, intersect=True, toolbar_id=DefaultToolbarID):
        super(RectangularSelectionTool, self).__init__(
            manager, self.select_items, toolbar_id=toolbar_id, fix_orientation=True
        )
        self.intersect = intersect

    def select_items(self, plot, p0, p1):
        items_to_select = []
        # select items that implement IShapeItemType (annotation shapes, ...)
        items = get_items_in_rectangle(
            plot,
            p0,
            p1,
            item_type=IShapeItemType,
            intersect=self.intersect,
        )
        for item in items:
            if item.isVisible():
                items_to_select.append(item)
        # select items that implement IExportROIImageItemType (TrImageItem, ...)
        items = get_items_in_rectangle(
            plot,
            p0,
            p1,
            item_type=IImageItemType,
            intersect=self.intersect,
        )
        for item in items:
            if item.isVisible():
                items_to_select.append(item)
        plot.select_some_items(items_to_select)
