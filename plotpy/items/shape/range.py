# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import guidata.io
import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.config import CONF, _
from plotpy.coords import canvas_to_axes
from plotpy.items.shape.base import AbstractShape
from plotpy.styles.shape import RangeShapeParam

if TYPE_CHECKING:
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QPainter
    from qwt import QwtSymbol

    from plotpy.plot import BasePlot
    from plotpy.styles.base import ItemParameters


class XRangeSelection(AbstractShape):
    """X range selection shape

    Args:
        _min: Minimum value
        _max: Maximum value
        shapeparam: Shape parameters
    """

    _icon_name = "xrange.png"

    def __init__(
        self,
        _min: float | None = None,
        _max: float | None = None,
        shapeparam: RangeShapeParam | None = None,
    ) -> None:
        super().__init__()
        self._min = _min
        self._max = _max
        if shapeparam is None:
            self.shapeparam = RangeShapeParam(_("Range"), icon="xrange.png")
            self.shapeparam.read_config(CONF, "histogram", "range")
        else:
            self.shapeparam: RangeShapeParam = shapeparam
        self.pen = None
        self.sel_pen = None
        self.brush = None
        self.handle = None
        self.symbol = None
        self.sel_symbol = None
        if self._min is not None and self._max is not None:
            self.shapeparam.update_item(self)  # creates all the above QObjects

    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        self.shapeparam.read_config(CONF, section, option)
        self.shapeparam.update_item(self)

    def __reduce__(self) -> tuple[type, tuple, tuple]:
        """Return state information for pickling"""
        self.shapeparam.update_param(self)
        state = (self.shapeparam, self._min, self._max)
        return (XRangeSelection, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Restore state information from pickling"""
        self.shapeparam, self._min, self._max = state
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
        writer.write(self._min, group_name="min")
        writer.write(self._max, group_name="max")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self._min = reader.read("min")
        self._max = reader.read("max")
        self.shapeparam = RangeShapeParam(_("Range"), icon="xrange.png")
        reader.read("shapeparam", instance=self.shapeparam)
        self.shapeparam.update_item(self)

    def get_handles_pos(self) -> tuple[float, float, float]:
        """Return the handles position

        Returns:
            Tuple with three elements (x0, x1, y).
        """
        plot = self.plot()
        rct = plot.canvas().contentsRect()
        y = rct.center().y()
        x0 = plot.transform(self.xAxis(), self._min)
        x1 = plot.transform(self.xAxis(), self._max)
        return x0, x1, y

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
        plot: BasePlot = self.plot()
        if not plot:
            return
        if self.selected:
            pen: QG.QPen = self.sel_pen
            sym: QwtSymbol = self.sel_symbol
        else:
            pen: QG.QPen = self.pen
            sym: QwtSymbol = self.symbol

        rct = QC.QRectF(plot.canvas().contentsRect())
        rct.setLeft(xMap.transform(self._min))
        rct.setRight(xMap.transform(self._max))

        painter.fillRect(rct, self.brush)
        painter.setPen(pen)
        painter.drawLine(rct.topLeft(), rct.bottomLeft())
        painter.drawLine(rct.topRight(), rct.bottomRight())

        dash = QG.QPen(pen)
        dash.setStyle(QC.Qt.DashLine)
        dash.setWidth(1)
        painter.setPen(dash)
        cx = rct.center().x()
        painter.drawLine(QC.QPointF(cx, rct.top()), QC.QPointF(cx, rct.bottom()))

        painter.setPen(pen)
        x0, x1, y = self.get_handles_pos()
        sym.drawSymbol(painter, QC.QPointF(x0, y))
        sym.drawSymbol(painter, QC.QPointF(x1, y))

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
        x, _y = pos.x(), pos.y()
        x0, x1, _yp = self.get_handles_pos()
        d0 = math.fabs(x0 - x)
        d1 = math.fabs(x1 - x)
        d2 = math.fabs((x0 + x1) / 2 - x)
        z = np.array([d0, d1, d2])
        dist = z.min()
        handle = z.argmin()
        inside = bool(x0 < x < x1)
        return dist, handle, inside, None

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        x, _y = canvas_to_axes(self, pos)
        self.move_point_to(handle, (x, 0), ctrl)

    def move_point_to(
        self, handle: int, pos: tuple[float, float], ctrl: bool = False
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        val, _ = pos
        if handle == 0:
            self._min = val
        elif handle == 1:
            self._max = val
        elif handle == 2:
            move = val - (self._max + self._min) / 2
            self._min += move
            self._max += move

        self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)
        # self.plot().replot()

    def get_range(self) -> tuple[float, float]:
        """Return the range

        Returns:
            Tuple with two elements (min, max).
        """
        return self._min, self._max

    def set_range(self, _min: float, _max: float, dosignal: bool = True) -> None:
        """Set the range

        Args:
            _min: Minimum value
            _max: Maximum value
            dosignal: True to emit the SIG_RANGE_CHANGED signal
        """
        self._min = _min
        self._max = _max
        if dosignal:
            self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)

    def move_shape(
        self, old_pos: tuple[float, float], new_pos: tuple[float, float]
    ) -> None:
        """Translate the shape such that old_pos becomes new_pos in axis coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        dx = new_pos[0] - old_pos[0]
        self._min += dx
        self._max += dx
        self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)
        self.plot().replot()

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
        self.sel_brush = QG.QBrush(self.brush)

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the shape

        Returns:
            Bounding rectangle of the shape
        """
        return QC.QRectF(self._min, 0, self._max - self._min, 0)


assert_interfaces_valid(XRangeSelection)
