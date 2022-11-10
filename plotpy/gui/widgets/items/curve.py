# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103

"""
plotpy.gui.widgets.items.curve
------------------------------

The `curve` module provides curve-related objects:
    * :py:class:`.curve.CurveItem`: a curve plot item
    * :py:class:`.curve.ErrorBarCurveItem`: a curve plot item with
      error bars
    * :py:class:`.curve.GridItem`

``CurveItem`` and ``GridItem`` objects are plot items (derived from
QwtPlotItem) that may be displayed on a 2D plotting widget like
:py:class:`.baseplot.BasePlot`.

.. seealso::

    Module :py:mod:`plotpy.gui.widgets.items.image`
        Module providing image-related plot items

    Module :py:mod:`plotpy.gui.widgets.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Examples
~~~~~~~~

Create a basic curve plotting widget:
    * before creating any widget, a `QApplication` must be instantiated (that
      is a `Qt` internal requirement):

>>> import plotpy.gui
>>> app = plotpy.gui.qapplication()

    * that is mostly equivalent to the following (the only difference is that
      the `plotpy` helper function also installs the `Qt` translation
      corresponding to the system locale):

>>> from PyQt5.QtWidgets import QApplication
>>> app = QApplication([])

    * now that a `QApplication` object exists, we may create the plotting
      widget:

>>> from plotpy.gui.widgets.baseplot import BasePlot, PlotType
>>> plot = BasePlot(title="Example", xlabel="X", ylabel="Y", type=PlotType.CURVE)

Create a curve item:
    * from the associated plot item class (e.g. `ErrorBarCurveItem` to
      create a curve with error bars): the item properties are then assigned
      by creating the appropriate style parameters object
      (e.g. :py:class:`.styles.ErrorBarParam`)

>>> from plotpy.gui.widgets.items.curve import CurveItem
>>> from plotpy.gui.widgets.styles import CurveParam
>>> param = CurveParam()
>>> param.label = 'My curve'
>>> curve = CurveItem(param)
>>> curve.set_data(x, y)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.gui.widgets.builder import make
>>> curve = make.curve(x, y, title='My curve')

Attach the curve to the plotting widget:

>>> plot.add_item(curve)

Display the plotting widget:

>>> plot.show()
>>> app.exec_()

Reference
~~~~~~~~~

.. autoclass:: CurveItem
   :members:
   :inherited-members:
.. autoclass:: ErrorBarCurveItem
   :members:
   :inherited-members:
.. autoclass:: GridItem
   :members:
"""

from __future__ import print_function, with_statement

import warnings
from sys import maxsize

import numpy as np

from plotpy.core.utils.dataset import update_dataset
from plotpy.gui.utils.gui import assert_interfaces_valid
from plotpy.gui.widgets.config import CONF, _
from plotpy.gui.config.misc import get_icon
from plotpy.gui.widgets.ext_gui_lib import (
    QBrush,
    QColor,
    QLineF,
    QPen,
    QPointF,
    QPolygonF,
    QRectF,
    QwtPlotCurve,
    QwtPlotGrid,
    QwtPlotItem,
    QwtScaleMap,
    QIcon
)
from plotpy.gui.widgets.interfaces import (
    IBasePlotItem,
    ICurveItemType,
    IDecoratorItemType,
    ISerializableType,
    ITrackableItemType,
)
from plotpy.gui.widgets.items.utils import canvas_to_axes
from plotpy.gui.widgets.styles import CurveParam, ErrorBarParam, GridParam, SymbolParam


def _simplify_poly(pts, off, scale, bounds):
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


try:
    from gshhs import simplify_poly
except ImportError:
    simplify_poly = _simplify_poly


def seg_dist(P, P0, P1):
    """
    Return distance between point P and segment (P0, P1)
    If P orthogonal projection on (P0, P1) is outside segment bounds, return
    either distance to P0 or to P1 (the closest one)
    P, P0, P1: QPointF instances
    """
    u = QLineF(P0, P).length()
    if P0 == P1:
        return u
    else:
        angle = QLineF(P0, P).angleTo(QLineF(P0, P1)) * np.pi / 180
        projection = u * np.cos(angle)
        if projection > QLineF(P0, P1).length():
            return QLineF(P1, P).length()
        elif projection < 0:
            return QLineF(P0, P).length()
        else:
            return abs(u * np.sin(angle))


def test_seg_dist():
    """

    """
    print(seg_dist(QPointF(200, 100), QPointF(150, 196), QPointF(250, 180)))
    print(seg_dist(QPointF(200, 100), QPointF(190, 196), QPointF(210, 180)))
    print(seg_dist(QPointF(201, 105), QPointF(201, 196), QPointF(201, 180)))


def norm2(v):
    """

    :param v:
    :return:
    """
    return (v ** 2).sum(axis=1)


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


def test_seg_dist_v():
    """Test de seg_dist_v"""
    a = (np.arange(10.0) ** 2).reshape(5, 2)
    ix, dist = seg_dist_v((2.1, 3.3), a[:-1, 0], a[:-1, 1], a[1:, 0], a[1:, 1])
    print(ix, dist)
    assert ix == 0


if __name__ == "__main__":
    test_seg_dist_v()
    test_seg_dist()


SELECTED_SYMBOL_PARAM = SymbolParam()
SELECTED_SYMBOL_PARAM.read_config(CONF, "plot", "selected_curve_symbol")
SELECTED_SYMBOL = SELECTED_SYMBOL_PARAM.build_symbol()


class GridItem(QwtPlotGrid):
    """
    Construct a grid `plot item` with the parameters *gridparam*
    (see :py:class:`.styles.GridParam`)
    """

    __implements__ = (IBasePlotItem,)

    _readonly = True
    _private = False

    def __init__(self, gridparam=None):
        super(GridItem, self).__init__()
        if gridparam is None:
            self.gridparam = GridParam(title=_("Grid"), icon="grid.png")
        else:
            self.gridparam = gridparam
        self.selected = False
        self.immutable = True  # set to false to allow moving points around
        self.update_params()  # won't work completely because it's not yet
        # attached to plot (actually, only canvas background won't be updated)
        self.setIcon(get_icon("grid.png"))

    def types(self):
        """

        :return:
        """
        return (IDecoratorItemType,)

    def attach(self, plot):
        """Reimplemented to update plot canvas background"""
        QwtPlotGrid.attach(self, plot)
        self.update_params()

    def set_readonly(self, state):
        """Set object read-only state"""
        self._readonly = state

    def is_readonly(self):
        """Return object read-only state"""
        return self._readonly

    def set_private(self, state):
        """Set object as private"""
        self._private = state

    def is_private(self):
        """Return True if object is private"""
        return self._private

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
        return False

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

    def select(self):
        """Select item"""
        pass

    def unselect(self):
        """Unselect item"""
        pass

    def hit_test(self, pos):
        """

        :param pos:
        :return:
        """
        return maxsize, 0, False, None

    def move_local_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        pass

    def move_local_shape(self, old_pos, new_pos):
        """

        :param old_pos:
        :param new_pos:
        """
        pass

    def move_with_selection(self, delta_x, delta_y):
        """

        :param delta_x:
        :param delta_y:
        """
        pass

    def update_params(self):
        """

        """
        self.gridparam.update_grid(self)

    def update_item_parameters(self):
        """

        """
        self.gridparam.update_param(self)

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        itemparams.add("GridParam", self, self.gridparam)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        self.gridparam = itemparams.get("GridParam")
        self.gridparam.update_grid(self)


assert_interfaces_valid(GridItem)


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
            return QRectF(xmin, ymin, xf.max() - xmin, yf.max() - ymin)
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
        """

        """
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
            return maxsize, 0, False, None
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
            return maxsize, 0, False, None
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
        distance = seg_dist(QPointF(pos), QPointF(p0x, p0y), QPointF(p1x, p1y))
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
        _distance, i, _inside, _other = self.hit_test(QPointF(xc, yc))
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
        """

        """
        self.param.update_item(self)
        if self.selected:
            self.select()

    def update_item_parameters(self):
        """

        """
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
        self._n = (
            None
        )  # Array of polygon offsets/ends Nx1 (polygon k points are _pts[_n[k-1]:_n[k]])
        self._c = None  # Color of polygon Nx2 [border,background] as RGBA uint32
        self.update_params()
        self.setIcon(get_icon("curve.png"))

    def types(self):
        """

        :return:
        """
        return (ICurveItemType, ITrackableItemType, ISerializableType)

    def can_select(self):
        """

        :return:
        """
        return self._can_select

    def can_resize(self):
        """

        :return:
        """
        return self._can_resize

    def can_rotate(self):
        """

        :return:
        """
        return self._can_rotate

    def can_move(self):
        """

        :return:
        """
        return self._can_move

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

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        writer.write(self._pts, group_name="Pdata")
        writer.write(self._n, group_name="Ndata")
        writer.write(self._c, group_name="Cdata")
        writer.write(self.z(), group_name="z")
        self.param.update_param(self)
        writer.write(self.param, group_name="curveparam")

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
        pts = reader.read(group_name="Pdata", func=reader.read_array)
        n = reader.read(group_name="Ndata", func=reader.read_array)
        c = reader.read(group_name="Cdata", func=reader.read_array)
        self.set_data(pts, n, c)
        self.setZ(reader.read("z"))
        self.param = CurveParam(_("PolygonMap"), icon="curve.png")
        reader.read("curveparam", instance=self.param)
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
        """

        """
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def select(self):
        """Select item"""
        self.selected = True
        self.setSymbol(SELECTED_SYMBOL)
        self.invalidate_plot()

    def unselect(self):
        """Unselect item"""
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
        self.bounds = QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def is_empty(self):
        """Return True if item data is empty"""
        return self._pts is None or self._pts.size == 0

    def hit_test(self, pos):
        """Calcul de la distance d'un point à une courbe
        renvoie (dist, handle, inside)"""
        if self.is_empty():
            return maxsize, 0, False, None
        # TODO
        return maxsize, 0, False, None

    def get_closest_coordinates(self, x, y):
        """Renvoie les coordonnées (x',y') du point le plus proche de (x,y)
        Méthode surchargée pour ErrorBarSignalCurve pour renvoyer
        les coordonnées des pointes des barres d'erreur"""
        # TODO
        return x, y

    def get_coordinates_label(self, xc, yc):
        """

        :param xc:
        :param yc:
        :return:
        """
        title = self.title().text()
        return f"{title}:<br>x = {xc:f}<br>y = {yc:f}"

    def move_local_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        :return:
        """
        return

    def move_local_shape(self, old_pos, new_pos):
        """

        :param old_pos:
        :param new_pos:
        """
        pass

    def move_with_selection(self, delta_x, delta_y):
        """

        :param delta_x:
        :param delta_y:
        """
        pass

    def update_params(self):
        """

        """
        self.param.update_item(self)
        if self.selected:
            self.select()

    def update_item_parameters(self):
        """

        """
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
        fgcol = QColor()
        bgcol = QColor()
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
                points.append(QPointF(poly[i, 0], poly[i, 1]))
            pg = QPolygonF(points)
            fgcol.setRgba(int(_c[num, 0]))
            bgcol.setRgba(int(_c[num, 1]))
            painter.setPen(QPen(fgcol))
            painter.setBrush(QBrush(bgcol))
            painter.drawPolygon(pg)
        # print "poly:", time()-t2

    def boundingRect(self):
        """

        :return:
        """
        return self.bounds


assert_interfaces_valid(PolygonMapItem)


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
        _distance, i, _inside, _other = self.hit_test(QPointF(xc, yc))
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

        return QRectF(xmin, ymin, xmaxf.max() - xmin, ymaxf.max() - ymin)

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
                lines.append(QLineF(txmin[i], yi, txmax[i], yi))
            painter.drawLines(lines)
            if cap > 0:
                lines = []
                for i in RN:
                    yi = ty[i]
                    lines.append(QLineF(txmin[i], yi - cap, txmin[i], yi + cap))
                    lines.append(QLineF(txmax[i], yi - cap, txmax[i], yi + cap))
            painter.drawLines(lines)

        if self._dy is not None:
            tymin = vmap(yMap, ymin)
            tymax = vmap(yMap, ymax)
            if self.errorbarparam.mode == 0:
                # Classic error bars
                lines = []
                for i in RN:
                    xi = tx[i]
                    lines.append(QLineF(xi, tymin[i], xi, tymax[i]))
                painter.drawLines(lines)
                if cap > 0:
                    # Cap
                    lines = []
                    for i in RN:
                        xi = tx[i]
                        lines.append(QLineF(xi - cap, tymin[i], xi + cap, tymin[i]))
                        lines.append(QLineF(xi - cap, tymax[i], xi + cap, tymax[i]))
                painter.drawLines(lines)
            else:
                # Error area
                points = []
                rpoints = []
                for i in RN:
                    xi = tx[i]
                    points.append(QPointF(xi, tymin[i]))
                    rpoints.append(QPointF(xi, tymax[i]))
                points += reversed(rpoints)
                painter.setBrush(QBrush(self.errorBrush))
                painter.drawPolygon(*points)

        painter.restore()

        if not self.errorOnTop:
            QwtPlotCurve.draw(self, painter, xMap, yMap, canvasRect)

    def update_params(self):
        """

        """
        self.errorbarparam.update_item(self)
        CurveItem.update_params(self)

    def update_item_parameters(self):
        """

        """
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
