# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
plotpy.core.items.annotations
-----------------------------

"""

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import update_dataset
from guidata.utils.misc import assert_interfaces_valid

from plotpy.config import CONF, _
from plotpy.core.coords import canvas_to_axes
from plotpy.core.interfaces.common import (
    IBasePlotItem,
    ISerializableType,
    IShapeItemType,
)
from plotpy.core.items.label import DataInfoLabel
from plotpy.core.items.shapes.base import AbstractShape
from plotpy.core.items.shapes.ellipse import EllipseShape
from plotpy.core.items.shapes.point import PointShape
from plotpy.core.items.shapes.rectangle import ObliqueRectangleShape, RectangleShape
from plotpy.core.items.shapes.segment import SegmentShape
from plotpy.core.styles.label import LabelParam
from plotpy.core.styles.shape import AnnotationParam
from plotpy.utils.geometry import (
    compute_angle,
    compute_center,
    compute_distance,
    compute_rect_size,
)


class AnnotatedShape(AbstractShape):
    """
    Construct an annotated shape with properties set with
    *annotationparam* (see :py:class:`.styles.AnnotationParam`)
    """

    __implements__ = (IBasePlotItem, ISerializableType)
    SHAPE_CLASS = None
    LABEL_ANCHOR = None

    def __init__(self, annotationparam=None):
        AbstractShape.__init__(self)
        assert self.LABEL_ANCHOR is not None
        self.shape = self.create_shape()
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

    def types(self):
        """

        :return:
        """
        return (IShapeItemType, ISerializableType)

    def __reduce__(self):
        self.annotationparam.update_param(self)
        state = (self.shape, self.label, self.annotationparam)
        return (self.__class__, (), state)

    def __setstate__(self, state):
        shape, label, param = state
        self.shape = shape
        self.label = label
        self.annotationparam = param
        self.annotationparam.update_annotation(self)

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        writer.write(self.annotationparam, group_name="annotationparam")
        self.shape.serialize(writer)
        self.label.serialize(writer)

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
        self.annotationparam = AnnotationParam(_("Annotation"), icon="annotation.png")
        reader.read("annotationparam", instance=self.annotationparam)
        self.annotationparam.update_annotation(self)
        self.shape.deserialize(reader)
        self.label.deserialize(reader)

    def set_style(self, section, option):
        """

        :param section:
        :param option:
        """
        self.shape.set_style(section, option)

    # ----QwtPlotItem API--------------------------------------------------------
    def draw(self, painter, xMap, yMap, canvasRect):
        """

        :param painter:
        :param xMap:
        :param yMap:
        :param canvasRect:
        """
        self.shape.draw(painter, xMap, yMap, canvasRect)
        if self.label.isVisible():
            self.label.draw(painter, xMap, yMap, canvasRect)

    # ----Public API-------------------------------------------------------------
    def create_shape(self):
        """Return the shape object associated to this annotated shape object"""
        shape = self.SHAPE_CLASS(0, 0, 1, 1)  # pylint: disable=not-callable
        return shape

    def create_label(self):
        """Return the label object associated to this annotated shape object"""
        label_param = LabelParam(_("Label"), icon="label.png")
        label_param.read_config(CONF, "plot", "shape/label")
        label_param.anchor = self.LABEL_ANCHOR
        return DataInfoLabel(label_param, [self])

    def is_label_visible(self):
        """Return True if associated label is visible"""
        return self.label.isVisible()

    def set_label_visible(self, state):
        """Set the annotated shape's label visibility"""
        self.label.setVisible(state)

    def update_label(self):
        """Update the annotated shape's label contents"""
        self.label.update_text()

    def get_text(self):
        """
        Return text associated to current shape
        (see :py:class:`.label.ObjectInfo`)
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

    def x_to_str(self, x):
        """Convert x (float) to a string
        (with associated unit and uncertainty)"""
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
        """Convert y (float) to a string
        (with associated unit and uncertainty)"""
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
        return "( {} ; {} )".format(self.x_to_str(xc), self.y_to_str(yc))

    def get_tr_size(self):
        """Return shape size after applying transform matrix"""
        raise NotImplementedError

    def get_tr_size_str(self):
        """Return size as a string (with units)"""
        xs, ys = self.get_tr_size()
        return "{} x {}".format(self.x_to_str(xs), self.y_to_str(ys))

    def get_infos(self):
        """Return formatted string with informations on current shape"""
        pass

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
    def hit_test(self, pos):
        """

        :param pos:
        :return:
        """
        return self.shape.poly_hit_test(self.plot(), self.xAxis(), self.yAxis(), pos)

    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        self.shape.move_point_to(handle, pos, ctrl)
        self.set_label_position()
        if self.plot():
            self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    def move_shape(self, old_pos, new_pos):
        """

        :param old_pos:
        :param new_pos:
        """
        self.shape.move_shape(old_pos, new_pos)
        self.label.move_local_shape(old_pos, new_pos)

    def move_local_shape(self, old_pos, new_pos):
        """

        :param old_pos:
        :param new_pos:
        """
        old_pt = canvas_to_axes(self, old_pos)
        new_pt = canvas_to_axes(self, new_pos)
        self.shape.move_shape(old_pt, new_pt)
        self.set_label_position()
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, *(old_pt + new_pt))
            self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    def move_with_selection(self, delta_x, delta_y):
        """
        Translate the shape together with other selected items
        delta_x, delta_y: translation in plot coordinates
        """
        self.shape.move_with_selection(delta_x, delta_y)
        self.label.move_with_selection(delta_x, delta_y)
        self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    def select(self):
        """Select item"""
        AbstractShape.select(self)
        self.shape.select()

    def unselect(self):
        """Unselect item"""
        AbstractShape.unselect(self)
        self.shape.unselect()

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        self.shape.get_item_parameters(itemparams)
        self.label.get_item_parameters(itemparams)
        self.annotationparam.update_param(self)
        itemparams.add("AnnotationParam", self, self.annotationparam)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        self.shape.set_item_parameters(itemparams)
        self.label.set_item_parameters(itemparams)
        update_dataset(
            self.annotationparam, itemparams.get("AnnotationParam"), visible_only=True
        )
        self.annotationparam.update_annotation(self)
        self.plot().SIG_ANNOTATION_CHANGED.emit(self)

    # Autoscalable types API

    def is_empty(self):
        """Returns True if the shape is empty"""
        return self.shape.is_empty()

    def boundingRect(self):
        """Returns boundingRect of the shape"""
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

    def get_infos(self):
        """Return formatted string with informations on current shape"""
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
    def get_infos(self):
        """Return formatted string with informations on current shape"""
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

    def get_rect(self):
        """
        Return the coordinates of the shape's top-left and bottom-right corners
        """
        return self.shape.get_rect()

    # ----AnnotatedShape API-----------------------------------------------------
    def set_label_position(self):
        """Set label position, for instance based on shape position"""
        x_label, y_label = self.shape.points.min(axis=0)
        self.label.set_pos(x_label, y_label)

    def get_computations_text(self):
        """Return formatted string with informations on current shape"""
        tdict = self.get_string_dict()
        return "{center_n} ( {center} )<br>{size_n} {size}".format_map(tdict)

    def get_tr_center(self):
        """Return shape center coordinates after applying transform matrix"""
        return compute_center(*self.get_transformed_coords(0, 2))

    def get_tr_size(self):
        """Return shape size after applying transform matrix"""
        return compute_rect_size(*self.get_transformed_coords(0, 2))

    def get_infos(self):
        """Return formatted string with informations on current shape"""
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
        return (compute_angle(reverse=yr1 > yr2, *xcoords) + 90) % 180 - 90

    def get_bounding_rect_coords(self):
        """Return bounding rectangle coordinates (in plot coordinates)"""
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
    def get_infos(self):
        """Return formatted string with informations on current shape"""
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
        self.shape.switch_to_ellipse()

    # ----Public API-------------------------------------------------------------
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
        return (compute_angle(reverse=yr1 > yr2, *xcoords) + 90) % 180 - 90

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

    def get_infos(self):
        """Return formatted string with informations on current shape"""
        return "<br>".join(
            [
                _("Center:") + " " + self.get_tr_center_str(),
                _("Size:") + " " + self.get_tr_size_str(),
                _("Angle:") + " {:.1f}°".format(self.get_tr_angle()),
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
    def get_infos(self):
        """Return formatted string with informations on current shape"""
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
