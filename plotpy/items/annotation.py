# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Annotations
-----------

The :mod:`annotation` module provides annotated shape plot items.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid

from plotpy.config import CONF, _
from plotpy.coords import canvas_to_axes
from plotpy.interfaces import IBasePlotItem, ISerializableType, IShapeItemType
from plotpy.items.label import DataInfoLabel
from plotpy.items.shape.base import AbstractShape
from plotpy.items.shape.ellipse import EllipseShape
from plotpy.items.shape.point import PointShape
from plotpy.items.shape.rectangle import ObliqueRectangleShape, RectangleShape
from plotpy.items.shape.segment import SegmentShape
from plotpy.mathutils.geometry import (
    compute_angle,
    compute_center,
    compute_distance,
    compute_rect_size,
)
from plotpy.styles.label import LabelParam
from plotpy.styles.shape import AnnotationParam

if TYPE_CHECKING:
    import guidata.io
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QPainter

    from plotpy.interfaces import IItemType
    from plotpy.styles.base import ItemParameters


class AnnotatedShape(AbstractShape):
    """
    Construct an annotated shape with properties set with
    *annotationparam* (see :py:class:`.styles.AnnotationParam`)

    Args:
        annotationparam: Annotation parameters
    """

    __implements__ = (IBasePlotItem, ISerializableType)
    SHAPE_CLASS: type[AbstractShape] = RectangleShape  # to be overridden
    LABEL_ANCHOR: str = ""

    def __init__(self, annotationparam: AnnotationParam | None = None) -> None:
        super().__init__()
        assert self.LABEL_ANCHOR is not None and len(self.LABEL_ANCHOR) != 0
        self.shape: AbstractShape = self.create_shape()
        self.label = self.create_label()
        self.area_computations_visible = True
        self.subtitle_visible = True
        if annotationparam is None:
            self.annotationparam = AnnotationParam(
                _("Annotation"), icon="annotation.png"
            )
        else:
            self.annotationparam = annotationparam
            self.annotationparam.update_annotation(self)
        self.setIcon(get_icon("annotation.png"))

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType, ISerializableType)

    def __reduce__(self) -> tuple[type, tuple, tuple]:
        """Return a tuple for pickling"""
        self.annotationparam.update_param(self)
        state = (self.shape, self.label, self.annotationparam)
        return (self.__class__, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Set state after unpickling"""
        shape, label, param = state
        self.shape = shape
        self.label = label
        self.annotationparam = param
        self.annotationparam.update_annotation(self)

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        writer.write(self.annotationparam, group_name="annotationparam")
        self.shape.serialize(writer)
        self.label.serialize(writer)

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.annotationparam = AnnotationParam(_("Annotation"), icon="annotation.png")
        reader.read("annotationparam", instance=self.annotationparam)
        self.annotationparam.update_annotation(self)
        self.shape.deserialize(reader)
        self.label.deserialize(reader)

    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        self.shape.set_style(section, option)

    # ----QwtPlotItem API--------------------------------------------------------
    def draw(
        self,
        painter: QPainter,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        canvasRect: QRectF,
    ) -> None:
        """Draw the item

        Args:
            painter: Painter
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Canvas rectangle
        """
        self.shape.draw(painter, xMap, yMap, canvasRect)
        if self.label.isVisible():
            self.label.draw(painter, xMap, yMap, canvasRect)

    # ----Public API-------------------------------------------------------------
    def create_shape(self):
        """Return the shape object associated to this annotated shape object"""
        shape = self.SHAPE_CLASS(0, 0, 1, 1)  # pylint: disable=not-callable
        return shape

    def create_label(self) -> DataInfoLabel:
        """Return the label object associated to this annotated shape object

        Returns:
            Label object
        """
        label_param = LabelParam(_("Label"), icon="label.png")
        label_param.read_config(CONF, "plot", "shape/label")
        label_param.anchor = self.LABEL_ANCHOR
        return DataInfoLabel(label_param, [self])

    def is_label_visible(self) -> bool:
        """Return True if associated label is visible

        Returns:
            True if associated label is visible
        """
        return self.label.isVisible()

    def set_label_visible(self, state: bool) -> None:
        """Set the annotated shape's label visibility

        Args:
            state: True if label should be visible
        """
        self.label.setVisible(state)

    def update_label(self) -> None:
        """Update the annotated shape's label contents"""
        self.label.update_text()

    def get_text(self) -> str:
        """Return text associated to current shape
        (see :py:class:`.label.ObjectInfo`)

        Returns:
            Text associated to current shape
        """
        text = ""
        title = self.title().text()
        if title:
            text += f"<b>{title}</b>"
        subtitle = self.annotationparam.subtitle
        if subtitle and self.subtitle_visible:
            if text:
                text += "<br>"
            text += f"<i>{subtitle}</i>"
        if self.area_computations_visible:
            infos = self.get_infos()
            if infos:
                if text:
                    text += "<br>"
                text += infos
        return text

    def x_to_str(self, x: float) -> str:
        """Convert x to a string (with associated unit and uncertainty)

        Args:
            x: X value

        Returns:
            str: Formatted string with x value
        """
        param = self.annotationparam
        if self.plot() is None:
            return ""
        else:
            xunit = self.plot().get_axis_unit(self.xAxis())
            fmt = param.format
            if param.uncertainty:
                fmt += " ± " + (fmt % (x * param.uncertainty))
            if xunit is not None:
                return (fmt + " " + xunit) % x
            else:
                return (fmt) % x

    def y_to_str(self, y):
        """Convert y to a string (with associated unit and uncertainty)

        Args:
            y: Y value

        Returns:
            str: Formatted string with x value
        """
        param = self.annotationparam
        if self.plot() is None:
            return ""
        else:
            yunit = self.plot().get_axis_unit(self.yAxis())
            fmt = param.format
            if param.uncertainty:
                fmt += " ± " + (fmt % (y * param.uncertainty))
            if yunit is not None:
                return (fmt + " " + yunit) % y
            else:
                return (fmt) % y

    def get_center(self):
        """Return shape center coordinates: (xc, yc)"""
        return self.shape.get_center()

    def get_tr_center(self):
        """Return shape center coordinates after applying transform matrix"""
        raise NotImplementedError

    def get_tr_center_str(self):
        """Return center coordinates as a string (with units)"""
        xc, yc = self.get_tr_center()
        return f"( {self.x_to_str(xc)} ; {self.y_to_str(yc)} )"

    def get_tr_size(self):
        """Return shape size after applying transform matrix"""
        raise NotImplementedError

    def get_tr_size_str(self):
        """Return size as a string (with units)"""
        xs, ys = self.get_tr_size()
        return f"{self.x_to_str(xs)} x {self.y_to_str(ys)}"

    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        return ""

    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        raise NotImplementedError

    def apply_transform_matrix(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        V = np.array([x, y, 1.0])
        W = np.dot(V, self.annotationparam.transform_matrix)
        return W[0], W[1]

    def get_transformed_coords(self, handle1, handle2):
        """

        :param handle1:
        :param handle2:
        :return:
        """
        x1, y1 = self.apply_transform_matrix(*self.shape.points[handle1])
        x2, y2 = self.apply_transform_matrix(*self.shape.points[handle2])
        return x1, y1, x2, y2

    # ----IBasePlotItem API------------------------------------------------------
    def hit_test(self, pos: QPointF) -> tuple[float, float, bool, None]:
        """Return a tuple (distance, attach point, inside, other_object)

        Args:
            pos: Position

        Returns:
            tuple: Tuple with four elements: (distance, attach point, inside,
             other_object).

        Description of the returned values:

        * distance: distance in pixels (canvas coordinates) to the closest
           attach point
        * attach point: handle of the attach point
        * inside: True if the mouse button has been clicked inside the object
        * other_object: if not None, reference of the object which will be
           considered as hit instead of self
        """
        return self.shape.poly_hit_test(self.plot(), self.xAxis(), self.yAxis(), pos)

    def move_point_to(
        self, handle: int, pos: tuple[float, float], ctrl: bool = False
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        self.shape.move_point_to(handle, pos, ctrl)
        self.set_label_position()
        if self.plot():
            self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    def move_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in axis coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        self.shape.move_shape(old_pos, new_pos)
        self.label.move_local_shape(old_pos, new_pos)

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        old_pt = canvas_to_axes(self, old_pos)
        new_pt = canvas_to_axes(self, new_pos)
        self.shape.move_shape(old_pt, new_pt)
        self.set_label_position()
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, *(old_pt + new_pt))
            self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        self.shape.move_with_selection(delta_x, delta_y)
        self.label.move_with_selection(delta_x, delta_y)
        self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    def select(self) -> None:
        """
        Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        AbstractShape.select(self)
        self.shape.select()

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        AbstractShape.unselect(self)
        self.shape.unselect()

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        self.shape.get_item_parameters(itemparams)
        self.label.get_item_parameters(itemparams)
        self.annotationparam.update_param(self)
        itemparams.add("AnnotationParam", self, self.annotationparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        self.shape.set_item_parameters(itemparams)
        self.label.set_item_parameters(itemparams)
        update_dataset(
            self.annotationparam, itemparams.get("AnnotationParam"), visible_only=True
        )
        self.annotationparam.update_annotation(self)
        self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    # Autoscalable types API

    def is_empty(self) -> bool:
        """Return True if the item is empty

        Returns:
            True if the item is empty, False otherwise
        """
        return self.shape.is_empty()

    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the shape

        Returns:
            Bounding rectangle of the shape
        """
        return self.shape.boundingRect()


assert_interfaces_valid(AnnotatedShape)


class AnnotatedPoint(AnnotatedShape):
    """
    Construct an annotated point at coordinates (x, y)
    with properties set with *annotationparam*
    (see :py:class:`.styles.AnnotationParam`)
    """

    SHAPE_CLASS = PointShape
    LABEL_ANCHOR = "TL"

    def __init__(self, x=0, y=0, annotationparam=None):
        AnnotatedShape.__init__(self, annotationparam)
        self.set_pos(x, y)
        self.setIcon(get_icon("point_shape.png"))

    # ----Public API-------------------------------------------------------------
    def set_pos(self, x, y):
        """Set the point coordinates to (x, y)"""
        self.shape.set_pos(x, y)
        self.set_label_position()

    def get_pos(self):
        """Return the point coordinates"""
        return self.shape.get_pos()

    # ----AnnotatedShape API-----------------------------------------------------
    def create_shape(self):
        """Return the shape object associated to this annotated shape object"""
        shape = self.SHAPE_CLASS(0, 0)
        return shape

    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        x, y = self.shape.points[0]
        self.label.set_pos(x, y)

    # ----AnnotatedShape API-----------------------------------------------------
    def get_tr_position(self):
        xt, yt = self.apply_transform_matrix(*self.shape.points[0])
        return xt, yt

    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        xt, yt = self.apply_transform_matrix(*self.shape.points[0])
        s = "{title} ( {posx} ; {posy} )"
        s = s.format(
            title=_("Position:"), posx=self.x_to_str(xt), posy=self.y_to_str(yt)
        )
        return s


class AnnotatedSegment(AnnotatedShape):
    """
    Construct an annotated segment between coordinates (x1, y1) and
    (x2, y2) with properties set with *annotationparam*
    (see :py:class:`.styles.AnnotationParam`)
    """

    SHAPE_CLASS = SegmentShape
    LABEL_ANCHOR = "C"

    def __init__(self, x1=0, y1=0, x2=0, y2=0, annotationparam=None):
        AnnotatedShape.__init__(self, annotationparam)
        self.set_rect(x1, y1, x2, y2)
        self.setIcon(get_icon("segment.png"))

    # ----Public API-------------------------------------------------------------
    def set_rect(self, x1, y1, x2, y2):
        """
        Set the coordinates of the shape's top-left corner to (x1, y1),
        and of its bottom-right corner to (x2, y2).
        """
        self.shape.set_rect(x1, y1, x2, y2)
        self.set_label_position()

    def get_rect(self):
        """
        Return the coordinates of the shape's top-left and bottom-right corners
        """
        return self.shape.get_rect()

    def get_tr_length(self):
        """Return segment length after applying transform matrix"""
        return compute_distance(*self.get_transformed_coords(0, 1))

    def get_tr_center(self):
        """Return segment position (middle) after applying transform matrix"""
        return compute_center(*self.get_transformed_coords(0, 1))

    # ----AnnotatedShape API-----------------------------------------------------
    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        x1, y1, x2, y2 = self.get_rect()
        self.label.set_pos(*compute_center(x1, y1, x2, y2))

    # ----AnnotatedShape API-----------------------------------------------------
    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        return "<br>".join(
            [
                _("Center:") + " " + self.get_tr_center_str(),
                _("Distance:") + " " + self.x_to_str(self.get_tr_length()),
            ]
        )


class AnnotatedRectangle(AnnotatedShape):
    """
    Construct an annotated rectangle between coordinates (x1, y1) and
    (x2, y2) with properties set with *annotationparam*
    (see :py:class:`.styles.AnnotationParam`)
    """

    SHAPE_CLASS = RectangleShape
    LABEL_ANCHOR = "TL"

    def __init__(self, x1=0, y1=0, x2=0, y2=0, annotationparam=None):
        AnnotatedShape.__init__(self, annotationparam)
        self.set_rect(x1, y1, x2, y2)
        self.setIcon(get_icon("rectangle.png"))

    # ----Public API-------------------------------------------------------------
    def set_rect(self, x1, y1, x2, y2):
        """
        Set the coordinates of the shape's top-left corner to (x1, y1),
        and of its bottom-right corner to (x2, y2).
        """
        self.shape.set_rect(x1, y1, x2, y2)
        self.set_label_position()

    def get_rect(self) -> tuple[float, float, float, float]:
        """
        Return the coordinates of the shape's top-left and bottom-right corners
        """
        return self.shape.get_rect()

    # ----AnnotatedShape API-----------------------------------------------------
    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        x_label, y_label = self.shape.points.min(axis=0)
        self.label.set_pos(x_label, y_label)

    def get_tr_center(self):
        """Return shape center coordinates after applying transform matrix"""
        return compute_center(*self.get_transformed_coords(0, 2))

    def get_tr_size(self):
        """Return shape size after applying transform matrix"""
        return compute_rect_size(*self.get_transformed_coords(0, 2))

    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        return "<br>".join(
            [
                _("Center:") + " " + self.get_tr_center_str(),
                _("Size:") + " " + self.get_tr_size_str(),
            ]
        )


class AnnotatedObliqueRectangle(AnnotatedRectangle):
    """
    Construct an annotated oblique rectangle between coordinates (x0, y0),
    (x1, y1), (x2, y2) and (x3, y3) with properties set with *annotationparam*
    (see :py:class:`.styles.AnnotationParam`)
    """

    SHAPE_CLASS = ObliqueRectangleShape
    LABEL_ANCHOR = "C"

    def __init__(
        self, x0=0, y0=0, x1=0, y1=0, x2=0, y2=0, x3=0, y3=0, annotationparam=None
    ):
        AnnotatedShape.__init__(self, annotationparam)
        self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        self.setIcon(get_icon("oblique_rectangle.png"))

    # ----Public API-------------------------------------------------------------
    def get_tr_angle(self):
        """Return X-diameter angle with horizontal direction,
        after applying transform matrix"""
        xcoords = self.get_transformed_coords(0, 1)
        _x, yr1 = self.apply_transform_matrix(1.0, 1.0)
        _x, yr2 = self.apply_transform_matrix(1.0, 2.0)
        return (compute_angle(*xcoords, reverse=yr1 > yr2) + 90) % 180 - 90

    def get_bounding_rect_coords(self) -> tuple[float, float, float, float]:
        """Return bounding rectangle coordinates (in plot coordinates)

        Returns:
            Bounding rectangle coordinates (in plot coordinates)
        """
        return self.shape.get_bounding_rect_coords()

    # ----AnnotatedShape API-----------------------------------------------------
    def create_shape(self):
        """Return the shape object associated to this annotated shape object"""
        shape = self.SHAPE_CLASS(0, 0, 0, 0, 0, 0, 0, 0)
        return shape

    # ----AnnotatedShape API-----------------------------------------------------
    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        self.label.set_pos(*self.get_center())

    # ----RectangleShape API-----------------------------------------------------
    def set_rect(self, x0, y0, x1, y1, x2, y2, x3, y3):
        """
        Set the rectangle corners coordinates:

            (x0, y0): top-left corner
            (x1, y1): top-right corner
            (x2, y2): bottom-right corner
            (x3, y3): bottom-left corner

        ::

            x: additionnal points

            (x0, y0)------>(x1, y1)
                ↑             |
                |             |
                x             x
                |             |
                |             ↓
            (x3, y3)<------(x2, y2)
        """
        self.shape.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        self.set_label_position()

    def get_tr_size(self):
        """Return shape size after applying transform matrix"""
        dx = compute_distance(*self.get_transformed_coords(0, 1))
        dy = compute_distance(*self.get_transformed_coords(0, 3))
        return dx, dy

    # ----AnnotatedShape API-----------------------------------------------------
    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        return "<br>".join(
            [
                _("Center:") + " " + self.get_tr_center_str(),
                _("Size:") + " " + self.get_tr_size_str(),
                _("Angle:") + " %.1f°" % self.get_tr_angle(),
            ]
        )

    def get_tr_center(self):
        x0, y0, x2, y2 = self.get_transformed_coords(0, 2)
        return compute_center(x0, y0, x2, y2)


class AnnotatedEllipse(AnnotatedShape):
    """
    Construct an annotated ellipse with X-axis diameter between
    coordinates (x1, y1) and (x2, y2)
    and properties set with *annotationparam*
    (see :py:class:`.styles.AnnotationParam`)
    """

    SHAPE_CLASS = EllipseShape
    LABEL_ANCHOR = "C"

    def __init__(self, x1=0, y1=0, x2=0, y2=0, annotationparam=None):
        AnnotatedShape.__init__(self, annotationparam)
        self.set_xdiameter(x1, y1, x2, y2)
        self.setIcon(get_icon("ellipse_shape.png"))
        self.switch_to_ellipse()

    # ----Public API-------------------------------------------------------------
    def switch_to_ellipse(self):
        """Switch to ellipse mode"""
        self.shape.switch_to_ellipse()

    def switch_to_circle(self):
        """Switch to circle mode"""
        self.shape.switch_to_circle()

    def set_xdiameter(self, x0, y0, x1, y1):
        """Set the coordinates of the ellipse's X-axis diameter
        Warning: transform matrix is not applied here"""
        self.shape.set_xdiameter(x0, y0, x1, y1)
        self.set_label_position()

    def get_xdiameter(self):
        """Return the coordinates of the ellipse's X-axis diameter
        Warning: transform matrix is not applied here"""
        return self.shape.get_xdiameter()

    def set_ydiameter(self, x2, y2, x3, y3):
        """Set the coordinates of the ellipse's Y-axis diameter
        Warning: transform matrix is not applied here"""
        self.shape.set_ydiameter(x2, y2, x3, y3)
        self.set_label_position()

    def get_ydiameter(self):
        """Return the coordinates of the ellipse's Y-axis diameter
        Warning: transform matrix is not applied here"""
        return self.shape.get_ydiameter()

    def get_rect(self):
        """

        :return:
        """
        return self.shape.get_rect()

    def set_rect(self, x0, y0, x1, y1):
        """

        :param x0:
        :param y0:
        :param x1:
        :param y1:
        """
        raise NotImplementedError

    def get_tr_angle(self):
        """Return X-diameter angle with horizontal direction,
        after applying transform matrix"""
        xcoords = self.get_transformed_coords(0, 1)
        _x, yr1 = self.apply_transform_matrix(1.0, 1.0)
        _x, yr2 = self.apply_transform_matrix(1.0, 2.0)
        return (compute_angle(*xcoords, reverse=yr1 > yr2) + 90) % 180 - 90

    # ----AnnotatedShape API-----------------------------------------------------
    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        x_label, y_label = self.shape.points.mean(axis=0)
        self.label.set_pos(x_label, y_label)

    def get_tr_center(self):
        """Return center coordinates: (xc, yc)"""
        return compute_center(*self.get_transformed_coords(0, 1))

    def get_tr_size(self):
        """Return shape size after applying transform matrix"""
        xcoords = self.get_transformed_coords(0, 1)
        ycoords = self.get_transformed_coords(2, 3)
        dx = compute_distance(*xcoords)
        dy = compute_distance(*ycoords)
        if np.fabs(self.get_tr_angle()) > 45:
            dx, dy = dy, dx
        return dx, dy

    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        return "<br>".join(
            [
                _("Center:") + " " + self.get_tr_center_str(),
                _("Size:") + " " + self.get_tr_size_str(),
                _("Angle:") + f" {self.get_tr_angle():.1f}°",
            ]
        )


class AnnotatedCircle(AnnotatedEllipse):
    """
    Construct an annotated circle with diameter between coordinates
    (x1, y1) and (x2, y2) and properties set with *annotationparam*
    (see :py:class:`.styles.AnnotationParam`)
    """

    def __init__(self, x1=0, y1=0, x2=0, y2=0, annotationparam=None):
        AnnotatedEllipse.__init__(self, x1, y1, x2, y2, annotationparam)
        self.shape.switch_to_circle()

    def get_tr_diameter(self):
        """Return circle diameter after applying transform matrix"""
        return compute_distance(*self.get_transformed_coords(0, 1))

    # ----AnnotatedShape API-------------------------------------------------
    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        return "<br>".join(
            [
                _("Center:") + " " + self.get_tr_center_str(),
                _("Diameter:") + " " + self.x_to_str(self.get_tr_diameter()),
            ]
        )

    # ----AnnotatedEllipse API---------------------------------------------------
    def set_rect(self, x0, y0, x1, y1):
        """

        :param x0:
        :param y0:
        :param x1:
        :param y1:
        """
        self.shape.set_rect(x0, y0, x1, y1)
