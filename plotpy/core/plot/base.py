# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103

"""
plotpy.widgets.base
---------------------------

The `base` module provides the `plotpy` plotting widget base class:
:py:class:`.base.BasePlot`. This is an enhanced version of
`PythonQwt`'s QwtPlot plotting widget which supports the following features:

    * add to plot, del from plot, hide/show and save/restore `plot items` easily
    * item selection and multiple selection
    * active item
    * plot parameters editing

.. seealso::

    Module :py:mod:`.curve`
        Module providing curve-related plot items

    Module :py:mod:`.image`
        Module providing image-related plot items

    Module :py:mod:`.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Reference
~~~~~~~~~

.. autoclass:: PlotType
   :members:
.. autoclass:: BasePlot
   :members:

"""

import pickle
import sys
from enum import Enum
from math import fabs

import numpy as np
from guidata.configtools import get_font
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtPrintSupport import QPrinter
from qwt import (
    QwtInterval,
    QwtLinearScaleEngine,
    QwtLogScaleEngine,
    QwtPlot,
    QwtPlotCanvas,
    QwtPlotCurve,
    QwtPlotItem,
    QwtText,
)

from plotpy.config import CONF, _
from plotpy.core import io
from plotpy.core.events import StatefulEventFilter
from plotpy.core.interfaces.common import (
    IBaseImageItem,
    IBasePlotItem,
    IColormapImageItemType,
    ICurveItemType,
    IImageItemType,
    IItemType,
    ISerializableType,
    ITrackableItemType,
)
from plotpy.core.items import annotations
from plotpy.core.items.curve.base import CurveItem
from plotpy.core.items.grid import GridItem
from plotpy.core.items.image.base import BaseImageItem
from plotpy.core.items.polygon import PolygonMapItem
from plotpy.core.items.shapes.marker import Marker
from plotpy.core.items.shapes.polygon import PolygonShape
from plotpy.core.styles.axes import AxesParam, AxeStyleParam, AxisParam, ImageAxesParam
from plotpy.core.styles.base import GridParam, ItemParameters


class PlotType(Enum):
    """
    This is the enum used for the plot type. Defines how the plot should deal with the
    different PlotItems types (curves and images)
    """

    AUTO = 1  #: Automatic plot type. The first PlotItem attached to the plot sets the
    # plot type (see CURVE and IMAGE values of the enum). All tools
    # (curve and image related) are registered and accessible depending on the last
    # selected PlotItem.
    CURVE = 2  #: Curve specialized plot : the y axis is not reversed and the aspect
    # ratio is not locked by default. Only CURVE typed tools are automatically
    # registered.
    IMAGE = 3  #: Image specialized plot : the y axis is reversed and the aspect ratio
    # is locked by default. Only IMAGE typed tools are automatically registered.
    MANUAL = 4  #: No assumption is made on the type of items to be displayed on the
    # plot. Acts like the CURVE value of the enum for y axis and aspect ratio. No tool
    # are automatically registered.


PARAMETERS_TITLE_ICON = {
    "grid": (_("Grid..."), "grid.png"),
    "axes": (_("Axes style..."), "axes.png"),
    "item": (_("Parameters..."), "settings.png"),
}


class BasePlot(QwtPlot):
    """
    An enhanced QwtPlot class that provides
    methods for handling plotitems and axes better

    It distinguishes activatable items from basic QwtPlotItems.

    Activatable items must support IBasePlotItem interface and should
    be added to the plot using add_item methods.
    """

    Y_LEFT, Y_RIGHT, X_BOTTOM, X_TOP = (
        QwtPlot.yLeft,
        QwtPlot.yRight,
        QwtPlot.xBottom,
        QwtPlot.xTop,
    )
    #    # To be replaced by (in the near future):
    #    Y_LEFT, Y_RIGHT, X_BOTTOM, X_TOP = range(4)
    AXIS_IDS = (Y_LEFT, Y_RIGHT, X_BOTTOM, X_TOP)
    AXIS_NAMES = {"left": Y_LEFT, "right": Y_RIGHT, "bottom": X_BOTTOM, "top": X_TOP}
    AXIS_TYPES = {"lin": QwtLinearScaleEngine, "log": QwtLogScaleEngine}
    AXIS_CONF_OPTIONS = ("axis", "axis", "axis", "axis")
    DEFAULT_ACTIVE_XAXIS = X_BOTTOM
    DEFAULT_ACTIVE_YAXIS = Y_LEFT

    AUTOSCALE_TYPES = (CurveItem, BaseImageItem, PolygonMapItem)
    AUTOSCALE_EXCLUDES = []

    #: Signal emitted by plot when an IBasePlotItem object was moved (args: x0,y0,x1,y1)
    SIG_ITEM_MOVED = QC.Signal("PyQt_PyObject", float, float, float, float)

    #: Signal emitted by plot when an IBasePlotItem object was resized
    SIG_ITEM_RESIZED = QC.Signal("PyQt_PyObject", float, float)

    #: Signal emitted by plot when an IBasePlotItem object was rotated (args: angle)
    SIG_ITEM_ROTATED = QC.Signal("PyQt_PyObject", float)

    #: Signal emitted by plot when a shapes.Marker position changes
    SIG_MARKER_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when a shapes.Axes position (or the angle) changes
    SIG_AXES_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when an annotation.AnnotatedShape position changes
    SIG_ANNOTATION_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when the a shapes.XRangeSelection range changes
    SIG_RANGE_CHANGED = QC.Signal("PyQt_PyObject", float, float)

    #: Signal emitted by plot when item list has changed (item removed, added, ...)
    SIG_ITEMS_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when selected item has changed
    SIG_ACTIVE_ITEM_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when an item was deleted from the item list or using the
    #: delete item tool
    SIG_ITEM_REMOVED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when an item is selected
    SIG_ITEM_SELECTION_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when plot's title or any axis label has changed
    SIG_PLOT_LABELS_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when any plot axis direction has changed
    SIG_AXIS_DIRECTION_CHANGED = QC.Signal("PyQt_PyObject", "PyQt_PyObject")

    #: Signal emitted by plot when LUT has been changed by the user
    SIG_LUT_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when image mask has changed
    SIG_MASK_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by cross section plot when cross section curve data has changed
    SIG_CS_CURVE_CHANGED = QC.Signal("PyQt_PyObject")

    #: Signal emitted by plot when plot axis has changed, e.g. when panning/zooming
    # (arg: plot))
    SIG_PLOT_AXIS_CHANGED = QC.Signal("PyQt_PyObject")

    EPSILON_ASPECT_RATIO = 1e-6

    def __init__(
        self,
        parent=None,
        type=PlotType.AUTO,
        title=None,
        xlabel=None,
        ylabel=None,
        zlabel=None,
        xunit=None,
        yunit=None,
        zunit=None,
        yreverse=None,
        aspect_ratio=1.0,
        lock_aspect_ratio=None,
        gridparam=None,
        section="plot",
        axes_synchronised=False,
        force_colorbar_enabled=False,
    ):
        super(BasePlot, self).__init__(parent)

        self.type = type

        self.__autoLockAspectRatio = False
        if lock_aspect_ratio is None:
            if type == PlotType.IMAGE:
                lock_aspect_ratio = True
            elif type == PlotType.CURVE or type == PlotType.MANUAL:
                lock_aspect_ratio = False
            elif type == PlotType.AUTO:
                lock_aspect_ratio = False
                self.__autoLockAspectRatio = True
            else:
                assert False

        self.__autoYReverse = False
        if yreverse is None:
            if type == PlotType.IMAGE:
                yreverse = True
            elif type == PlotType.CURVE or type == PlotType.MANUAL:
                yreverse = False
            elif type == PlotType.AUTO:
                yreverse = False
                self.__autoYReverse = True
            else:
                assert False

        self.colormap_axis = self.Y_RIGHT

        self.__autoColorBarEnabled = False
        self.force_colorbar_enabled = force_colorbar_enabled
        if force_colorbar_enabled or type == PlotType.IMAGE:
            self.enableAxis(self.colormap_axis)
            self.axisWidget(self.colormap_axis).setColorBarEnabled(True)
        elif type == PlotType.AUTO:
            self.__autoColorBarEnabled = True

        self.lock_aspect_ratio = lock_aspect_ratio

        if zlabel is not None:
            if ylabel is not None and not isinstance(ylabel, str):
                ylabel = ylabel[0]
            ylabel = (ylabel, zlabel)
        if zunit is not None:
            if yunit is not None and not isinstance(yunit, str):
                yunit = yunit[0]
            yunit = (yunit, zunit)

        self._start_autoscaled = True
        self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)
        self.manager = None
        self.plot_id = None  # id assigned by it's manager
        self.filter = StatefulEventFilter(self)
        self.items = []
        self.active_item = None
        self.last_selected = {}  # a mapping from item type to last selected item
        self.axes_styles = [
            AxeStyleParam(_("Left")),
            AxeStyleParam(_("Right")),
            AxeStyleParam(_("Bottom")),
            AxeStyleParam(_("Top")),
        ]
        self._active_xaxis = self.DEFAULT_ACTIVE_XAXIS
        self._active_yaxis = self.DEFAULT_ACTIVE_YAXIS
        self.read_axes_styles(section, self.AXIS_CONF_OPTIONS)
        self.font_title = get_font(CONF, section, "title")
        canvas = self.canvas()
        canvas.setFocusPolicy(QC.Qt.FocusPolicy.StrongFocus)
        canvas.setFocusIndicator(QwtPlotCanvas.ItemFocusIndicator)

        self.SIG_ITEM_MOVED.connect(self._move_selected_items_together)
        self.SIG_ITEM_RESIZED.connect(self._resize_selected_items_together)
        self.SIG_ITEM_ROTATED.connect(self._rotate_selected_items_together)
        self.legendDataChanged.connect(
            lambda item, _legdata: item.update_item_parameters()
        )

        self.axes_reverse = [False] * 4

        self.set_titles(
            title=title, xlabel=xlabel, ylabel=ylabel, xunit=xunit, yunit=yunit
        )

        self.antialiased = False

        self.set_antialiasing(CONF.get(section, "antialiasing"))

        self.axes_synchronised = axes_synchronised

        # Installing our own event filter:
        # (qwt's event filter does not fit our needs)
        self.canvas().installEventFilter(self.filter)
        self.canvas().setMouseTracking(True)

        self.cross_marker = Marker()
        self.curve_marker = Marker(
            label_cb=self.get_coordinates_str, constraint_cb=self.on_active_curve
        )
        self.cross_marker.set_style(section, "marker/cross")
        self.curve_marker.set_style(section, "marker/curve")
        self.cross_marker.setVisible(False)
        self.curve_marker.setVisible(False)
        self.cross_marker.attach(self)
        self.curve_marker.attach(self)

        # Background color
        self.setCanvasBackground(QC.Qt.GlobalColor.white)

        self.curve_pointer = False
        self.canvas_pointer = False

        # Setting up grid
        if gridparam is None:
            gridparam = GridParam(title=_("Grid"), icon="grid.png")
            gridparam.read_config(CONF, section, "grid")
        self.grid = GridItem(gridparam)
        self.add_item(self.grid, z=-1)

        self.__aspect_ratio = None
        self.set_axis_direction("left", yreverse)
        self.set_aspect_ratio(aspect_ratio, lock_aspect_ratio)
        self.replot()  # Workaround for the empty image widget bug

    def replot(self):
        QwtPlot.replot(self)
        if self.lock_aspect_ratio:
            self.apply_aspect_ratio()

    # ---- Private API ----------------------------------------------------------
    def __del__(self):
        # Sometimes, an obscure exception happens when we quit an application
        # because if we don't remove the eventFilter it can still be called
        # after the filter object has been destroyed by Python.
        canvas = self.canvas()
        if canvas:
            try:
                canvas.removeEventFilter(self.filter)
            except RuntimeError as exc:
                # Depending on which widget owns the plot,
                # Qt may have already deleted the canvas when
                # the plot is deleted.
                if "wrapped C/C++ object of type" not in str(exc):
                    raise

    # generic helper methods
    def canvas2plotitem(self, plot_item, x_canvas, y_canvas):
        """

        :param plot_item:
        :param x_canvas:
        :param y_canvas:
        :return:
        """
        return (
            self.invTransform(plot_item.xAxis(), x_canvas),
            self.invTransform(plot_item.yAxis(), y_canvas),
        )

    def plotitem2canvas(self, plot_item, x, y):
        """

        :param plot_item:
        :param x:
        :param y:
        :return:
        """
        return (
            self.transform(plot_item.xAxis(), x),
            self.transform(plot_item.yAxis(), y),
        )

    def on_active_curve(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        curve = self.get_last_active_item(ITrackableItemType)
        if curve:
            x, y = curve.get_closest_coordinates(x, y)
        return x, y

    def get_coordinates_str(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        title = _("Grid")
        item = self.get_last_active_item(ITrackableItemType)
        if item:
            return item.get_coordinates_label(x, y)
        return f"<b>{title}</b><br>x = {x:g}<br>y = {y:g}"

    def set_marker_axes(self):
        """ """
        curve = self.get_last_active_item(ITrackableItemType)
        if curve:
            self.cross_marker.setAxes(curve.xAxis(), curve.yAxis())
            self.curve_marker.setAxes(curve.xAxis(), curve.yAxis())

    def do_move_marker(self, event):
        """

        :param event:
        """
        pos = event.pos()
        self.set_marker_axes()
        if (
            event.modifiers() & QC.Qt.KeyboardModifier.ShiftModifier
            or self.curve_pointer
        ):
            self.curve_marker.setZ(self.get_max_z() + 1)
            self.cross_marker.setVisible(False)
            self.curve_marker.setVisible(True)
            self.curve_marker.move_local_point_to(0, pos)
            self.replot()
            # self.move_curve_marker(self.curve_marker, xc, yc)
        elif (
            event.modifiers() & QC.Qt.KeyboardModifier.AltModifier
            or self.canvas_pointer
        ):
            self.cross_marker.setZ(self.get_max_z() + 1)
            self.cross_marker.setVisible(True)
            self.curve_marker.setVisible(False)
            self.cross_marker.move_local_point_to(0, pos)
            self.replot()
            # self.move_canvas_marker(self.cross_marker, xc, yc)
        else:
            vis_cross = self.cross_marker.isVisible()
            vis_curve = self.curve_marker.isVisible()
            self.cross_marker.setVisible(False)
            self.curve_marker.setVisible(False)
            if vis_cross or vis_curve:
                self.replot()

    def get_axes_to_update(self, dx, dy):
        """

        :param dx:
        :param dy:
        :return:
        """
        if self.axes_synchronised:
            axes = []
            for axis_name in self.AXIS_NAMES:
                if axis_name in ("left", "right"):
                    d = dy
                else:
                    d = dx
                axes.append((d, self.get_axis_id(axis_name)))
            return axes
        else:
            xaxis, yaxis = self.get_active_axes()
            return [(dx, xaxis), (dy, yaxis)]

    def do_pan_view(self, dx, dy):
        """
        Translate the active axes by dx, dy
        dx, dy are tuples composed of (initial pos, dest pos)
        """
        auto = self.autoReplot()
        self.setAutoReplot(False)
        axes_to_update = self.get_axes_to_update(dx, dy)

        for (x1, x0, _start, _width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            i_lbound = self.transform(axis_id, lbound)
            i_hbound = self.transform(axis_id, hbound)
            delta = x1 - x0
            vmin = self.invTransform(axis_id, i_lbound - delta)
            vmax = self.invTransform(axis_id, i_hbound - delta)
            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        self.replot()
        # the signal MUST be emitted after replot, otherwise
        # we receiver won't see the new bounds (don't know why?)
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

    def do_zoom_view(self, dx, dy, lock_aspect_ratio=None):
        """
        Change the scale of the active axes (zoom/dezoom) according to dx, dy
        dx, dy are tuples composed of (initial pos, dest pos)
        We try to keep initial pos fixed on the canvas as the scale changes
        """
        # See plotpy/gui/widgets/events.py where dx and dy are defined like this:
        #   dx = (pos.x(), self.last.x(), self.start.x(), rct.width())
        #   dy = (pos.y(), self.last.y(), self.start.y(), rct.height())
        # where:
        #   * self.last is the mouse position seen during last event
        #   * self.start is the first mouse position (here, this is the
        #     coordinate of the point which is at the center of the zoomed area)
        #   * rct is the plot rect contents
        #   * pos is the current mouse cursor position

        if lock_aspect_ratio is None:
            lock_aspect_ratio = self.lock_aspect_ratio

        auto = self.autoReplot()
        self.setAutoReplot(False)
        dx = (-1,) + dx  # adding direction to tuple dx
        dy = (1,) + dy  # adding direction to tuple dy
        if lock_aspect_ratio:
            direction, x1, x0, start, width = dx
            F = 1 + 3 * direction * float(x1 - x0) / width
        axes_to_update = self.get_axes_to_update(dx, dy)

        for (direction, x1, x0, start, width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            if not lock_aspect_ratio:
                F = 1 + 3 * direction * float(x1 - x0) / width
            if F * (hbound - lbound) == 0:
                continue
            if self.get_axis_scale(axis_id) == "lin":
                orig = self.invTransform(axis_id, start)
                vmin = orig - F * (orig - lbound)
                vmax = orig + F * (hbound - orig)
            else:  # log scale
                i_lbound = self.transform(axis_id, lbound)
                i_hbound = self.transform(axis_id, hbound)
                imin = start - F * (start - i_lbound)
                imax = start + F * (i_hbound - start)
                vmin = self.invTransform(axis_id, imin)
                vmax = self.invTransform(axis_id, imax)
            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        self.replot()
        # the signal MUST be emitted after replot, otherwise
        # we receiver won't see the new bounds (don't know why?)
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

    def do_zoom_rect_view(self, start, end):
        """

        :param start:
        :param end:
        """
        # XXX implement the case when axes are synchronised
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()
        xaxis, yaxis = self.get_active_axes()
        active_axes = [(x1, x2, xaxis), (y1, y2, yaxis)]
        for h1, h2, k in active_axes:
            o1 = self.invTransform(k, h1)
            o2 = self.invTransform(k, h2)
            if o1 > o2:
                o1, o2 = o2, o1
            if o1 == o2:
                continue
            if self.get_axis_direction(k):
                o1, o2 = o2, o1
            self.setAxisScale(k, o1, o2)
        self.replot()
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

        if self.lock_aspect_ratio:
            self.apply_aspect_ratio()

    def get_default_item(self):
        """Return default item, depending on plot's default item type
        (e.g. for a curve plot, this is a curve item type).

        Return nothing if there is more than one item matching
        the default item type."""
        if self.type == PlotType.IMAGE:
            items = self.get_items(item_type=IImageItemType)
        elif self.type == PlotType.CURVE:
            items = self.get_items(item_type=ICurveItemType)
        else:
            items = [
                item
                for item in self.items
                if IImageItemType in item.types() or ICurveItemType in item.types()
            ]
        if len(items) == 1:
            return items[0]

    # ---- QWidget API ---------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """Reimplement QWidget method"""
        for axis_id in self.AXIS_IDS:
            widget = self.axisWidget(axis_id)
            if widget.geometry().contains(event.pos()):
                self.edit_axis_parameters(axis_id)
                break
        else:
            QwtPlot.mouseDoubleClickEvent(self, event)

    # ---- QwtPlot API ---------------------------------------------------------
    def showEvent(self, event):
        """Reimplement Qwt method"""
        if self.lock_aspect_ratio:
            self._start_autoscaled = True
        QwtPlot.showEvent(self, event)
        if self._start_autoscaled:
            self.do_autoscale()

    def resizeEvent(self, event):
        """Reimplement Qt method to resize widget"""
        QwtPlot.resizeEvent(self, event)
        if self.lock_aspect_ratio:
            self.apply_aspect_ratio()
            self.replot()

    # ---- Public API ----------------------------------------------------------
    def _move_selected_items_together(self, item, x0, y0, x1, y1):
        """Selected items move together"""
        for selitem in self.get_selected_items():
            if selitem is not item and selitem.can_move():
                selitem.move_with_selection(x1 - x0, y1 - y0)

    def _resize_selected_items_together(self, item, zoom_dx, zoom_dy):
        """Selected items resize together"""
        for selitem in self.get_selected_items():
            if (
                selitem is not item
                and selitem.can_resize()
                and IBaseImageItem in selitem.__implements__
            ):
                if zoom_dx != 0 or zoom_dy != 0:
                    selitem.resize_with_selection(zoom_dx, zoom_dy)

    def _rotate_selected_items_together(self, item, angle):
        """Selected items rotate together"""
        for selitem in self.get_selected_items():
            if (
                selitem is not item
                and selitem.can_rotate()
                and IBaseImageItem in selitem.__implements__
            ):
                selitem.rotate_with_selection(angle)

    def set_manager(self, manager, plot_id):
        """Set the associated :py:class:`.plot.PlotManager` instance"""
        self.manager = manager
        self.plot_id = plot_id

    def sizeHint(self):
        """Preferred size"""
        return QC.QSize(400, 300)

    def get_title(self):
        """Get plot title"""
        return str(self.title().text())

    def set_title(self, title):
        """Set plot title"""
        text = QwtText(title)
        text.setFont(self.font_title)
        self.setTitle(text)
        self.SIG_PLOT_LABELS_CHANGED.emit(self)

    def get_axis_id(self, axis_name):
        """Return axis ID from axis name
        If axis ID is passed directly, check the ID"""
        assert axis_name in self.AXIS_NAMES or axis_name in self.AXIS_IDS
        return self.AXIS_NAMES.get(axis_name, axis_name)

    def read_axes_styles(self, section, options):
        """
        Read axes styles from section and options (one option
        for each axis in the order left, right, bottom, top)

        Skip axis if option is None
        """
        for prm, option in zip(self.axes_styles, options):
            if option is None:
                continue
            prm.read_config(CONF, section, option)
        self.update_all_axes_styles()

    def get_axis_title(self, axis_id):
        """Get axis title"""
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].title

    def set_axis_title(self, axis_id, text):
        """Set axis title"""
        axis_id = self.get_axis_id(axis_id)
        self.axes_styles[axis_id].title = text
        self.update_axis_style(axis_id)

    def get_axis_unit(self, axis_id):
        """Get axis unit"""
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].unit

    def set_axis_unit(self, axis_id, text):
        """Set axis unit"""
        axis_id = self.get_axis_id(axis_id)
        self.axes_styles[axis_id].unit = text
        self.update_axis_style(axis_id)

    def get_axis_font(self, axis_id):
        """Get axis font"""
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].title_font.build_font()

    def set_axis_font(self, axis_id, font):
        """Set axis font"""
        axis_id = self.get_axis_id(axis_id)
        self.axes_styles[axis_id].title_font.update_param(font)
        self.axes_styles[axis_id].ticks_font.update_param(font)
        self.update_axis_style(axis_id)

    def get_axis_color(self, axis_id):
        """Get axis color (color name, i.e. string)"""
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].color

    def set_axis_color(self, axis_id, color):
        """
        Set axis color
        color: color name (string) or QColor instance
        """
        axis_id = self.get_axis_id(axis_id)
        if isinstance(color, str):
            color = QG.QColor(color)
        self.axes_styles[axis_id].color = str(color.name())
        self.update_axis_style(axis_id)

    def update_axis_style(self, axis_id):
        """Update axis style"""
        axis_id = self.get_axis_id(axis_id)
        style = self.axes_styles[axis_id]

        title_font = style.title_font.build_font()
        ticks_font = style.ticks_font.build_font()
        self.setAxisFont(axis_id, ticks_font)

        if style.title and style.unit:
            title = f"{style.title} ({style.unit})"
        elif style.title:
            title = style.title
        else:
            title = style.unit
        axis_text = self.axisTitle(axis_id)
        axis_text.setFont(title_font)
        axis_text.setText(title)
        axis_text.setColor(QG.QColor(style.color))
        self.setAxisTitle(axis_id, axis_text)
        self.SIG_PLOT_LABELS_CHANGED.emit(self)

    def update_all_axes_styles(self):
        """Update all axes styles"""
        for axis_id in self.AXIS_IDS:
            self.update_axis_style(axis_id)

    def get_axis_limits(self, axis_id):
        """Return axis limits (minimum and maximum values)"""
        axis_id = self.get_axis_id(axis_id)
        sdiv = self.axisScaleDiv(axis_id)
        return sdiv.lowerBound(), sdiv.upperBound()

    def set_axis_limits(self, axis_id, vmin, vmax, stepsize=0):
        """Set axis limits (minimum and maximum values) and optional
        step size"""
        axis_id = self.get_axis_id(axis_id)
        vmin, vmax = sorted([vmin, vmax])
        if self.get_axis_direction(axis_id):
            self.setAxisScale(axis_id, vmax, vmin, stepsize)
        else:
            self.setAxisScale(axis_id, vmin, vmax, stepsize)
        self._start_autoscaled = False

    def set_axis_ticks(self, axis_id, nmajor=None, nminor=None):
        """Set axis maximum number of major ticks
        and maximum of minor ticks"""
        axis_id = self.get_axis_id(axis_id)
        if nmajor is not None:
            self.setAxisMaxMajor(axis_id, nmajor)
        if nminor is not None:
            self.setAxisMaxMinor(axis_id, nminor)

    def get_axis_scale(self, axis_id):
        """Return the name ('lin' or 'log') of the scale used by axis"""
        axis_id = self.get_axis_id(axis_id)
        engine = self.axisScaleEngine(axis_id)
        for axis_label, axis_type in list(self.AXIS_TYPES.items()):
            if isinstance(engine, axis_type):
                return axis_label
        return "lin"  # unknown default to linear

    def set_axis_scale(self, axis_id, scale, autoscale=True):
        """Set axis scale
        Example: self.set_axis_scale(curve.yAxis(), 'lin')"""
        axis_id = self.get_axis_id(axis_id)
        self.setAxisScaleEngine(axis_id, self.AXIS_TYPES[scale]())
        if autoscale:
            self.do_autoscale(replot=False)

    def get_scales(self):
        """Return active curve scales"""
        ax, ay = self.get_active_axes()
        return self.get_axis_scale(ax), self.get_axis_scale(ay)

    def set_scales(self, xscale, yscale):
        """Set active curve scales
        Example: self.set_scales('lin', 'lin')"""
        ax, ay = self.get_active_axes()
        self.set_axis_scale(ax, xscale)
        self.set_axis_scale(ay, yscale)
        self.replot()

    def enable_used_axes(self):
        """
        Enable only used axes
        For now, this is needed only by the pyplot interface
        """
        for axis in self.AXIS_IDS:
            self.enableAxis(axis, True)
        self.disable_unused_axes()

    def disable_unused_axes(self):
        """Disable unused axes"""
        used_axes = set()

        has_image = False
        if self.type == PlotType.IMAGE or self.force_colorbar_enabled:
            has_image = True

        for item in self.get_items():
            used_axes.add(item.xAxis())
            used_axes.add(item.yAxis())
            if not has_image and isinstance(item, BaseImageItem):
                has_image = True
        unused_axes = set(self.AXIS_IDS) - set(used_axes)
        for axis in unused_axes:
            self.enableAxis(axis, False)

        if has_image:
            self.enableAxis(self.colormap_axis)

    def get_items(self, z_sorted=False, item_type=None):
        """Return widget's item list
        (items are based on IBasePlotItem's interface)"""
        if z_sorted:
            items = sorted(self.items, reverse=True, key=lambda x: x.z())
        else:
            items = self.items
        if item_type is None:
            return items
        else:
            assert issubclass(item_type, IItemType)
            return [item for item in items if item_type in item.types()]

    def get_public_items(self, z_sorted=False, item_type=None):
        """Return widget's public item list
        (items are based on IBasePlotItem's interface)"""
        return [
            item
            for item in self.get_items(z_sorted=z_sorted, item_type=item_type)
            if not item.is_private()
        ]

    def get_private_items(self, z_sorted=False, item_type=None):
        """Return widget's private item list
        (items are based on IBasePlotItem's interface)"""
        return [
            item
            for item in self.get_items(z_sorted=z_sorted, item_type=item_type)
            if item.is_private()
        ]

    def copy_to_clipboard(self):
        """Copy widget's window to clipboard"""
        clipboard = QW.QApplication.clipboard()
        pixmap = self.grab()
        clipboard.setPixmap(pixmap)

    def save_widget(self, fname):
        """Grab widget's window and save it to filename (/*.png, /*.pdf)"""
        fname = str(fname)
        if fname.lower().endswith(".pdf"):
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOrientation(QPrinter.orientation.Landscape)
            printer.setOutputFileName(fname)
            printer.setCreator("plotpy")
            self.print_(printer)
        elif fname.lower().endswith(".png"):
            pixmap = self.grab()
            pixmap.save(fname, "PNG")
        else:
            raise RuntimeError(_("Unknown file extension"))

    def get_selected_items(self, z_sorted=False, item_type=None):
        """Return selected items"""
        return [
            item
            for item in self.get_items(item_type=item_type, z_sorted=z_sorted)
            if item.selected
        ]

    def get_max_z(self):
        """
        Return maximum z-order for all items registered in plot
        If there is no item, return 0
        """
        if self.items:
            return max([_it.z() for _it in self.items])
        else:
            return 0

    def add_item(self, item, z=None, autoscale=True):
        """
        Add a *plot item* instance to this *plot widget*

            * item: :py:class:`qwt.plot.QwtPlotItem` object implementing
              the :py:class:`.interfaces.IBasePlotItem` interface
            * z: item's z order (None -> z = max(self.get_items())+1)
        """
        assert hasattr(item, "__implements__")
        assert IBasePlotItem in item.__implements__

        if isinstance(item, QwtPlotCurve):
            item.setRenderHint(QwtPlotItem.RenderAntialiased, self.antialiased)

        item.attach(self)
        if z is not None:
            z_exists = False
            for _it in self.get_items():
                if z == _it.z():
                    z_exists = True
                    break
            if z_exists:
                for _it in self.get_items():
                    if _it.z() > z:
                        _it.setZ(_it.z() + 1)
                z += 1
            item.setZ(z)
        else:
            item.setZ(self.get_max_z() + 1)
        if item in self.items:
            print(
                "Warning: item %r is already attached to plot" % item, file=sys.stderr
            )
        else:
            self.items.append(item)

            # PlotType handling when adding the first CurveItem or ImageItem
            if (
                self.__autoLockAspectRatio
                or self.__autoYReverse
                or self.__autoColorBarEnabled
            ):
                is_curve = isinstance(item, CurveItem)
                is_image = isinstance(item, BaseImageItem)
                if is_curve or is_image:
                    if self.__autoYReverse:
                        if is_image:
                            self.set_axis_direction("left", True)
                        self.__autoYReverse = False
                    if self.__autoLockAspectRatio:
                        if is_image:
                            self.set_aspect_ratio(lock=True)
                        self.__autoLockAspectRatio = False
                    if self.__autoColorBarEnabled:
                        if is_image:
                            self.axisWidget(self.colormap_axis).setColorBarEnabled(True)
                            self.enableAxis(self.colormap_axis)
                        self.__autoColorBarEnabled = False

        self.SIG_ITEMS_CHANGED.emit(self)

        if isinstance(item, BaseImageItem):
            parent = self.parent()
            if parent is not None:
                parent.setUpdatesEnabled(False)
            self.update_colormap_axis(item)
            if autoscale:
                self.do_autoscale()
            if parent is not None:
                parent.setUpdatesEnabled(True)

    def add_item_with_z_offset(self, item, zoffset):
        """
        Add a plot *item* instance within a specified z range, over *zmin*
        """
        zlist = sorted(
            [_it.z() for _it in self.items if _it.z() >= zoffset] + [zoffset - 1]
        )
        dzlist = np.argwhere(np.diff(zlist) > 1)
        if len(dzlist) == 0:
            z = max(zlist) + 1
        else:
            z = zlist[int(dzlist[0])] + 1
        self.add_item(item, z=z)

    def __clean_item_references(self, item):
        """Remove all reference to this item (active,
        last_selected"""
        if item is self.active_item:
            self.active_item = None
            self._active_xaxis = self.DEFAULT_ACTIVE_XAXIS
            self._active_yaxis = self.DEFAULT_ACTIVE_YAXIS
        for key, it in list(self.last_selected.items()):
            if item is it:
                del self.last_selected[key]

    def del_items(self, items):
        """Remove item from widget"""
        items = items[:]  # copy the list to avoid side effects when we empty it
        active_item = self.get_active_item()
        while items:
            item = items.pop()
            item.detach()
            # raises ValueError if item not in list
            self.items.remove(item)
            self.__clean_item_references(item)
            self.SIG_ITEM_REMOVED.emit(item)
        self.SIG_ITEMS_CHANGED.emit(self)
        if active_item is not self.get_active_item():
            self.SIG_ACTIVE_ITEM_CHANGED.emit(self)

    def del_item(self, item):
        """
        Remove item from widget
        Convenience function (see 'del_items')
        """
        try:
            self.del_items([item])
        except ValueError:
            raise ValueError("item not in plot")

    def set_item_visible(self, item, state, notify=True, replot=True):
        """Show/hide *item* and emit a SIG_ITEMS_CHANGED signal"""
        item.setVisible(state)
        if item is self.active_item and not state:
            self.set_active_item(None)  # Notify the item list (see baseplot)
        if notify:
            self.SIG_ITEMS_CHANGED.emit(self)
        if replot:
            self.replot()

    def __set_items_visible(self, state, items=None, item_type=None):
        """Show/hide items (if *items* is None, show/hide all items)"""
        if items is None:
            items = self.get_items(item_type=item_type)
        for item in items:
            self.set_item_visible(item, state, notify=False, replot=False)
        self.SIG_ITEMS_CHANGED.emit(self)
        self.replot()

    def show_items(self, items=None, item_type=None):
        """Show items (if *items* is None, show all items)"""
        self.__set_items_visible(True, items, item_type=item_type)

    def hide_items(self, items=None, item_type=None):
        """Hide items (if *items* is None, hide all items)"""
        self.__set_items_visible(False, items, item_type=item_type)

    def save_items(self, iofile, selected=False):
        """
        Save (serializable) items to file using the :py:mod:`pickle` protocol
            * iofile: file object or filename
            * selected=False: if True, will save only selected items

        See also :py:meth:`.baseplot.BasePlot.restore_items`
        """
        if selected:
            items = self.get_selected_items()
        else:
            items = self.items[:]
        items = [item for item in items if ISerializableType in item.types()]

        pickle.dump(items, iofile)

    def restore_items(self, iofile):
        """
        Restore items from file using the :py:mod:`pickle` protocol
            * iofile: file object or filename

        See also :py:meth:`.baseplot.BasePlot.save_items`
        """

        items = pickle.load(iofile)
        for item in items:
            self.add_item(item)

    def serialize(self, writer, selected=False):
        """
        Save (serializable) items to HDF5 file:
            * writer: :py:class:`guidata.dataset.hdf5io.HDF5Writer` object
            * selected=False: if True, will save only selected items

        See also :py:meth:`.baseplot.BasePlot.restore_items`
        """
        if selected:
            items = self.get_selected_items()
        else:
            items = self.items[:]
        items = [item for item in items if ISerializableType in item.types()]
        io.save_items(writer, items)

    def deserialize(self, reader):
        """
        Restore items from HDF5 file:
            * reader: :py:class:`guidata.dataset.hdf5io.HDF5Reader` object

        See also :py:meth:`.baseplot.BasePlot.save_items`
        """
        for item in io.load_items(reader):
            self.add_item(item)

    def set_items(self, *args):
        """Utility function used to quickly setup a plot
        with a set of items"""
        self.del_all_items()
        for item in args:
            self.add_item(item)

    def del_all_items(self, except_grid=True):
        """Del all items, eventually (default) except grid"""
        items = [
            item for item in self.items if not except_grid or item is not self.grid
        ]
        self.del_items(items)

    def __swap_items_z(self, item1, item2):
        old_item1_z, old_item2_z = item1.z(), item2.z()
        item1.setZ(max([_it.z() for _it in self.items]) + 1)
        item2.setZ(old_item1_z)
        item1.setZ(old_item2_z)

    def move_up(self, item_list):
        """Move item(s) up, i.e. to the foreground
        (swap item with the next item in z-order)

        item: plot item *or* list of plot items

        Return True if items have been moved effectively"""
        objects = self.get_items(z_sorted=True)
        items = sorted(list(item_list), reverse=True, key=lambda x: objects.index(x))
        changed = False
        if objects.index(items[-1]) > 0:
            for item in items:
                index = objects.index(item)
                self.__swap_items_z(item, objects[index - 1])
                changed = True
        if changed:
            self.SIG_ITEMS_CHANGED.emit(self)
        return changed

    def move_down(self, item_list):
        """Move item(s) down, i.e. to the background
        (swap item with the previous item in z-order)

        item: plot item *or* list of plot items

        Return True if items have been moved effectively"""
        objects = self.get_items(z_sorted=True)
        items = sorted(list(item_list), reverse=False, key=lambda x: objects.index(x))
        changed = False
        if objects.index(items[-1]) < len(objects) - 1:
            for item in items:
                index = objects.index(item)
                self.__swap_items_z(item, objects[index + 1])
                changed = True
        if changed:
            self.SIG_ITEMS_CHANGED.emit(self)
        return changed

    def set_items_readonly(self, state):
        """Set all items readonly state to *state*
        Default item's readonly state: False (items may be deleted)"""
        for item in self.get_items():
            item.set_readonly(state)
        self.SIG_ITEMS_CHANGED.emit(self)

    def select_item(self, item):
        """Select item"""
        item.select()
        for itype in item.types():
            self.last_selected[itype] = item
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def unselect_item(self, item):
        """Unselect item"""
        item.unselect()
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def get_last_active_item(self, item_type):
        """Return last active item corresponding to passed `item_type`"""
        assert issubclass(item_type, IItemType)
        return self.last_selected.get(item_type)

    def select_all(self):
        """Select all selectable items"""
        last_item = None
        block = self.blockSignals(True)
        for item in self.items:
            if item.can_select():
                self.select_item(item)
                last_item = item
        self.blockSignals(block)
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)
        self.set_active_item(last_item)

    def unselect_all(self):
        """Unselect all selected items"""
        for item in self.items:
            if item.can_select():
                item.unselect()
        self.set_active_item(None)
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def select_some_items(self, items):
        """Select items"""
        active = self.active_item
        block = self.blockSignals(True)
        self.unselect_all()
        if items:
            new_active_item = items[-1]
        else:
            new_active_item = None
        for item in items:
            self.select_item(item)
            if active is item:
                new_active_item = item
        self.set_active_item(new_active_item)
        self.blockSignals(block)
        if new_active_item is not active:
            # if the new selection doesn't include the
            # previously active item
            self.SIG_ACTIVE_ITEM_CHANGED.emit(self)
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def set_active_item(self, item):
        """Set active item, and unselect the old active item. For CurveItems,
        the grid axes are changed according to the selected item"""
        old_active = self.active_item
        self.active_item = item
        if self.active_item is not None:
            if not item.selected:
                self.select_item(self.active_item)
            self._active_xaxis = item.xAxis()
            self._active_yaxis = item.yAxis()

        self.SIG_ACTIVE_ITEM_CHANGED.emit(self)

        if item is not None and old_active is not item:
            if isinstance(item, CurveItem):
                self.grid.setAxes(item.xAxis(), item.yAxis())
            elif isinstance(item, BaseImageItem):
                self.update_colormap_axis(item)

    def get_active_axes(self):
        """Return active axes"""
        item = self.active_item
        if item is not None:
            self._active_xaxis = item.xAxis()
            self._active_yaxis = item.yAxis()
        return self._active_xaxis, self._active_yaxis

    def get_active_item(self, force=False):
        """
        Return active item
        Force item activation if there is no active item
        """
        if force and not self.active_item:
            for item in self.get_items():
                if item.can_select():
                    self.set_active_item(item)
                    break
        return self.active_item

    def get_nearest_object(self, pos, close_dist=0):
        """
        Return nearest item from position 'pos'

        If close_dist > 0:

            Return the first found item (higher z) which distance to 'pos' is
            less than close_dist

        else:

            Return the closest item
        """
        selobj, distance, inside, handle = None, sys.maxsize, None, None
        for obj in self.get_items(z_sorted=True):
            if not obj.isVisible() or not obj.can_select():
                continue
            d, _handle, _inside, other = obj.hit_test(pos)
            if d < distance:
                selobj, distance, handle, inside = obj, d, _handle, _inside
                if d < close_dist:
                    break
            if other is not None:
                # e.g. LegendBoxItem: selecting a curve ('other') instead of
                #                     legend box ('obj')
                return other, 0, None, True
        return selobj, distance, handle, inside

    def get_nearest_object_in_z(self, pos):
        """
        Return nearest item for which position 'pos' is inside of it
        (iterate over items with respect to their 'z' coordinate)
        """
        selobj, distance, inside, handle = None, sys.maxsize, None, None
        for obj in self.get_items(z_sorted=True):
            if not obj.isVisible() or not obj.can_select():
                continue
            d, _handle, _inside, _other = obj.hit_test(pos)
            if _inside:
                selobj, distance, handle, inside = obj, d, _handle, _inside
                break
        return selobj, distance, handle, inside

    def get_context_menu(self):
        """Return widget context menu"""
        return self.manager.get_context_menu(self)

    def get_plot_parameters_status(self, key):
        """

        :param key:
        :return:
        """
        if key == "item":
            return self.get_active_item() is not None
        else:
            return True

    def get_selected_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        for item in self.get_selected_items():
            item.get_item_parameters(itemparams)
        # Retrieving active_item's parameters after every other item:
        # this way, the common datasets will be based on its parameters
        active_item = self.get_active_item()
        active_item.get_item_parameters(itemparams)

    def get_axesparam_class(self, item):
        """Return AxesParam dataset class associated to item's type"""
        if isinstance(item, BaseImageItem):
            return ImageAxesParam
        else:
            return AxesParam

    def get_plot_parameters(self, key, itemparams):
        """
        Return a list of DataSets for a given parameter key
        the datasets will be edited and passed back to set_plot_parameters

        this is a generic interface to help building context menus
        using the BasePlotMenuTool
        """
        if key == "axes":
            for i, axeparam in enumerate(self.axes_styles):
                itemparams.add(f"AxeStyleParam{i}", self, axeparam)
        elif key == "grid":
            self.grid.gridparam.update_param(self.grid)
            itemparams.add("GridParam", self, self.grid.gridparam)
        elif key == "item":
            active_item = self.get_active_item()
            if not active_item:
                return
            self.get_selected_item_parameters(itemparams)
            Param = self.get_axesparam_class(active_item)
            axesparam = Param(
                title=_("Axes"),
                icon="lin_lin.png",
                comment=_("Axes associated to selected item"),
            )
            axesparam.update_param(active_item)
            itemparams.add("AxesParam", self, axesparam)

    def set_item_parameters(self, itemparams):
        """Set item (plot, here) parameters"""
        # Grid style
        dataset = itemparams.get("GridParam")
        if dataset is not None:
            dataset.update_grid(self.grid)
            self.grid.gridparam = dataset
        # Axe styles
        datasets = [itemparams.get(f"AxeStyleParam{i}") for i in range(4)]
        if datasets[0] is not None:
            self.axes_styles = datasets
            self.update_all_axes_styles()
        # Changing active item's associated axes
        dataset = itemparams.get("AxesParam")
        if dataset is not None:
            active_item = self.get_active_item()
            dataset.update_axes(active_item)

    def edit_plot_parameters(self, key):
        """
        Edit plot parameters
        """
        multiselection = len(self.get_selected_items()) > 1
        itemparams = ItemParameters(multiselection=multiselection)
        self.get_plot_parameters(key, itemparams)
        title, icon = PARAMETERS_TITLE_ICON[key]
        itemparams.edit(self, title, icon)

    def get_plot_names(self):
        """
        return names selected items   item.title().text()
        """
        return [item.get_filename() for item in self.get_items() if item.selected]

    def edit_axis_parameters(self, axis_id):
        """Edit axis parameters"""
        if axis_id != self.colormap_axis:
            if axis_id in (self.Y_LEFT, self.Y_RIGHT):
                title = _("Y Axis")
            else:
                title = _("X Axis")
            param = AxisParam(title=title)
            param.update_param(self, axis_id)
            if param.edit(parent=self):
                param.update_axis(self, axis_id)
                self.replot()

    def do_autoscale(self, replot=True, axis_id=None):
        """Do autoscale on all axes"""
        auto = self.autoReplot()
        self.setAutoReplot(False)
        # XXX implement the case when axes are synchronised
        for axis_id in self.AXIS_IDS if axis_id is None else [axis_id]:
            vmin, vmax = None, None
            if not self.axisEnabled(axis_id):
                continue
            for item in self.get_items():
                if (
                    isinstance(item, self.AUTOSCALE_TYPES)
                    and not item.is_empty()
                    and item.isVisible()
                    and item not in self.AUTOSCALE_EXCLUDES
                ):
                    bounds = item.boundingRect()
                    if axis_id == item.xAxis():
                        xmin, xmax = bounds.left(), bounds.right()
                        if vmin is None or xmin < vmin:
                            vmin = xmin
                        if vmax is None or xmax > vmax:
                            vmax = xmax
                    elif axis_id == item.yAxis():
                        ymin, ymax = bounds.top(), bounds.bottom()
                        if vmin is None or ymin < vmin:
                            vmin = ymin
                        if vmax is None or ymax > vmax:
                            vmax = ymax
            if vmin is None or vmax is None:
                continue
            if vmin == vmax:  # same behavior as MATLAB
                vmin -= 1
                vmax += 1
            elif self.get_axis_scale(axis_id) == "lin":
                dv = vmax - vmin
                vmin -= 0.002 * dv
                vmax += 0.002 * dv
            elif vmin > 0 and vmax > 0:  # log scale
                dv = np.log10(vmax) - np.log10(vmin)
                vmin = 10 ** (np.log10(vmin) - 0.002 * dv)
                vmax = 10 ** (np.log10(vmax) + 0.002 * dv)
            self.set_axis_limits(axis_id, vmin, vmax)
        self.setAutoReplot(auto)

        self.updateAxes()
        #        if self.lock_aspect_ratio:
        #            self.replot()
        #            self.apply_aspect_ratio(full_scale=True)
        if replot:
            self.replot()
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

    def disable_autoscale(self):
        """Re-apply the axis scales so as to disable autoscaling
        without changing the view"""
        for axis_id in self.AXIS_IDS:
            vmin, vmax = self.get_axis_limits(axis_id)
            self.set_axis_limits(axis_id, vmin, vmax)

    def invalidate(self):
        """Invalidate paint cache and schedule redraw
        use instead of replot when only the content
        of the canvas needs redrawing (axes, shouldn't change)
        """
        self.canvas().replot()
        self.update()

    def get_axis_direction(self, axis_id):
        """
        Return axis direction of increasing values

            * axis_id: axis id (BasePlot.Y_LEFT, BasePlot.X_BOTTOM, ...)
              or string: 'bottom', 'left', 'top' or 'right'
        """
        axis_id = self.get_axis_id(axis_id)
        return self.axes_reverse[axis_id]

    def set_axis_direction(self, axis_id, reverse=False):
        """
        Set axis direction of increasing values

            * axis_id: axis id (BasePlot.Y_LEFT, BasePlot.X_BOTTOM, ...)
              or string: 'bottom', 'left', 'top' or 'right'
            * reverse: False (default)
                - x-axis values increase from left to right
                - y-axis values increase from bottom to top
            * reverse: True
                - x-axis values increase from right to left
                - y-axis values increase from top to bottom
        """
        axis_id = self.get_axis_id(axis_id)
        if reverse != self.axes_reverse[axis_id]:
            self.replot()
            self.axes_reverse[axis_id] = reverse
            axis_map = self.canvasMap(axis_id)
            self.setAxisScale(axis_id, axis_map.s2(), axis_map.s1())
            self.updateAxes()
            self.SIG_AXIS_DIRECTION_CHANGED.emit(self, axis_id)

    def set_titles(self, title=None, xlabel=None, ylabel=None, xunit=None, yunit=None):
        """
        Set plot and axes titles at once

            * title: plot title
            * xlabel: (bottom axis title, top axis title)
              or bottom axis title only
            * ylabel: (left axis title, right axis title)
              or left axis title only
            * xunit: (bottom axis unit, top axis unit)
              or bottom axis unit only
            * yunit: (left axis unit, right axis unit)
              or left axis unit only
        """
        if title is not None:
            self.set_title(title)
        if xlabel is not None:
            if isinstance(xlabel, str):
                xlabel = (xlabel, "")
            for label, axis in zip(xlabel, ("bottom", "top")):
                if label is not None:
                    self.set_axis_title(axis, label)
        if ylabel is not None:
            if isinstance(ylabel, str):
                ylabel = (ylabel, "")
            for label, axis in zip(ylabel, ("left", "right")):
                if label is not None:
                    self.set_axis_title(axis, label)
        if xunit is not None:
            if isinstance(xunit, str):
                xunit = (xunit, "")
            for unit, axis in zip(xunit, ("bottom", "top")):
                if unit is not None:
                    self.set_axis_unit(axis, unit)
        if yunit is not None:
            if isinstance(yunit, str):
                yunit = (yunit, "")
            for unit, axis in zip(yunit, ("left", "right")):
                if unit is not None:
                    self.set_axis_unit(axis, unit)

    def set_pointer(self, pointer_type):
        """
        Set pointer.

        Valid values of `pointer_type`:

            * None: disable pointer
            * "canvas": enable canvas pointer
            * "curve": enable on-curve pointer
        """
        self.canvas_pointer = False
        self.curve_pointer = False
        if pointer_type == "canvas":
            self.canvas_pointer = True
        elif pointer_type == "curve":
            self.curve_pointer = True

    def set_antialiasing(self, checked):
        """Toggle curve antialiasing"""
        self.antialiased = checked
        for curve in self.itemList():
            if isinstance(curve, QwtPlotCurve):
                curve.setRenderHint(QwtPlotItem.RenderAntialiased, self.antialiased)

    def set_plot_limits(self, x0, x1, y0, y1, xaxis="bottom", yaxis="left"):
        """Set plot scale limits"""
        self.set_axis_limits(yaxis, y0, y1)
        self.set_axis_limits(xaxis, x0, x1)
        self.updateAxes()
        self.SIG_AXIS_DIRECTION_CHANGED.emit(self, self.get_axis_id(yaxis))
        self.SIG_AXIS_DIRECTION_CHANGED.emit(self, self.get_axis_id(xaxis))

    def set_plot_limits_synchronised(self, x0, x1, y0, y1):
        """

        :param x0:
        :param x1:
        :param y0:
        :param y1:
        """
        for yaxis, xaxis in (("left", "bottom"), ("right", "top")):
            self.set_plot_limits(x0, x1, y0, y1, xaxis=xaxis, yaxis=yaxis)

    def get_plot_limits(self, xaxis="bottom", yaxis="left"):
        """Return plot scale limits"""
        x0, x1 = self.get_axis_limits(xaxis)
        y0, y1 = self.get_axis_limits(yaxis)
        return x0, x1, y0, y1

    def add_autoscale_types(self, item_types):
        """add AUTOSCALE TYPES
        item_types: tuple of types
        """
        self.AUTOSCALE_TYPES += item_types

    def add_autoscale_excludes(self, items):
        for item in items:
            if item not in self.AUTOSCALE_EXCLUDES:
                self.AUTOSCALE_EXCLUDES.append(item)

    # ---- Levels histogram-related API ----------------------------------------
    def update_lut_range(self, _min, _max):
        """update the LUT scale"""
        # self.set_items_lut_range(_min, _max, replot=False)
        self.updateAxes()

    # ---- Image scale/aspect ratio -related API -------------------------------
    def set_full_scale(self, item):
        """

        :param item:
        """
        if item.can_setfullscale():
            bounds = item.boundingRect()
            self.set_plot_limits(
                bounds.left(), bounds.right(), bounds.top(), bounds.bottom()
            )

    def get_current_aspect_ratio(self):
        """Return current aspect ratio"""
        dx = self.axisScaleDiv(self.X_BOTTOM).range()
        dy = self.axisScaleDiv(self.Y_LEFT).range()
        h = self.canvasMap(self.Y_LEFT).pDist()
        w = self.canvasMap(self.X_BOTTOM).pDist()
        return fabs((h * dx) / (w * dy))

    def get_aspect_ratio(self):
        """Return aspect ratio"""
        return self.__aspect_ratio

    def set_aspect_ratio(self, ratio=None, lock=None):
        """Set aspect ratio"""
        if ratio is not None:
            self.__aspect_ratio = ratio
        if lock is not None:
            self.lock_aspect_ratio = lock
        self.apply_aspect_ratio()

    def apply_aspect_ratio(self, full_scale=False):
        """

        :param full_scale:
        :return:
        """
        if not self.isVisible():
            return
        current_aspect = self.get_current_aspect_ratio()
        if abs(current_aspect - self.__aspect_ratio) < self.EPSILON_ASPECT_RATIO:
            return
        ymap = self.canvasMap(self.Y_LEFT)
        xmap = self.canvasMap(self.X_BOTTOM)
        h = ymap.pDist()
        w = xmap.pDist()
        dx1, dy1 = xmap.sDist(), fabs(ymap.sDist())
        x0, y0 = xmap.s1(), ymap.s1()
        x1, y1 = xmap.s2(), ymap.s2()
        if y0 > y1:
            y0, y1 = y1, y0

        if w == 0 or h == 0:
            return  # avoid division by zero

        dy2 = (h * dx1) / (w * self.__aspect_ratio)
        dx2 = (w * dy1 * self.__aspect_ratio) / h

        fix_yaxis = False
        if dy2 > dy1:
            fix_yaxis = True
        elif full_scale:
            fix_yaxis = True

        if fix_yaxis:
            delta_y = 0.5 * (dy2 - dy1)
            y0 -= delta_y
            y1 += delta_y
        else:
            delta_x = 0.5 * (dx2 - dx1)
            x0 -= delta_x
            x1 += delta_x

        self.set_plot_limits(x0, x1, y0, y1)

    # ---- LUT/colormap-related API --------------------------------------------
    def notify_colormap_changed(self):
        """Levels histogram range has changed"""
        item = self.get_last_active_item(IColormapImageItemType)
        if item is not None:
            self.update_colormap_axis(item)
        self.replot()
        self.SIG_LUT_CHANGED.emit(self)
        self.SIG_ACTIVE_ITEM_CHANGED.emit(self)

    def update_colormap_axis(self, item):
        """

        :param item:
        :return:
        """
        if IColormapImageItemType not in item.types():
            return
        zaxis = self.colormap_axis
        axiswidget = self.axisWidget(zaxis)
        self.setAxisScale(zaxis, item.min, item.max)
        # XXX: the colormap can't be displayed if min>max, to fix this
        # we should pass an inverted colormap along with _max, _min values
        axiswidget.setColorMap(QwtInterval(item.min, item.max), item.get_color_map())
        self.updateAxes()

    @classmethod
    def register_autoscale_type(cls, type_):
        """Add *type_* to the list of types used to check if an item is
        taken into account to compute the scale.

        Class must defines the following methods:

        * is_empty(): returns True if the item is empty
        * boundingRect(): returns the bouding rect as a QRectF
        * isVisible(): returns True if item is visible
        * xAxis() and yAxis()
        """
        cls.AUTOSCALE_TYPES += (type_,)


# Register PolygonShape and annotated shape.
# It's not possible to simply register AnnotatedShape class
# because their is no warranty that SHAPE_CLASS implements all methods.
for shape in (
    PolygonShape,
    annotations.AnnotatedRectangle,
    annotations.AnnotatedCircle,
    annotations.AnnotatedEllipse,
    annotations.AnnotatedObliqueRectangle,
    annotations.AnnotatedSegment,
    annotations.AnnotatedPoint,
):
    BasePlot.register_autoscale_type(shape)

# Keep this around to debug too many replots
#    def replot(self):
#        import traceback
#        traceback.print_stack()
#        QwtPlot.replot(self)
