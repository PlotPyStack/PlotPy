# -*- coding: utf-8 -*-
from guidata.dataset.dataitems import ChoiceItem, ColorItem, FloatItem, StringItem
from guidata.dataset.datatypes import BeginGroup, DataSet, EndGroup, ObjectItem
from guidata.dataset.qtitemwidgets import DataSetWidget
from guidata.dataset.qtwidgets import DataSetEditLayout
from qwt import QwtPlot

from plotpy.config import _
from plotpy.styles.base import FontItem


class AxeStyleParam(DataSet):
    title = StringItem(_("Title"), default="")
    unit = StringItem(_("Unit"), default="")
    color = ColorItem(_("Color"), default="black").set_pos(col=1)
    title_font = FontItem(_("Title font"))
    ticks_font = FontItem(_("Values font"))


class AxisParam(DataSet):
    scale = ChoiceItem(
        _("Scale"), [("lin", _("linear")), ("log", _("logarithmic"))], default="lin"
    )
    vmin = FloatItem("Min", help=_("Lower axis limit"))
    vmax = FloatItem("Max", help=_("Upper axis limit"))

    def update_param(self, plot, axis_id):
        """

        :param plot:
        :param axis_id:
        """
        self.scale = plot.get_axis_scale(axis_id)
        axis = plot.axisScaleDiv(axis_id)
        self.vmin = axis.lowerBound()
        self.vmax = axis.upperBound()

    def update_axis(self, plot, axis_id):
        """

        :param plot:
        :param axis_id:
        """
        plot.enableAxis(axis_id, True)
        plot.set_axis_scale(axis_id, self.scale, autoscale=False)
        plot.setAxisScale(axis_id, self.vmin, self.vmax)
        plot.disable_unused_axes()


class AxisItemWidget(DataSetWidget):
    klass = AxisParam


class AxisItem(ObjectItem):
    klass = AxisParam


DataSetEditLayout.register(AxisItem, AxisItemWidget)


class AxesParam(DataSet):
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

    def update_param(self, item):
        """

        :param item:
        """
        plot = item.plot()
        self.xaxis_id = item.xAxis()
        self.xaxis.update_param(plot, self.xaxis_id)
        self.yaxis_id = item.yAxis()
        self.yaxis.update_param(plot, self.yaxis_id)

    def update_axes(self, item):
        """

        :param item:
        """
        plot = item.plot()
        plot.grid.setAxes(self.xaxis_id, self.yaxis_id)
        item.setXAxis(self.xaxis_id)
        self.xaxis.update_axis(plot, self.xaxis_id)
        item.setYAxis(self.yaxis_id)
        self.yaxis.update_axis(plot, self.yaxis_id)


class ImageAxesParam(DataSet):
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

    def update_param(self, item):
        """

        :param item:
        """
        plot = item.plot()
        xaxis = plot.axisScaleDiv(item.xAxis())
        self.xmin = xaxis.lowerBound()
        self.xmax = xaxis.upperBound()
        yaxis = plot.axisScaleDiv(item.yAxis())
        self.ymin = yaxis.lowerBound()
        self.ymax = yaxis.upperBound()
        self.zmin, self.zmax = item.min, item.max

    def update_axes(self, item):
        """

        :param item:
        """
        plot = item.plot()
        plot.set_plot_limits(self.xmin, self.xmax, self.ymin, self.ymax)
        item.set_lut_range([self.zmin, self.zmax])
        plot.update_colormap_axis(item)
