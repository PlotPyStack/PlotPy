# -*- coding: utf-8 -*-
import sys

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import assert_interfaces_valid, update_dataset
from qtpy import QtCore as QC
from qwt import QwtPlotCurve

from plotpy.config import CONF, _
from plotpy.core.interfaces.common import (
    IBasePlotItem,
    ICurveItemType,
    ISerializableType,
    ITrackableItemType,
)
from plotpy.core.items.utils import canvas_to_axes
from plotpy.core.styles.base import SymbolParam
from plotpy.core.styles.curve import CurveParam

SELECTED_SYMBOL_PARAM = SymbolParam()
SELECTED_SYMBOL_PARAM.read_config(CONF, "plot", "selected_curve_symbol")
SELECTED_SYMBOL = SELECTED_SYMBOL_PARAM.build_symbol()


def seg_dist(P, P0, P1):
    """
    Return distance between point P and segment (P0, P1)
    If P orthogonal projection on (P0, P1) is outside segment bounds, return
    either distance to P0 or to P1 (the closest one)
    P, P0, P1: QPointF instances
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


def norm2(v):
    """

    :param v:
    :return:
    """
    return (v**2).sum(axis=1)


def seg_dist_v(P, X0, Y0, X1, Y1):
    """Version vectorielle de seg_dist"""
    V = np.zeros((X0.shape[0], 2), float)
    PP = np.zeros((X0.shape[0], 2), float)
    PP[:, 0] = X0
    PP[:, 1] = Y0
    V[:, 0] = X1 - X0
    V[:, 1] = Y1 - Y0
    dP = np.array(P).reshape(1, 2) - PP
    nV = np.sqrt(norm2(V)).clip(1e-12)  # clip: avoid division by zero
    w2 = V / nV[:, np.newaxis]
    w = np.array([-w2[:, 1], w2[:, 0]]).T
    distances = np.fabs((dP * w).sum(axis=1))
    ix = distances.argmin()
    return ix, distances[ix]


class CurveItem(QwtPlotCurve):
    """
    Construct a curve `plot item` with the parameters *curveparam*
    (see :py:class:`.styles.CurveParam`)
    """

    __implements__ = (IBasePlotItem, ISerializableType)

    _readonly = False
    _private = False

    def __init__(self, curveparam=None):
        super(CurveItem, self).__init__()
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

    def _get_visible_axis_min(self, axis_id, axis_data):
        """Return axis minimum excluding zero and negative values when
        corresponding plot axis scale is logarithmic"""
        if self.plot().get_axis_scale(axis_id) == "log":
            if len(axis_data[axis_data > 0]) == 0:
                return 0
            else:
                return axis_data[axis_data > 0].min()
        else:
            return axis_data.min()

    def boundingRect(self):
        """Return the bounding rectangle of the data"""
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

    def types(self):
        """

        :return:
        """
        return (ICurveItemType, ITrackableItemType, ISerializableType)

    def set_selectable(self, state):
        """Set item selectable state"""
        self._can_select = state

    def set_resizable(self, state):
        """Set item resizable state
        (or any action triggered when moving an handle, e.g. rotation)"""
        self._can_resize = state

    def set_movable(self, state):
        """Set item movable state"""
        self._can_move = state

    def set_rotatable(self, state):
        """Set item rotatable state"""
        self._can_rotate = state

    def can_select(self):
        """

        :return:
        """
        return True

    def can_resize(self):
        """

        :return:
        """
        return False

    def can_rotate(self):
        """

        :return:
        """
        return False

    def can_move(self):
        """

        :return:
        """
        return False

    def __reduce__(self):
        state = (self.param, self._x, self._y, self.z())
        res = (CurveItem, (), state)
        return res

    def __setstate__(self, state):
        param, x, y, z = state
        self.param = param
        self.set_data(x, y)
        self.setZ(z)
        self.update_params()

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        writer.write(self._x, group_name="Xdata")
        writer.write(self._y, group_name="Ydata")
        writer.write(self.z(), group_name="z")
        self.param.update_param(self)
        writer.write(self.param, group_name="curveparam")

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
        self.param = CurveParam(_("Curve"), icon="curve.png")
        reader.read("curveparam", instance=self.param)
        x = reader.read(group_name="Xdata", func=reader.read_array)
        y = reader.read(group_name="Ydata", func=reader.read_array)
        self.set_data(x, y)
        self.setZ(reader.read("z"))
        self.update_params()

    def set_readonly(self, state):
        """Set object readonly state"""
        self._readonly = state

    def is_readonly(self):
        """Return object readonly state"""
        return self._readonly

    def set_private(self, state):
        """Set object as private"""
        self._private = state

    def is_private(self):
        """Return True if object is private"""
        return self._private

    def invalidate_plot(self):
        """ """
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def select(self):
        """Select item"""
        self.selected = True
        plot = self.plot()
        if plot is not None:
            plot.blockSignals(True)
        self.setSymbol(SELECTED_SYMBOL)
        if plot is not None:
            plot.blockSignals(False)
        self.invalidate_plot()

    def unselect(self):
        """Unselect item"""
        self.selected = False
        # Restoring initial curve parameters:
        self.param.update_item(self)
        self.invalidate_plot()

    def get_data(self):
        """Return curve data x, y (NumPy arrays)"""
        return self._x, self._y

    def set_data(self, x, y):
        """
        Set curve data:
            * x: NumPy array
            * y: NumPy array
        """
        self._x = np.array(x, copy=False)
        self._y = np.array(y, copy=False)
        self.setData(self._x, self._y)

    def is_empty(self):
        """Return True if item data is empty"""
        return self._x is None or self._y is None or self._y.size == 0

    def hit_test(self, pos):
        """Calcul de la distance d'un point à une courbe
        renvoie (dist, handle, inside)"""
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
        return distance, i, False, None

    def get_closest_coordinates(self, x, y):
        """Renvoie les coordonnées (x',y') du point le plus proche de (x,y)
        Méthode surchargée pour ErrorBarSignalCurve pour renvoyer
        les coordonnées des pointes des barres d'erreur"""
        plot = self.plot()
        ax = self.xAxis()
        ay = self.yAxis()
        xc = plot.transform(ax, x)
        yc = plot.transform(ay, y)
        _distance, i, _inside, _other = self.hit_test(QC.QPointF(xc, yc))
        point = self.sample(i)
        return point.x(), point.y()

    def get_coordinates_label(self, xc, yc):
        """

        :param xc:
        :param yc:
        :return:
        """
        title = self.title().text()
        return f"{title}:<br>x = {xc:g}<br>y = {yc:g}"

    def get_closest_x(self, xc):
        """

        :param xc:
        :return:
        """
        # We assume X is sorted, otherwise we'd need :
        # argmin(abs(x-xc))
        i = self._x.searchsorted(xc)
        if i > 0:
            if np.fabs(self._x[i - 1] - xc) < np.fabs(self._x[i] - xc):
                return self._x[i - 1], self._y[i - 1]
        return self._x[i], self._y[i]

    def move_local_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        :return:
        """
        if self.immutable:
            return
        if handle < 0 or handle > self._x.shape[0]:
            return
        x, y = canvas_to_axes(self, pos)
        self._x[handle] = x
        self._y[handle] = y
        self.setData(self._x, self._y)
        self.plot().replot()

    def move_local_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in canvas coordinates"""
        nx, ny = canvas_to_axes(self, new_pos)
        ox, oy = canvas_to_axes(self, old_pos)
        self._x += nx - ox
        self._y += ny - oy
        self.setData(self._x, self._y)

    def move_with_selection(self, delta_x, delta_y):
        """
        Translate the shape together with other selected items
        delta_x, delta_y: translation in plot coordinates
        """
        self._x += delta_x
        self._y += delta_y
        self.setData(self._x, self._y)

    def update_params(self):
        """ """
        self.param.update_item(self)
        if self.selected:
            self.select()

    def update_item_parameters(self):
        """ """
        self.param.update_param(self)

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        itemparams.add("CurveParam", self, self.param)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        update_dataset(self.param, itemparams.get("CurveParam"), visible_only=True)
        self.update_params()


assert_interfaces_valid(CurveItem)
