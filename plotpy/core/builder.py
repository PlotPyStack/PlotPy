# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Item builder
------------

The `builder` module provides a builder singleton class that can be
used to simplify the creation of plot items.
"""

from __future__ import annotations

import os.path as osp
from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy  # only to help intersphinx finding numpy doc
import numpy as np

from plotpy.config import CONF, _, make_title
from plotpy.core import io
from plotpy.core.items.annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
)
from plotpy.core.items.curve.base import CurveItem
from plotpy.core.items.curve.errorbar import ErrorBarCurveItem
from plotpy.core.items.grid import GridItem
from plotpy.core.items.histogram import HistogramItem
from plotpy.core.items.image.image_items import ImageItem, RGBImageItem, XYImageItem
from plotpy.core.items.image.masked import MaskedImageItem, MaskedXYImageItem
from plotpy.core.items.image.misc import Histogram2DItem, QuadGridItem
from plotpy.core.items.image.transform import TrImageItem
from plotpy.core.items.label import (
    DataInfoLabel,
    LabelItem,
    LegendBoxItem,
    RangeComputation,
    RangeComputation2d,
    RangeInfo,
    SelectedLegendBoxItem,
)
from plotpy.core.items.shapes.ellipse import EllipseShape
from plotpy.core.items.shapes.marker import Marker
from plotpy.core.items.shapes.polygon import ContourShape
from plotpy.core.items.shapes.range import XRangeSelection
from plotpy.core.items.shapes.rectangle import RectangleShape
from plotpy.core.items.shapes.segment import SegmentShape
from plotpy.core.plot.base import BasePlot
from plotpy.core.plot.histogram.utils import lut_range_threshold
from plotpy.core.styles.base import (
    COLORS,
    MARKERS,
    GridParam,
    LineStyleParam,
    style_generator,
    update_style_attr,
)
from plotpy.core.styles.curve import CurveParam
from plotpy.core.styles.errorbar import ErrorBarParam
from plotpy.core.styles.histogram import Histogram2DParam, HistogramParam
from plotpy.core.styles.image import (
    ImageFilterParam,
    ImageParam,
    LUTAlpha,
    MaskedImageParam,
    MaskedXYImageParam,
    QuadGridParam,
    RGBImageParam,
    TrImageParam,
    XYImageParam,
)
from plotpy.core.styles.label import LabelParam, LabelParamWithContents, LegendParam
from plotpy.core.styles.shape import AnnotationParam, MarkerParam, ShapeParam
from plotpy.utils.contour import contour

if TYPE_CHECKING:
    from plotpy.core.items.image.filter import ImageFilterItem


# default offset positions for anchors
ANCHOR_OFFSETS = {
    "TL": (5, 5),
    "TR": (-5, 5),
    "BL": (5, -5),
    "BR": (-5, -5),
    "L": (5, 0),
    "R": (-5, 0),
    "T": (0, 5),
    "B": (0, -5),
}

CURVE_COUNT = 0
HISTOGRAM_COUNT = 0
IMAGE_COUNT = 0
LABEL_COUNT = 0
HISTOGRAM2D_COUNT = 0


class PlotItemBuilder:
    """
    This is just a bare class used to regroup
    a set of factory functions in a single object
    """

    def __init__(self):
        self.style = style_generator()

    def gridparam(
        self,
        background: str | None = None,
        major_enabled: tuple[bool, bool] | None = None,
        minor_enabled: tuple[bool, bool] | None = None,
        major_style: tuple[str, str, int] | None = None,
        minor_style: tuple[str, str, int] | None = None,
    ) -> GridParam:
        """Make :py:class:`.GridParam` instance

        Args:
            background: canvas background color
            major_enabled: major grid enabled (x, y)
            minor_enabled: minor grid enabled (x, y)
            major_style: major grid style (linestyle, color, width)
            minor_style: minor grid style (linestyle, color, width)

        Returns:
            :py:class:`.GridParam`: grid parameters
        """
        gridparam = GridParam(title=_("Grid"), icon="lin_lin.png")
        gridparam.read_config(CONF, "plot", "grid")
        if background is not None:
            gridparam.background = background
        if major_enabled is not None:
            gridparam.maj_xenabled, gridparam.maj_yenabled = major_enabled
        if minor_enabled is not None:
            gridparam.min_xenabled, gridparam.min_yenabled = minor_enabled
        if major_style is not None:
            style = LineStyleParam()
            linestyle, color, style.width = major_style
            style.set_style_from_matlab(linestyle)
            style.color = COLORS.get(color, color)  # MATLAB-style
        if minor_style is not None:
            style = LineStyleParam()
            linestyle, color, style.width = minor_style
            style.set_style_from_matlab(linestyle)
            style.color = COLORS.get(color, color)  # MATLAB-style
        return gridparam

    def grid(
        self,
        background: str | None = None,
        major_enabled: tuple[bool, bool] | None = None,
        minor_enabled: tuple[bool, bool] | None = None,
        major_style: tuple[str, str, int] | None = None,
        minor_style: tuple[str, str, int] | None = None,
    ) -> GridItem:
        """Make a grid `plot item` (:py:class:`.GridItem` object)

        Args:
            background: canvas background color
            major_enabled: major grid enabled (x, y)
            minor_enabled: minor grid enabled (x, y)
            major_style: major grid style (linestyle, color, width)
            minor_style: minor grid style (linestyle, color, width)

        Returns:
            :py:class:`.GridItem`: grid item
        """
        gridparam = self.gridparam(
            background, major_enabled, minor_enabled, major_style, minor_style
        )
        return GridItem(gridparam)

    def __set_curve_axes(self, curve: CurveItem, xaxis: str, yaxis: str) -> None:
        """Set curve axes"""
        for axis in (xaxis, yaxis):
            if axis not in BasePlot.AXIS_NAMES:
                raise RuntimeError(f"Unknown axis {axis}")
        curve.setXAxis(BasePlot.AXIS_NAMES[xaxis])
        curve.setYAxis(BasePlot.AXIS_NAMES[yaxis])

    def __set_baseparam(
        self,
        param: CurveParam | MarkerParam,
        color: str | None = None,
        linestyle: str | None = None,
        linewidth: int | None = None,
        marker: str | None = None,
        markersize: int | None = None,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
    ) -> None:
        """Apply parameters to a :py:class:`.CurveParam` or
        :py:class:`.MarkerParam` instance"""
        if color is not None:
            color = COLORS.get(color, color)  # MATLAB-style
            param.line.color = color
        if linestyle is not None:
            param.line.set_style_from_matlab(linestyle)
        if linewidth is not None:
            param.line.width = linewidth
        if marker is not None:
            if marker in MARKERS:
                param.symbol.update_param(MARKERS[marker])  # MATLAB-style
            else:
                param.symbol.marker = marker
        if markersize is not None:
            param.symbol.size = markersize
        if markerfacecolor is not None:
            markerfacecolor = COLORS.get(
                markerfacecolor, markerfacecolor
            )  # MATLAB-style
            param.symbol.facecolor = markerfacecolor
        if markeredgecolor is not None:
            markeredgecolor = COLORS.get(
                markeredgecolor, markeredgecolor
            )  # MATLAB-style
            param.symbol.edgecolor = markeredgecolor

    def __set_param(
        self,
        param: CurveParam,
        title: str | None = None,
        color: str | None = None,
        linestyle: str | None = None,
        linewidth: int | None = None,
        marker: str | None = None,
        markersize: int | None = None,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
        shade: bool | None = None,
        curvestyle: str | None = None,
        baseline: float | None = None,
    ) -> None:
        """Apply parameters to a :py:class:`.CurveParam` instance"""
        self.__set_baseparam(
            param,
            color,
            linestyle,
            linewidth,
            marker,
            markersize,
            markerfacecolor,
            markeredgecolor,
        )
        if title:
            param.label = title
        if shade is not None:
            param.shade = shade
        if curvestyle is not None:
            param.curvestyle = curvestyle
        if baseline is not None:
            param.baseline = baseline

    def __get_arg_triple_plot(self, args):
        """Convert MATLAB-like arguments into x, y, style"""

        def get_x_y_from_data(data):
            """

            :param data:
            :return:
            """
            if isinstance(data, (tuple, list)):
                data = np.array(data)
            if len(data.shape) == 1 or 1 in data.shape:
                x = np.arange(data.size)
                y = data
            else:
                x = np.arange(len(data[:, 0]))
                y = [data[:, i] for i in range(len(data[0, :]))]
            return x, y

        if len(args) == 1:
            if isinstance(args[0], str):
                x = np.array((), float)
                y = np.array((), float)
                style = args[0]
            else:
                x, y = get_x_y_from_data(args[0])
                y_matrix = not isinstance(y, np.ndarray)
                if y_matrix:
                    style = [next(self.style) for yi in y]
                else:
                    style = next(self.style)
        elif len(args) == 2:
            a1, a2 = args
            if isinstance(a2, str):
                x, y = get_x_y_from_data(a1)
                style = a2
            else:
                x = a1
                y = a2
                style = next(self.style)
        elif len(args) == 3:
            x, y, style = args
        else:
            raise TypeError("Wrong number of arguments")
        if isinstance(x, (list, tuple)):
            x = np.array(x)
        if isinstance(y, (list, tuple)) and not y_matrix:
            y = np.array(y)
        return x, y, style

    def __get_arg_triple_errorbar(self, args):
        """Convert MATLAB-like arguments into x, y, style"""
        if len(args) == 2:
            y, dy = args
            x = np.arange(len(y))
            dx = np.zeros(len(y))
            style = next(self.style)
        elif len(args) == 3:
            a1, a2, a3 = args
            if isinstance(a3, str):
                y, dy = a1, a2
                x = np.arange(len(y))
                dx = np.zeros(len(y))
                style = a3
            else:
                x, y, dy = args
                dx = np.zeros(len(y))
                style = next(self.style)
        elif len(args) == 4:
            a1, a2, a3, a4 = args
            if isinstance(a4, str):
                x, y, dy = a1, a2, a3
                dx = np.zeros(len(y))
                style = a4
            else:
                x, y, dx, dy = args
                style = next(self.style)
        elif len(args) == 5:
            x, y, dx, dy, style = args
        else:
            raise TypeError("Wrong number of arguments")
        return x, y, dx, dy, style

    def mcurve(self, *args, **kwargs) -> CurveItem | list[CurveItem]:
        """Make a curve `plot item` based on MATLAB-like syntax
        (may returns a list of curves if data contains more than one signal)

        Args:
            \*args: x, y, style
            \*\*kwargs: title, color, linestyle, linewidth, marker, markersize,
            markerfacecolor, markeredgecolor, shade, curvestyle, baseline

        Returns:
            :py:class:`.CurveItem` object

        Example::
            mcurve(x, y, 'r+')
        """  # noqa: E501
        x, y, style = self.__get_arg_triple_plot(args)
        if isinstance(y, np.ndarray):
            y = [y]
        if not isinstance(style, list):
            style = [style]
        if len(y) > len(style):
            style = [style[0]] * len(y)
        basename = _("Curve")
        curves = []
        for yi, stylei in zip(y, style):
            param = CurveParam(title=basename, icon="curve.png")
            if "label" in kwargs:
                param.label = kwargs.pop("label")
            else:
                global CURVE_COUNT
                CURVE_COUNT += 1
                param.label = make_title(basename, CURVE_COUNT)
            update_style_attr(stylei, param)
            curves.append(self.pcurve(x, yi, param, **kwargs))
        if len(curves) == 1:
            return curves[0]
        else:
            return curves

    def pcurve(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        param: CurveParam,
        xaxis: str = "bottom",
        yaxis: str = "left",
    ) -> CurveItem:
        """Make a curve `plot item` based on a :py:class:`.CurveParam` instance

        Args:
            x: x data
            y: y data
            param: curve parameters
            xaxis: x axis name. Default is 'bottom'
            yaxis: y axis name. Default is 'left'

        Returns:
            :py:class:`.CurveItem` object

        Example::
            pcurve(x, y, param)
        """
        curve = CurveItem(param)
        curve.set_data(x, y)
        curve.update_params()
        self.__set_curve_axes(curve, xaxis, yaxis)
        return curve

    def curve(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        title: str = "",
        color: str | None = None,
        linestyle: str | None = None,
        linewidth: int | None = None,
        marker: str | None = None,
        markersize: int | None = None,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
        shade: bool | None = None,
        curvestyle: str | None = None,
        baseline: float | None = None,
        xaxis: str = "bottom",
        yaxis: str = "left",
        dx: numpy.ndarray | None = None,
        dy: numpy.ndarray | None = None,
        errorbarwidth: int | None = None,
        errorbarcap: int | None = None,
        errorbarmode: str | None = None,
        errorbaralpha: float | None = None,
    ) -> CurveItem:
        """Make a curve `plot item` from x, y, data

        Args:
            x: x data
            y: y data
            title: curve title. Default is ''
            color: curve color name. Default is None
            linestyle: curve line style (MATLAB-like string or "SolidLine",
             "DashLine", "DotLine", "DashDotLine", "DashDotDotLine", "NoPen").
             Default is None
            linewidth: line width (pixels). Default is None
            marker: marker shape (MATLAB-like string or "Cross",
             "Ellipse", "Star1", "XCross", "Rect", "Diamond", "UTriangle",
             "DTriangle", "RTriangle", "LTriangle", "Star2", "NoSymbol").
             Default is None
            markersize: marker size (pixels). Default is None
            markerfacecolor: marker face color name. Default is None
            markeredgecolor: marker edge color name. Default is None
            shade: 0 <= float <= 1 (curve shade). Default is None
            curvestyle: "Lines", "Sticks", "Steps", "Dots", "NoCurve".
             Default is None
            baseline: baseline value. Default is None
            xaxis: x axis name. Default is 'bottom'
            yaxis: y axis name. Default is 'left'
            dx: x error data. Default is None
            dy: y error data. Default is None
            errorbarwidth: error bar width (pixels). Default is None
            errorbarcap: error bar cap size (pixels). Default is None
            errorbarmode: error bar mode ("Vertical", "Horizontal",
             "Both"). Default is None
            errorbaralpha: 0 <= float <= 1 (error bar transparency).
             Default is None

        Returns:
            :py:class:`.CurveItem` object

        Example::
            curve(x, y, marker='Ellipse', markerfacecolor='#ffffff')

        which is equivalent to (MATLAB-style support)::

            curve(x, y, marker='o', markerfacecolor='w')
        """

        if dx is not None or dy is not None:
            return self.error(
                x,
                y,
                dx,
                dy,
                title=title,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                errorbarwidth=errorbarwidth,
                errorbarcap=errorbarcap,
                errorbarmode=errorbarmode,
                errorbaralpha=errorbaralpha,
                marker=marker,
                markersize=markersize,
                markerfacecolor=markerfacecolor,
                markeredgecolor=markeredgecolor,
                shade=shade,
                curvestyle=curvestyle,
                baseline=baseline,
                xaxis=xaxis,
                yaxis=yaxis,
            )

        basename = _("Curve")
        param = CurveParam(title=basename, icon="curve.png")
        if not title:
            global CURVE_COUNT
            CURVE_COUNT += 1
            title = make_title(basename, CURVE_COUNT)
        self.__set_param(
            param,
            title,
            color,
            linestyle,
            linewidth,
            marker,
            markersize,
            markerfacecolor,
            markeredgecolor,
            shade,
            curvestyle,
            baseline,
        )
        return self.pcurve(x, y, param, xaxis, yaxis)

    def merror(self, *args, **kwargs) -> ErrorBarCurveItem:
        """Make an errorbar curve `plot item` based on MATLAB-like syntax

        Args:
            \*args: x, y, dx, dy, style
            \*\*kwargs: title, color, linestyle, linewidth, marker, markersize,
             markerfacecolor, markeredgecolor, shade, curvestyle, baseline,
             xaxis, yaxis, errorbarwidth, errorbarcap, errorbarmode,
             errorbaralpha

        Returns:
            :py:class:`.ErrorBarCurveItem` object

        Example::
            mcurve(x, y, 'r+')
        """  # noqa: E501
        x, y, dx, dy, style = self.__get_arg_triple_errorbar(args)
        basename = _("Curve")
        curveparam = CurveParam(title=basename, icon="curve.png")
        errorbarparam = ErrorBarParam(title=_("Error bars"), icon="errorbar.png")
        if "label" in kwargs:
            curveparam.label = kwargs["label"]
        else:
            global CURVE_COUNT
            CURVE_COUNT += 1
            curveparam.label = make_title(basename, CURVE_COUNT)
        update_style_attr(style, curveparam)
        errorbarparam.color = curveparam.line.color
        return self.perror(x, y, dx, dy, curveparam, errorbarparam)

    def perror(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        dx: numpy.ndarray,
        dy: numpy.ndarray,
        curveparam: CurveParam,
        errorbarparam: ErrorBarParam,
        xaxis: str = "bottom",
        yaxis: str = "left",
    ) -> ErrorBarCurveItem:
        """Make an errorbar curve `plot item`
        based on a :py:class:`.ErrorBarParam` instance

        Args:
            x: x data
            y: y data
            dx: x error data
            dy: y error data
            curveparam: curve style
            errorbarparam: error bar style
            xaxis: x axis name. Default is 'bottom'
            yaxis: y axis name. Default is 'left'

        Returns:
            :py:class:`.ErrorBarCurveItem` object

        Example::
            perror(x, y, dx, dy, curveparam, errorbarparam)
        """
        curve = ErrorBarCurveItem(curveparam, errorbarparam)
        curve.set_data(x, y, dx, dy)
        curve.update_params()
        self.__set_curve_axes(curve, xaxis, yaxis)
        return curve

    def error(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        dx: numpy.ndarray,
        dy: numpy.ndarray,
        title: str = "",
        color: str | None = None,
        linestyle: str | None = None,
        linewidth: float | None = None,
        errorbarwidth: int | None = None,
        errorbarcap: int | None = None,
        errorbarmode: str | None = None,
        errorbaralpha: float | None = None,
        marker: str | None = None,
        markersize: float | None = None,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
        shade: bool | None = None,
        curvestyle: str | None = None,
        baseline: float | None = None,
        xaxis: str = "bottom",
        yaxis: str = "left",
    ) -> ErrorBarCurveItem:
        """Make an errorbar curve `plot item`

        Args:
            x: x data
            y: y data
            dx: x error data
            dy: y error data
            title: curve title. Default is ''
            color: curve color name. Default is None
            linestyle: curve line style (MATLAB-like string or attribute
             name from the `PyQt5.QtCore.Qt.PenStyle` enum
             (i.e. "SolidLine" "DashLine", "DotLine", "DashDotLine",
             "DashDotDotLine" or "NoPen"). Default is None
            linewidth: line width (pixels). Default is None
            errorbarwidth: error bar width (pixels). Default is None
            errorbarcap: error bar cap length (pixels). Default is None
            errorbarmode: error bar mode (MATLAB-like string or attribute
             name from the `qwt.QwtPlotCurve.ErrorBar` enum
             (i.e. "NoError", "ErrorBar", "ErrorSymbol", "ErrorBarSymbol",
             "ErrorBarCurve"). Default is None
            errorbaralpha: error bar alpha value (0.0 transparent
             through 1.0 opaque). Default is None
            marker: marker shape (MATLAB-like string or attribute name
             from the `qwt.QwtSymbol.Style` enum (i.e. "Cross",
             "Ellipse", "Star1", "XCross", "Rect", "Diamond", "UTriangle",
             "DTriangle", "RTriangle", "LTriangle", "NoSymbol"). Default is None
            markersize: marker size (pixels). Default is None
            markerfacecolor: marker face color name. Default is None
            markeredgecolor: marker edge color name. Default is None
            shade: shade under curve. Default is None
            curvestyle: curve style (MATLAB-like string or attribute name
             from the `qwt.QwtPlotCurve.CurveStyle` enum (i.e. "NoCurve",
             "Lines", "Sticks", "Steps", "Dots"). Default is None
            baseline: baseline value. Default is None
            xaxis: x axis name. Default is 'bottom'
            yaxis: y axis name. Default is 'left'

        Returns:
            :py:class:`.ErrorBarCurveItem` object

        Example::
            error(x, y, None, dy, marker='Ellipse', markerfacecolor='#ffffff')
        which is equivalent to (MATLAB-style support)::
            error(x, y, None, dy, marker='o', markerfacecolor='w')
        """
        basename = _("Curve")
        curveparam = CurveParam(title=basename, icon="curve.png")
        errorbarparam = ErrorBarParam(title=_("Error bars"), icon="errorbar.png")
        if not title:
            global CURVE_COUNT
            CURVE_COUNT += 1
            curveparam.label = make_title(basename, CURVE_COUNT)
        self.__set_param(
            curveparam,
            title,
            color,
            linestyle,
            linewidth,
            marker,
            markersize,
            markerfacecolor,
            markeredgecolor,
            shade,
            curvestyle,
            baseline,
        )
        errorbarparam.color = curveparam.line.color
        if errorbarwidth is not None:
            errorbarparam.width = errorbarwidth
        if errorbarcap is not None:
            errorbarparam.cap = errorbarcap
        if errorbarmode is not None:
            errorbarparam.mode = errorbarmode
        if errorbaralpha is not None:
            errorbarparam.alpha = errorbaralpha
        return self.perror(x, y, dx, dy, curveparam, errorbarparam, xaxis, yaxis)

    def histogram(
        self,
        data: numpy.ndarray,
        bins: int | None = None,
        logscale: bool | None = None,
        title: str = "",
        color: str | None = None,
        xaxis: str = "bottom",
        yaxis: str = "left",
    ) -> HistogramItem:
        """Make 1D Histogram `plot item`

        Args:
            data: data
            bins: number of bins. Default is None
            logscale: Y-axis scale. Default is None
            title: curve title. Default is ''
            color: curve color name. Default is None
            xaxis: x axis name. Default is 'bottom'
            yaxis: y axis name. Default is 'left'

        Returns:
            :py:class:`.HistogramItem` object
        """
        basename = _("Histogram")
        histparam = HistogramParam(title=basename, icon="histogram.png")
        curveparam = CurveParam(_("Curve"), icon="curve.png")
        curveparam.read_config(CONF, "histogram", "curve")
        if not title:
            global HISTOGRAM_COUNT
            HISTOGRAM_COUNT += 1
            title = make_title(basename, HISTOGRAM_COUNT)
        curveparam.label = title
        if color is not None:
            curveparam.line.color = color
        if bins is not None:
            histparam.n_bins = bins
        if logscale is not None:
            histparam.logscale = logscale
        return self.phistogram(data, curveparam, histparam, xaxis, yaxis)

    def phistogram(
        self,
        data: numpy.ndarray,
        curveparam: CurveParam,
        histparam: HistogramParam,
        xaxis: str = "bottom",
        yaxis: str = "left",
    ) -> HistogramItem:
        """Make 1D histogram `plot item` based on a :py:class:`.CurveParam` and
        :py:class:`.HistogramParam` instances

        Args:
            data: data
            curveparam: curve parameters
            histparam: histogram parameters
            xaxis: x axis name. Default is 'bottom'
            yaxis: y axis name. Default is 'left'

        Returns:
            :py:class:`.HistogramItem` object

        Example::
            phistogram(data, curveparam, histparam)
        """
        hist = HistogramItem(curveparam, histparam)
        hist.update_params()
        hist.set_hist_data(data)
        self.__set_curve_axes(hist, xaxis, yaxis)
        return hist

    def __set_image_param(
        self,
        param: ImageParam,
        title: str | None,
        alpha_function: LUTAlpha | None,
        alpha: float | None,
        interpolation: str,
        **kwargs,
    ) -> None:
        if title:
            param.label = title
        else:
            global IMAGE_COUNT
            IMAGE_COUNT += 1
            param.label = make_title(_("Image"), IMAGE_COUNT)
        if alpha_function is not None:
            assert isinstance(alpha_function, LUTAlpha)
            param.alpha_function = alpha_function.value
        if alpha is not None:
            assert 0.0 <= alpha <= 1.0
            param.alpha = alpha
        interp_methods = {"nearest": 0, "linear": 1, "antialiasing": 5}
        param.interpolation = interp_methods[interpolation]
        for key, val in list(kwargs.items()):
            if val is not None:
                setattr(param, key, val)

    def _get_image_data(
        self,
        data: numpy.ndarray,
        filename: str | None,
        title: str | None,
        to_grayscale: bool,
    ) -> tuple[numpy.ndarray, str | None, str | None]:
        if data is None:
            assert filename is not None
            data = io.imread(filename, to_grayscale=to_grayscale)
        if title is None and filename is not None:
            title = osp.basename(filename)
        return data, filename, title

    @staticmethod
    def compute_bounds(
        data: numpy.ndarray,
        pixel_size: float | tuple[float, float],
        center_on: tuple[float, float] | None = None,
    ) -> tuple[float, float, float, float]:
        """Return image bounds from *pixel_size* (scalar or tuple)

        Args:
            data: image data
            pixel_size: pixel size
            center_on: center coordinates. Default is None

        Returns:
            tuple: xmin, xmax, ymin, ymax
        """
        if not isinstance(pixel_size, (tuple, list)):
            pixel_size = [pixel_size, pixel_size]
        dx, dy = pixel_size
        xmin, ymin = 0.0, 0.0
        xmax, ymax = data.shape[1] * dx, data.shape[0] * dy
        if center_on is not None:
            xc, yc = center_on
            dx, dy = 0.5 * (xmax - xmin) - xc, 0.5 * (ymax - ymin) - yc
            xmin -= dx
            xmax -= dx
            ymin -= dy
            ymax -= dy
        return xmin, xmax, ymin, ymax

    def image(
        self,
        data: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | None = None,
        alpha: float | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        xdata: list[float] = [None, None],
        ydata: list[float] = [None, None],
        pixel_size: float | tuple[float, float] | None = None,
        center_on: tuple[float, float] | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        x: numpy.ndarray | None = None,
        y: numpy.ndarray | None = None,
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = False,
    ) -> ImageItem:
        """Make an image `plot item` from data

        Args:
            data: data. Default is None
            filename: image filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is None
            background_color: background color name. Default is None
            colormap: colormap name. Default is None
            xdata: x data. Default is [None, None]
            ydata: y data. Default is [None, None]
            pixel_size: pixel size. Default is None
            center_on: center on. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            x: x data. Default is None
            y: y data. Default is None
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.ImageItem` object or
            :py:class:`.RGBImageItem` object if data has 3 dimensions
        """
        if x is not None or y is not None:
            assert pixel_size is None and center_on is None, (
                "Ambiguous parameters:"
                "both `x`/`y` and `pixel_size`/`center_on`/`xdata`/`ydata`"
                " were specified"
            )
            return self.xyimage(
                x,
                y,
                data,
                title=title,
                alpha_function=alpha_function,
                alpha=alpha,
                background_color=background_color,
                colormap=colormap,
                interpolation=interpolation,
                eliminate_outliers=eliminate_outliers,
                xformat=xformat,
                yformat=yformat,
                zformat=zformat,
                lut_range=lut_range,
                lock_position=lock_position,
            )

        assert isinstance(xdata, (tuple, list)) and len(xdata) == 2
        assert isinstance(ydata, (tuple, list)) and len(ydata) == 2
        param = ImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=True
        )
        if data.ndim == 3:
            return self.rgbimage(
                data=data,
                filename=filename,
                title=title,
                alpha_function=alpha_function,
                alpha=alpha,
            )
        assert data.ndim == 2, "Data must have 2 dimensions"
        if pixel_size is None:
            assert center_on is None, (
                "Ambiguous parameters: both `center_on`"
                " and `xdata`/`ydata` were specified"
            )
            xmin, xmax = xdata
            ymin, ymax = ydata
        else:
            xmin, xmax, ymin, ymax = self.compute_bounds(data, pixel_size, center_on)
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = ImageItem(data, param)
        image.set_filename(filename)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_range(lut_range_threshold(image, 256, eliminate_outliers))
        return image

    def maskedimage(
        self,
        data: numpy.ndarray | None = None,
        mask: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | None = None,
        alpha: float = 1.0,
        xdata: list[float] = [None, None],
        ydata: list[float] = [None, None],
        pixel_size: float | tuple[float, float] | None = None,
        center_on: tuple[float, float] | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        show_mask: bool = False,
        fill_value: float | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        x: numpy.ndarray | None = None,
        y: numpy.ndarray | None = None,
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = True,
    ) -> ImageItem | RGBImageItem:
        """Make a masked image `plot item` from data

        Args:
            data: data. Default is None
            mask: mask. Default is None
            filename: image filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is 1.0
            xdata: x data. Default is [None, None]
            ydata: y data. Default is [None, None]
            pixel_size: pixel size. Default is None
            center_on: center on. Default is None
            background_color: background color. Default is None
            colormap: colormap. Default is None
            show_mask: show mask. Default is False
            fill_value: fill value. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            x: x data. Default is None
            y: y data. Default is None
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.MaskedImageItem` object
        """
        if x is not None or y is not None:
            assert pixel_size is None and center_on is None, (
                "Ambiguous parameters:"
                "both `x`/`y` and `pixel_size`/`center_on`/`xdata`/`ydata`"
                " were specified"
            )
            return self.maskedxyimage(
                x,
                y,
                data,
                mask=mask,
                title=title,
                alpha_function=alpha_function,
                alpha=alpha,
                background_color=background_color,
                colormap=colormap,
                show_mask=show_mask,
                fill_value=fill_value,
                interpolation=interpolation,
                eliminate_outliers=eliminate_outliers,
                xformat=xformat,
                yformat=yformat,
                zformat=zformat,
                lut_range=lut_range,
                lock_position=lock_position,
            )

        assert isinstance(xdata, (tuple, list)) and len(xdata) == 2
        assert isinstance(ydata, (tuple, list)) and len(ydata) == 2
        param = MaskedImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=True
        )
        assert data.ndim == 2, "Data must have 2 dimensions"
        if pixel_size is None:
            assert center_on is None, (
                "Ambiguous parameters: both `center_on`"
                " and `xdata`/`ydata` were specified"
            )
            xmin, xmax = xdata
            ymin, ymax = ydata
        else:
            xmin, xmax, ymin, ymax = self.compute_bounds(data, pixel_size, center_on)
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            show_mask=show_mask,
            fill_value=fill_value,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = MaskedImageItem(data, mask, param)
        image.set_filename(filename)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_range(lut_range_threshold(image, 256, eliminate_outliers))
        return image

    def maskedxyimage(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        data: numpy.ndarray,
        mask: numpy.ndarray | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | None = None,
        alpha: float = 1.0,
        background_color: str | None = None,
        colormap: str | None = None,
        show_mask: bool = False,
        fill_value: float | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = True,
    ) -> MaskedImageItem:
        """Make a masked XY image `plot item` from data

        Args:
            x: x data
            y: y data
            data: data
            mask: mask. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is 1.0
            background_color: background color. Default is None
            colormap: colormap. Default is None
            show_mask: show mask. Default is False
            fill_value: fill value. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.MaskedXYImageItem` object
        """

        if isinstance(x, (list, tuple)):
            x = np.array(x)
        if isinstance(y, (list, tuple)):
            y = np.array(y)

        param = MaskedXYImageParam(title=_("Image"), icon="image.png")
        assert data.ndim == 2, "Data must have 2 dimensions"

        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            show_mask=show_mask,
            fill_value=fill_value,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = MaskedXYImageItem(x, y, data, mask, param)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_range(lut_range_threshold(image, 256, eliminate_outliers))
        return image

    def rgbimage(
        self,
        data: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | None = None,
        alpha: float = 1.0,
        xdata: list | tuple = [None, None],
        ydata: list | tuple = [None, None],
        pixel_size: float | None = None,
        center_on: tuple | None = None,
        interpolation: str = "linear",
        lock_position: bool = True,
    ) -> RGBImageItem:
        """Make a RGB image `plot item` from data

        Args:
            data: data
            filename: filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is 1.0
            xdata: x data. Default is [None, None]
            ydata: y data. Default is [None, None]
            pixel_size: pixel size. Default is None
            center_on: center on. Default is None
            interpolation: interpolation method. Default is 'linear'
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.RGBImageItem` object
        """
        assert isinstance(xdata, (tuple, list)) and len(xdata) == 2
        assert isinstance(ydata, (tuple, list)) and len(ydata) == 2
        param = RGBImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=False
        )
        assert data.ndim == 3, "RGB data must have 3 dimensions"
        if pixel_size is None:
            assert center_on is None, (
                "Ambiguous parameters: both `center_on`"
                " and `xdata`/`ydata` were specified"
            )
            xmin, xmax = xdata
            ymin, ymax = ydata
        else:
            xmin, xmax, ymin, ymax = self.compute_bounds(data, pixel_size, center_on)
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            lock_position=lock_position,
        )
        image = RGBImageItem(data, param)
        image.set_filename(filename)
        return image

    def quadgrid(
        self,
        X: numpy.ndarray,
        Y: numpy.ndarray,
        Z: numpy.ndarray,
        title: str | None = None,
        alpha_function: LUTAlpha | None = None,
        alpha: float | None = None,
        colormap: str | None = None,
        interpolation: str = "linear",
        lock_position: bool = True,
    ) -> QuadGridItem:
        """Make a pseudocolor `plot item` of a 2D array

        Args:
            X: x data
            Y: y data
            Z: data
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is None
            colormap: colormap. Default is None
            interpolation: interpolation method. Default is 'linear'
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.QuadGridItem` object
        """
        param = QuadGridParam(title=_("Image"), icon="image.png")
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            colormap=colormap,
            lock_position=lock_position,
        )
        image = QuadGridItem(X, Y, Z, param)
        return image

    def pcolor(self, *args, **kwargs) -> QuadGridItem:
        """Make a pseudocolor `plot item` of a 2D array
        based on MATLAB-like syntax

        Args:
            \*args: non-keyword arguments
            \*\*kwargs: keyword arguments

        Returns:
            :py:class:`.QuadGridItem` object

        Examples::
            pcolor(C)
            pcolor(X, Y, C)
        """  # noqa: E501
        if len(args) == 1:
            (Z,) = args
            M, N = Z.shape
            X, Y = np.meshgrid(np.arange(N, dtype=Z.dtype), np.arange(M, dtype=Z.dtype))
        elif len(args) == 3:
            X, Y, Z = args
        else:
            raise RuntimeError("1 or 3 non-keyword arguments expected")
        return self.quadgrid(X, Y, Z, **kwargs)

    def trimage(
        self,
        data: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: bool | None = None,
        alpha: float | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        x0: float = 0.0,
        y0: float = 0.0,
        angle: float = 0.0,
        dx: float = 1.0,
        dy: float = 1.0,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = False,
    ):
        """Make a transformable image `plot item` (image with an arbitrary
        affine transform)

        Args:
            data: data
            filename: filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is None
            background_color: background color. Default is None
            colormap: colormap. Default is None
            x0: x position. Default is 0.0
            y0: y position. Default is 0.0
            angle: angle (radians). Default is 0.0
            dx: pixel size along X axis. Default is 1.0
            dy: pixel size along Y axis. Default is 1.0
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is False

        Returns:
            :py:class:`.TrImageItem` object
        """
        param = TrImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=True
        )
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            x0=x0,
            y0=y0,
            angle=angle,
            dx=dx,
            dy=dy,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = TrImageItem(data, param)
        image.set_filename(filename)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_range(lut_range_threshold(image, 256, eliminate_outliers))
        return image

    def xyimage(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        data: numpy.ndarray,
        title: str | None = None,
        alpha_function: bool | None = None,
        alpha: float | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = False,
    ) -> XYImageItem:
        """Make an xyimage `plot item` (image with non-linear X/Y axes) from data

        Args:
            x: X coordinates
            y: Y coordinates
            data: data
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
            alpha: alpha value. Default is None
            background_color: background color. Default is None
            colormap: colormap. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.XYImageItem` object
        """
        param = XYImageParam(title=_("Image"), icon="image.png")
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        if isinstance(x, (list, tuple)):
            x = np.array(x)
        if isinstance(y, (list, tuple)):
            y = np.array(y)
        image = XYImageItem(x, y, data, param)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_range(lut_range_threshold(image, 256, eliminate_outliers))
        return image

    def imagefilter(
        self,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        imageitem: ImageItem,
        filter: Callable,
        title: str | None = None,
    ) -> ImageFilterItem:
        """Make a rectangular area image filter `plot item`

        Args:
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            imageitem: image item
            filter: filter function
            title: filter title. Default is None

        Returns:
            :py:class:`.ImageFilterItem` object
        """
        param = ImageFilterParam(_("Filter"), icon="funct.png")
        param.xmin, param.xmax, param.ymin, param.ymax = xmin, xmax, ymin, ymax
        if title is not None:
            param.label = title
        filt = imageitem.get_filter(filter, param)
        _m, _M = imageitem.get_lut_range()
        filt.set_lut_range([_m, _M])
        return filt

    def contours(
        self,
        Z: np.ndarray,
        levels: float | np.ndarray,
        X: np.ndarray | None = None,
        Y: np.ndarray | None = None,
    ) -> list[ContourShape]:
        """Make a contour curves

        Args:
            Z: The height values over which the contour is drawn.
            levels : Determines the number and positions of the contour lines/regions.
             If a float, draw contour lines at this specified levels
             If array-like, draw contour lines at the specified levels.
             The values must be in increasing order.
            X: The coordinates of the values in *Z*.
             *X* must be 2-D with the same shape as *Z* (e.g. created via
             ``numpy.meshgrid``), or it must both be 1-D such that ``len(X) == M``
             is the number of columns in *Z*.
             If none, they are assumed to be integer indices, i.e. ``X = range(M)``.
            Y: The coordinates of the values in *Z*.
             *Y* must be 2-D with the same shape as *Z* (e.g. created via
             ``numpy.meshgrid``), or it must both be 1-D such that ``len(Y) == N``
             is the number of rows in *Z*.
             If none, they are assumed to be integer indices, i.e. ``Y = range(N)``.
        """
        items = []
        lines = contour(X, Y, Z, levels)
        for line in lines:
            param = ShapeParam("Contour", icon="contour.png")
            item = ContourShape(points=line.vertices, shapeparam=param)
            item.set_style("plot", "shape/contour")
            item.setTitle(_("Contour") + f"[Z={line.level}]")
            items.append(item)
        return items

    def histogram2D(
        self,
        X: numpy.ndarray,
        Y: numpy.ndarray,
        NX: int | None = None,
        NY: int | None = None,
        logscale: bool | None = None,
        title: str | None = None,
        transparent: bool | None = None,
        Z: numpy.ndarray | None = None,
        computation: int = -1,
        interpolation: int = 0,
        lock_position: bool = True,
    ) -> Histogram2DItem:
        """Make a 2D Histogram `plot item`

        Args:
            X: X data
            Y: Y data
            NX: number of bins along x-axis. Default is None
            NY: number of bins along y-axis. Default is None
            logscale: Z-axis scale. Default is None
            title: item title. Default is None
            transparent: enable transparency. Default is None
            Z: Z data. Default is None
            computation: computation mode. Default is -1
            interpolation: interpolation mode. Default is 0
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.Histogram2DItem` object
        """
        basename = _("2D Histogram")
        param = Histogram2DParam(title=basename, icon="histogram2d.png")
        if NX is not None:
            param.nx_bins = NX
        if NY is not None:
            param.ny_bins = NY
        if logscale is not None:
            param.logscale = int(logscale)
        if title is not None:
            param.label = title
        else:
            global HISTOGRAM2D_COUNT
            HISTOGRAM2D_COUNT += 1
            param.label = make_title(basename, HISTOGRAM2D_COUNT)
        if transparent is not None:
            param.transparent = transparent
        param.computation = computation
        param.interpolation = interpolation
        param.lock_position = lock_position
        return Histogram2DItem(X, Y, param, Z=Z)

    def label(
        self,
        text: str,
        g: tuple[float, float] | str,
        c: tuple[int, int],
        anchor: str,
        title: str = "",
    ) -> LabelItem:
        """Make a label `plot item`

        Args:
            text: label text
            g: position in plot coordinates or relative position (string)
            c: position in canvas coordinates
            anchor: anchor position in relative position (string)
            title: label title. Default is ''

        Returns:
            :py:class:`.LabelItem` object

        Examples::
            make.label("Relative position", (x[0], y[0]), (10, 10), "BR")
            make.label("Absolute position", "R", (0,0), "R")
        """
        basename = _("Label")
        param = LabelParamWithContents(basename, icon="label.png")
        param.read_config(CONF, "plot", "label")
        if title:
            param.label = title
        else:
            global LABEL_COUNT
            LABEL_COUNT += 1
            param.label = make_title(basename, LABEL_COUNT)
        if isinstance(g, tuple):
            param.abspos = False
            param.xg, param.yg = g
        else:
            param.abspos = True
            param.absg = g
        if c is None:
            c = ANCHOR_OFFSETS[anchor]
        param.xc, param.yc = c
        param.anchor = anchor
        return LabelItem(text, param)

    def legend(
        self,
        anchor: str = "TR",
        c: tuple[int, int] | None = None,
        restrict_items: list | None = None,
    ) -> LegendBoxItem | SelectedLegendBoxItem:
        """Make a legend `plot item`

        Args:
            anchor: legend position in relative position (string)
            c: position in canvas coordinates
            restrict_items: list of items to be shown in legend box.
             Default is None. If None, all items are shown in legend box.
             If [], no item is shown in legend box. If [item1, item2],
             item1, item2 are shown in legend box.

        Returns:
            :py:class:`.LegendBoxItem` or
            :py:class:`.SelectedLegendBoxItem` object
        """
        param = LegendParam(_("Legend"), icon="legend.png")
        param.read_config(CONF, "plot", "legend")
        param.abspos = True
        param.absg = anchor
        param.anchor = anchor
        if c is None:
            c = ANCHOR_OFFSETS[anchor]
        param.xc, param.yc = c
        if restrict_items is None:
            return LegendBoxItem(param)
        else:
            return SelectedLegendBoxItem(param, restrict_items)

    def range(self, xmin: float, xmax: float) -> XRangeSelection:
        """Make a range `plot item`

        Args:
            xmin: minimum value
            xmax: maximum value

        Returns:
            :py:class:`.XRangeSelection` object
        """
        return XRangeSelection(xmin, xmax)

    def vcursor(
        self,
        x: float,
        label: str | None = None,
        constraint_cb: Callable | None = None,
        movable: bool = True,
        readonly: bool = False,
    ) -> Marker:
        """Make a vertical cursor `plot item`

        Args:
            x: cursor position
            label: cursor label. Default is None
            constraint_cb: constraint callback. Default is None
            movable: enable/disable cursor move. Default is True
            readonly: enable/disable cursor edition. Default is False

        Returns:
            :py:class:`.Marker` object
        """
        if label is None:

            def label_cb(x, y):
                """Label callback"""
                return ""

        else:

            def label_cb(x, y):
                """Label callback"""
                return label % x

        return self.marker(
            position=(x, 0),
            markerstyle="|",
            label_cb=label_cb,
            constraint_cb=constraint_cb,
            movable=movable,
            readonly=readonly,
        )

    def hcursor(
        self,
        y: float,
        label: str | None = None,
        constraint_cb: Callable | None = None,
        movable: bool = True,
        readonly: bool = False,
    ) -> Marker:
        """Make an horizontal cursor `plot item`

        Args:
            y: cursor position
            label: cursor label. Default is None
            constraint_cb: constraint callback. Default is None
            movable: enable/disable cursor move. Default is True
            readonly: enable/disable cursor edition. Default is False

        Returns:
            :py:class:`.Marker` object
        """
        if label is None:

            def label_cb(x, y):
                """Label callback"""
                return ""

        else:

            def label_cb(x, y):
                """Label callback"""
                return label % y

        return self.marker(
            position=(0, y),
            markerstyle="-",
            label_cb=label_cb,
            constraint_cb=constraint_cb,
            movable=movable,
            readonly=readonly,
        )

    def xcursor(
        self,
        x: float,
        y: float,
        label: str | None = None,
        constraint_cb: Callable | None = None,
        movable: bool = True,
        readonly: bool = False,
    ) -> Marker:
        """Make a cross cursor `plot item`

        Args:
            x: cursor position
            y: cursor position
            label: cursor label. Default is None
            constraint_cb: constraint callback. Default is None
            movable: enable/disable cursor move. Default is True
            readonly: enable/disable cursor edition. Default is False

        Returns:
            :py:class:`.Marker` object
        """
        if label is None:

            def label_cb(x, y):
                """Label callback"""
                return ""

        else:

            def label_cb(x, y):
                """Label callback"""
                return label % (x, y)

        return self.marker(
            position=(x, y),
            markerstyle="+",
            label_cb=label_cb,
            constraint_cb=constraint_cb,
            movable=movable,
            readonly=readonly,
        )

    def marker(
        self,
        position: tuple[float, float] | None = None,
        label_cb: Callable | None = None,
        constraint_cb: Callable | None = None,
        movable: bool = True,
        readonly: bool = False,
        markerstyle: str | None = None,
        markerspacing: float | None = None,
        color: str | None = None,
        linestyle: str | None = None,
        linewidth: float | None = None,
        marker: str | None = None,
        markersize: float | None = None,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
    ) -> Marker:
        """Make a marker `plot item`

        Args:
            position: marker position
            label_cb: label callback. Default is None
            constraint_cb: constraint callback. Default is None
            movable: enable/disable marker move. Default is True
            readonly: enable/disable marker edition. Default is False
            markerstyle: marker style. Default is None
            markerspacing: spacing between text and marker line.
             Default is None
            color: marker color name. Default is None
            linestyle: marker line style (MATLAB-like string or attribute
             name from the `PyQt5.QtCore.Qt.PenStyle` enum
             (i.e. "SolidLine" "DashLine", "DotLine", "DashDotLine",
             "DashDotDotLine" or "NoPen"). Default is None
            linewidth: line width (pixels). Default is None
            marker: marker shape (MATLAB-like string or "Cross", "Plus",
             "Circle", "Disc", "Square", "Diamond", "TriangleUp",
             "TriangleDown", "TriangleLeft", "TriangleRight", "TriRight",
             "TriLeft", "TriDown", "TriUp", "Octagon", "Star1", "Star2",
             "Pentagon", "Hexagon1", "Hexagon2", "Plus (filled)", "Cross
             (filled)", "Square (filled)", "Diamond (filled)", "TriangleUp
             (filled)", "TriangleDown (filled)", "TriangleLeft (filled)",
             "TriangleRight (filled)", "TriRight (filled)", "TriLeft
             (filled)", "TriDown (filled)", "TriUp (filled)", "Octagon
             (filled)", "Star1 (filled)", "Star2 (filled)", "Pentagon
             (filled)", "Hexagon1 (filled)", "Hexagon2 (filled)"). Default is
             None
            markersize: marker size (pixels). Default is None
            markerfacecolor: marker face color name. Default is None
            markeredgecolor: marker edge color name. Default is None

        Returns:
            :py:class:`.Marker` object
        """
        param = MarkerParam(_("Marker"), icon="marker.png")
        param.read_config(CONF, "plot", "marker/cursor")
        if (
            color
            or linestyle
            or linewidth
            or marker
            or markersize
            or markerfacecolor
            or markeredgecolor
        ):
            param.line = param.sel_line
            param.symbol = param.sel_symbol
            param.text = param.sel_text
            self.__set_baseparam(
                param,
                color,
                linestyle,
                linewidth,
                marker,
                markersize,
                markerfacecolor,
                markeredgecolor,
            )
            param.sel_line = param.line
            param.sel_symbol = param.symbol
            param.sel_text = param.text
        if markerstyle:
            param.set_markerstyle(markerstyle)
        if markerspacing:
            param.spacing = markerspacing
        if not movable:
            param.symbol.marker = param.sel_symbol.marker = "NoSymbol"
        marker = Marker(
            label_cb=label_cb, constraint_cb=constraint_cb, markerparam=param
        )
        if position is not None:
            x, y = position
            marker.set_pos(x, y)
        marker.set_readonly(readonly)
        if not movable:
            marker.set_movable(False)
            marker.set_resizable(False)
        return marker

    def __shape(self, shapeclass, x0, y0, x1, y1, title=None):
        shape = shapeclass(x0, y0, x1, y1)
        shape.set_style("plot", "shape/drag")
        if title is not None:
            shape.setTitle(title)
        return shape

    def rectangle(
        self, x0: float, y0: float, x1: float, y1: float, title: str | None = None
    ) -> RectangleShape:
        """Make a rectangle shape `plot item`

        Args:
            x0: rectangle x0 coordinate
            y0: rectangle y0 coordinate
            x1: rectangle x1 coordinate
            y1: rectangle y1 coordinate
            title: label name. Default is None

        Returns:
            :py:class:`.RectangleShape` object
        """
        return self.__shape(RectangleShape, x0, y0, x1, y1, title)

    def ellipse(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        x2: float | None = None,
        y2: float | None = None,
        x3: float | None = None,
        y3: float | None = None,
        title: str | None = None,
    ) -> EllipseShape:
        """Make an ellipse shape `plot item`

        Args:
            x0: ellipse x0 coordinate
            y0: ellipse y0 coordinate
            x1: ellipse x1 coordinate
            y1: ellipse y1 coordinate
            x2: ellipse x2 coordinate. Default is None
            y2: ellipse y2 coordinate. Default is None
            x3: ellipse x3 coordinate. Default is None
            y3: ellipse y3 coordinate. Default is None
            title: label name. Default is None

        Returns:
            :py:class:`.EllipseShape` object
        """
        item = self.__shape(EllipseShape, x0, y0, x1, y1, title)
        item.switch_to_ellipse()
        if x2 is not None and y2 is not None and x3 is not None and y3 is not None:
            item.set_ydiameter(x2, y2, x3, y3)
        return item

    def circle(
        self, x0: float, y0: float, x1: float, y1: float, title: str | None = None
    ) -> EllipseShape:
        """Make a circle shape `plot item`

        Args:
            x0: circle x0 coordinate
            y0: circle y0 coordinate
            x1: circle x1 coordinate
            y1: circle y1 coordinate
            title: label name. Default is None

        Returns:
            :py:class:`.EllipseShape` object
        """
        item = self.__shape(EllipseShape, x0, y0, x1, y1, title)
        item.switch_to_circle()
        return item

    def segment(
        self, x0: float, y0: float, x1: float, y1: float, title: str | None = None
    ) -> SegmentShape:
        """Make a segment shape `plot item`

        Args:
            x0: segment x0 coordinate
            y0: segment y0 coordinate
            x1: segment x1 coordinate
            y1: segment y1 coordinate
            title: label name. Default is None

        Returns:
            :py:class:`.SegmentShape` object
        """
        return self.__shape(SegmentShape, x0, y0, x1, y1, title)

    def __get_annotationparam(self, title: str, subtitle: str) -> AnnotationParam:
        param = AnnotationParam(_("Annotation"), icon="annotation.png")
        if title is not None:
            param.title = title
        if subtitle is not None:
            param.subtitle = subtitle
        return param

    def annotated_point(
        self, x: float, y: float, title: str | None = None, subtitle: str | None = None
    ) -> AnnotatedPoint:
        """Make an annotated point `plot item`

        Args:
            x: point x coordinate
            y: point y coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None

        Returns:
            :py:class:`.AnnotatedPoint` object
        """
        param = self.__get_annotationparam(title, subtitle)
        shape = AnnotatedPoint(x, y, param)
        shape.set_style("plot", "shape/drag")
        return shape

    def __annotated_shape(self, shapeclass, x0, y0, x1, y1, title, subtitle):
        param = self.__get_annotationparam(title, subtitle)
        shape = shapeclass(x0, y0, x1, y1, param)
        shape.set_style("plot", "shape/drag")
        return shape

    def annotated_rectangle(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> AnnotatedRectangle:
        """Make an annotated rectangle `plot item`

        Args:
            x0: rectangle x0 coordinate
            y0: rectangle y0 coordinate
            x1: rectangle x1 coordinate
            y1: rectangle y1 coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None

        Returns:
            :py:class:`.AnnotatedRectangle` object
        """
        return self.__annotated_shape(
            AnnotatedRectangle, x0, y0, x1, y1, title, subtitle
        )

    def annotated_ellipse(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        x2: float = None,
        y2: float = None,
        x3: float = None,
        y3: float = None,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> AnnotatedEllipse:
        """Make an annotated ellipse `plot item`

        Args:
            x0: ellipse x0 coordinate
            y0: ellipse y0 coordinate
            x1: ellipse x1 coordinate
            y1: ellipse y1 coordinate
            x2: ellipse x2 coordinate. Default is None
            y2: ellipse y2 coordinate. Default is None
            x3: ellipse x3 coordinate. Default is None
            y3: ellipse y3 coordinate. Default is None
            title: label name. Default is None
            subtitle: label subtitle. Default is None

        Returns:
            :py:class:`.AnnotatedEllipse` object
        """
        item = self.__annotated_shape(AnnotatedEllipse, x0, y0, x1, y1, title, subtitle)
        if x2 is not None and y2 is not None and x3 is not None and y3 is not None:
            item.set_ydiameter(x2, y2, x3, y3)
        return item

    def annotated_circle(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> AnnotatedCircle:
        """Make an annotated circle `plot item`

        Args:
            x0: circle x0 coordinate
            y0: circle y0 coordinate
            x1: circle x1 coordinate
            y1: circle y1 coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None

        Returns:
            :py:class:`.AnnotatedCircle` object
        """
        return self.__annotated_shape(AnnotatedCircle, x0, y0, x1, y1, title, subtitle)

    def annotated_segment(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> AnnotatedSegment:
        """Make an annotated segment `plot item`

        Args:
            x0: segment x0 coordinate
            y0: segment y0 coordinate
            x1: segment x1 coordinate
            y1: segment y1 coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None

        Returns:
            :py:class:`.AnnotatedSegment` object
        """
        return self.__annotated_shape(AnnotatedSegment, x0, y0, x1, y1, title, subtitle)

    def info_label(
        self, anchor: str, comps: list, title: str | None = None
    ) -> DataInfoLabel:
        """Make an info label `plot item`

        Args:
            anchor: anchor position. See :py:class:`.LabelParam` for details
            comps: list of :py:class:`.label.RangeComputation` objects
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        basename = _("Computation")
        param = LabelParam(basename, icon="label.png")
        param.read_config(CONF, "plot", "info_label")
        if title is not None:
            param.label = title
        else:
            global LABEL_COUNT
            LABEL_COUNT += 1
            param.label = make_title(basename, LABEL_COUNT)
        param.abspos = True
        param.absg = anchor
        param.anchor = anchor
        c = ANCHOR_OFFSETS[anchor]
        param.xc, param.yc = c
        return DataInfoLabel(param, comps)

    def range_info_label(
        self,
        range: XRangeSelection,
        anchor: str,
        label: str,
        function: Callable = None,
        title: str | None = None,
    ) -> DataInfoLabel:
        """Make an info label `plot item` showing an XRangeSelection object infos

        Args:
            range: range selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            label: label name. See :py:class:`.DataInfoLabel` for details
            function: function to apply to the range selection object
             Default is None (default function is `lambda x, dx: (x, dx)`)
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object

        Example::

            x = linspace(-10, 10, 10)
            y = sin(sin(sin(x)))
            range = make.range(-2, 2)
            disp = make.range_info_label(range, 'BL', "x = %.1f ± %.1f cm",
                                         lambda x, dx: (x, dx))
        """
        info = RangeInfo(label, range, function)
        return make.info_label(anchor, info, title=title)

    def computation(
        self,
        range: XRangeSelection,
        anchor: str,
        label: str,
        curve: CurveItem,
        function: Callable,
        title: str | None = None,
    ) -> DataInfoLabel:
        """Make a computation label `plot item`

        Args:
            range: range selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            label: label name. See :py:class:`.DataInfoLabel` for details
            curve: curve item
            function: function to apply to the range selection object
             Default is None (default function is `lambda x, dx: (x, dx)`)

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        if title is None:
            title = curve.param.label
        return self.computations(range, anchor, [(curve, label, function)], title=title)

    def computations(
        self, range: XRangeSelection, anchor: str, specs: list, title: str | None = None
    ) -> DataInfoLabel:
        """Make computation labels  `plot item`

        Args:
            range: range selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            specs: list of (curve, label, function) tuples
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        comps = []
        same_curve = True
        curve0 = None
        for curve, label, function in specs:
            comp = RangeComputation(label, curve, range, function)
            comps.append(comp)
            if curve0 is None:
                curve0 = curve
            same_curve = same_curve and curve is curve0
        if title is None and same_curve:
            title = curve.param.label
        return self.info_label(anchor, comps, title=title)

    def computation2d(
        self,
        rect: RectangleShape,
        anchor: str,
        label: str,
        image: ImageItem,
        function: Callable,
        title: str | None = None,
    ) -> RangeComputation2d:
        """Make a 2D computation label `plot item`

        Args:
            rect: rectangle selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            label: label name. See :py:class:`.DataInfoLabel` for details
            image: image item
            function: function to apply to the rectangle selection object
             Default is None (default function is `lambda x, dx: (x, dx)`)
            title: label name. Default is None

        Returns:
            :py:class:`.RangeComputation2d` object
        """
        return self.computations2d(
            rect, anchor, [(image, label, function)], title=title
        )

    def computations2d(
        self, rect: RectangleShape, anchor: str, specs: list, title: str | None = None
    ) -> DataInfoLabel:
        """Make 2D computation labels `plot item`

        Args:
            rect: rectangle selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            specs: list of (image, label, function) tuples
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        comps = []
        same_image = True
        image0 = None
        for image, label, function in specs:
            comp = RangeComputation2d(label, image, rect, function)
            comps.append(comp)
            if image0 is None:
                image0 = image
            same_image = same_image and image is image0
        if title is None and same_image:
            title = image.param.label
        return self.info_label(anchor, comps, title=title)


#: Instance of :py:class:`.PlotItemBuilder`
make = PlotItemBuilder()
