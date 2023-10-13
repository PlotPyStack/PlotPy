# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.config import CONF, _
from plotpy.items.shapes.polygon import PolygonShape
from plotpy.styles.shape import AxesShapeParam

if TYPE_CHECKING:  # pragma: no cover
    import guidata.dataset.io
    import qwt.scale_map
    from qtpy.QtCore import QRectF
    from qtpy.QtGui import QPainter

    from plotpy.styles.base import ItemParameters
    from plotpy.styles.shape import ShapeParam


class Axes(PolygonShape):
    """Axes shape

    Args:
        p0: First point (0,1)
        p1: Second point (1,1)
        p2: Third point (0,0)
        axesparam: Axes parameters
        shapeparam: Shape parameters
    """

    CLOSED: bool = True

    def __init__(
        self,
        p0: tuple[float, float] = (0, 0),
        p1: tuple[float, float] = (0, 0),
        p2: tuple[float, float] = (0, 0),
        axesparam: AxesShapeParam = None,
        shapeparam: ShapeParam = None,
    ) -> None:
        super().__init__(shapeparam=shapeparam)
        self.set_rect(p0, p1, p2)
        self.arrow_angle = 15  # degrees
        self.arrow_size = 0.05  # % of axe length
        self.x_pen = self.pen
        self.x_brush = self.brush
        self.y_pen = self.pen
        self.y_brush = self.brush
        if axesparam is None:
            self.axesparam = AxesShapeParam(_("Axes"), icon="gtaxes.png")
        else:
            self.axesparam = axesparam
        self.axesparam.update_param(self)
        self.setIcon(get_icon("gtaxes.png"))

    def __reduce__(self) -> tuple:
        """Reduce object to picklable state"""
        self.axesparam.update_param(self)
        state = (self.shapeparam, self.axesparam, self.points, self.z())
        return (self.__class__, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
        shapeparam, axesparam, points, z = state
        self.points = points
        self.setZ(z)
        self.shapeparam = shapeparam
        self.shapeparam.update_shape(self)
        self.axesparam = axesparam
        self.axesparam.update_axes(self)

    def serialize(
        self,
        writer: guidata.dataset.io.HDF5Writer
        | guidata.dataset.io.INIWriter
        | guidata.dataset.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        super().serialize(writer)
        self.axesparam.update_param(self)
        writer.write(self.axesparam, group_name="axesparam")

    def deserialize(
        self,
        reader: guidata.dataset.io.HDF5Reader
        | guidata.dataset.io.INIReader
        | guidata.dataset.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        super().deserialize(reader)
        self.axesparam = AxesShapeParam(_("Axes"), icon="gtaxes.png")
        reader.read("axesparam", instance=self.axesparam)
        self.axesparam.update_axes(self)

    def get_transform_matrix(self, dx: float = 1.0, dy: float = 1.0) -> np.ndarray:
        """Return the transformation matrix

        Args:
            dx: X scale
            dy: Y scale

        Returns:
            Transformation matrix
        """
        p0, p1, _p3, p2 = [np.array([p[0], p[1], 1.0]) for p in self.points]
        matrix = np.array([(p1 - p0) / dx, (p2 - p0) / dy, p0])
        if abs(np.linalg.det(matrix)) > 1e-12:
            return np.linalg.inv(matrix)

    def set_rect(
        self, p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float]
    ) -> None:
        """Set the coordinates of the axes

        Args:
            p0: First point (0,1)
            p1: Second point (1,1)
            p2: Third point (0,0)
        """
        p3x = p1[0] + p2[0] - p0[0]
        p3y = p1[1] + p2[1] - p0[1]
        self.set_points([p0, p1, (p3x, p3y), p2])

    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        PolygonShape.set_style(self, section, option + "/border")
        self.axesparam.read_config(CONF, section, option)
        self.axesparam.update_axes(self)

    def move_point_to(
        self, handle: int, pos: tuple[float, float], ctrl: bool = False
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        _nx, _ny = pos
        p0, p1, _p3, p2 = list(self.points)
        d1x = p1[0] - p0[0]
        d1y = p1[1] - p0[1]
        d2x = p2[0] - p0[0]
        d2y = p2[1] - p0[1]
        if handle == 0:
            pp0 = pos
            pp1 = pos[0] + d1x, pos[1] + d1y
            pp2 = pos[0] + d2x, pos[1] + d2y
        elif handle == 1:
            pp0 = p0
            pp1 = pos
            pp2 = p2
        elif handle == 3:
            pp0 = p0
            pp1 = p1
            pp2 = pos
        elif handle == 2:
            # find (a,b) such that p3 = a*d1 + b*d2 + p0
            d3x = pos[0] - p0[0]
            d3y = pos[1] - p0[1]
            det = d1x * d2y - d2x * d1y
            if abs(det) < 1e-6:
                # reset
                d1x = d2y = 1.0
                d1y = d2x = 0.0
                det = 1.0
            a = (d2y * d3x - d2x * d3y) / det
            b = (-d1y * d3x + d1x * d3y) / det
            _pp3 = pos
            pp1 = p0[0] + a * d1x, p0[1] + a * d1y
            pp2 = p0[0] + b * d2x, p0[1] + b * d2y
            pp0 = p0
        self.set_rect(pp0, pp1, pp2)
        if self.plot():
            self.plot().SIG_AXES_CHANGED.emit(self)

    def move_shape(self, old_pos: QC.QPointF, new_pos: QC.QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in axis coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        PolygonShape.move_shape(self, old_pos, new_pos)
        if self.plot():
            self.plot().SIG_AXES_CHANGED.emit(self)

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
        PolygonShape.draw(self, painter, xMap, yMap, canvasRect)
        p0, p1, _, p2 = list(self.points)

        points = self.transform_points(xMap, yMap)  # points is a QPolygonF

        painter.setPen(self.x_pen)
        painter.setBrush(self.x_brush)
        painter.drawLine(points.at(0), points.at(1))
        self.draw_arrow(painter, xMap, yMap, p0, p1)
        painter.setPen(self.y_pen)
        painter.setBrush(self.y_brush)
        painter.drawLine(points.at(0), points.at(3))
        self.draw_arrow(painter, xMap, yMap, p0, p2)

    def draw_arrow(
        self,
        painter: QPainter,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        p0: tuple[float, float],
        p1: tuple[float, float],
    ) -> None:
        """Draw an arrow

        Args:
            painter: Painter
            xMap: X axis scale map
            yMap: Y axis scale map
            p0: First point
            p1: Second point
        """
        sz = self.arrow_size
        angle = math.pi * self.arrow_angle / 180.0
        ca, sa = math.cos(angle), math.sin(angle)
        d1x = xMap.transform(p1[0]) - xMap.transform(p0[0])
        d1y = yMap.transform(p1[1]) - yMap.transform(p0[1])
        norm = math.sqrt(d1x**2 + d1y**2)
        if abs(norm) < 1e-6:
            return
        d1x *= sz / norm
        d1y *= sz / norm
        n1x = -d1y
        n1y = d1x
        # arrow : a0 - a1 == p1 - a2
        a1x = xMap.transform(p1[0])
        a1y = yMap.transform(p1[1])
        a0x = a1x - ca * d1x + sa * n1x
        a0y = a1y - ca * d1y + sa * n1y
        a2x = a1x - ca * d1x - sa * n1x
        a2y = a1y - ca * d1y - sa * n1y

        poly = QG.QPolygonF()
        poly.append(QC.QPointF(a0x, a0y))
        poly.append(QC.QPointF(a1x, a1y))
        poly.append(QC.QPointF(a2x, a2y))
        painter.drawPolygon(poly)

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.axesparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        PolygonShape.get_item_parameters(self, itemparams)
        self.update_item_parameters()
        itemparams.add("AxesShapeParam", self, self.axesparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        PolygonShape.set_item_parameters(self, itemparams)
        update_dataset(
            self.axesparam, itemparams.get("AxesShapeParam"), visible_only=True
        )
        self.axesparam.update_axes(self)


assert_interfaces_valid(Axes)
