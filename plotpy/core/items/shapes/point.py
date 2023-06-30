# -*- coding: utf-8 -*-
from guidata.configtools import get_icon
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.config import _
from plotpy.core.items.shapes.polygon import PolygonShape


class PointShape(PolygonShape):
    """ """

    CLOSED = False

    def __init__(self, x=0, y=0, shapeparam=None):
        super(PointShape, self).__init__(shapeparam=shapeparam)
        self.set_pos(x, y)
        self.setIcon(get_icon("point_shape.png"))

    def set_pos(self, x, y):
        """Set the point coordinates to (x, y)"""
        self.set_points([(x, y)])

    def get_pos(self):
        """Return the point coordinates"""
        return tuple(self.points[0])

    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        nx, ny = pos
        self.points[0] = (nx, ny)

    def __reduce__(self):
        state = (self.shapeparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state):
        self.shapeparam, self.points, z = state
        self.setZ(z)
        self.shapeparam.update_shape(self)

    def boundingRect(self):
        """Return the bounding rectangle of the data"""
        poly = QG.QPolygonF()
        if self.ADDITIONNAL_POINTS:
            shape_points = self.points[: -self.ADDITIONNAL_POINTS]
        else:
            shape_points = self.points
        for i in range(shape_points.shape[0]):
            poly.append(QC.QPointF(shape_points[i, 0], shape_points[i, 1]))
        return poly.boundingRect()


assert_interfaces_valid(PointShape)
