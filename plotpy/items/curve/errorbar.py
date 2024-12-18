# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotCurve, QwtScaleMap

from plotpy.config import _
from plotpy.items.curve.base import CurveItem
from plotpy.styles.curve import CurveParam
from plotpy.styles.errorbar import ErrorBarParam

if TYPE_CHECKING:
    import guidata.io

    from plotpy.plot.base import BasePlot
    from plotpy.styles.base import ItemParameters


def _transform(map: QwtScaleMap, v: float) -> float:
    """Transform coordinates"""
    return QwtScaleMap.transform(map, v)


def vmap(map: QwtScaleMap, v: np.ndarray) -> np.ndarray:
    """Transform coordinates while handling RuntimeWarning
    that could be raised by NumPy when trying to transform
    a zero in logarithmic scale for example

    Args:
        map: Scale map
        v: Array of coordinates

    Returns:
        Array of transformed coordinates
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        output = np.vectorize(_transform)(map, v)
    return output


class ErrorBarCurveItem(CurveItem):
    """Error-bar curve item

    Args:
        curveparam: Curve parameters
        errorbarparam: Error-bar parameters
    """

    _icon_name = "errorbar.png"

    def __init__(
        self,
        curveparam: CurveParam | None = None,
        errorbarparam: ErrorBarParam | None = None,
    ) -> None:
        if errorbarparam is None:
            self.errorbarparam = ErrorBarParam(_("Error bars"), icon="errorbar.png")
        else:
            self.errorbarparam = errorbarparam
        self.errorPen: QG.QPen | None = None
        self.errorBrush: QG.QBrush | None = None
        self.errorCap: int | None = None
        self.errorOnTop: bool | None = None
        super().__init__(curveparam)
        self._dx = None
        self._dy = None
        self.__minmaxarrays: dict[bool, tuple[float, float, float, float]] = {}

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        super().serialize(writer)
        writer.write(self._dx, group_name="dXdata")
        writer.write(self._dy, group_name="dYdata")
        self.errorbarparam.update_param(self)
        writer.write(self.errorbarparam, group_name="errorbarparam")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.param = CurveParam(_("Curve"), icon="curve.png")
        reader.read("curveparam", instance=self.param)
        self.errorbarparam = ErrorBarParam(_("Error bars"), icon="errorbar.png")
        reader.read("errorbarparam", instance=self.errorbarparam)
        x = reader.read(group_name="Xdata", func=reader.read_array)
        y = reader.read(group_name="Ydata", func=reader.read_array)
        dx = reader.read(group_name="dXdata", func=reader.read_array)
        dy = reader.read(group_name="dYdata", func=reader.read_array)
        self.set_data(x, y, dx, dy)
        self.setZ(reader.read("z"))
        self.update_params()

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        CurveItem.unselect(self)
        self.errorbarparam.update_item(self)

    def get_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get data

        Returns:
            Data as a tuple (x, y, dx, dy)
        """
        return self._x, self._y, self._dx, self._dy

    def set_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        dx: np.ndarray | float | None = None,
        dy: np.ndarray | float | None = None,
    ) -> None:
        """Set data

        Args:
            x: X data
            y: Y data
            dx: X error data
            dy: Y error data
        """
        CurveItem.set_data(self, x, y)
        if dx is not None:
            dx = np.asarray(dx)
            if dx.size == 0:
                dx = None
        if dy is not None:
            dy = np.asarray(dy)
            if dy.size == 0:
                dy = None
        self._dx = dx
        self._dy = dy
        self.__minmaxarrays = {}

    def get_minmax_arrays(
        self, all_values: bool = True
    ) -> tuple[
        np.ndarray[float], np.ndarray[float], np.ndarray[float], np.ndarray[float]
    ]:
        """Get min/max arrays

        Args:
            all_values: If True, return all values, else return only finite values

        Returns:
            Min/max arrays
        """
        if self.__minmaxarrays.get(all_values) is None:
            x = self.dsamp(self._x)
            y = self.dsamp(self._y)
            dx = self.dsamp(self._dx)
            dy = self.dsamp(self._dy)
            if all_values:
                if dx is None:
                    xmin = xmax = x
                else:
                    xmin, xmax = x - dx, x + dx
                if dy is None:
                    ymin = ymax = y
                else:
                    ymin, ymax = y - dy, y + dy
                self.__minmaxarrays.setdefault(all_values, (xmin, xmax, ymin, ymax))
            else:
                isf = np.logical_and(np.isfinite(x), np.isfinite(y))
                if dx is not None:
                    isf = np.logical_and(isf, np.isfinite(dx))
                if dy is not None:
                    isf = np.logical_and(isf, np.isfinite(dy))
                if dx is None:
                    xmin = xmax = x[isf]
                else:
                    xmin, xmax = x[isf] - dx[isf], x[isf] + dx[isf]
                if dy is None:
                    ymin = ymax = y[isf]
                else:
                    ymin, ymax = y[isf] - dy[isf], y[isf] + dy[isf]
                self.__minmaxarrays.setdefault(
                    all_values, (x[isf], y[isf], xmin, xmax, ymin, ymax)
                )
        return self.__minmaxarrays[all_values]

    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """
        # Surcharge d'une méthode de base de CurveItem
        plot: BasePlot = self.plot()
        xc = plot.transform(self.xAxis(), x)
        yc = plot.transform(self.yAxis(), y)
        _distance, i, _inside, _other = self.hit_test(QC.QPointF(xc, yc))
        xi = self.dsamp(self._x)[i]
        yi = self.dsamp(self._y)[i]
        xmin, xmax, ymin, ymax = self.get_minmax_arrays()
        if abs(y - y) > abs(y - ymin[i]):
            yi = ymin[i]
        elif abs(y - y) > abs(y - ymax[i]):
            yi = ymax[i]
        if abs(x - x) > abs(x - xmin[i]):
            xi = xmin[i]
        elif abs(x - x) > abs(x - xmax[i]):
            xi = xmax[i]
        return xi, yi

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the data

        Returns:
            Bounding rectangle of the data
        """
        xmin, xmax, ymin, ymax = self.get_minmax_arrays()
        if xmin is None or xmin.size == 0:
            return CurveItem.boundingRect(self)
        plot: BasePlot = self.plot()
        xminf, yminf = xmin[np.isfinite(xmin)], ymin[np.isfinite(ymin)]
        xmaxf, ymaxf = xmax[np.isfinite(xmax)], ymax[np.isfinite(ymax)]
        if plot is not None and "log" in (
            plot.get_axis_scale(self.xAxis()),
            plot.get_axis_scale(self.yAxis()),
        ):
            xmin = self._get_visible_axis_min(self.xAxis(), xminf)
            ymin = self._get_visible_axis_min(self.yAxis(), yminf)
        else:
            xmin = xminf.min()
            ymin = yminf.min()
        return QC.QRectF(xmin, ymin, xmaxf.max() - xmin, ymaxf.max() - ymin)

    def draw(
        self,
        painter: QG.QPainter,
        xMap: QwtScaleMap,
        yMap: QwtScaleMap,
        canvasRect: QC.QRectF,
    ) -> None:
        """Draw the item

        Args:
            painter: Painter
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Canvas rectangle
        """
        if self._x is None or self._x.size == 0:
            return
        x, y, xmin, xmax, ymin, ymax = self.get_minmax_arrays(all_values=False)
        tx = vmap(xMap, x)
        ty = vmap(yMap, y)
        RN = list(range(len(tx)))
        if self.errorOnTop:
            QwtPlotCurve.draw(self, painter, xMap, yMap, canvasRect)

        painter.save()
        painter.setPen(self.errorPen)
        cap = self.errorCap / 2.0

        if self._dx is not None and self.errorbarparam.mode == 0:
            txmin = vmap(xMap, xmin)
            txmax = vmap(xMap, xmax)
            # Classic error bars
            lines = []
            for i in RN:
                yi = ty[i]
                lines.append(QC.QLineF(txmin[i], yi, txmax[i], yi))
            painter.drawLines(lines)
            if cap > 0:
                lines = []
                for i in RN:
                    yi = ty[i]
                    lines.append(QC.QLineF(txmin[i], yi - cap, txmin[i], yi + cap))
                    lines.append(QC.QLineF(txmax[i], yi - cap, txmax[i], yi + cap))
            painter.drawLines(lines)

        if self._dy is not None:
            tymin = vmap(yMap, ymin)
            tymax = vmap(yMap, ymax)
            if self.errorbarparam.mode == 0:
                # Classic error bars
                lines = []
                for i in RN:
                    xi = tx[i]
                    lines.append(QC.QLineF(xi, tymin[i], xi, tymax[i]))
                painter.drawLines(lines)
                if cap > 0:
                    # Cap
                    lines = []
                    for i in RN:
                        xi = tx[i]
                        lines.append(QC.QLineF(xi - cap, tymin[i], xi + cap, tymin[i]))
                        lines.append(QC.QLineF(xi - cap, tymax[i], xi + cap, tymax[i]))
                painter.drawLines(lines)
            else:
                # Error area
                points = []
                rpoints = []
                for i in RN:
                    xi = tx[i]
                    points.append(QC.QPointF(xi, tymin[i]))
                    rpoints.append(QC.QPointF(xi, tymax[i]))
                points += reversed(rpoints)
                painter.setBrush(QG.QBrush(self.errorBrush))
                painter.drawPolygon(*points)

        painter.restore()

        if not self.errorOnTop:
            QwtPlotCurve.draw(self, painter, xMap, yMap, canvasRect)

    def update_params(self):
        """Update object properties from item parameters"""
        self.errorbarparam.update_item(self)

        # In case the downsampling factor/state has changed,
        # we need to invalidate cached data
        self.__minmaxarrays = {}

        CurveItem.update_params(self)

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        CurveItem.update_item_parameters(self)
        self.errorbarparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        CurveItem.get_item_parameters(self, itemparams)
        itemparams.add("ErrorBarParam", self, self.errorbarparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(
            self.errorbarparam, itemparams.get("ErrorBarParam"), visible_only=True
        )
        CurveItem.set_item_parameters(self, itemparams)


assert_interfaces_valid(ErrorBarCurveItem)
