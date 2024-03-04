# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Curve/cursor/marker Item builder
--------------------------------

This module provides a set of factory functions to simplify the creation of
curve, cursor and marker items.
"""

# Note: when adding method to builder classes, please do not forget to update the
# documentation (see builder.rst file). Because of class inheritance, the methods
# are not automatically documented (otherwise, they would be sorted alphabetically,
# due to a limitation of sphinx auto-doc).

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy  # only to help intersphinx finding numpy doc
import numpy as np

from plotpy.config import CONF, _, make_title
from plotpy.items import (
    CurveItem,
    ErrorBarCurveItem,
    HistogramItem,
    Marker,
    XRangeSelection,
)
from plotpy.plot import BasePlot
from plotpy.styles import (
    COLORS,
    MARKERS,
    CurveParam,
    ErrorBarParam,
    HistogramParam,
    MarkerParam,
    style_generator,
    update_style_attr,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable

CURVE_COUNT = 0
HISTOGRAM_COUNT = 0


class CurveMarkerCursorBuilder:
    """Class regrouping a set of factory functions to simplify the creation
    of curve, cursor and marker items."""

    def __init__(self):
        self.style = style_generator()

    # ---- Plot items -----------------------------------------------------------------

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
        dsamp_factor: int | None = None,
        use_dsamp: bool | None = None,
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
        if dsamp_factor is not None:
            param.dsamp_factor = dsamp_factor
        if use_dsamp is not None:
            param.use_dsamp = use_dsamp

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
                if not isinstance(y, np.ndarray):
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
        if isinstance(y, (list, tuple)) and isinstance(y, np.ndarray):
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
            args: x, y, style
            kwargs: title, color, linestyle, linewidth, marker, markersize,
            markerfacecolor, markeredgecolor, shade, curvestyle, baseline,
            dsamp_factor, use_dsamp

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
            if "dsamp_factor" in kwargs:
                param.dsamp_factor = kwargs.pop("dsamp_factor")
            if "use_dsamp" in kwargs:
                param.use_dsamp = kwargs.pop("use_dsamp")
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
        dsamp_factor: int | None = None,
        use_dsamp: bool | None = None,
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
            dsamp_factor: downsampling factor. Default is None
            use_dsamp: use downsampling. Default is None
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
                dsamp_factor=dsamp_factor,
                use_dsamp=use_dsamp,
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
            dsamp_factor,
            use_dsamp,
        )
        return self.pcurve(x, y, param, xaxis, yaxis)

    def merror(self, *args, **kwargs) -> ErrorBarCurveItem:
        """Make an errorbar curve `plot item` based on MATLAB-like syntax

        Args:
            args: x, y, dx, dy, style
            kwargs: title, color, linestyle, linewidth, marker, markersize,
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
        dsamp_factor: int | None = None,
        use_dsamp: bool | None = None,
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
            dsamp_factor: downsampling factor. Default is None
            use_dsamp: use downsampling. Default is None

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
            dsamp_factor,
            use_dsamp,
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
