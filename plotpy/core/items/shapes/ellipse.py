# -*- coding: utf-8 -*-
import math
import sys

import numpy as np
from guidata.configtools import get_icon
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtSymbol

from plotpy.core.items.shapes.polygon import PolygonShape
from plotpy.utils.geometry import compute_angle, compute_center


class EllipseShape(PolygonShape):
    """ """

    CLOSED = True

    def __init__(self, x1=0, y1=0, x2=0, y2=0, shapeparam=None):
        super(EllipseShape, self).__init__(shapeparam=shapeparam)
        self.is_ellipse = False
        self.set_xdiameter(x1, y1, x2, y2)
        self.setIcon(get_icon("circle.png"))

    def switch_to_ellipse(self):
        self.is_ellipse = True
        self.setIcon(get_icon("ellipse_shape.png"))

    def switch_to_circle(self):
        self.is_ellipse = False
        self.setIcon(get_icon("circle.png"))

    def set_xdiameter(self, x0, y0, x1, y1):
        """Set the coordinates of the ellipse's X-axis diameter"""
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

    def get_xdiameter(self):
        """Return the coordinates of the ellipse's X-axis diameter"""
        return tuple(self.points[0]) + tuple(self.points[1])

    def set_ydiameter(self, x2, y2, x3, y3):
        """Set the coordinates of the ellipse's Y-axis diameter"""
        yline = QC.QLineF(x2, y2, x3, y3)
        xline = yline.normalVector()
        xline.translate(yline.pointAt(0.5) - yline.p1())
        if self.is_ellipse:
            xline.setLength(self.get_xline().length())
        xline.translate(xline.pointAt(0.5) - xline.p2())
        self.set_points(
            [(xline.x1(), xline.y1()), (xline.x2(), xline.y2()), (x2, y2), (x3, y3)]
        )

    def get_ydiameter(self):
        """Return the coordinates of the ellipse's Y-axis diameter"""
        return tuple(self.points[2]) + tuple(self.points[3])

    def get_rect(self):
        """Circle only!"""
        (x0, y0), (x1, y1) = self.points[0], self.points[1]
        xc, yc = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        radius = 0.5 * np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        return xc - radius, yc - radius, xc + radius, yc + radius

    def boundingRect(self):
        """Return the bounding rectangle"""
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

    def get_center(self):
        """Return center coordinates: (xc, yc)"""
        return compute_center(*self.get_xdiameter())

    def set_rect(self, x0, y0, x1, y1):
        """Circle only!"""
        self.set_xdiameter(x0, 0.5 * (y0 + y1), x1, 0.5 * (y0 + y1))

    def compute_elements(self, xMap, yMap):
        """Return points, lines and ellipse rect"""
        points = self.transform_points(xMap, yMap)
        line0 = QC.QLineF(points[0], points[1])
        line1 = QC.QLineF(points[2], points[3])
        rect = QC.QRectF()
        rect.setWidth(line0.length())
        rect.setHeight(line1.length())
        rect.moveCenter(line0.pointAt(0.5))
        return points, line0, line1, rect

    def hit_test(self, pos):
        """return (dist, handle, inside)"""
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

    def draw(self, painter, xMap, yMap, canvasRect):
        """

        :param painter:
        :param xMap:
        :param yMap:
        :param canvasRect:
        """
        points, line0, line1, rect = self.compute_elements(xMap, yMap)
        pen, brush, symbol = self.get_pen_brush(xMap, yMap)
        painter.setRenderHint(QG.QPainter.Antialiasing)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawLine(line0)
        painter.drawLine(line1)
        painter.save()
        painter.translate(rect.center())
        painter.rotate(-line0.angle())
        painter.translate(-rect.center())
        painter.drawEllipse(rect.toRect())
        painter.restore()
        if symbol != QwtSymbol.NoSymbol:
            for i in range(points.size()):
                symbol.drawSymbol(painter, points[i].toPoint())

    def get_xline(self):
        """

        :return:
        """
        return QC.QLineF(*(tuple(self.points[0]) + tuple(self.points[1])))

    def get_yline(self):
        """

        :return:
        """
        return QC.QLineF(*(tuple(self.points[2]) + tuple(self.points[3])))

    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
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

    def __reduce__(self):
        state = (self.shapeparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state):
        self.shapeparam, self.points, z = state
        self.setZ(z)
        self.shapeparam.update_shape(self)


assert_interfaces_valid(EllipseShape)
