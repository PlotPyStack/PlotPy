# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.configtools import get_icon

from plotpy.config import _
from plotpy.constants import ID_LCS, ID_OCS, ID_XCS, ID_YCS
from plotpy.interfaces import IImageItemType
from plotpy.items import (
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
)
from plotpy.styles import AnnotationParam
from plotpy.tools.base import PanelTool
from plotpy.tools.image import update_image_tool_status
from plotpy.tools.shape import RectangularShapeTool

if TYPE_CHECKING:
    from plotpy.plot import BasePlot


class CrossSectionTool(RectangularShapeTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Cross section")
    ICON = "csection.png"
    SHAPE_STYLE_KEY = "shape/cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_XCS, ID_YCS)

    def update_status(self, plot: BasePlot) -> None:
        """Update status of the tool"""
        if update_image_tool_status(self, plot):
            item = plot.get_selected_items(item_type=IImageItemType)
            self.action.setEnabled(len(item) > 0)

    def create_shape(self) -> AnnotatedPoint:
        """Create shape for the tool"""
        return AnnotatedPoint(0, 0), 0, 0

    def setup_shape(self, shape: AnnotatedPoint) -> None:
        """Set up shape for the tool"""
        self.setup_shape_appearance(shape)
        super().setup_shape(shape)
        self.register_shape(shape)

    def setup_shape_appearance(self, shape: AnnotatedPoint) -> None:
        """Set up shape appearance"""
        self.set_shape_style(shape)
        param = shape.annotationparam
        param.title = self.SHAPE_TITLE
        #        param.show_computations = False
        param.update_item(shape)

    def register_shape(self, shape: AnnotatedPoint) -> None:
        """Register shape"""
        plot = shape.plot()
        if plot is not None:
            plot.unselect_all()
            plot.set_active_item(shape)
        for panel_id in self.PANEL_IDS:
            panel = self.manager.get_panel(panel_id)
            if panel is not None:
                panel.register_shape(shape)

    def activate(self) -> None:
        """Activate tool"""
        super().activate()
        for panel_id in self.PANEL_IDS:
            panel = self.manager.get_panel(panel_id)
            panel.setVisible(True)
            shape = self.get_last_final_shape()
            if shape is not None:
                panel.update_plot(shape)

    def handle_final_shape(self, shape: AnnotatedPoint) -> None:
        """Handle final shape"""
        super().handle_final_shape(shape)
        self.register_shape(shape)


class AverageCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Average cross section")
    ICON = "csection_a.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE

    def create_shape(self) -> AnnotatedRectangle:
        """Create shape for the tool"""
        return AnnotatedRectangle(0, 0, 1, 1), 0, 2


class LineCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Line cross section")
    ICON = "csection_line.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_LCS,)

    def create_shape(self) -> AnnotatedSegment:
        """Create shape for the tool"""
        param = AnnotationParam.create(show_label=False, show_computations=False)
        return AnnotatedSegment(0, 0, 1, 1, param), 0, 1


class ObliqueCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Oblique averaged cross section")
    ICON = "csection_oblique.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_OCS,)

    def create_shape(self) -> AnnotatedObliqueRectangle:
        """Create shape for the tool"""
        annotation = AnnotatedObliqueRectangle(0, 0, 1, 0, 1, 1, 0, 1)
        self.set_shape_style(annotation)
        annotation.set_icon_name(self.ICON)
        return annotation, 0, 2


class XCSPanelTool(PanelTool):
    panel_name = _("X-axis cross section")
    panel_id = ID_XCS


class YCSPanelTool(PanelTool):
    panel_name = _("Y-axis cross section")
    panel_id = ID_YCS


class OCSPanelTool(PanelTool):
    panel_name = _("Oblique averaged cross section")
    panel_id = ID_OCS


class LCSPanelTool(PanelTool):
    panel_name = _("Line cross section")
    panel_id = ID_LCS
