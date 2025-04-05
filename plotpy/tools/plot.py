# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Plot tools"""

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.configtools import get_icon
from guidata.qthelpers import add_actions, add_separator
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.constants import PARAMETERS_TITLE_ICON
from plotpy.events import ZoomRectHandler, setup_standard_tool_filter
from plotpy.interfaces import IImageItemType, IShapeItemType
from plotpy.items import RectangleShape, get_items_in_rectangle
from plotpy.tools.base import (
    CommandTool,
    DefaultToolbarID,
    GuiTool,
    InteractiveTool,
    RectangularActionTool,
)

if TYPE_CHECKING:
    from plotpy.plot import BasePlot, PlotManager


class DoAutoscaleTool(CommandTool):
    """A tool to perform autoscale for associated plot."""

    def __init__(
        self,
        manager,
        title=_("AutoScale"),
        icon="autoscale.png",
        tip=None,
        toolbar_id=DefaultToolbarID,
    ):
        super().__init__(
            manager, title=title, icon=icon, tip=tip, toolbar_id=toolbar_id
        )

    def setup_context_menu(self, menu: QW.QMenu, plot: BasePlot) -> None:
        """
        Set up the context menu for the tool.

        Args:
            menu: Context menu
            plot: Plot instance
        """
        pass

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
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
        super().__init__(manager, title, icon, tip, toolbar_id)
        # Warning: icon (str) --(Base class constructor)--> self.icon (QIcon)
        self.key = key

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
        plot.edit_plot_parameters(self.key)

    def update_status(self, plot: BasePlot) -> None:
        """
        Update the status of the tool.

        Args:
            plot: Plot instance
        """
        status = plot.get_plot_parameters_status(self.key)
        self.action.setEnabled(status)


class DisplayCoordsTool(CommandTool):
    """Tool for displaying coordinates."""

    def __init__(self, manager):
        super().__init__(
            manager,
            _("Markers"),
            icon=get_icon("on_curve.png"),
            tip=None,
            toolbar_id=None,
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager: PlotManager) -> QW.QMenu:
        """
        Create and return menu for the tool's action.

        Args:
            manager: Plot manager

        Returns:
            Menu for the tool's action
        """
        menu = QW.QMenu()
        self.canvas_act = manager.create_action(
            _("Free"), toggled=self.activate_canvas_pointer
        )
        self.curve_act = manager.create_action(
            _("Bound to active item"), toggled=self.activate_curve_pointer
        )
        add_actions(menu, (self.canvas_act, self.curve_act))
        return menu

    def activate_canvas_pointer(self, enable: bool) -> None:
        """
        Activate canvas pointer.

        Args:
            enable: Whether to enable the canvas pointer
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_pointer("canvas" if enable else None)

    def activate_curve_pointer(self, enable: bool) -> None:
        """
        Activate curve pointer.

        Args:
            enable: Whether to enable the curve pointer
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_pointer("curve" if enable else None)

    def update_status(self, plot: BasePlot) -> None:
        """
        Update the status of the tool.

        Args:
            plot: Plot instance
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
        super().__init__(manager, toolbar_id)

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
    ICON = "select_area.svg"

    def __init__(self, manager, intersect=True, toolbar_id=DefaultToolbarID):
        super().__init__(
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
