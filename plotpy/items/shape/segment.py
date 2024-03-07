# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.utils.misc import assert_interfaces_valid

from plotpy.items.shape.polygon import PolygonShape

if TYPE_CHECKING:
    from plotpy.styles.shape import ShapeParam


class SegmentShape(PolygonShape):
    """Segment shape

    Args:
        x1: X coordinate of the first point
        y1: Y coordinate of the first point
        x2: X coordinate of the second point
        y2: Y coordinate of the second point
        shapeparam: Shape parameters
    """

    CLOSED = False
    ADDITIONNAL_POINTS = 1  # Number of points which are not part of the shape

    def __init__(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 0.0,
        y2: float = 0.0,
        shapeparam: ShapeParam = None,
    ):
        super().__init__(shapeparam=shapeparam)
        self.set_rect(x1, y1, x2, y2)
        self.setIcon(get_icon("segment.png"))

    def set_rect(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Set the segment coordinates

        Args:
            x1: X coordinate of the first point
            y1: Y coordinate of the first point
            x2: X coordinate of the second point
            y2: Y coordinate of the second point
        """
        self.set_points([(x1, y1), (x2, y2), (0.5 * (x1 + x2), 0.5 * (y1 + y2))])

    def get_rect(self) -> tuple[float, float, float, float]:
        """Return the segment coordinates

        Returns:
            Segment coordinates as a tuple (x1, y1, x2, y2)
        """
        return tuple(self.points[0]) + tuple(self.points[1])

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
        x1, y1, x2, y2 = self.get_rect()
        if ctrl:
            # compute linear coefficient y = a * x + b
            # When ctrl is pressed, the point is moved on the line
            # defined by the segment, and the line is conserved
            # (the segment is not rotated)
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
        else:
            # Ctrl is not pressed, the segment may be rotated freely
            if handle == 0:
                self.set_rect(nx, ny, x2, y2)
            elif handle == 1:
                self.set_rect(x1, y1, nx, ny)
            elif handle in (2, -1):
                delta = (nx, ny) - self.points.mean(axis=0)
                self.points += delta

    def __reduce__(self) -> tuple:
        """Reduce object to picklable state"""
        state = (self.shapeparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
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
