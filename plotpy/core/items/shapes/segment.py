# -*- coding: utf-8 -*-
import numpy as np
from guidata.configtools import get_icon
from guidata.utils.misc import assert_interfaces_valid

from plotpy.core.items.shapes.polygon import PolygonShape


class SegmentShape(PolygonShape):
    """ """

    CLOSED = False
    ADDITIONNAL_POINTS = 1  # Number of points which are not part of the shape

    def __init__(self, x1=0, y1=0, x2=0, y2=0, shapeparam=None):
        super(SegmentShape, self).__init__(shapeparam=shapeparam)
        self.set_rect(x1, y1, x2, y2)
        self.setIcon(get_icon("segment.png"))

    def set_rect(self, x1, y1, x2, y2):
        """
        Set the start point of this segment to (x1, y1)
        and the end point of this line to (x2, y2)
        """
        self.set_points([(x1, y1), (x2, y2), (0.5 * (x1 + x2), 0.5 * (y1 + y2))])

    def get_rect(self):
        """

        :return:
        """
        return tuple(self.points[0]) + tuple(self.points[1])

    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        nx, ny = pos
        x1, y1, x2, y2 = self.get_rect()
        if not ctrl or ctrl is None:
            if handle == 0:
                self.set_rect(nx, ny, x2, y2)
            elif handle == 1:
                self.set_rect(x1, y1, nx, ny)
            elif handle in (2, -1):
                delta = (nx, ny) - self.points.mean(axis=0)
                self.points += delta
        else:
            # compute linear coefficient y = a * x + b
            # en appuyant sur la touche Ctrl : deplacement du point en
            # conservant la droite du segment initial
            if x2 == x1:
                yA = ny
                xA = x1
            elif y2 == y1:
                yA = y1
                xA = nx
            else:
                a = (y2 - y1) / (x2 - x1)
                b = y1 - a * x1
                xA = a / (a * a + 1) * (nx / a + ny - b)
                yA = a * xA + b
            if handle == 0:
                self.set_rect(xA, yA, x2, y2)
            elif handle == 1:
                self.set_rect(x1, y1, xA, yA)
            elif handle in (2, -1):
                # selection du point milieu, on déplace le segment
                # c'est identique au comportmeent sans la touche Ctrl
                delta = (nx, ny) - self.points.mean(axis=0)
                self.points += delta

    def __reduce__(self):
        state = (self.shapeparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state):
        param, points, z = state
        # ----------------------------------------------------------------------
        # compatibility with previous version of SegmentShape:
        x1, y1, x2, y2, x3, y3 = points.ravel()
        v12 = np.array((x2 - x1, y2 - y1))
        v13 = np.array((x3 - x1, y3 - y1))
        if np.linalg.norm(v12) < np.linalg.norm(v13):
            # old pickle format
            points = np.flipud(np.roll(points, -1, axis=0))
        # ----------------------------------------------------------------------
        self.points = points
        self.setZ(z)
        self.shapeparam = param
        self.shapeparam.update_shape(self)


assert_interfaces_valid(SegmentShape)
