# -*- coding: utf-8 -*-
import warnings

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import update_dataset
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qwt import QwtPlotCurve, QwtScaleMap

from plotpy.config import _
from plotpy.utils.gui import assert_interfaces_valid
from plotpy.widgets.items.curve.base import CurveItem
from plotpy.widgets.styles.curve import CurveParam
from plotpy.widgets.styles.errorbar import ErrorBarParam


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
        super(ErrorBarCurveItem, self).__init__(curveparam)
        self._dx = None
        self._dy = None
        self._minmaxarrays = {}
        self.setIcon(get_icon("errorbar.png"))

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        super(ErrorBarCurveItem, self).serialize(writer)
        writer.write(self._dx, group_name="dXdata")
        writer.write(self._dy, group_name="dYdata")
        self.errorbarparam.update_param(self)
        writer.write(self.errorbarparam, group_name="errorbarparam")

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
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

    def unselect(self):
        """Unselect item"""
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

    def get_closest_coordinates(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        # Surcharge d'une méthode de base de CurveItem
        plot = self.plot()
        ax = self.xAxis()
        ay = self.yAxis()
        xc = plot.transform(ax, x)
        yc = plot.transform(ay, y)
        _distance, i, _inside, _other = self.hit_test(QC.QPointF(xc, yc))
        x0, y0 = self.plot().canvas2plotitem(self, xc, yc)
        x = self._x[i]
        y = self._y[i]
        xmin, xmax, ymin, ymax = self.get_minmax_arrays()
        if abs(y0 - y) > abs(y0 - ymin[i]):
            y = ymin[i]
        elif abs(y0 - y) > abs(y0 - ymax[i]):
            y = ymax[i]
        if abs(x0 - x) > abs(x0 - xmin[i]):
            x = xmin[i]
        elif abs(x0 - x) > abs(x0 - xmax[i]):
            x = xmax[i]
        return x, y

    def boundingRect(self):
        """Return the bounding rectangle of the data, error bars included"""
        xmin, xmax, ymin, ymax = self.get_minmax_arrays()
        if xmin is None or xmin.size == 0:
            return CurveItem.boundingRect(self)
        plot = self.plot()
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

    def update_item_parameters(self):
        """ """
        CurveItem.update_item_parameters(self)
        self.errorbarparam.update_param(self)

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        CurveItem.get_item_parameters(self, itemparams)
        itemparams.add("ErrorBarParam", self, self.errorbarparam)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        update_dataset(
            self.errorbarparam, itemparams.get("ErrorBarParam"), visible_only=True
        )
        CurveItem.set_item_parameters(self, itemparams)


assert_interfaces_valid(ErrorBarCurveItem)
