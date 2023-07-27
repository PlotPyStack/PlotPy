# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.config import CONF, _
from plotpy.core.coords import canvas_to_axes
from plotpy.core.items.shapes.base import AbstractShape
from plotpy.core.styles.shape import RangeShapeParam

if TYPE_CHECKING:
    from qtpy.QtCore import QPointF

    from plotpy.core.styles.base import ItemParameters


class XRangeSelection(AbstractShape):
    """ """

    def __init__(self, _min, _max, shapeparam=None):
        super(XRangeSelection, self).__init__()
        self._min = _min
        self._max = _max
        if shapeparam is None:
            self.shapeparam = RangeShapeParam(_("Range"), icon="xrange.png")
            self.shapeparam.read_config(CONF, "histogram", "range")
        else:
            self.shapeparam = shapeparam
        self.pen = None
        self.sel_pen = None
        self.brush = None
        self.handle = None
        self.symbol = None
        self.sel_symbol = None
        self.shapeparam.update_range(self)  # creates all the above QObjects
        self.setIcon(get_icon("xrange.png"))

    def get_handles_pos(self):
        """

        :return:
        """
        plot = self.plot()
        rct = plot.canvas().contentsRect()
        y = rct.center().y()
        x0 = plot.transform(self.xAxis(), self._min)
        x1 = plot.transform(self.xAxis(), self._max)
        return x0, x1, y

    def draw(self, painter, xMap, yMap, canvasRect):
        """

        :param painter:
        :param xMap:
        :param yMap:
        :param canvasRect:
        :return:
        """
        plot = self.plot()
        if not plot:
            return
        if self.selected:
            pen = self.sel_pen
            sym = self.sel_symbol
        else:
            pen = self.pen
            sym = self.symbol

        rct = plot.canvas().contentsRect()
        rct2 = QC.QRectF(rct)
        rct2.setLeft(xMap.transform(self._min))
        rct2.setRight(xMap.transform(self._max))

        painter.fillRect(rct2, self.brush)
        painter.setPen(pen)
        painter.drawLine(rct2.topLeft(), rct2.bottomLeft())
        painter.drawLine(rct2.topRight(), rct2.bottomRight())
        dash = QG.QPen(pen)
        dash.setStyle(QC.Qt.DashLine)
        dash.setWidth(1)
        painter.setPen(dash)

        center_x = int(rct2.center().x())
        top = int(rct2.top())
        bottom = int(rct2.bottom())
        painter.drawLine(center_x, top, center_x, bottom)

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
        self.move_point_to(handle, (x, 0))

    def move_point_to(self, hnd, pos, ctrl=None):
        """

        :param hnd:
        :param pos:
        :param ctrl:
        """
        val, _ = pos
        if hnd == 0:
            self._min = val
        elif hnd == 1:
            self._max = val
        elif hnd == 2:
            move = val - (self._max + self._min) / 2
            self._min += move
            self._max += move

        self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)
        # self.plot().replot()

    def get_range(self):
        """

        :return:
        """
        return self._min, self._max

    def set_range(self, _min, _max, dosignal=True):
        """

        :param _min:
        :param _max:
        :param dosignal:
        """
        self._min = _min
        self._max = _max
        if dosignal:
            self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)

    def move_shape(self, old_pos, new_pos):
        """

        :param old_pos:
        :param new_pos:
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
        self.shapeparam.update_range(self)
        self.sel_brush = QG.QBrush(self.brush)

    def boundingRect(self):
        """

        :return:
        """
        return QC.QRectF(self._min, 0, self._max - self._min, 0)


assert_interfaces_valid(XRangeSelection)
