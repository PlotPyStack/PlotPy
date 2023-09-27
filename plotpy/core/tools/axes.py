# -*- coding: utf-8 -*-

from guidata.configtools import get_icon
from guidata.qthelpers import add_actions
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.core.items import Axes
from plotpy.core.tools.base import CommandTool
from plotpy.core.tools.shapes import RectangularShapeTool


class AxisScaleTool(CommandTool):
    """ """

    def __init__(self, manager):
        super(AxisScaleTool, self).__init__(
            manager, _("Scale"), icon=get_icon("log_log.png"), tip=None, toolbar_id=None
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
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

    def update_status(self, plot):
        """

        :param plot:
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

    def set_scale(self, checked, xscale, yscale):
        """

        :param checked:
        :param xscale:
        :param yscale:
        :return:
        """
        if not checked:
            return
        plot = self.get_active_plot()
        if plot is not None:
            cur_xscale, cur_yscale = plot.get_scales()
            if cur_xscale != xscale or cur_yscale != yscale:
                plot.set_scales(xscale, yscale)


class PlaceAxesTool(RectangularShapeTool):
    TITLE = _("Axes")
    ICON = "gtaxes.png"
    SHAPE_STYLE_KEY = "shape/axes"

    def create_shape(self):
        """

        :return:
        """
        shape = Axes((0, 1), (1, 1), (0, 0))
        self.set_shape_style(shape)
        return shape, 0, 2
