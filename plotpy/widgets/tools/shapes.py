# -*- coding: utf-8 -*-
from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.widgets.events import (
    KeyEventMatch,
    QtDragHandler,
    setup_standard_tool_filter,
)
from plotpy.widgets.items.shapes.ellipse import EllipseShape
from plotpy.widgets.items.shapes.point import PointShape
from plotpy.widgets.items.shapes.polygon import PolygonShape
from plotpy.widgets.items.shapes.rectangle import ObliqueRectangleShape
from plotpy.widgets.items.shapes.segment import SegmentShape
from plotpy.widgets.tools.base import (
    SHAPE_Z_OFFSET,
    DefaultToolbarID,
    InteractiveTool,
    RectangularActionTool,
)


class MultiLineTool(InteractiveTool):
    """ """

    TITLE = _("Polyline")
    ICON = "polyline.png"
    CURSOR = QC.Qt.CursorShape.ArrowCursor

    def __init__(
        self,
        manager,
        handle_final_shape_cb=None,
        shape_style=None,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=None,
    ):
        super(MultiLineTool, self).__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        self.handle_final_shape_cb = handle_final_shape_cb
        self.shape = None
        self.current_handle = None
        self.init_pos = None
        if shape_style is not None:
            self.shape_style_sect = shape_style[0]
            self.shape_style_key = shape_style[1]
        else:
            self.shape_style_sect = "plot"
            self.shape_style_key = "shape/drag"

    def reset(self):
        """ """
        self.shape = None
        self.current_handle = None

    def create_shape(self, filter, pt):
        """

        :param filter:
        :param pt:
        :return:
        """
        self.shape = PolygonShape(closed=False)
        filter.plot.add_item_with_z_offset(self.shape, SHAPE_Z_OFFSET)
        self.shape.setVisible(True)
        self.shape.set_style(self.shape_style_sect, self.shape_style_key)
        self.shape.add_local_point(pt)
        return self.shape.add_local_point(pt)

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
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

    def validate(self, filter, event):
        """

        :param filter:
        :param event:
        """
        super(MultiLineTool, self).validate(filter, event)
        if self.handle_final_shape_cb is not None:
            self.handle_final_shape_cb(self.shape)
        self.reset()

    def cancel_point(self, filter, event):
        """

        :param filter:
        :param event:
        :return:
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

    def mouse_press(self, filter, event):
        """We create a new shape if it's the first point
        otherwise we add a new point
        """
        if self.shape is None:
            self.init_pos = event.pos()
            self.current_handle = self.create_shape(filter, event.pos())
            filter.plot.replot()
        else:
            self.current_handle = self.shape.add_local_point(event.pos())

    def move(self, filter, event):
        """moving while holding the button down lets the user
        position the last created point
        """
        if self.shape is None or self.current_handle is None:
            # Error ??
            return
        self.shape.move_local_point_to(self.current_handle, event.pos())
        filter.plot.replot()

    def mouse_release(self, filter, event):
        """Releasing the mouse button validate the last point position"""
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
    TITLE = _("Free form")
    ICON = "freeform.png"

    def cancel_point(self, filter, event):
        """Reimplement base class method"""
        super(FreeFormTool, self).cancel_point(filter, event)
        self.shape.closed = len(self.shape.points) > 2

    def mouse_press(self, filter, event):
        """Reimplement base class method"""
        super(FreeFormTool, self).mouse_press(filter, event)
        self.shape.closed = len(self.shape.points) > 2


class RectangularShapeTool(RectangularActionTool):
    """ """

    TITLE = None
    ICON = None

    def __init__(
        self,
        manager,
        setup_shape_cb=None,
        handle_final_shape_cb=None,
        shape_style=None,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=None,
    ):
        super(RectangularShapeTool, self).__init__(
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

    def add_shape_to_plot(self, plot, p0, p1):
        """
        Method called when shape's rectangular area
        has just been drawn on screen.
        Adding the final shape to plot and returning it.
        """
        shape = self.get_final_shape(plot, p0, p1)
        self.handle_final_shape(shape)
        plot.replot()

    def setup_shape(self, shape):
        """To be reimplemented"""
        shape.setTitle(self.TITLE)
        if self.setup_shape_cb is not None:
            self.setup_shape_cb(shape)

    def handle_final_shape(self, shape):
        """To be reimplemented"""
        if self.handle_final_shape_cb is not None:
            self.handle_final_shape_cb(shape)


class RectangleTool(RectangularShapeTool):
    TITLE = _("Rectangle")
    ICON = "rectangle.png"


class ObliqueRectangleTool(RectangularShapeTool):
    TITLE = _("Oblique rectangle")
    ICON = "oblique_rectangle.png"
    AVOID_NULL_SHAPE = True

    def create_shape(self):
        """

        :return:
        """
        shape = ObliqueRectangleShape(1, 1, 2, 1, 2, 2, 1, 2)
        self.set_shape_style(shape)
        return shape, 0, 2


class PointTool(RectangularShapeTool):
    TITLE = _("Point")
    ICON = "point_shape.png"
    SHAPE_STYLE_KEY = "shape/point"

    def create_shape(self):
        """

        :return:
        """
        shape = PointShape(0, 0)
        self.set_shape_style(shape)
        return shape, 0, 0


class SegmentTool(RectangularShapeTool):
    TITLE = _("Segment")
    ICON = "segment.png"
    SHAPE_STYLE_KEY = "shape/segment"

    def create_shape(self):
        """

        :return:
        """
        shape = SegmentShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 1


class CircleTool(RectangularShapeTool):
    TITLE = _("Circle")
    ICON = "circle.png"

    def create_shape(self):
        """

        :return:
        """
        shape = EllipseShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 1


class EllipseTool(RectangularShapeTool):
    TITLE = _("Ellipse")
    ICON = "ellipse_shape.png"

    def create_shape(self):
        """

        :return:
        """
        shape = EllipseShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 1

    def handle_final_shape(self, shape):
        """

        :param shape:
        """
        shape.switch_to_ellipse()
        super(EllipseTool, self).handle_final_shape(shape)
