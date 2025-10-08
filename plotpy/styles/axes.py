# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.dataset import (
    BeginGroup,
    ChoiceItem,
    ColorItem,
    DataSet,
    EndGroup,
    FloatItem,
    ObjectItem,
    StringItem,
)
from guidata.dataset.qtitemwidgets import DataSetWidget
from guidata.dataset.qtwidgets import DataSetEditLayout
from qwt import QwtPlot

from plotpy.config import _
from plotpy.constants import X_BOTTOM, Y_LEFT, Y_RIGHT
from plotpy.styles.base import FontItem

if TYPE_CHECKING:
    from qwt import QwtPlotItem, QwtScaleDiv

    from plotpy.items import BaseImageItem
    from plotpy.plot import BasePlot


class AxeStyleParam(DataSet):
    """Style parameters for an axis."""

    title = StringItem(_("Title"), default="")
    unit = StringItem(_("Unit"), default="")
    color = ColorItem(_("Color"), default="black").set_pos(col=1)
    title_font = FontItem(_("Title font"))
    ticks_font = FontItem(_("Values font"))


class AxisParam(DataSet):
    """Scale parameters for an axis."""

    scale = ChoiceItem(
        _("Scale"),
        [("lin", _("linear")), ("log", _("logarithmic")), ("datetime", _("date/time"))],
        default="lin",
    )
    vmin = FloatItem("Min", help=_("Lower axis limit"), default=0.0)
    vmax = FloatItem("Max", help=_("Upper axis limit"), default=1.0)

    def update_param(self, plot: BasePlot, axis_id: int) -> None:
        """
        Update the parameters of the axis.

        Args:
            plot: The plot from which to update the parameters.
            axis_id: The axis ID to update.
        """
        self.scale = plot.get_axis_scale(axis_id)
        axis: QwtScaleDiv = plot.axisScaleDiv(axis_id)
        self.vmin = axis.lowerBound()
        self.vmax = axis.upperBound()

    def update_axis(self, plot: BasePlot, axis_id: int) -> None:
        """
        Update the axis with the parameters.

        Args:
            plot: The plot to update.
            axis_id: The axis ID to update.
        """
        plot.enableAxis(axis_id, True)
        plot.set_axis_scale(axis_id, self.scale, autoscale=False)
        plot.setAxisScale(axis_id, self.vmin, self.vmax)
        plot.disable_unused_axes()
        plot.SIG_AXIS_PARAMETERS_CHANGED.emit(axis_id)


class AxisItemWidget(DataSetWidget):
    """Widget for the axis item."""

    klass = AxisParam


class AxisItem(ObjectItem):
    """Item for an axis."""

    klass = AxisParam


DataSetEditLayout.register(AxisItem, AxisItemWidget)


class AxesParam(DataSet):
    """Parameters for the axes of a plot."""

    xaxis_id = ChoiceItem(
        _("X-axis position"),
        [(QwtPlot.xBottom, _("bottom")), (QwtPlot.xTop, _("top"))],
        default=QwtPlot.xBottom,
    )
    xaxis = AxisItem(_("X Axis"))
    yaxis_id = ChoiceItem(
        _("Y-axis position"),
        [(QwtPlot.yLeft, _("left")), (QwtPlot.yRight, _("right"))],
        default=QwtPlot.yLeft,
    )
    yaxis = AxisItem(_("Y Axis"))

    def update_param(self, item: QwtPlotItem) -> None:
        """
        Update the parameters of the axes.

        Args:
            item: The plot item from which to update the parameters.
        """
        plot: BasePlot = item.plot()
        self.xaxis: AxisParam
        self.yaxis: AxisParam
        self.xaxis_id = item.xAxis()
        self.xaxis.update_param(plot, self.xaxis_id)
        self.yaxis_id = item.yAxis()
        self.yaxis.update_param(plot, self.yaxis_id)

    def update_item(self, item: QwtPlotItem) -> None:
        """
        Update the axes with the parameters.

        Args:
            item: The plot item to update.
        """
        plot: BasePlot = item.plot()
        self.xaxis: AxisParam
        self.yaxis: AxisParam
        plot.grid.setAxes(self.xaxis_id, self.yaxis_id)
        item.setXAxis(self.xaxis_id)
        self.xaxis.update_axis(plot, self.xaxis_id)
        item.setYAxis(self.yaxis_id)
        self.yaxis.update_axis(plot, self.yaxis_id)


class ImageAxesParam(DataSet):
    """Parameters for the axes of an image plot."""

    xparams = BeginGroup(_("X Axis"))
    xmin = FloatItem("x|min", help=_("Lower x-axis limit"))
    xmax = FloatItem("x|max", help=_("Upper x-axis limit"))
    _xparams = EndGroup("end X")
    yparams = BeginGroup(_("Y Axis"))
    ymin = FloatItem("y|min", help=_("Lower y-axis limit"))
    ymax = FloatItem("y|max", help=_("Upper y-axis limit"))
    _yparams = EndGroup("end Y")
    zparams = BeginGroup(_("Z Axis"))
    zmin = FloatItem("z|min", help=_("Lower z-axis limit"))
    zmax = FloatItem("z|max", help=_("Upper z-axis limit"))
    _zparams = EndGroup("end Z")

    def update_param(self, item: BaseImageItem) -> None:
        """
        Update the parameters of the axes associated with the image item.

        Args:
            item: The image item from which to update the parameters.
        """
        plot: BasePlot = item.plot()
        xaxis: QwtScaleDiv = plot.axisScaleDiv(item.xAxis())
        self.xmin = xaxis.lowerBound()
        self.xmax = xaxis.upperBound()
        yaxis: QwtScaleDiv = plot.axisScaleDiv(item.yAxis())
        self.ymin = yaxis.lowerBound()
        self.ymax = yaxis.upperBound()
        self.zmin, self.zmax = item.min, item.max

    def update_item(self, item: BaseImageItem) -> None:
        """
        Update the axes with the parameters associated with the image item.

        Args:
            item: The image item to update.
        """
        plot: BasePlot = item.plot()
        plot.set_plot_limits(self.xmin, self.xmax, self.ymin, self.ymax)
        item.set_lut_range([self.zmin, self.zmax])
        plot.update_colormap_axis(item)
        for axis_id in (X_BOTTOM, Y_LEFT, Y_RIGHT):
            plot.SIG_AXIS_PARAMETERS_CHANGED.emit(axis_id)
