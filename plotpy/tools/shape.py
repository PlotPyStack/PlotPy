# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Shape tools"""

from __future__ import annotations

import warnings
from typing import Callable

import numpy as np
from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.constants import SHAPE_Z_OFFSET
from plotpy.events import (
    MultilineSelectionHandler,
    PointSelectionHandler,
    StatefulEventFilter,
    setup_standard_tool_filter,
)
from plotpy.items import (
    EllipseShape,
    ObliqueRectangleShape,
    PointShape,
    PolygonShape,
    SegmentShape,
)
from plotpy.plot import BasePlot
from plotpy.tools.base import DefaultToolbarID, InteractiveTool, RectangularActionTool


class MultiLineTool(InteractiveTool):
    """
    A tool for drawing multi-line shapes (polylines) on a plot.

    This tool allows users to create polyline shapes by clicking on the plot
    to add points. The shape can be finalized using the Enter or Space key.

    Args:
        manager: The plot manager.
        handle_final_shape_cb: Callback function to handle the final shape.
        shape_style: Tuple containing the style section and key for the shape.
        toolbar_id: ID of the toolbar to which this tool belongs.
        title: Title of the tool.
        icon: Icon for the tool.
        tip: Tooltip for the tool.
        switch_to_default_tool: Whether to switch to the default tool after use.
    """

    TITLE: str = _("Polyline")
    ICON: str = "polyline.png"
    CLOSED: bool = False
    CURSOR: QC.Qt.CursorShape = QC.Qt.CursorShape.PointingHandCursor

    def __init__(
        self,
        manager,
        setup_shape_cb: Callable | None = None,
        handle_final_shape_cb: Callable | None = None,
        shape_style: tuple[str, str] | None = None,
        toolbar_id: str = DefaultToolbarID,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
        switch_to_default_tool: bool | None = None,
    ):
        super().__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        self.handler: MultilineSelectionHandler | None = None
        self.switch_to_default_tool = switch_to_default_tool
        self.setup_shape_cb = setup_shape_cb
        self.handle_final_shape_cb = handle_final_shape_cb
        if shape_style is not None:
            self.shape_style_sect, self.shape_style_key = shape_style
        else:
            self.shape_style_sect = "plot"
            self.shape_style_key = "shape/drag"

    def set_shape_style(self, shape: PolygonShape) -> None:
        """Set shape style

        Args:
            shape: shape
        """
        shape.set_style(self.shape_style_sect, self.shape_style_key)

    def create_shape(self) -> PolygonShape:
        """Create shape"""
        shape = PolygonShape(closed=False)
        self.set_shape_style(shape)
        return shape

    def setup_shape(self, shape: PolygonShape) -> None:
        """Setup shape"""
        shape.setTitle(self.TITLE)
        if self.setup_shape_cb is not None:
            self.setup_shape_cb(shape)

    def get_shape(self) -> PolygonShape:
        """
        Get shape

        Returns:
            shape
        """
        shape = self.create_shape()
        self.setup_shape(shape)
        return shape

    def setup_filter(self, baseplot: BasePlot) -> StatefulEventFilter:
        """
        Set up the event filter for the tool.

        Args:
            baseplot: The base plot object.

        Returns:
            The configured filter.
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        self.handler = MultilineSelectionHandler(
            filter, QC.Qt.LeftButton, start_state=start_state, closed=self.CLOSED
        )
        self.handler.SIG_END_POLYLINE.connect(self.end_polyline)
        shape = self.get_shape()
        self.handler.set_shape(shape, self.setup_shape)
        return setup_standard_tool_filter(filter, start_state)

    def handle_final_shape(self, shape) -> None:
        """
        Handle the final shape after it's been created.

        Args:
            shape: The final shape object.
        """
        if self.handle_final_shape_cb is not None:
            self.handle_final_shape_cb(shape)

    def end_polyline(self, filter: StatefulEventFilter, points: np.ndarray) -> None:
        """
        End the polyline and reset the tool.

        Args:
            filter: The plot filter.
            points: The points of the polyline.
        """
        plot = filter.plot
        shape = self.get_shape()
        shape.set_points(points)
        shape.set_closed(self.CLOSED)
        plot.add_item_with_z_offset(shape, SHAPE_Z_OFFSET)
        self.handle_final_shape(shape)
        self.SIG_TOOL_JOB_FINISHED.emit()
        if self.switch_to_default_tool:
            plot.set_active_item(shape)


class PolygonTool(MultiLineTool):
    """
    A tool for drawing free-form shapes on a plot.

    This tool extends the MultiLineTool to create closed shapes when
    there are more than 2 points.
    """

    TITLE: str = _("Polygon")
    ICON: str = "polygon.png"
    CLOSED: bool = True


# The old name of the class was FreeFormTool, but the class is now PolygonTool
# The old name is kept for backward compatibility, but a warning is issued when
# the class is instantiated using the old name.
class FreeFormTool(PolygonTool):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "FreeFormTool is deprecated, use PolygonTool instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class RectangularShapeTool(RectangularActionTool):
    """
    Base class for tools that create rectangular shapes.

    Args:
        manager: The plot manager.
        setup_shape_cb: Callback function to set up the shape.
        handle_final_shape_cb: Callback function to handle the final shape.
        shape_style: Tuple containing the style section and key for the shape.
        toolbar_id: ID of the toolbar to which this tool belongs.
        title: Title of the tool.
        icon: Icon for the tool.
        tip: Tooltip for the tool.
        switch_to_default_tool: Whether to switch to the default tool after use.
    """

    TITLE: str | None = None
    ICON: str | None = None

    def __init__(
        self,
        manager,
        setup_shape_cb: Callable | None = None,
        handle_final_shape_cb: Callable | None = None,
        shape_style: tuple[str, str] | None = None,
        toolbar_id: str = DefaultToolbarID,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
        switch_to_default_tool: bool | None = None,
    ):
        super().__init__(
            manager,
            self.add_shape_to_plot,
            shape_style,
            toolbar_id=toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        self.setup_shape_cb = setup_shape_cb
        self.handle_final_shape_cb = handle_final_shape_cb

    def add_shape_to_plot(self, plot, p0: QC.QPointF, p1: QC.QPointF):
        """
        Add the final shape to the plot.

        Args:
            plot: The plot object.
            p0: The first point of the shape.
            p1: The second point of the shape.
        """
        shape = self.get_final_shape(plot, p0, p1)
        self.handle_final_shape(shape)
        plot.replot()

    def setup_shape(self, shape) -> None:
        """
        Set up the shape properties.

        Args:
            shape: The shape object to set up.
        """
        shape.setTitle(self.TITLE)
        if self.setup_shape_cb is not None:
            self.setup_shape_cb(shape)

    def handle_final_shape(self, shape) -> None:
        """
        Handle the final shape after it's been created.

        Args:
            shape: The final shape object.
        """
        if self.handle_final_shape_cb is not None:
            self.handle_final_shape_cb(shape)


class RectangleTool(RectangularShapeTool):
    """Tool for creating rectangle shapes."""

    TITLE: str = _("Rectangle")
    ICON: str = "rectangle.png"


class ObliqueRectangleTool(RectangularShapeTool):
    """Tool for creating oblique rectangle shapes."""

    TITLE: str = _("Oblique rectangle")
    ICON: str = "oblique_rectangle.png"
    AVOID_NULL_SHAPE: bool = True

    def create_shape(self):
        """
        Create an oblique rectangle shape.

        Returns:
            A tuple containing the shape object and its handle indices.
        """
        shape = ObliqueRectangleShape(1, 1, 2, 1, 2, 2, 1, 2)
        self.set_shape_style(shape)
        return shape, 0, 2


class PointTool(RectangularShapeTool):
    """Tool for creating point shapes."""

    TITLE: str = _("Point")
    ICON: str = "point_shape.png"
    SHAPE_STYLE_KEY: str = "shape/point"

    def create_shape(self):
        """
        Create a point shape.

        Returns:
            A tuple containing the shape object and its handle indices.
        """
        shape = PointShape(0, 0)
        self.set_shape_style(shape)
        return shape, 0, 0

    def get_selection_handler(self, filter, start_state):
        """
        Get the selection handler for the point tool.

        Args:
            filter: The plot filter.
            start_state: The initial state.

        Returns:
            A PointSelectionHandler object.
        """
        return PointSelectionHandler(filter, QC.Qt.LeftButton, start_state=start_state)


class SegmentTool(RectangularShapeTool):
    """Tool for creating segment shapes."""

    TITLE: str = _("Segment")
    ICON: str = "segment.png"
    SHAPE_STYLE_KEY: str = "shape/segment"

    def create_shape(self):
        """
        Create a segment shape.

        Returns:
            A tuple containing the shape object and its handle indices.
        """
        shape = SegmentShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 1


class CircleTool(RectangularShapeTool):
    """Tool for creating circle shapes."""

    TITLE: str = _("Circle")
    ICON: str = "circle.png"

    def create_shape(self):
        """
        Create a circle shape.

        Returns:
            A tuple containing the shape object and its handle indices.
        """
        shape = EllipseShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 1


class EllipseTool(RectangularShapeTool):
    """Tool for creating ellipse shapes."""

    TITLE: str = _("Ellipse")
    ICON: str = "ellipse_shape.png"

    def create_shape(self):
        """
        Create an ellipse shape.

        Returns:
            A tuple containing the shape object and its handle indices.
        """
        shape = EllipseShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 1

    def handle_final_shape(self, shape) -> None:
        """
        Handle the final ellipse shape after it's been created.

        Args:
            shape: The final ellipse shape object.
        """
        shape.switch_to_ellipse()
        super().handle_final_shape(shape)
