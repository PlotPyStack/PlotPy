# -*- coding: utf-8 -*-
#
# For licensing and distribution details, please read carefully xgrid/__init__.py

# pylint: disable=invalid-name  # Allows short reference names like x, y, ...

from __future__ import annotations

from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtSvg as QS
from qwt.scale_map import QwtScaleMap
from qwt.symbol import QwtSymbol

from plotpy.items import shapes
from plotpy.styles import ShapeParam


class RectangleSVGShape(shapes.RectangleShape):
    """Rectangle SVG shape

    Args:
        x1: X coordinate of the top-left corner
        y1: Y coordinate of the top-left corner
        x2: X coordinate of the bottom-right corner
        y2: Y coordinate of the bottom-right corner
        svg_data: SVG bytes
        shapeparam: Shape parameters
    """

    def __init__(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 0.0,
        y2: float = 0.0,
        svg_data: bytes | None = None,
        shapeparam: ShapeParam = None,
    ) -> None:
        self.svg_data = svg_data
        shapes.RectangleShape.__init__(self, x1, y1, x2, y2, shapeparam)

    def set_data(self, svg_data: bytes) -> None:
        """Set SVG data"""
        self.svg_data = svg_data

    def draw(
        self,
        painter: QG.QPainter,
        xMap: QwtScaleMap,
        yMap: QwtScaleMap,
        canvasRect: QC.QRectF,
    ) -> None:
        """Draw shape (reimplement shapes.Shape.draw))"""
        points = self.transform_points(xMap, yMap)
        renderer = QS.QSvgRenderer(self.svg_data)
        renderer.render(painter, points.boundingRect())


class SquareSVGShape(RectangleSVGShape):
    """Square SVG shape

    Args:
        svg_data: SVG bytes
        x1: X coordinate of the top-left corner
        y1: Y coordinate of the top-left corner
        x2: X coordinate of the bottom-right corner
        y2: Y coordinate of the bottom-right corner
        shapeparam: Shape parameters
    """

    def move_point_to(self, handle: int, pos: tuple[float], ctrl: bool = None):
        """Reimplement RectangleShape.move_point_to"""
        nx, ny = pos
        x1, y1, x2, y2 = self.get_rect()
        if handle == 0:
            self.set_rect(nx, y2 - (x2 - nx), x2, y2)
        elif handle == 1:
            self.set_rect(x1, y2 - (nx - x1), nx, y2)
        elif handle == 2:
            self.set_rect(x1, y1, nx, y1 + (nx - x1))
        elif handle == 3:
            self.set_rect(nx, y1, x2, y1 + (x2 - nx))
        elif handle == -1:
            delta = (nx, ny) - self.points.mean(axis=0)
            self.points += delta


class CircleSVGShape(shapes.EllipseShape):
    """Circle SVG shape

    Args:
        x1: X coordinate of the top-left corner
        y1: Y coordinate of the top-left corner
        x2: X coordinate of the bottom-right corner
        y2: Y coordinate of the bottom-right corner
        svg_data: SVG bytes
        shapeparam: Shape parameters
    """

    def __init__(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 0.0,
        y2: float = 0.0,
        svg_data: bytes | None = None,
        shapeparam: ShapeParam = None,
    ) -> None:
        self.svg_data = svg_data
        shapes.EllipseShape.__init__(self, x1, y1, x2, y2, shapeparam)

    def set_data(self, svg_data: bytes) -> None:
        """Set SVG data"""
        self.svg_data = svg_data

    def draw(
        self,
        painter: QG.QPainter,
        xMap: QwtScaleMap,
        yMap: QwtScaleMap,
        canvasRect: QC.QRect,
    ) -> None:
        """Draw shape (reimplement shapes.Shape.draw))"""
        points, line0, line1, rect = self.compute_elements(xMap, yMap)
        if canvasRect.intersects(rect.toRect()) and self.svg_data is not None:
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
            renderer = QS.QSvgRenderer(self.svg_data)
            renderer.render(painter, rect)
            painter.restore()
            if symbol != QwtSymbol.NoSymbol:
                for i in range(points.size()):
                    symbol.drawSymbol(painter, points[i].toPoint())
