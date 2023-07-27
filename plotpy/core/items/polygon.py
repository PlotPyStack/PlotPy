# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

from __future__ import annotations

from sys import maxsize
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset.datatypes import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotItem

from plotpy.config import _
from plotpy.core.interfaces.common import (
    IBasePlotItem,
    ICurveItemType,
    ISerializableType,
    ITrackableItemType,
)
from plotpy.core.items.curve.base import SELECTED_SYMBOL
from plotpy.core.styles.curve import CurveParam

if TYPE_CHECKING:
    from guidata.dataset.io import (
        HDF5Reader,
        HDF5Writer,
        INIReader,
        INIWriter,
        JSONReader,
        JSONWriter,
    )
    from qtpy.QtCore import QPointF

    from plotpy.core.interfaces.common import IItemType
    from plotpy.core.styles.base import ItemParameters


def simplify_poly(pts, off, scale, bounds):
    """Simplify a polygon by removing points outside the canvas"""
    ax, bx, ay, by = scale
    xm, ym, xM, yM = bounds
    a = np.array([[ax, ay]])
    b = np.array([[bx, by]])
    _pts = a * pts + b
    poly = []
    NP = off.shape[0]
    for i in range(off.shape[0]):
        i0 = off[i, 1]
        if i + 1 < NP:
            i1 = off[i + 1, 1]
        else:
            i1 = pts.shape[0]
        poly.append((_pts[i0:i1], i))
    return poly


class PolygonMapItem(QwtPlotItem):
    """
    Construct a curve `plot item` with the parameters *curveparam*
    (see :py:class:`.styles.CurveParam`)
    """

    __implements__ = (IBasePlotItem, ISerializableType)

    _readonly = False
    _private = False
    _can_select = False
    _can_resize = False
    _can_move = False
    _can_rotate = False

    def __init__(self, curveparam=None):
        super(PolygonMapItem, self).__init__()
        if curveparam is None:
            self.param = CurveParam(_("PolygonMap"), icon="curve.png")
        else:
            self.param = curveparam
        self.selected = False
        self.immutable = True  # set to false to allow moving points around
        self._pts = None  # Array of points Mx2
        self._n = None  # Array of polygon offsets/ends Nx1
        #                 (polygon k points are _pts[_n[k-1]:_n[k]])
        self._c = None  # Color of polygon Nx2 [border,background] as RGBA uint32
        self.update_params()
        self.setIcon(get_icon("curve.png"))

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (ICurveItemType, ITrackableItemType, ISerializableType)

    def can_select(self) -> bool:
        """
        Returns True if this item can be selected

        Returns:
            bool: True if item can be selected, False otherwise
        """
        return self._can_select

    def can_resize(self) -> bool:
        """
        Returns True if this item can be resized

        Returns:
            bool: True if item can be resized, False otherwise
        """
        return self._can_resize

    def can_rotate(self) -> bool:
        """
        Returns True if this item can be rotated

        Returns:
            bool: True if item can be rotated, False otherwise
        """
        return self._can_rotate

    def can_move(self) -> bool:
        """
        Returns True if this item can be moved

        Returns:
            bool: True if item can be moved, False otherwise
        """
        return self._can_move

    def set_selectable(self, state: bool) -> None:
        """Set item selectable state

        Args:
            state: True if item is selectable, False otherwise
        """
        self._can_select = state

    def set_resizable(self, state: bool) -> None:
        """Set item resizable state
        (or any action triggered when moving an handle, e.g. rotation)

        Args:
            state: True if item is resizable, False otherwise
        """
        self._can_resize = state

    def set_movable(self, state: bool) -> None:
        """Set item movable state

        Args:
            state: True if item is movable, False otherwise
        """
        self._can_move = state

    def set_rotatable(self, state: bool) -> None:
        """Set item rotatable state

        Args:
            state: True if item is rotatable, False otherwise
        """
        self._can_rotate = state

    def setPen(self, x):
        """

        :param x:
        """
        pass

    def setBrush(self, x):
        """

        :param x:
        """
        pass

    def setSymbol(self, x):
        """

        :param x:
        """
        pass

    def setCurveAttribute(self, x, y):
        """

        :param x:
        :param y:
        """
        pass

    def setStyle(self, x):
        """

        :param x:
        """
        pass

    def setCurveType(self, x):
        """

        :param x:
        """
        pass

    def setBaseline(self, x):
        """

        :param x:
        """
        pass

    def __reduce__(self):
        state = (self.param, self._pts, self._n, self._c, self.z())
        res = (PolygonMapItem, (), state)
        return res

    def __setstate__(self, state):
        param, pts, n, c, z = state
        self.param = param
        self.set_data(pts, n, c)
        self.setZ(z)
        self.update_params()

    def serialize(self, writer: HDF5Writer | INIWriter | JSONWriter) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        writer.write(self._pts, group_name="Pdata")
        writer.write(self._n, group_name="Ndata")
        writer.write(self._c, group_name="Cdata")
        writer.write(self.z(), group_name="z")
        self.param.update_param(self)
        writer.write(self.param, group_name="curveparam")

    def deserialize(self, reader: HDF5Reader | INIReader | JSONReader) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        pts = reader.read(group_name="Pdata", func=reader.read_array)
        n = reader.read(group_name="Ndata", func=reader.read_array)
        c = reader.read(group_name="Cdata", func=reader.read_array)
        self.set_data(pts, n, c)
        self.setZ(reader.read("z"))
        self.param = CurveParam(_("PolygonMap"), icon="curve.png")
        reader.read("curveparam", instance=self.param)
        self.update_params()

    def set_readonly(self, state: bool) -> None:
        """Set object readonly state

        Args:
            state: True if object is readonly, False otherwise
        """
        self._readonly = state

    def is_readonly(self) -> bool:
        """Return object readonly state

        Returns:
            bool: True if object is readonly, False otherwise
        """
        return self._readonly

    def set_private(self, state: bool) -> None:
        """Set object as private

        Args:
            state: True if object is private, False otherwise
        """
        self._private = state

    def is_private(self) -> bool:
        """Return True if object is private

        Returns:
            bool: True if object is private, False otherwise
        """
        return self._private

    def invalidate_plot(self):
        """ """
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def select(self) -> None:
        """
        Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        self.selected = True
        self.setSymbol(SELECTED_SYMBOL)
        self.invalidate_plot()

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        self.selected = False
        # Restoring initial curve parameters:
        self.param.update_item(self)
        self.invalidate_plot()

    def get_data(self):
        """Return curve data x, y (NumPy arrays)"""
        return self._pts, self._n, self._c

    def set_data(self, pts, n, c):
        """
        Set curve data:
            * x: NumPy array
            * y: NumPy array
        """
        self._pts = np.array(pts, copy=False)
        self._n = np.array(n, copy=False)
        self._c = np.array(c, copy=False)
        xmin, ymin = self._pts.min(axis=0)
        xmax, ymax = self._pts.max(axis=0)
        self.bounds = QC.QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def is_empty(self):
        """Return True if item data is empty"""
        return self._pts is None or self._pts.size == 0

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
        if self.is_empty():
            return maxsize, 0, False, None
        # TODO: Implement PolygonMapItem.hit_test
        return maxsize, 0, False, None

    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """
        # TODO: Implement PolygonMapItem.get_closest_coordinates
        return x, y

    def get_coordinates_label(self, x: float, y: float) -> str:
        """
        Get the coordinates label for the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            str: Coordinates label
        """
        title = self.title().text()
        return f"{title}:<br>x = {x:f}<br>y = {y:f}"

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """

    def move_with_selection(self, delta_x, delta_y):
        """

        :param delta_x:
        :param delta_y:
        """

    def update_params(self):
        """ """
        self.param.update_item(self)
        if self.selected:
            self.select()

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.param.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        itemparams.add("CurveParam", self, self.param)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(self.param, itemparams.get("CurveParam"), visible_only=True)
        self.update_params()

    def draw(self, painter, xMap, yMap, canvasRect):
        """

        :param painter:
        :param xMap:
        :param yMap:
        :param canvasRect:
        """
        # from time import time
        p1x = xMap.p1()
        s1x = xMap.s1()
        ax = (xMap.p2() - p1x) / (xMap.s2() - s1x)
        p1y = yMap.p1()
        s1y = yMap.s1()
        ay = (yMap.p2() - p1y) / (yMap.s2() - s1y)
        bx, by = p1x - s1x * ax, p1y - s1y * ay
        _c = self._c
        _n = self._n
        fgcol = QG.QColor()
        bgcol = QG.QColor()
        # t0 = time()
        polygons = simplify_poly(
            self._pts, _n, (ax, bx, ay, by), canvasRect.getCoords()
        )
        # t1 = time()
        # print len(polygons), t1-t0
        # t2 = time()
        for poly, num in polygons:
            points = []
            for i in range(poly.shape[0]):
                points.append(QC.QPointF(poly[i, 0], poly[i, 1]))
            pg = QG.QPolygonF(points)
            fgcol.setRgba(int(_c[num, 0]))
            bgcol.setRgba(int(_c[num, 1]))
            painter.setPen(QG.QPen(fgcol))
            painter.setBrush(QG.QBrush(bgcol))
            painter.drawPolygon(pg)
        # print "poly:", time()-t2

    def boundingRect(self):
        """

        :return:
        """
        return self.bounds


assert_interfaces_valid(PolygonMapItem)
