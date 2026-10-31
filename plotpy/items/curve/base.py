# -*- coding: utf-8 -*-

from __future__ import annotations

import math
import sys
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import numpy as np
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotCurve
from qwt.plot_curve import series_to_polyline

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

if TYPE_CHECKING:
    import guidata.io
    from qwt import QwtScaleMap

    from plotpy.interfaces import IItemType
    from plotpy.plot import BasePlot
    from plotpy.styles.base import ItemParameters


SELECTED_SYMBOL_PARAM = SymbolParam()
SELECTED_SYMBOL_PARAM.read_config(CONF, "plot", "selected_curve_symbol")
SELECTED_SYMBOL = SELECTED_SYMBOL_PARAM.build_symbol()


def minmax_downsampling_indices(data: np.ndarray, factor: int) -> np.ndarray:
    """Return the indices of the points kept by min/max downsampling

    The data is split into groups of ``2 * factor`` points, and the indices of the
    minimum and of the maximum of each group are kept, in increasing order, so that
    peaks are preserved with about as many points as when keeping one point out of
    ``factor``. The first and the last points are always kept. NaN values are
    ignored, except in groups containing only NaN values, which keep one of them so
    that the curve is still interrupted there.

    Args:
        data: Data to downsample (e.g. Y values of a curve)
        factor: Downsampling factor

    Returns:
        Sorted indices of the points to keep
    """
    data = np.asarray(data, dtype=float)
    size = data.size
    if factor <= 1 or size <= 2:
        return np.arange(size)
    bucket = 2 * factor
    nbuckets = -(-size // bucket)  # Last group may be incomplete
    padded = np.full(nbuckets * bucket, np.nan)
    padded[:size] = data
    groups = padded.reshape(nbuckets, bucket)
    isnan = np.isnan(groups)
    imin = np.argmin(np.where(isnan, np.inf, groups), axis=1)
    imax = np.argmax(np.where(isnan, -np.inf, groups), axis=1)
    offsets = np.arange(nbuckets) * bucket
    indices = np.concatenate(([0, size - 1], offsets + imin, offsets + imax))
    return np.unique(indices[indices < size])


def get_screen_pen(painter: QG.QPainter, pen: QG.QPen) -> QG.QPen:
    """Return the pen to draw a line on screen

    On high-DPI screens (e.g. with a 150 % scaling factor), a pen of width 1 is
    drawn wider than one device pixel, which makes Qt's raster engine take its
    much slower path for wide pens. When painting on screen (raster engine,
    without scaling transform), pens of width 1 or less are therefore made
    cosmetic, i.e. one device pixel wide. Printing and exporting, which use other
    paint engines or a scaling transform, are not affected.

    This behavior may be disabled with the ``curve/cosmetic_hairline`` option of
    the ``plot`` configuration section.

    Args:
        painter: Painter
        pen: Pen to draw with

    Returns:
        A cosmetic copy of the pen if applicable, the pen itself otherwise
    """
    if (
        pen.isCosmetic()
        or pen.widthF() > 1.0
        or painter.paintEngine().type() != QG.QPaintEngine.Raster
        or painter.worldTransform().isScaling()
        or not CONF.get("plot", "curve/cosmetic_hairline", True)
    ):
        return pen
    pen = QG.QPen(pen)
    pen.setCosmetic(True)
    return pen


#: Maximum width, in device pixels, of the lines drawn as several one-pixel strokes
#: (see :py:func:`get_thick_line_strokes`): wider lines are drawn with their pen
THICK_LINE_MAX_STROKES_WIDTH = 8.0


def get_thick_line_strokes(
    painter: QG.QPainter, pen: QG.QPen
) -> tuple[QG.QPen, list[tuple[float, float]]] | None:
    """Return the strokes drawing a thick line quickly on screen

    Qt's raster engine draws pens wider than one device pixel much more slowly
    than one-pixel pens (up to a hundred times slower for noisy curves, with
    antialiasing). When painting on screen (raster engine, without scaling
    transform), an opaque solid line wider than one device pixel may instead be
    drawn as several one-device-pixel strokes, offset horizontally and vertically
    by at most one device pixel from each other so as to cover the line width,
    whatever the line direction. Dash patterns are scaled by the line width, as
    for the original pen.

    The line is drawn with its pen when printing or exporting (other paint engines
    or scaling transform), for translucent colors (whose overlapping strokes would
    accumulate), for lines wider than :py:data:`THICK_LINE_MAX_STROKES_WIDTH`
    device pixels, or when the ``curve/fast_thick_lines`` option of the ``plot``
    configuration section is disabled.

    Args:
        painter: Painter
        pen: Pen to draw with

    Returns:
        A tuple (stroke pen, stroke offsets in logical coordinates), or None if
        the line must be drawn with the pen itself
    """
    if (
        pen.style() == QC.Qt.NoPen
        or pen.isCosmetic()
        or pen.brush().style() != QC.Qt.SolidPattern
        or pen.color().alpha() < 255
        or painter.paintEngine().type() != QG.QPaintEngine.Raster
        or painter.worldTransform().isScaling()
    ):
        return None
    ratio = painter.device().devicePixelRatioF()
    width = pen.widthF() * ratio
    if (
        width <= 1.0
        or width > THICK_LINE_MAX_STROKES_WIDTH
        or not CONF.get("plot", "curve/fast_thick_lines", True)
    ):
        return None
    stroke_pen = QG.QPen(pen)
    stroke_pen.setWidthF(1.0)
    stroke_pen.setCosmetic(True)
    if pen.style() != QC.Qt.SolidLine:
        stroke_pen.setDashPattern([length * width for length in pen.dashPattern()])
    extra = width - 1.0
    shifts = np.linspace(-extra / 2, extra / 2, math.ceil(extra) + 1) / ratio
    offsets = [(float(shift), 0.0) for shift in shifts]
    offsets += [(0.0, float(shift)) for shift in shifts if shift != 0.0]
    return stroke_pen, offsets


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
    _icon_name = "curve.svg"

    def __init__(self, curveparam: CurveParam | None = None) -> None:
        super().__init__()
        if curveparam is None:
            self.param = CurveParam(_("Curve"), icon="curve.svg")
        else:
            self.param = curveparam
        self.selected = False
        self.immutable = True  # set to false to allow moving points around
        self._x = None
        self._y = None
        self._dsamp_indices: np.ndarray | None = None
        self._dsamp_size = 0
        self._dsamp_frozen = False
        self.update_params()

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
                return 0.0
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

    def drawCurve(
        self,
        painter: QG.QPainter,
        style: int,
        xMap: QwtScaleMap,
        yMap: QwtScaleMap,
        canvasRect: QC.QRectF,
        from_: int,
        to: int,
    ) -> None:
        """Draw the line part (without symbols) of a curve interval

        Reimplemented to draw thin curves with a cosmetic pen on screen
        (see :py:func:`get_screen_pen`).

        Args:
            painter: Painter
            style: Curve style, see ``QwtPlotCurve.CurveStyle``
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Contents rectangle of the canvas
            from_: Index of the first point to be painted
            to: Index of the last point to be painted
        """
        pen = painter.pen()
        screen_pen = get_screen_pen(painter, pen)
        if screen_pen is not pen:
            painter.setPen(screen_pen)
        super().drawCurve(painter, style, xMap, yMap, canvasRect, from_, to)

    def drawLines(
        self,
        painter: QG.QPainter,
        xMap: QwtScaleMap,
        yMap: QwtScaleMap,
        canvasRect: QC.QRectF,
        from_: int,
        to: int,
    ) -> None:
        """Draw lines

        Reimplemented to draw thick lines quickly on screen, as several one-pixel
        strokes (see :py:func:`get_thick_line_strokes`).

        Args:
            painter: Painter
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Contents rectangle of the canvas
            from_: Index of the first point to be painted
            to: Index of the last point to be painted
        """
        strokes = get_thick_line_strokes(painter, painter.pen())
        if strokes is None:
            super().drawLines(painter, xMap, yMap, canvasRect, from_, to)
            return
        if from_ > to:
            return
        stroke_pen, offsets = strokes
        polyline = series_to_polyline(xMap, yMap, self.data(), from_, to)
        painter.save()
        painter.setPen(stroke_pen)
        for dx, dy in offsets:
            painter.translate(dx, dy)
            painter.drawPolyline(polyline)
            painter.translate(-dx, -dy)
        painter.restore()
        brush = self.brush()
        if brush.style() != QC.Qt.NoBrush and brush.color().alpha() > 0:
            self.fillCurve(painter, xMap, yMap, canvasRect, polyline)

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (ICurveItemType, ITrackableItemType, ISerializableType)

    def get_icon_name(self) -> str:
        """Return the icon name

        Returns:
            Icon name
        """
        return self._icon_name

    def set_icon_name(self, icon_name: str) -> None:
        """Set the icon name

        Args:
            icon_name: Icon name
        """
        self._icon_name = icon_name

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
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
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
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.param = CurveParam(_("Curve"), icon="curve.svg")
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
        return self._x, self._y

    def update_data(self) -> None:
        """Update curve data with current arrays."""
        if isinstance(self._x, np.ndarray) and isinstance(self._y, np.ndarray):
            self._setData(self._x, self._y)

    def dsamp(self, data: np.ndarray | None) -> np.ndarray | None:
        """Downsample data

        Args:
            data: Data to downsample (X, Y or error data of the curve)

        Returns:
            Downsampled data
        """
        if data is None or self._dsamp_indices is None:
            return data
        return data[self._dsamp_indices]

    def get_dsamp_indices(self) -> np.ndarray | None:
        """Return the indices of the points kept by downsampling

        Returns:
            Sorted indices of the points of the curve data that are drawn, or None if
            the curve is not downsampled
        """
        return self._dsamp_indices

    @contextmanager
    def frozen_downsampling(self) -> Generator[None, None, None]:
        """Keep the points kept by downsampling while the curve data is updated

        This is useful when editing curve points: with min/max downsampling, a
        point which is moved could otherwise be replaced by another point of its
        group. The points kept by downsampling are computed again when the number
        of points changes, or when the data is updated after this context.
        """
        self._dsamp_frozen = True
        try:
            yield
        finally:
            self._dsamp_frozen = False

    def __update_dsamp_indices(self, values: np.ndarray) -> None:
        """Update the indices of the points kept by downsampling

        Args:
            values: Curve values (Y data, or X data for vertical curves)
        """
        indices = self._dsamp_indices
        if (
            self._dsamp_frozen
            and indices is not None
            and self._dsamp_size == values.size
        ):
            return
        self._dsamp_size = values.size
        factor = self.param.dsamp_factor
        if not self.param.use_dsamp or factor <= 1:
            self._dsamp_indices = None
        elif self.param.dsamp_method == "stride":
            self._dsamp_indices = np.arange(0, values.size, factor)
        else:
            self._dsamp_indices = minmax_downsampling_indices(values, factor)

    def _setData(self, x: np.ndarray, y: np.ndarray) -> None:
        """Wrapper around QwtPlotCurve.setData() to handle downsampling"""
        values = x if self.orientation() == QC.Qt.Vertical else y
        self.__update_dsamp_indices(np.asarray(values))
        return super().setData(self.dsamp(x), self.dsamp(y))

    def set_data(self, x: np.ndarray, y: np.ndarray) -> None:
        """Set curve data

        Args:
            x: X data
            y: Y data
            decimated_data: Set to True if CurveItem X and Y arrays are already set and
             this method is called to update decimated data (i.e. only update 1/N value
             with N set in CurveItem.param.decimation).
        """
        self._x = np.asarray(x)
        self._y = np.asarray(y)
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
        indices = self._dsamp_indices
        if indices is None:
            final_index = int(i)
        else:
            # Index of the last point kept by downsampling at or before point `i`
            final_index = max(int(np.searchsorted(indices, i, side="right")) - 1, 0)
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

        # Use the plot's consolidated coordinate formatting method
        plot: BasePlot = self.plot()
        if plot is not None:
            # Format using the plot's consolidated coordinate formatting method
            return plot.format_coordinate_values(
                x, y, self.xAxis(), self.yAxis(), title
            )
        else:
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
        if i > 0 and np.fabs(self._x[i - 1] - xc) < np.fabs(self._x[i] - xc):
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
        indices = self._dsamp_indices
        if indices is not None:
            # The handle is the index of a point kept by downsampling
            if handle < 0 or handle >= indices.size:
                return
            handle = int(indices[handle])
        if handle < 0 or handle > self._x.shape[0]:
            return
        x, y = canvas_to_axes(self, pos)
        self._x[handle] = x
        self._y[handle] = y
        with self.frozen_downsampling():
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
