# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotCurve, QwtScaleMap

from plotpy.config import _
from plotpy.core.items.curve.base import CurveItem
from plotpy.core.styles.curve import CurveParam
from plotpy.core.styles.errorbar import ErrorBarParam

if TYPE_CHECKING:
    import guidata.dataset.io

    from plotpy.core.plot.base import BasePlot
    from plotpy.core.styles.base import ItemParameters


def _transform(map, v):
    return QwtScaleMap.transform(map, v)


def vmap(map, v):
    """Transform coordinates while handling RuntimeWarning
    that could be raised by NumPy when trying to transform
    a zero in logarithmic scale for example"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        output = np.vectorize(_transform)(map, v)
    return output


class ErrorBarCurveItem(CurveItem):
    """
    Construct an error-bar curve `plot item`
    with the parameters *errorbarparam*
    (see :py:class:`.styles.ErrorBarParam`)
    """

    def __init__(self, curveparam=None, errorbarparam=None):
        if errorbarparam is None:
            self.errorbarparam = ErrorBarParam(_("Error bars"), icon="errorbar.png")
        else:
            self.errorbarparam = errorbarparam
        self.errorPen: QG.QPen | None = None
        self.errorBrush: QG.QBrush | None = None
        self.errorCap: int | None = None
        self.errorOnTop: bool | None = None
        super(ErrorBarCurveItem, self).__init__(curveparam)
        self._dx = None
        self._dy = None
        self._minmaxarrays = {}
        self.setIcon(get_icon("errorbar.png"))

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
        super(ErrorBarCurveItem, self).serialize(writer)
        writer.write(self._dx, group_name="dXdata")
        writer.write(self._dy, group_name="dYdata")
        self.errorbarparam.update_param(self)
        writer.write(self.errorbarparam, group_name="errorbarparam")

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

    def get_data(self):
        """
        Return error-bar curve data: x, y, dx, dy

            * x: NumPy array
            * y: NumPy array
            * dx: float or NumPy array (non-constant error bars)
            * dy: float or NumPy array (non-constant error bars)
        """
        return self._x, self._y, self._dx, self._dy

    def set_data(self, x, y, dx=None, dy=None):
        """
        Set error-bar curve data:

            * x: NumPy array
            * y: NumPy array
            * dx: float or NumPy array (non-constant error bars)
            * dy: float or NumPy array (non-constant error bars)
        """
        CurveItem.set_data(self, x, y)
        if dx is not None:
            dx = np.array(dx, copy=False)
            if dx.size == 0:
                dx = None
        if dy is not None:
            dy = np.array(dy, copy=False)
            if dy.size == 0:
                dy = None
        self._dx = dx
        self._dy = dy
        self._minmaxarrays = {}

    def get_minmax_arrays(self, all_values=True):
        """

        :param all_values:
        :return:
        """
        if self._minmaxarrays.get(all_values) is None:
            x = self._x
            y = self._y
            dx = self._dx
            dy = self._dy
            if all_values:
                if dx is None:
                    xmin = xmax = x
                else:
                    xmin, xmax = x - dx, x + dx
                if dy is None:
                    ymin = ymax = y
                else:
                    ymin, ymax = y - dy, y + dy
                self._minmaxarrays.setdefault(all_values, (xmin, xmax, ymin, ymax))
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
                self._minmaxarrays.setdefault(
                    all_values, (x[isf], y[isf], xmin, xmax, ymin, ymax)
                )
        return self._minmaxarrays[all_values]

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
        xi = self._x[i]
        yi = self._y[i]
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

    def boundingRect(self):
        """Return the bounding rectangle of the data, error bars included"""
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

        xmin = np.float64(xmin)
        ymin = np.float64(ymin)
        xmax = np.float64(xmax)
        ymax = np.float64(ymax)

        return QC.QRectF(xmin, ymin, xmaxf.max() - xmin, ymaxf.max() - ymin)

    def draw(self, painter, xMap, yMap, canvasRect):
        """

        :param painter:
        :param xMap:
        :param yMap:
        :param canvasRect:
        :return:
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
        """ """
        self.errorbarparam.update_item(self)
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
