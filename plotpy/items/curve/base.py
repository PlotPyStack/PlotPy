# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qwt import QwtPlotCurve

from plotpy.config import CONF, _
from plotpy.coords import canvas_to_axes
from plotpy.interfaces import (
    IBasePlotItem,
    ICurveItemType,
    ISerializableType,
    ITrackableItemType,
)
from plotpy.styles.base import SymbolParam
from plotpy.styles.curve import CurveParam

if TYPE_CHECKING:  # pragma: no cover
    import guidata.dataset.io

    from plotpy.interfaces import IItemType
    from plotpy.styles.base import ItemParameters


SELECTED_SYMBOL_PARAM = SymbolParam()
SELECTED_SYMBOL_PARAM.read_config(CONF, "plot", "selected_curve_symbol")
SELECTED_SYMBOL = SELECTED_SYMBOL_PARAM.build_symbol()


def seg_dist(P: QC.QPointF, P0: QC.QPointF, P1: QC.QPointF) -> float:
    """Compute distance between point P and segment (P0, P1)

    Args:
        P: QPointF instance
        P0: QPointF instance
        P1: QPointF instance

    Returns:
        Distance between point P and segment (P0, P1)

    .. note::

        If P orthogonal projection on (P0, P1) is outside segment bounds, return
        either distance to P0 or to P1 (the closest one)
    """
    u = QC.QLineF(P0, P).length()
    if P0 == P1:
        return u
    else:
        angle = QC.QLineF(P0, P).angleTo(QC.QLineF(P0, P1)) * np.pi / 180
        projection = u * np.cos(angle)
        if projection > QC.QLineF(P0, P1).length():
            return QC.QLineF(P1, P).length()
        elif projection < 0:
            return QC.QLineF(P0, P).length()
        else:
            return abs(u * np.sin(angle))


def seg_dist_v(
    P: tuple[float, float], X0: float, Y0: float, X1: float, Y1: float
) -> tuple[int, float]:
    """Compute distance between point P and segment (X0, Y0), (X1, Y1)

    Args:
        P: Point
        X0: X coordinate of first point
        Y0: Y coordinate of first point
        X1: X coordinate of second point
        Y1: Y coordinate of second point

    Returns:
        tuple: Tuple with two elements: (index, distance)

    .. note::

        This is the vectorized version of ``seg_dist`` function
    """
    V = np.zeros((X0.shape[0], 2), float)
    PP = np.zeros((X0.shape[0], 2), float)
    PP[:, 0] = X0
    PP[:, 1] = Y0
    V[:, 0] = X1 - X0
    V[:, 1] = Y1 - Y0
    dP = np.array(P).reshape(1, 2) - PP
    norm2V = (V**2).sum(axis=1)
    nV = np.sqrt(norm2V).clip(1e-12)  # clip: avoid division by zero
    w2 = V / nV[:, np.newaxis]
    w = np.array([-w2[:, 1], w2[:, 0]]).T
    distances = np.fabs((dP * w).sum(axis=1))
    ix = distances.argmin()
    return ix, distances[ix]


class CurveItem(QwtPlotCurve):
    """Curve item

    Args:
        curveparam: Curve parameters
    """

    __implements__ = (IBasePlotItem, ISerializableType)

    _readonly = False
    _private = False

    def __init__(self, curveparam: CurveParam | None = None) -> None:
        super().__init__()
        if curveparam is None:
            self.param = CurveParam(_("Curve"), icon="curve.png")
        else:
            self.param = curveparam
        self.selected = False
        self.immutable = True  # set to false to allow moving points around
        self._x = None
        self._y = None
        self.update_params()
        self.setIcon(get_icon("curve.png"))

    def _get_visible_axis_min(self, axis_id: int, axis_data: np.ndarray) -> float:
        """Return axis minimum excluding zero and negative values when
        corresponding plot axis scale is logarithmic

        Args:
            axis_id: Axis ID
            axis_data: Axis data

        Returns:
            Axis minimum
        """
        if self.plot().get_axis_scale(axis_id) == "log":
            if len(axis_data[axis_data > 0]) == 0:
                return 0
            else:
                return axis_data[axis_data > 0].min()
        else:
            return axis_data.min()

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the data

        Returns:
            Bounding rectangle of the data
        """
        plot = self.plot()
        if plot is not None and "log" in (
            plot.get_axis_scale(self.xAxis()),
            plot.get_axis_scale(self.yAxis()),
        ):
            x, y = self._x, self._y
            xf, yf = x[np.isfinite(x)], y[np.isfinite(y)]
            xmin = self._get_visible_axis_min(self.xAxis(), xf)
            ymin = self._get_visible_axis_min(self.yAxis(), yf)
            return QC.QRectF(xmin, ymin, xf.max() - xmin, yf.max() - ymin)
        else:
            return QwtPlotCurve.boundingRect(self)

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (ICurveItemType, ITrackableItemType, ISerializableType)

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

    def can_select(self) -> bool:
        """
        Returns True if this item can be selected

        Returns:
            bool: True if item can be selected, False otherwise
        """
        return True

    def can_resize(self) -> bool:
        """
        Returns True if this item can be resized

        Returns:
            bool: True if item can be resized, False otherwise
        """
        return False

    def can_rotate(self) -> bool:
        """
        Returns True if this item can be rotated

        Returns:
            bool: True if item can be rotated, False otherwise
        """
        return False

    def can_move(self) -> bool:
        """
        Returns True if this item can be moved

        Returns:
            bool: True if item can be moved, False otherwise
        """
        return False

    def __reduce__(self) -> tuple[type, tuple, tuple]:
        """Return state information for pickling"""
        state = (self.param, self._x, self._y, self.z())
        res = (CurveItem, (), state)
        return res

    def __setstate__(self, state: tuple) -> None:
        """Restore state information for unpickling"""
        param, x, y, z = state
        self.param = param
        self.set_data(x, y)
        self.setZ(z)
        self.update_params()

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
        writer.write(self._x, group_name="Xdata")
        writer.write(self._y, group_name="Ydata")
        writer.write(self.z(), group_name="z")
        self.param.update_param(self)
        writer.write(self.param, group_name="curveparam")

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
        self.param = CurveParam(_("Curve"), icon="curve.png")
        reader.read("curveparam", instance=self.param)
        x = reader.read(group_name="Xdata", func=reader.read_array)
        y = reader.read(group_name="Ydata", func=reader.read_array)
        self.set_data(x, y)
        self.setZ(reader.read("z"))
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

    def invalidate_plot(self) -> None:
        """Invalidate the plot to force a redraw"""
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def select(self) -> None:
        """Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        self.selected = True
        plot = self.plot()
        if plot is not None:
            plot.blockSignals(True)
        self.setSymbol(SELECTED_SYMBOL)
        if plot is not None:
            plot.blockSignals(False)
        self.invalidate_plot()

    def unselect(self) -> None:
        """Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        self.selected = False
        # Restoring initial curve parameters:
        self.param.update_item(self)
        self.invalidate_plot()

    def get_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Return curve data x, y (NumPy arrays)

        Returns:
            tuple: Tuple with two elements: x and y NumPy arrays
        """
        assert isinstance(self._x, np.ndarray) and isinstance(self._y, np.ndarray)
        # if ignore_decimation:
        return self._x, self._y
        # return (
        #     self._x[:: self.param.decimation],
        #     self._y[:: self.param.decimation],
        # )

    def update_data(self):
        if isinstance(self._x, np.ndarray) and isinstance(self._y, np.ndarray):
            self._setData(self._x, self._y)

    def _setData(self, x: np.ndarray, y: np.ndarray):
        if not self.param.use_downsampling or self.param.downsampling_factor == 1:
            return super().setData(x, y)
        return super().setData(
            x[:: self.param.downsampling_factor],
            y[:: self.param.downsampling_factor],
        )

    def set_data(self, x: np.ndarray, y: np.ndarray) -> None:
        """Set curve data

        Args:
            x: X data
            y: Y data
            decimated_data: Set to True if CurveItem X and Y arrays are already set and
            this method is called to update decimated data (i.e. only update 1/N value
            with N set in CurveItem.param.decimation).
        """
        # if (
        #     isinstance(self._x, np.ndarray)
        #     and isinstance(self._y, np.ndarray)
        #     # and decimated_data > 1
        # ):
        #     self._x[:: self.param.decimation] = np.array(x, copy=False)
        #     self._y[:: self.param.decimation] = np.array(y, copy=False)
        # else:
        self._x = np.array(x, copy=False)
        self._y = np.array(y, copy=False)
        self._setData(self._x, self._y)

    def is_empty(self) -> bool:
        """Return True if the item is empty

        Returns:
            True if the item is empty, False otherwise
        """
        return self._x is None or self._y is None or self._y.size == 0

    def hit_test(self, pos: QC.QPointF) -> tuple[float, float, bool, None]:
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
            return sys.maxsize, 0, False, None
        plot = self.plot()
        ax = self.xAxis()
        ay = self.yAxis()
        px = plot.invTransform(ax, pos.x())
        py = plot.invTransform(ay, pos.y())
        # On cherche les 4 points qui sont les plus proches en X et en Y
        # avant et après ie tels que p1x < x < p2x et p3y < y < p4y
        tmpx = self._x - px
        tmpy = self._y - py
        if np.count_nonzero(tmpx) != len(tmpx) or np.count_nonzero(tmpy) != len(tmpy):
            # Avoid dividing by zero warning when computing dx or dy
            return sys.maxsize, 0, False, None
        dx = 1 / tmpx
        dy = 1 / tmpy
        i0 = dx.argmin()
        i1 = dx.argmax()
        i2 = dy.argmin()
        i3 = dy.argmax()
        t = np.array((i0, i1, i2, i3))
        t2 = (t + 1).clip(0, self._x.shape[0] - 1)
        i, _d = seg_dist_v((px, py), self._x[t], self._y[t], self._x[t2], self._y[t2])
        i = t[i]
        # Recalcule la distance dans le répère du widget
        p0x = plot.transform(ax, self._x[i])
        p0y = plot.transform(ay, self._y[i])
        if i + 1 >= self._x.shape[0]:
            p1x = p0x
            p1y = p0y
        else:
            p1x = plot.transform(ax, self._x[i + 1])
            p1y = plot.transform(ay, self._y[i + 1])
        distance = seg_dist(QC.QPointF(pos), QC.QPointF(p0x, p0y), QC.QPointF(p1x, p1y))
        final_index = i // (
            int(not self.param.use_downsampling) or self.param.downsampling_factor
        )
        return distance, final_index, False, None

    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """
        plot = self.plot()
        ax = self.xAxis()
        ay = self.yAxis()
        xc = plot.transform(ax, x)
        yc = plot.transform(ay, y)
        _distance, i, _inside, _other = self.hit_test(QC.QPointF(xc, yc))
        point = self.sample(i)
        return point.x(), point.y()

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
        return f"{title}:<br>x = {x:g}<br>y = {y:g}"

    def get_closest_x(self, xc: float) -> tuple[float, float]:
        """
        Get the closest point to the given x coordinate

        Args:
            xc: X coordinate

        Returns:
            tuple[float, float]: Closest point coordinates
        """
        # We assume X is sorted, otherwise we'd need :
        # argmin(abs(x-xc))
        i = self._x.searchsorted(xc)
        if i > 0:
            if np.fabs(self._x[i - 1] - xc) < np.fabs(self._x[i] - xc):
                return self._x[i - 1], self._y[i - 1]
        return self._x[i], self._y[i]

    def move_local_point_to(
        self, handle: int, pos: QC.QPointF, ctrl: bool = None
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        if self.immutable:
            return
        if handle < 0 or handle > self._x.shape[0]:
            return
        x, y = canvas_to_axes(self, pos)
        self._x[handle] = x
        self._y[handle] = y
        self._setData(self._x, self._y)
        self.plot().replot()

    def move_local_shape(self, old_pos: QC.QPointF, new_pos: QC.QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        nx, ny = canvas_to_axes(self, new_pos)
        ox, oy = canvas_to_axes(self, old_pos)
        self._x += nx - ox
        self._y += ny - oy
        self._setData(self._x, self._y)

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        self._x += delta_x
        self._y += delta_y
        self._setData(self._x, self._y)

    def update_params(self):
        """Update item parameters (object properties) from datasets"""
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


assert_interfaces_valid(CurveItem)
