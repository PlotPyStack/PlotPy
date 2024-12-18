# -*- coding: utf-8 -*-

from __future__ import annotations

import math
import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtSymbol

from plotpy.config import CONF, _
from plotpy.coords import canvas_to_axes
from plotpy.interfaces import IBasePlotItem, ISerializableType, IShapeItemType
from plotpy.items.shape.base import AbstractShape
from plotpy.styles.shape import ShapeParam

if TYPE_CHECKING:
    import guidata.io
    import qwt.scale_map
    import qwt.symbol
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QBrush, QPainter, QPen, QPolygonF

    from plotpy.interfaces import IItemType
    from plotpy.plot.base import BasePlot
    from plotpy.styles.base import ItemParameters


class PolygonShape(AbstractShape):
    """Polygon shape class

    Args:
        points: List of point coordinates
        closed: True if the polygon is closed, False otherwise
        shapeparam: Shape parameters
    """

    __implements__ = (IBasePlotItem, ISerializableType)
    ADDITIONNAL_POINTS = 0  # Number of points which are not part of the shape
    LINK_ADDITIONNAL_POINTS = False  # Link additionnal points with dotted lines
    CLOSED = True
    _icon_name = "polygon.png"

    def __init__(
        self,
        points: list[tuple[float, float]] | np.ndarray | None = None,
        closed: bool | None = None,
        shapeparam: ShapeParam | None = None,
    ) -> None:
        super().__init__()
        self.closed = self.CLOSED if closed is None else closed
        self.selected = False

        if shapeparam is None:
            self.shapeparam = ShapeParam(_("Shape"), icon="rectangle.png")
        else:
            self.shapeparam = shapeparam
            self.shapeparam.update_item(self)

        self.pen = QG.QPen()
        self.brush = QG.QBrush()
        self.symbol = QwtSymbol.NoSymbol
        self.sel_pen = QG.QPen()
        self.sel_brush = QG.QBrush()
        self.sel_symbol = QwtSymbol.NoSymbol
        self.points: np.ndarray | None = None
        self.set_points(points)

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType, ISerializableType)

    def __reduce__(self) -> tuple[type, tuple, tuple]:
        """Return state information for pickling"""
        self.shapeparam.update_param(self)
        state = (self.shapeparam, self.points, self.closed, self.z())
        return (PolygonShape, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Set state information for unpickling"""
        self.shapeparam, self.points, self.closed, z = state
        self.setZ(z)
        self.shapeparam.update_item(self)

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        self.shapeparam.update_param(self)
        writer.write(self.shapeparam, group_name="shapeparam")
        writer.write(self.points, group_name="points")
        writer.write(self.closed, group_name="closed")
        writer.write(self.z(), group_name="z")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.closed = reader.read("closed")
        self.shapeparam = ShapeParam(_("Shape"), icon="rectangle.png")
        reader.read("shapeparam", instance=self.shapeparam)
        self.shapeparam.update_item(self)
        self.points = reader.read(group_name="points", func=reader.read_array)
        self.setZ(reader.read("z"))

    # ----Public API-------------------------------------------------------------

    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        self.shapeparam.read_config(CONF, section, option)
        self.shapeparam.update_item(self)

    def set_points(self, points: list[tuple[float, float]] | np.ndarray | None) -> None:
        """Set polygon points

        Args:
            points: List of point coordinates
        """
        if points is None:
            self.points = np.zeros((0, 2), float)
        else:
            self.points = np.array(points, float)
            assert self.points.shape[1] == 2

    def get_points(self) -> np.ndarray:
        """Return polygon points

        Returns:
            Polygon points (array of shape (N, 2))
        """
        return self.points

    def set_closed(self, state: bool) -> None:
        """Set closed state

        Args:
            state: True if the polygon is closed, False otherwise
        """
        self.closed = state

    def is_closed(self) -> bool:
        """Return True if the polygon is closed, False otherwise

        Returns:
            True if the polygon is closed, False otherwise
        """
        return self.closed

    def get_center(self) -> tuple[float, float]:
        """Return the center of the polygon

        Returns:
            Center of the polygon
        """
        if self.points is not None and self.points.size > 0:
            return self.points.mean(axis=0)
        return 0.0, 0.0

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the data

        Returns:
            Bounding rectangle of the data
        """
        poly = QG.QPolygonF()
        if self.ADDITIONNAL_POINTS:
            shape_points = self.points[: -self.ADDITIONNAL_POINTS]
        else:
            shape_points = self.points
        for i in range(shape_points.shape[0]):
            poly.append(QC.QPointF(shape_points[i, 0], shape_points[i, 1]))
        return poly.boundingRect()

    def is_empty(self) -> bool:
        """Return True if the item is empty

        Returns:
            True if the item is empty, False otherwise
        """
        return len(self.points) == 0

    def get_bounding_rect_coords(self) -> tuple[float, float, float, float]:
        """Return bounding rectangle coordinates (in plot coordinates)

        Returns:
            Bounding rectangle coordinates (in plot coordinates)
        """
        poly = QG.QPolygonF()
        shape_points = self.points[: -self.ADDITIONNAL_POINTS]
        for i in range(shape_points.shape[0]):
            poly.append(QC.QPointF(shape_points[i, 0], shape_points[i, 1]))
        return poly.boundingRect().getCoords()

    def transform_points(
        self, xMap: qwt.scale_map.QwtScaleMap, yMap: qwt.scale_map.QwtScaleMap
    ) -> QPolygonF:
        """Transform points to canvas coordinates

        Args:
            xMap: X axis scale map
            yMap: Y axis scale map

        Returns:
            Transformed points
        """
        points = QG.QPolygonF()
        for i in range(self.points.shape[0]):
            points.append(
                QC.QPointF(
                    xMap.transform(self.points[i, 0]), yMap.transform(self.points[i, 1])
                )
            )
        return points

    def get_reference_point(self) -> tuple[float, float] | None:
        """Return a reference point for the item

        Returns:
            Reference point for the item
        """
        if self.points.size:
            return self.points.mean(axis=0)

    def get_pen_brush(
        self, xMap: qwt.scale_map.QwtScaleMap, yMap: qwt.scale_map.QwtScaleMap
    ) -> tuple[QPen, QBrush, qwt.symbol.QwtSymbol]:
        """Get pen, brush and symbol for the item

        Args:
            xMap: X axis scale map
            yMap: Y axis scale map

        Returns:
            Tuple with pen, brush and symbol for the item
        """
        if self.selected:
            pen = self.sel_pen
            brush = self.sel_brush
            sym = self.sel_symbol
        else:
            pen = self.pen
            brush = self.brush
            sym = self.symbol
        if self.points.size > 0:
            x0, y0 = self.get_reference_point()
            xx0 = xMap.transform(x0)
            yy0 = yMap.transform(y0)
            try:
                # Optimized version in PyQt >= v4.5
                t0 = QG.QTransform.fromTranslate(xx0, yy0)
            except AttributeError:
                # Fallback for PyQt <= v4.4
                t0 = QG.QTransform().translate(xx0, yy0)
            tr = brush.transform()
            tr = tr * t0
            brush = QG.QBrush(brush)
            brush.setTransform(tr)
        return pen, brush, sym

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
        pen, brush, symbol = self.get_pen_brush(xMap, yMap)
        painter.setRenderHint(QG.QPainter.Antialiasing)
        painter.setPen(pen)
        painter.setBrush(brush)
        points = self.transform_points(xMap, yMap)
        if self.ADDITIONNAL_POINTS:
            # Slice indexing is not supported by PySide6, so we convert the `QPolygonF`
            # object to a list before converting it back to a `QPolygonF` object:
            shape_points = QG.QPolygonF(list(points)[: -self.ADDITIONNAL_POINTS])
            other_points = QG.QPolygonF(list(points)[-self.ADDITIONNAL_POINTS :])
        else:
            shape_points = points
            other_points = []
        if self.closed:
            painter.drawPolygon(shape_points)
        else:
            painter.drawPolyline(shape_points)
        if symbol != QwtSymbol.NoSymbol:
            symbol.drawSymbols(painter, points)
        if self.LINK_ADDITIONNAL_POINTS and other_points:
            pen2 = painter.pen()
            pen2.setStyle(QC.Qt.DotLine)
            painter.setPen(pen2)
            painter.drawPolyline(other_points)

    def poly_hit_test(self, plot: BasePlot, ax: int, ay: int, pos: QPointF) -> tuple:
        """Return a tuple (distance, attach point, inside, other_object)

        Args:
            plot: Plot
            ax: X axis index
            ay: Y axis index
            pos: Position

        Returns:
            Tuple with four elements (distance, attach point, inside, other_object).
        """
        pos = QC.QPointF(pos)
        dist = sys.maxsize
        handle = -1
        Cx, Cy = pos.x(), pos.y()
        poly = QG.QPolygonF()
        pts = self.points
        for i in range(pts.shape[0]):
            # Compute distance to the line segment in canvas coordinates
            px = plot.transform(ax, pts[i, 0])
            py = plot.transform(ay, pts[i, 1])
            if i < pts.shape[0] - self.ADDITIONNAL_POINTS:
                poly.append(QC.QPointF(px, py))
            d = (Cx - px) ** 2 + (Cy - py) ** 2
            if d < dist:
                dist = d
                handle = i
        inside = poly.containsPoint(QC.QPointF(Cx, Cy), QC.Qt.OddEvenFill)
        return math.sqrt(dist), handle, inside, None

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
        return self.poly_hit_test(self.plot(), self.xAxis(), self.yAxis(), pos)

    def add_local_point(self, pos: tuple[float, float]) -> int:
        """Add a point in canvas coordinates (local coordinates)

        Args:
            pos: Position

        Returns:
            Handle of the added point
        """
        pt = canvas_to_axes(self, pos)
        return self.add_point(pt)

    def add_point(self, pt: tuple[float, float]) -> int:
        """Add a point in axis coordinates

        Args:
            pt: Position

        Returns:
            Handle of the added point
        """
        if self.points.size == 0:
            self.points = np.array([pt])
            return 0
        N, _ = self.points.shape
        self.points = np.resize(self.points, (N + 1, 2))
        self.points[N, :] = pt
        return N

    def del_point(self, handle: int) -> int:
        """Delete a point

        Args:
            handle: Handle

        Returns:
            Handle of the deleted point
        """
        self.points = np.delete(self.points, handle, 0)
        if handle < len(self.points):
            return handle
        else:
            return self.points.shape[0] - 1

    def move_point_to(
        self, handle: int, pos: tuple[float, float], ctrl: bool = False
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        self.points[handle, :] = pos

    def move_shape(self, old_pos: QC.QPointF, new_pos: QC.QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in axis coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        dx = new_pos[0] - old_pos[0]
        dy = new_pos[1] - old_pos[1]
        self.points += np.array([[dx, dy]])

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.shapeparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        self.update_item_parameters()
        itemparams.add("ShapeParam", self, self.shapeparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(self.shapeparam, itemparams.get("ShapeParam"), visible_only=True)
        self.shapeparam.update_item(self)


assert_interfaces_valid(PolygonShape)
