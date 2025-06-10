# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
import weakref
from typing import TYPE_CHECKING

import numpy as np
from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.constants import X_BOTTOM, Y_LEFT
from plotpy.coords import axes_to_canvas, canvas_to_axes
from plotpy.interfaces import IBasePlotItem
from plotpy.items.curve.errorbar import ErrorBarCurveItem
from plotpy.items.image.misc import get_image_from_qrect
from plotpy.mathutils.geometry import rotate, translate, vector_angle, vector_norm

if TYPE_CHECKING:
    from plotpy.items import AnnotatedObliqueRectangle, AnnotatedSegment

try:
    from plotpy._scaler import INTERP_LINEAR, _scale_tr
except ImportError:
    print(
        ("Module 'plotpy.items.image.base': missing C extension"),
        file=sys.stderr,
    )
    print(
        ("try running :python setup.py build_ext --inplace -c mingw32"),
        file=sys.stderr,
    )
    raise

TEMP_ITEM = None


def get_rectangular_area(obj):
    """
    Return rectangular area covered by object

    Return None if object does not support this feature
    (like markers, points, ...)
    """
    if hasattr(obj, "get_rect"):
        return obj.get_rect()


def get_object_coordinates(obj):
    """Return Marker or PointShape/AnnotatedPoint object coordinates"""
    if hasattr(obj, "get_pos"):
        return obj.get_pos()
    else:
        return obj.xValue(), obj.yValue()


def get_plot_x_section(obj, apply_lut=False):
    """
    Return plot cross section along x-axis,
    at the y value defined by 'obj', a Marker/AnnotatedPoint object
    """
    _x0, y0 = get_object_coordinates(obj)
    plot = obj.plot()
    xmap = plot.canvasMap(plot.X_BOTTOM)
    xc0, xc1 = xmap.p1(), xmap.p2()
    _xc0, yc0 = axes_to_canvas(obj, 0, y0)
    if plot.get_axis_direction("left"):
        yc1 = yc0 + 1
    else:
        yc1 = yc0 - 3
    try:
        # TODO: Eventually add an option to apply interpolation algorithm
        data = get_image_from_qrect(
            plot,
            QC.QPointF(xc0, yc0),
            QC.QPointF(xc1, yc1),
            apply_lut=apply_lut,
            add_images=True,
            apply_interpolation=False,
        )
    except (ValueError, ZeroDivisionError, TypeError):
        return np.array([]), np.array([])
    if data.size == 0:
        return np.array([]), np.array([])
    y = data.mean(axis=0)
    x0, _y0 = canvas_to_axes(obj, QC.QPointF(xc0, yc0))
    x1, _y1 = canvas_to_axes(obj, QC.QPointF(xc1, yc1))
    x = np.linspace(x0, x1, len(y))
    return x, y


def get_plot_y_section(obj, apply_lut=False):
    """
    Return plot cross section along y-axis,
    at the x value defined by 'obj', a Marker/AnnotatedPoint object
    """
    x0, _y0 = get_object_coordinates(obj)
    plot = obj.plot()
    ymap = plot.canvasMap(Y_LEFT)
    yc0, yc1 = ymap.p1(), ymap.p2()
    if plot.get_axis_direction("left"):
        yc1, yc0 = yc0, yc1
    xc0, _yc0 = axes_to_canvas(obj, x0, 0)
    xc1 = xc0 + 1
    try:
        data = get_image_from_qrect(
            plot,
            QC.QPointF(xc0, yc0),
            QC.QPointF(xc1, yc1),
            apply_lut=apply_lut,
            add_images=True,
            apply_interpolation=False,
        )
    except (ValueError, ZeroDivisionError, TypeError):
        return np.array([]), np.array([])
    if data.size == 0:
        return np.array([]), np.array([])
    y = data.mean(axis=1)
    _x0, y0 = canvas_to_axes(obj, QC.QPointF(xc0, yc0))
    _x1, y1 = canvas_to_axes(obj, QC.QPointF(xc1, yc1))
    x = np.linspace(y0, y1, len(y))
    return x, y


def get_plot_average_x_section(obj, apply_lut=False):
    """
    Return cross section along x-axis, averaged on ROI defined by 'obj'
    'obj' is an AbstractShape object supporting the 'get_rect' method
    (RectangleShape, AnnotatedRectangle, etc.)
    """
    x0, y0, x1, y1 = obj.get_rect()
    xc0, yc0 = axes_to_canvas(obj, x0, y0)
    xc1, yc1 = axes_to_canvas(obj, x1, y1)
    invert = False
    if xc0 > xc1:
        invert = True
        xc1, xc0 = xc0, xc1
    ydir = obj.plot().get_axis_direction("left")
    if (ydir and yc0 > yc1) or (not ydir and yc0 < yc1):
        yc1, yc0 = yc0, yc1
    try:
        data = get_image_from_qrect(
            obj.plot(),
            QC.QPointF(xc0, yc0),
            QC.QPointF(xc1, yc1),
            apply_lut=apply_lut,
            apply_interpolation=False,
        )
    except (ValueError, ZeroDivisionError, TypeError):
        return np.array([]), np.array([])
    if data.size == 0:
        return np.array([]), np.array([])
    y = data.mean(axis=0)
    if invert:
        y = y[::-1]
    x = np.linspace(x0, x1, len(y))
    return x, y


def get_plot_average_y_section(obj, apply_lut=False):
    """
    Return cross section along y-axis, averaged on ROI defined by 'obj'
    'obj' is an AbstractShape object supporting the 'get_rect' method
    (RectangleShape, AnnotatedRectangle, etc.)
    """
    x0, y0, x1, y1 = obj.get_rect()
    xc0, yc0 = axes_to_canvas(obj, x0, y0)
    xc1, yc1 = axes_to_canvas(obj, x1, y1)
    invert = False
    ydir = obj.plot().get_axis_direction("left")
    if (ydir and yc0 > yc1) or (not ydir and yc0 < yc1):
        invert = True
        yc1, yc0 = yc0, yc1
    if xc0 > xc1:
        xc1, xc0 = xc0, xc1
    try:
        data = get_image_from_qrect(
            obj.plot(),
            QC.QPointF(xc0, yc0),
            QC.QPointF(xc1, yc1),
            apply_lut=apply_lut,
            apply_interpolation=False,
        )
    except (ValueError, ZeroDivisionError, TypeError):
        return np.array([]), np.array([])
    if data.size == 0:
        return np.array([]), np.array([])
    y = data.mean(axis=1)
    x = np.linspace(y0, y1, len(y))
    if invert:
        x = x[::-1]
    return x, y


def compute_oblique_section(item, obj, debug=False):
    """Return oblique averaged cross section"""
    global TEMP_ITEM

    if obj.plot() is None:
        # Item has not yet been added to the plot
        return np.array([]), np.array([])

    xa, ya, xb, yb = obj.get_bounding_rect_coords()
    x0, y0, x1, y1, x2, y2, x3, y3 = obj.get_rect()

    getcpi = item.get_closest_pixel_indexes
    ixa, iya = getcpi(xa, ya)
    ixb, iyb = getcpi(xb, yb)
    ix0, iy0 = getcpi(x0, y0)
    ix1, iy1 = getcpi(x1, y1)
    ix3, iy3 = getcpi(x3, y3)

    destw = int(vector_norm(ix0, iy0, ix1, iy1))
    desth = int(vector_norm(ix0, iy0, ix3, iy3))
    ysign = -1 if obj.plot().get_axis_direction("left") else 1
    angle = vector_angle(ix1 - ix0, (iy1 - iy0) * ysign)

    dst_rect = (0, 0, int(destw), int(desth))
    dst_image = np.empty((int(desth), int(destw)), dtype=np.float64)

    if isinstance(item.data, np.ma.MaskedArray):
        if item.data.dtype in (np.float32, np.float64):
            item_data = item.data
        else:
            item_data = np.ma.array(item.data, dtype=np.float32, copy=True)
        data = np.ma.filled(item_data, np.nan)
    else:
        data = item.data

    ixr = 0.5 * (ixb + ixa)
    iyr = 0.5 * (iyb + iya)
    mat = translate(ixr, iyr) @ rotate(-angle) @ translate(-0.5 * destw, -0.5 * desth)
    _scale_tr(data, mat, dst_image, dst_rect, (1.0, 0.0, np.nan), (INTERP_LINEAR,))

    if debug:
        plot = obj.plot()
        if TEMP_ITEM is None:
            from plotpy.builder import make

            TEMP_ITEM = make.image(dst_image)
            plot.add_item(TEMP_ITEM)
        else:
            TEMP_ITEM.set_data(dst_image)
        if False:
            from plotpy.constants import LUTAlpha

            TEMP_ITEM.param.alpha_function = LUTAlpha.LINEAR.value
            xmin, ymin = ixa, iya
            xmax, ymax = xmin + destw, ymin + desth
            TEMP_ITEM.param.xmin = xmin
            TEMP_ITEM.param.xmax = xmax
            TEMP_ITEM.param.ymin = ymin
            TEMP_ITEM.param.ymax = ymax
            TEMP_ITEM.param.update_item(TEMP_ITEM)
        plot.replot()

    fixed_image = np.ma.fix_invalid(dst_image, copy=debug)
    if fixed_image.size == 0:
        return np.array([]), np.array([])
    ydata = fixed_image.mean(axis=1)
    xdata = item.get_x_values(0, ydata.size)[: ydata.size]
    try:
        xdata -= xdata[0]
    except IndexError:
        print(xdata, ydata)
    return xdata, ydata


class CrossSectionItem(ErrorBarCurveItem):
    """A Qwt item representing cross section data"""

    __implements__ = (IBasePlotItem,)
    ORIENTATION = None

    def __init__(self, curveparam=None, errorbarparam=None):
        ErrorBarCurveItem.__init__(self, curveparam, errorbarparam)
        self.setOrientation(self.ORIENTATION)
        self.perimage_mode = True
        self.autoscale_mode = False
        self.apply_lut = False
        self.source = None

    def set_source_image(self, src):
        """
        Set source image
        (source: object with methods 'get_xsection' and 'get_ysection',
         e.g. objects derived from plotpy.items.image.BaseImageItem)
        """
        self.source = weakref.ref(src)

    def get_source_image(self):
        """

        :return:
        """
        if self.source is not None:
            return self.source()

    def get_cross_section(self, obj):
        """Get cross section data from source image"""
        raise NotImplementedError

    def clear_data(self):
        """ """
        self.set_data(np.array([]), np.array([]), None, None)
        self.plot().SIG_CS_CURVE_CHANGED.emit(self)

    def setStyle(self, style):
        """
        Update the curve style and update the curve data to shift axes
        according to the style.
        """
        super().setStyle(style)
        plot = self.plot()
        if plot is not None:
            obj = plot.get_last_obj()
            if obj is not None:
                self.update_curve_data(obj)

    def update_curve_data(self, obj):
        """

        :param obj:
        """
        sectx, secty = self.get_cross_section(obj)
        if secty.size == 0 or np.all(np.isnan(secty)):
            sectx, secty = np.array([]), np.array([])
        elif self.param.curvestyle != "Steps" and sectx.size > 1:
            # Center the symbols at the middle of pixels:
            sectx[:-1] += np.mean(np.diff(sectx) / 2)
        if self.orientation() == QC.Qt.Orientation.Vertical:
            self.process_curve_data(secty, sectx)
        else:
            self.process_curve_data(sectx, secty)

    def process_curve_data(self, x, y, dx=None, dy=None):
        """
        Override this method to process data
        before updating the displayed curve
        """
        self.set_data(x, y, dx, dy)

    def update_item(self, obj):
        """

        :param obj:
        :return:
        """
        plot = self.plot()
        if not plot:
            return
        source = self.get_source_image()
        if source is None or not plot.isVisible():
            return
        self.update_curve_data(obj)
        self.plot().SIG_CS_CURVE_CHANGED.emit(self)
        if not self.autoscale_mode:
            self.update_scale()

    def update_scale(self):
        """ """
        plot = self.plot()
        if self.orientation() == QC.Qt.Orientation.Vertical:
            axis_id = Y_LEFT
        else:
            axis_id = X_BOTTOM
        source = self.get_source_image()
        sdiv = source.plot().axisScaleDiv(axis_id)
        plot.setAxisScale(axis_id, sdiv.lowerBound(), sdiv.upperBound())
        plot.replot()


class XCrossSectionItem(CrossSectionItem):
    """A Qwt item representing x-axis cross section data"""

    ORIENTATION = QC.Qt.Orientation.Horizontal

    def get_cross_section(self, obj):
        """Get x-cross section data from source image"""
        source = self.get_source_image()
        rect = get_rectangular_area(obj)
        fmt = source.param.yformat
        if rect is None:
            # Object is a marker or an annotated point
            _x0, y0 = get_object_coordinates(obj)
            self.param.label = _("Cross section") + " @ y=" + (fmt % y0)
            if self.perimage_mode:
                data = source.get_xsection(y0, apply_lut=self.apply_lut)
            else:
                data = get_plot_x_section(obj, apply_lut=self.apply_lut)
        else:
            if self.perimage_mode:
                x0, y0, x1, y1 = rect
                data = source.get_average_xsection(
                    x0, y0, x1, y1, apply_lut=self.apply_lut
                )
            else:
                data = get_plot_average_x_section(obj, apply_lut=self.apply_lut)
                x0, y0, x1, y1 = obj.get_rect()
            text = _("Average cross section")
            self.param.label = f"{text} @ y=[{fmt % y0} ; {fmt % y1}]"
        return data


class YCrossSectionItem(CrossSectionItem):
    """A Qwt item representing y-axis cross section data"""

    ORIENTATION = QC.Qt.Orientation.Vertical

    def get_cross_section(self, obj):
        """Get y-cross section data from source image"""
        source = self.get_source_image()
        rect = get_rectangular_area(obj)
        fmt = source.param.xformat
        if rect is None:
            # Object is a marker or an annotated point
            x0, _y0 = get_object_coordinates(obj)
            self.param.label = _("Cross section") + " @ x=" + (fmt % x0)
            if self.perimage_mode:
                data = source.get_ysection(x0, apply_lut=self.apply_lut)
            else:
                data = get_plot_y_section(obj, apply_lut=self.apply_lut)
        else:
            if self.perimage_mode:
                x0, y0, x1, y1 = rect
                data = source.get_average_ysection(
                    x0, y0, x1, y1, apply_lut=self.apply_lut
                )
            else:
                data = get_plot_average_y_section(obj, apply_lut=self.apply_lut)
                x0, y0, x1, y1 = obj.get_rect()
            text = _("Average cross section")
            self.param.label = f"{text} @ x=[{fmt % x0} ; {fmt % x1}]"
        return data


# Oblique cross section item
class ObliqueCrossSectionItem(CrossSectionItem):
    """A Qwt item representing radially-averaged cross section data"""

    DEBUG = False

    def update_curve_data(self, obj: AnnotatedObliqueRectangle) -> None:
        """Update curve data"""
        source = self.get_source_image()
        rect = obj.get_bounding_rect_coords()
        if rect is not None and source.data is not None:
            #            x0, y0, x1, y1 = rect
            #            angle = obj.get_tr_angle()
            sectx, secty = compute_oblique_section(source, obj, debug=self.DEBUG)
            if secty.size == 0 or np.all(np.isnan(secty)):
                sectx, secty = np.array([]), np.array([])
            self.process_curve_data(sectx, secty, None, None)

    def update_scale(self):
        """ """
        pass


def compute_line_section(
    data: np.ndarray, row0, col0, row1, col1
) -> tuple[np.ndarray, np.ndarray]:
    """Return intensity profile of data along a line

    Args:
        data: 2D array
        row0, col0: start point
        row1, col1: end point
    """
    # Keep coordinates inside the image
    row0 = max(0, min(row0, data.shape[0] - 1))
    col0 = max(0, min(col0, data.shape[1] - 1))
    row1 = max(0, min(row1, data.shape[0] - 1))
    col1 = max(0, min(col1, data.shape[1] - 1))
    # Keep coordinates in the right order
    row0, row1 = min(row0, row1), max(row0, row1)
    col0, col1 = min(col0, col1), max(col0, col1)
    # Extract the line
    line = np.zeros((2, max(abs(row1 - row0), abs(col1 - col0)) + 1), dtype=int)
    line[0, :] = np.linspace(row0, row1, line.shape[1]).astype(int)
    line[1, :] = np.linspace(col0, col1, line.shape[1]).astype(int)
    # Interpolate the line
    y = np.ma.array(data[line[0], line[1]], float).filled(np.nan)
    x = np.arange(y.size)
    return x, y


# Line cross section item
class LineCrossSectionItem(CrossSectionItem):
    """A Qwt item representing line cross section data"""

    def update_curve_data(self, obj: AnnotatedSegment) -> None:
        """Update curve data"""
        source = self.get_source_image()
        rect = obj.get_rect()
        if rect is not None and source.data is not None:
            x0, y0, x1, y1 = obj.get_rect()
            c0, r0 = source.get_closest_pixel_indexes(x0, y0)
            c1, r1 = source.get_closest_pixel_indexes(x1, y1)
            sectx, secty = compute_line_section(source.data, r0, c0, r1, c1)
            if secty.size == 0 or np.all(np.isnan(secty)):
                sectx, secty = np.array([]), np.array([])
            self.process_curve_data(sectx, secty, None, None)

    def update_scale(self):
        """ """
        pass
