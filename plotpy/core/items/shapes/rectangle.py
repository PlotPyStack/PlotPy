# -*- coding: utf-8 -*-
import numpy as np
from guidata.configtools import get_icon
from guidata.utils.misc import assert_interfaces_valid

from plotpy.core.items.shapes.polygon import PolygonShape
from plotpy.utils.geometry import (
    compute_center,
    vector_norm,
    vector_projection,
    vector_rotation,
)


def _no_null_vector(x0, y0, x1, y1, x2, y2, x3, y3):
    return (
        vector_norm(x0, y0, x1, y1)
        and vector_norm(x0, y0, x2, y2)
        and vector_norm(x0, y0, x3, y3)
        and vector_norm(x1, y1, x2, y2)
        and vector_norm(x1, y1, x3, y3)
        and vector_norm(x2, y2, x3, y3)
    )


class RectangleShape(PolygonShape):
    """ """

    CLOSED = True

    def __init__(self, x1=0, y1=0, x2=0, y2=0, shapeparam=None):
        super(RectangleShape, self).__init__(shapeparam=shapeparam)
        self.set_rect(x1, y1, x2, y2)
        self.setIcon(get_icon("rectangle.png"))

    def set_rect(self, x1, y1, x2, y2):
        """
        Set the coordinates of the rectangle's top-left corner to (x1, y1),
        and of its bottom-right corner to (x2, y2).
        """
        self.set_points([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

    def get_rect(self):
        """

        :return:
        """
        return tuple(self.points[0]) + tuple(self.points[2])

    def get_center(self):
        """Return center coordinates: (xc, yc)"""
        return compute_center(*self.get_rect())

    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        nx, ny = pos
        x1, y1, x2, y2 = self.get_rect()
        if handle == 0:
            self.set_rect(nx, ny, x2, y2)
        elif handle == 1:
            self.set_rect(x1, ny, nx, y2)
        elif handle == 2:
            self.set_rect(x1, y1, nx, ny)
        elif handle == 3:
            self.set_rect(nx, y1, x2, ny)
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


assert_interfaces_valid(RectangleShape)


class ObliqueRectangleShape(PolygonShape):
    """ """

    CLOSED = True
    ADDITIONNAL_POINTS = 2  # Number of points which are not part of the shape
    LINK_ADDITIONNAL_POINTS = True  # Link additionnal points with dotted lines

    def __init__(self, x0=0, y0=0, x1=0, y1=0, x2=0, y2=0, x3=0, y3=0, shapeparam=None):
        super(ObliqueRectangleShape, self).__init__(shapeparam=shapeparam)
        self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        self.setIcon(get_icon("oblique_rectangle.png"))

    def set_rect(self, x0, y0, x1, y1, x2, y2, x3, y3):
        """
        Set the rectangle corners coordinates:

            (x0, y0): top-left corner
            (x1, y1): top-right corner
            (x2, y2): bottom-right corner
            (x3, y3): bottom-left corner

        ::

            x: additionnal points (handles used for rotation -- other handles
            being used for rectangle resizing)

            (x0, y0)------>(x1, y1)
                ↑             |
                |             |
                x             x
                |             |
                |             ↓
            (x3, y3)<------(x2, y2)
        """
        self.set_points(
            [
                (x0, y0),
                (x1, y1),
                (x2, y2),
                (x3, y3),
                (0.5 * (x0 + x3), 0.5 * (y0 + y3)),
                (0.5 * (x1 + x2), 0.5 * (y1 + y2)),
            ]
        )

    def get_rect(self):
        """

        :return:
        """
        return self.points.ravel()[: -self.ADDITIONNAL_POINTS * 2]

    def get_center(self):
        """Return center coordinates: (xc, yc)"""
        rect = tuple(self.points[0]) + tuple(self.points[2])
        return compute_center(*rect)

    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        nx, ny = pos
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_rect()
        if handle == 0:
            if vector_norm(x2, y2, x3, y3) and vector_norm(x2, y2, x1, y1):
                v0n = np.array((nx - x0, ny - y0))
                x3, y3 = vector_projection(v0n, x2, y2, x3, y3)
                x1, y1 = vector_projection(v0n, x2, y2, x1, y1)
                x0, y0 = nx, ny
                if _no_null_vector(x0, y0, x1, y1, x2, y2, x3, y3):
                    self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        elif handle == 1:
            if vector_norm(x3, y3, x0, y0) and vector_norm(x3, y3, x2, y2):
                v1n = np.array((nx - x1, ny - y1))
                x0, y0 = vector_projection(v1n, x3, y3, x0, y0)
                x2, y2 = vector_projection(v1n, x3, y3, x2, y2)
                x1, y1 = nx, ny
                if _no_null_vector(x0, y0, x1, y1, x2, y2, x3, y3):
                    self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        elif handle == 2:
            if vector_norm(x0, y0, x1, y1) and vector_norm(x0, y0, x3, y3):
                v2n = np.array((nx - x2, ny - y2))
                x1, y1 = vector_projection(v2n, x0, y0, x1, y1)
                x3, y3 = vector_projection(v2n, x0, y0, x3, y3)
                x2, y2 = nx, ny
                if _no_null_vector(x0, y0, x1, y1, x2, y2, x3, y3):
                    self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        elif handle == 3:
            if vector_norm(x1, y1, x0, y0) and vector_norm(x1, y1, x2, y2):
                v3n = np.array((nx - x3, ny - y3))
                x0, y0 = vector_projection(v3n, x1, y1, x0, y0)
                x2, y2 = vector_projection(v3n, x1, y1, x2, y2)
                x3, y3 = nx, ny
                if _no_null_vector(x0, y0, x1, y1, x2, y2, x3, y3):
                    self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        elif handle == 4:
            x4, y4 = 0.5 * (x0 + x3), 0.5 * (y0 + y3)
            x5, y5 = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
            nx, ny = x0 + nx - x4, y0 + ny - y4  # moving handle #4 to handle #0

            v10 = np.array((x0 - x1, y0 - y1))
            v12 = np.array((x2 - x1, y2 - y1))
            v10n = np.array((nx - x1, ny - y1))
            k = np.linalg.norm(v12) / np.linalg.norm(v10)
            v12n = vector_rotation(-np.pi / 2, *v10n) * k
            x2, y2 = v12n + np.array([x1, y1])
            x3, y3 = v12n + v10n + np.array([x1, y1])
            x0, y0 = nx, ny

            dx = x5 - 0.5 * (x1 + x2)
            dy = y5 - 0.5 * (y1 + y2)
            x0, y0 = x0 + dx, y0 + dy
            x1, y1 = x1 + dx, y1 + dy
            x2, y2 = x2 + dx, y2 + dy
            x3, y3 = x3 + dx, y3 + dy
            self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
        elif handle == 5:
            x4, y4 = 0.5 * (x0 + x3), 0.5 * (y0 + y3)
            x5, y5 = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
            nx, ny = x1 + nx - x5, y1 + ny - y5  # moving handle #5 to handle #1

            v01 = np.array((x1 - x0, y1 - y0))
            v03 = np.array((x3 - x0, y3 - y0))
            v01n = np.array((nx - x0, ny - y0))
            k = np.linalg.norm(v03) / np.linalg.norm(v01)
            v03n = vector_rotation(np.pi / 2, *v01n) * k
            x3, y3 = v03n + np.array([x0, y0])
            x2, y2 = v03n + v01n + np.array([x0, y0])
            x1, y1 = nx, ny

            dx = x4 - 0.5 * (x0 + x3)
            dy = y4 - 0.5 * (y0 + y3)
            x0, y0 = x0 + dx, y0 + dy
            x1, y1 = x1 + dx, y1 + dy
            x2, y2 = x2 + dx, y2 + dy
            x3, y3 = x3 + dx, y3 + dy
            self.set_rect(x0, y0, x1, y1, x2, y2, x3, y3)
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


assert_interfaces_valid(ObliqueRectangleShape)
