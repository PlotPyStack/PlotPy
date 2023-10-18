# -*- coding: utf-8 -*-

from guidata.configtools import get_icon

from plotpy.config import _
from plotpy.interfaces import IImageItemType
from plotpy.items import AnnotatedObliqueRectangle, AnnotatedPoint, AnnotatedRectangle
from plotpy.panels.base import ID_OCS, ID_XCS, ID_YCS
from plotpy.tools.base import PanelTool
from plotpy.tools.image import update_image_tool_status
from plotpy.tools.shape import RectangularShapeTool


class CrossSectionTool(RectangularShapeTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Cross section")
    ICON = "csection.png"
    SHAPE_STYLE_KEY = "shape/cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_XCS, ID_YCS)

    def update_status(self, plot):
        if update_image_tool_status(self, plot):
            item = plot.get_selected_items(item_type=IImageItemType)
            self.action.setEnabled(len(item) > 0)

    def create_shape(self):
        """

        :return:
        """
        return AnnotatedPoint(0, 0), 0, 0

    def setup_shape(self, shape):
        """

        :param shape:
        """
        self.setup_shape_appearance(shape)
        super().setup_shape(shape)
        self.register_shape(shape, final=False)

    def setup_shape_appearance(self, shape):
        """

        :param shape:
        """
        self.set_shape_style(shape)
        param = shape.annotationparam
        param.title = self.SHAPE_TITLE
        #        param.show_computations = False
        param.update_annotation(shape)

    def register_shape(self, shape, final=False):
        """

        :param shape:
        :param final:
        """
        plot = shape.plot()
        if plot is not None:
            plot.unselect_all()
            plot.set_active_item(shape)
        for panel_id in self.PANEL_IDS:
            panel = self.manager.get_panel(panel_id)
            if panel is not None:
                panel.register_shape(shape, final=final)

    def activate(self):
        """Activate tool"""
        super().activate()
        for panel_id in self.PANEL_IDS:
            panel = self.manager.get_panel(panel_id)
            panel.setVisible(True)
            shape = self.get_last_final_shape()
            if shape is not None:
                panel.update_plot(shape)

    def handle_final_shape(self, shape):
        """

        :param shape:
        """
        super().handle_final_shape(shape)
        self.register_shape(shape, final=True)


class AverageCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Average cross section")
    ICON = "csection_a.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE

    def create_shape(self):
        """

        :return:
        """
        return AnnotatedRectangle(0, 0, 1, 1), 0, 2


class ObliqueCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Oblique averaged cross section")
    ICON = "csection_oblique.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_OCS,)

    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedObliqueRectangle(0, 0, 1, 0, 1, 1, 0, 1)
        self.set_shape_style(annotation)
        annotation.setIcon(get_icon(self.ICON))
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
