# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.items.shape.polygon import PolygonShape

if TYPE_CHECKING:
    from plotpy.styles.shape import ShapeParam


class PointShape(PolygonShape):
    """Point shape

    Args:
        x: X coordinate
        y: Y coordinate
        shapeparam: Shape parameters
    """

    CLOSED = False
    _icon_name = "point_shape.png"

    def __init__(
        self, x: float = 0.0, y: float = 0.0, shapeparam: ShapeParam = None
    ) -> None:
        super().__init__(shapeparam=shapeparam)
        self.set_pos(x, y)

    def set_pos(self, x: float, y: float) -> None:
        """Set the point coordinates to (x, y)

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.set_points([(x, y)])

    def get_pos(self) -> tuple[float, float]:
        """Return the point coordinates

        Returns:
            Point coordinates
        """
        return tuple(self.points[0])

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
        self.points[0] = (nx, ny)

    def __reduce__(self) -> tuple:
        """Reduce object to picklable state"""
        state = (self.shapeparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
        self.shapeparam, self.points, z = state
        self.setZ(z)
        self.shapeparam.update_item(self)

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the shape

        Returns:
            Bounding rectangle of the shape
        """
        poly = QG.QPolygonF()
        if self.ADDITIONNAL_POINTS:
            shape_points = self.points[: -self.ADDITIONNAL_POINTS]
        else:
            shape_points = self.points
        for i in range(shape_points.shape[0]):
            poly.append(QC.QPointF(shape_points[i, 0], shape_points[i, 1]))
        return poly.boundingRect()


assert_interfaces_valid(PointShape)
