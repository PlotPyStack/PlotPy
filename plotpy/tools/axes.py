# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Axes tools"""

from __future__ import annotations

from guidata.configtools import get_icon
from guidata.qthelpers import add_actions
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.items import Axes
from plotpy.tools.base import CommandTool
from plotpy.tools.shape import RectangularShapeTool


class AxisScaleTool(CommandTool):
    """
    A tool for changing the scale of plot axes.

    This tool provides options to switch between linear and logarithmic scales
    for both x and y axes.
    """

    def __init__(self, manager):
        """
        Initialize the AxisScaleTool.

        Args:
            manager: The plot manager.
        """
        super().__init__(
            manager, _("Scale"), icon=get_icon("log_log.png"), tip=None, toolbar_id=None
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager) -> QW.QMenu:
        """
        Create and return menu for the tool's action.

        Args:
            manager: The plot manager.

        Returns:
            A QMenu object containing scale options.
        """
        menu = QW.QMenu()
        group = QW.QActionGroup(manager.get_main())
        lin_lin = manager.create_action(
            "Lin Lin",
            icon=get_icon("lin_lin.png"),
            toggled=lambda state, x="lin", y="lin": self.set_scale(state, x, y),
        )
        lin_log = manager.create_action(
            "Lin Log",
            icon=get_icon("lin_log.png"),
            toggled=lambda state, x="lin", y="log": self.set_scale(state, x, y),
        )
        log_lin = manager.create_action(
            "Log Lin",
            icon=get_icon("log_lin.png"),
            toggled=lambda state, x="log", y="lin": self.set_scale(state, x, y),
        )
        log_log = manager.create_action(
            "Log Log",
            icon=get_icon("log_log.png"),
            toggled=lambda state, x="log", y="log": self.set_scale(state, x, y),
        )
        self.scale_menu = {
            ("lin", "lin"): lin_lin,
            ("lin", "log"): lin_log,
            ("log", "lin"): log_lin,
            ("log", "log"): log_log,
        }
        for obj in (group, menu):
            add_actions(obj, (lin_lin, lin_log, log_lin, log_log))
        return menu

    def update_status(self, plot) -> None:
        """
        Update the status of scale actions based on the current plot scales.

        Args:
            plot: The current plot object.
        """
        item = plot.get_active_item()
        active_scale = ("lin", "lin")
        if item is not None:
            xscale = plot.get_axis_scale(item.xAxis())
            yscale = plot.get_axis_scale(item.yAxis())
            active_scale = xscale, yscale
        for scale_type, scale_action in list(self.scale_menu.items()):
            if item is None:
                scale_action.setEnabled(False)
            else:
                scale_action.setEnabled(True)
                if active_scale == scale_type:
                    scale_action.setChecked(True)
                else:
                    scale_action.setChecked(False)

    def set_scale(self, checked: bool, xscale: str, yscale: str) -> None:
        """
        Set the scale of the active plot.

        Args:
            checked: Whether the action is checked.
            xscale: The scale for the x-axis ('lin' or 'log').
            yscale: The scale for the y-axis ('lin' or 'log').
        """
        if not checked:
            return
        plot = self.get_active_plot()
        if plot is not None:
            cur_xscale, cur_yscale = plot.get_scales()
            if cur_xscale != xscale or cur_yscale != yscale:
                plot.set_scales(xscale, yscale)


class PlaceAxesTool(RectangularShapeTool):
    """
    A tool for placing axes on the plot.

    This tool allows users to draw a rectangular shape to define
    the position and size of the axes on the plot.
    """

    TITLE: str = _("Axes")
    ICON: str = "gtaxes.png"
    SHAPE_STYLE_KEY: str = "shape/axes"

    def create_shape(self) -> tuple[Axes, int, int]:
        """
        Create an Axes shape.

        Returns:
            A tuple containing the Axes object and its handle indices.
        """
        shape = Axes((0, 1), (1, 1), (0, 0))
        self.set_shape_style(shape)
        return shape, 0, 2
