# -*- coding: utf-8 -*-

from __future__ import annotations

import math
import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtSymbol

from plotpy.items.shape.polygon import PolygonShape
from plotpy.mathutils.geometry import compute_angle, compute_center

if TYPE_CHECKING:
    import qwt.scale_map
    from qtpy.QtCore import QLineF, QPointF, QRectF
    from qtpy.QtGui import QPainter, QPolygonF

    from plotpy.styles.shape import ShapeParam


class EllipseShape(PolygonShape):
    """Ellipse shape

    Args:
        x1: X coordinate of the first point
        y1: Y coordinate of the first point
        x2: X coordinate of the second point
        y2: Y coordinate of the second point
        shapeparam: Shape parameters
    """

    CLOSED = True
    _icon_name = "circle.png"

    def __init__(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 0.0,
        y2: float = 0.0,
        shapeparam: ShapeParam = None,
    ) -> None:
        super().__init__(shapeparam=shapeparam)
        self.is_ellipse = False
        self.set_xdiameter(x1, y1, x2, y2)

    def switch_to_ellipse(self):
        """Switch to ellipse mode"""
        self.is_ellipse = True
        self.set_icon_name("ellipse_shape.png")

    def switch_to_circle(self):
        """Switch to circle mode"""
        self.is_ellipse = False
        self.set_icon_name("circle.png")

    def set_xdiameter(self, x0: float, y0: float, x1: float, y1: float) -> None:
        """Set the coordinates of the ellipse's X-axis diameter

        Args:
            x0: X coordinate of the first point
            y0: Y coordinate of the first point
            x1: X coordinate of the second point
            y1: Y coordinate of the second point
        """
        xline = QC.QLineF(x0, y0, x1, y1)
        yline = xline.normalVector()
        yline.translate(xline.pointAt(0.5) - xline.p1())
        if self.is_ellipse:
            yline.setLength(self.get_yline().length())
        else:
            yline.setLength(xline.length())
        yline.translate(yline.pointAt(0.5) - yline.p2())
        self.set_points(
            [(x0, y0), (x1, y1), (yline.x1(), yline.y1()), (yline.x2(), yline.y2())]
        )

    def get_xdiameter(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return the coordinates of the ellipse's X-axis diameter

        Returns:
            Tuple with two tuples of floats
        """
        return tuple(self.points[0]) + tuple(self.points[1])

    def set_ydiameter(self, x2: float, y2: float, x3: float, y3: float) -> None:
        """Set the coordinates of the ellipse's Y-axis diameter

        Args:
            x2: X coordinate of the first point
            y2: Y coordinate of the first point
            x3: X coordinate of the second point
            y3: Y coordinate of the second point
        """
        yline = QC.QLineF(x2, y2, x3, y3)
        xline = yline.normalVector()
        xline.translate(yline.pointAt(0.5) - yline.p1())
        if self.is_ellipse:
            xline.setLength(self.get_xline().length())
        xline.translate(xline.pointAt(0.5) - xline.p2())
        self.set_points(
            [(xline.x2(), xline.y2()), (xline.x1(), xline.y1()), (x2, y2), (x3, y3)]
        )

    def get_ydiameter(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return the coordinates of the ellipse's Y-axis diameter

        Returns:
            Tuple with two tuples of floats
        """
        return tuple(self.points[2]) + tuple(self.points[3])

    def get_rect(self) -> tuple[float, float, float, float]:
        """Get the bounding rectangle of the shape

        Returns:
            Tuple with four floats

        .. warning::

            This method is valid for circle only!
        """
        assert not self.is_ellipse
        (x0, y0), (x1, y1) = self.points[0], self.points[1]
        xc, yc = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        radius = 0.5 * np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        return xc - radius, yc - radius, xc + radius, yc + radius

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the shape

        Returns:
            Bounding rectangle of the shape
        """
        # See https://stackoverflow.com/a/14163413
        (x0, y0), (x1, y1) = self.points[0], self.points[1]
        radius1 = 0.5 * np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

        (x2, y2), (x3, y3) = self.points[2], self.points[3]
        radius2 = 0.5 * np.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)

        xc, yc = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        phi = math.radians(compute_angle(xc, yc, x1, y1))

        ux = radius1 * math.cos(phi)
        uy = radius1 * math.sin(phi)
        vx = radius2 * math.cos(phi + math.pi / 2)
        vy = radius2 * math.sin(phi + math.pi / 2)

        bbox_halfwidth = math.sqrt(ux * ux + vx * vx)
        bbox_halfheight = math.sqrt(uy * uy + vy * vy)

        return QC.QRectF(
            xc - bbox_halfwidth,
            yc - bbox_halfheight,
            2 * bbox_halfwidth,
            2 * bbox_halfheight,
        )

    def get_center(self) -> tuple[float, float]:
        """Return center coordinates

        Returns:
            Tuple with two floats (x, y)
        """
        return compute_center(*self.get_xdiameter())

    def set_rect(self, x0: float, y0: float, x1: float, y1: float) -> None:
        """Set the bounding rectangle of the shape

        Args:
            x0: X coordinate of the first point
            y0: Y coordinate of the first point
            x1: X coordinate of the second point
            y1: Y coordinate of the second point

        .. warning::

            This method is valid for circle only!
        """
        assert not self.is_ellipse
        self.set_xdiameter(x0, 0.5 * (y0 + y1), x1, 0.5 * (y0 + y1))

    def compute_elements(
        self, xMap: qwt.scale_map.QwtScaleMap, yMap: qwt.scale_map.QwtScaleMap
    ) -> tuple[QPolygonF, QLineF, QLineF, QRectF]:
        """Return points, lines and ellipse rect

        Args:
            xMap: X axis scale map
            yMap: Y axis scale map

        Returns:
            Tuple with four elements (points, line0, line1, rect)
        """
        points = self.transform_points(xMap, yMap)
        line0 = QC.QLineF(points[0], points[1])
        line1 = QC.QLineF(points[2], points[3])
        rect = QC.QRectF()
        rect.setWidth(line0.length())
        rect.setHeight(line1.length())
        rect.moveCenter(line0.pointAt(0.5))
        return points, line0, line1, rect

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
        if not self.plot():
            return sys.maxsize, 0, False, None
        dist, handle, inside, other = self.poly_hit_test(
            self.plot(), self.xAxis(), self.yAxis(), pos
        )
        if not inside:
            xMap = self.plot().canvasMap(self.xAxis())
            yMap = self.plot().canvasMap(self.yAxis())
            _points, _line0, _line1, rect = self.compute_elements(xMap, yMap)
            inside = rect.contains(QC.QPointF(pos))
        return dist, handle, inside, other

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
        points, line0, line1, rect = self.compute_elements(xMap, yMap)
        pen, brush, symbol = self.get_pen_brush(xMap, yMap)
        painter.setRenderHint(QG.QPainter.Antialiasing)
        painter.setPen(pen)
        painter.setBrush(brush)

        # Draw the axes lines connecting handles
        painter.drawLine(line0)
        painter.drawLine(line1)

        # For the ellipse, we need to handle non-uniform aspect ratios properly.
        # The ellipse should have its semi-axes aligned with line0 and line1 directions.
        # We use QPainterPath to draw an ellipse transformed to match the actual
        # geometry.
        center = line0.pointAt(0.5)

        # Create the ellipse in a local coordinate system where line0 is horizontal
        # and line1 is vertical, then transform it to match the actual geometry
        path = QG.QPainterPath()

        # Calculate the angle between line0 and line1 in pixel space
        # (they should be 90° in data space but may differ after transformation)
        angle0 = math.radians(line0.angle())
        angle1 = math.radians(line1.angle())

        # Semi-axes lengths
        a = line0.length() / 2  # semi-major axis (along line0)
        b = line1.length() / 2  # semi-minor axis (along line1)

        # Draw ellipse using parametric form, accounting for non-perpendicular axes
        # We sample points around the ellipse and create a path
        n_points = 72  # Number of points for smooth ellipse
        first_point = True
        for i in range(n_points + 1):
            t = 2 * math.pi * i / n_points
            # Parametric ellipse with potentially non-perpendicular axes
            # Point = center + cos(t) * a * dir0 + sin(t) * b * dir1
            dx = math.cos(t) * a * math.cos(angle0) + math.sin(t) * b * math.cos(angle1)
            dy = -math.cos(t) * a * math.sin(angle0) - math.sin(t) * b * math.sin(
                angle1
            )
            px = center.x() + dx
            py = center.y() + dy
            if first_point:
                path.moveTo(px, py)
                first_point = False
            else:
                path.lineTo(px, py)
        path.closeSubpath()
        painter.drawPath(path)

        if symbol != QwtSymbol.NoSymbol:
            for i in range(points.size()):
                symbol.drawSymbol(painter, points[i].toPoint())

    def get_xline(self) -> QC.QLineF:
        """Get the X axis diameter

        Returns:
            X axis diameter
        """
        return QC.QLineF(*(tuple(self.points[0]) + tuple(self.points[1])))

    def get_yline(self) -> QC.QLineF:
        """Get the Y axis diameter

        Returns:
            Y axis diameter
        """
        return QC.QLineF(*(tuple(self.points[2]) + tuple(self.points[3])))

    def move_point_to(
        self, handle: int, pos: tuple[float, float], ctrl: bool = False
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        nx, ny = pos
        if handle == 0:
            x1, y1 = self.points[1]
            if ctrl:
                # When <Ctrl> is pressed, the center position is unchanged
                x0, y0 = self.points[0]
                x1, y1 = x1 + x0 - nx, y1 + y0 - ny
            self.set_xdiameter(nx, ny, x1, y1)
        elif handle == 1:
            x0, y0 = self.points[0]
            if ctrl:
                # When <Ctrl> is pressed, the center position is unchanged
                x1, y1 = self.points[1]
                x0, y0 = x0 + x1 - nx, y0 + y1 - ny
            self.set_xdiameter(x0, y0, nx, ny)
        elif handle == 2:
            x3, y3 = self.points[3]
            if ctrl:
                # When <Ctrl> is pressed, the center position is unchanged
                x2, y2 = self.points[2]
                x3, y3 = x3 + x2 - nx, y3 + y2 - ny
            self.set_ydiameter(nx, ny, x3, y3)
        elif handle == 3:
            x2, y2 = self.points[2]
            if ctrl:
                # When <Ctrl> is pressed, the center position is unchanged
                x3, y3 = self.points[3]
                x2, y2 = x2 + x3 - nx, y2 + y3 - ny
            self.set_ydiameter(x2, y2, nx, ny)
        elif handle == -1:
            delta = (nx, ny) - self.points.mean(axis=0)
            self.points += delta

    def __reduce__(self) -> tuple:
        """Return a tuple used by pickle"""
        state = (self.shapeparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Set the state of the object from a tuple"""
        self.shapeparam, self.points, z = state
        self.setZ(z)
        self.shapeparam.update_item(self)


assert_interfaces_valid(EllipseShape)
