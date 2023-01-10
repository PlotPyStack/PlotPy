# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103
from __future__ import print_function, with_statement

from sys import maxsize

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset.datatypes import update_dataset
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotItem

from plotpy.config import _
from plotpy.utils.gui import assert_interfaces_valid
from plotpy.widgets.interfaces import (
    IBasePlotItem,
    ICurveItemType,
    ISerializableType,
    ITrackableItemType,
)
from plotpy.widgets.items.curve.base import SELECTED_SYMBOL
from plotpy.widgets.styles.curve import CurveParam


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
        self._n = None  # Array of polygon offsets/ends Nx1 (polygon k points are _pts[_n[k-1]:_n[k]])
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
        """ """
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
        self.bounds = QC.QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

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
