# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Shape tools"""

from __future__ import annotations

from typing import Callable

from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.constants import SHAPE_Z_OFFSET
from plotpy.events import (
    KeyEventMatch,
    PointSelectionHandler,
    QtDragHandler,
    setup_standard_tool_filter,
)
from plotpy.items import (
    EllipseShape,
    ObliqueRectangleShape,
    PointShape,
    PolygonShape,
    SegmentShape,
)
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
    CURSOR: QC.Qt.CursorShape = QC.Qt.CursorShape.ArrowCursor

    def __init__(
        self,
        manager,
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
        self.handle_final_shape_cb = handle_final_shape_cb
        self.shape: PolygonShape | None = None
        self.current_handle: int | None = None
        self.init_pos: QC.QPointF | None = None
        if shape_style is not None:
            self.shape_style_sect, self.shape_style_key = shape_style
        else:
            self.shape_style_sect = "plot"
            self.shape_style_key = "shape/drag"

    def reset(self) -> None:
        """Reset the tool's state."""
        self.shape = None
        self.current_handle = None

    def create_shape(self, filter, pt: QC.QPointF) -> int:
        """
        Create a new PolygonShape and add it to the plot.

        Args:
            filter: The plot filter.
            pt: The initial point of the shape.

        Returns:
            The handle of the second point added to the shape.
        """
        self.shape = PolygonShape(closed=False)
        filter.plot.add_item_with_z_offset(self.shape, SHAPE_Z_OFFSET)
        self.shape.setVisible(True)
        self.shape.set_style(self.shape_style_sect, self.shape_style_key)
        self.shape.add_local_point(pt)
        return self.shape.add_local_point(pt)

    def setup_filter(self, baseplot):
        """
        Set up the event filter for the tool.

        Args:
            baseplot: The base plot object.

        Returns:
            The configured filter.
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        handler = QtDragHandler(filter, QC.Qt.LeftButton, start_state=start_state)
        filter.add_event(
            start_state,
            KeyEventMatch((QC.Qt.Key_Enter, QC.Qt.Key_Return, QC.Qt.Key_Space)),
            self.validate,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch((QC.Qt.Key_Backspace, QC.Qt.Key_Escape)),
            self.cancel_point,
            start_state,
        )
        handler.SIG_START_TRACKING.connect(self.mouse_press)
        handler.SIG_MOVE.connect(self.move)
        handler.SIG_STOP_NOT_MOVING.connect(self.mouse_release)
        handler.SIG_STOP_MOVING.connect(self.mouse_release)
        return setup_standard_tool_filter(filter, start_state)

    def validate(self, filter, event) -> None:
        """
        Validate the current shape and reset the tool.

        Args:
            filter: The plot filter.
            event: The triggering event.
        """
        super().validate(filter, event)
        if self.handle_final_shape_cb is not None:
            self.handle_final_shape_cb(self.shape)
        self.reset()

    def cancel_point(self, filter, event) -> None:
        """
        Cancel the last point or remove the shape if it has less than 3 points.

        Args:
            filter: The plot filter.
            event: The triggering event.
        """
        if self.shape is None:
            return
        points = self.shape.get_points()
        if points is None:
            return
        elif len(points) <= 2:
            filter.plot.del_item(self.shape)
            self.reset()
        else:
            if self.current_handle:
                newh = self.shape.del_point(self.current_handle)
            else:
                newh = self.shape.del_point(-1)
            self.current_handle = newh
        filter.plot.replot()

    def mouse_press(self, filter, event) -> None:
        """
        Handle mouse press event to create a new shape or add a new point.

        Args:
            filter: The plot filter.
            event: The mouse event.
        """
        if self.shape is None:
            self.init_pos = event.pos()
            self.current_handle = self.create_shape(filter, event.pos())
            filter.plot.replot()
        else:
            self.current_handle = self.shape.add_local_point(event.pos())

    def move(self, filter, event) -> None:
        """
        Handle mouse move event to update the position of the last point.

        Args:
            filter: The plot filter.
            event: The mouse event.
        """
        if self.shape is None or self.current_handle is None:
            return
        self.shape.move_local_point_to(self.current_handle, event.pos())
        filter.plot.replot()

    def mouse_release(self, filter, event) -> None:
        """
        Handle mouse release event to finalize the position of the last point.

        Args:
            filter: The plot filter.
            event: The mouse event.
        """
        if self.current_handle is None:
            return
        if self.init_pos is not None and self.init_pos == event.pos():
            self.shape.del_point(-1)
        else:
            self.shape.move_local_point_to(self.current_handle, event.pos())
        self.init_pos = None
        self.current_handle = None
        filter.plot.replot()


class FreeFormTool(MultiLineTool):
    """
    A tool for drawing free-form shapes on a plot.

    This tool extends the MultiLineTool to create closed shapes when
    there are more than 2 points.
    """

    TITLE: str = _("Free form")
    ICON: str = "freeform.png"

    def cancel_point(self, filter, event) -> None:
        """
        Cancel the last point and update the shape's closed status.

        Args:
            filter: The plot filter.
            event: The triggering event.
        """
        super().cancel_point(filter, event)
        self.shape.closed = len(self.shape.points) > 2

    def mouse_press(self, filter, event) -> None:
        """
        Handle mouse press event and update the shape's closed status.

        Args:
            filter: The plot filter.
            event: The mouse event.
        """
        super().mouse_press(filter, event)
        self.shape.closed = len(self.shape.points) > 2


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
