# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Plotting widget base class
--------------------------

The `base` module provides the :mod:`plotpy` plotting widget base class:
:py:class:`.base.BasePlot`.
"""

from __future__ import annotations

import dataclasses
import pickle
import sys
import warnings
import weakref
from datetime import datetime
from math import fabs
from typing import TYPE_CHECKING, Any

import numpy as np
import qwt
from guidata.configtools import get_font
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtPrintSupport import QPrinter

from plotpy import constants as cst
from plotpy import io
from plotpy.config import CONF, _
from plotpy.constants import PARAMETERS_TITLE_ICON, PlotType
from plotpy.events import StatefulEventFilter
from plotpy.interfaces import items as itf
from plotpy.items import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedPolygon,
    AnnotatedRectangle,
    AnnotatedSegment,
    BaseImageItem,
    CurveItem,
    GridItem,
    Marker,
    PolygonMapItem,
    PolygonShape,
)
from plotpy.styles.axes import AxesParam, AxeStyleParam, AxisParam, ImageAxesParam
from plotpy.styles.base import GridParam, ItemParameters

if TYPE_CHECKING:
    from typing import IO

    from qwt.scale_widget import QwtScaleWidget

    from plotpy.plot.manager import PlotManager

    TrackableItem = CurveItem | BaseImageItem
    import guidata.io


@dataclasses.dataclass
class BasePlotOptions:
    """Base plot options

    Args:
        title: The plot title
        xlabel: (bottom axis title, top axis title) or bottom axis title only
        ylabel: (left axis title, right axis title) or left axis title only
        zlabel: The Z-axis label
        xunit: (bottom axis unit, top axis unit) or bottom axis unit only
        yunit: (left axis unit, right axis unit) or left axis unit only
        zunit: The Z-axis unit
        yreverse: If True, the Y-axis is reversed
        aspect_ratio: The plot aspect ratio
        lock_aspect_ratio: If True, the aspect ratio is locked
        curve_antialiasing: If True, the curve antialiasing is enabled
        gridparam: The grid parameters
        section: The plot configuration section name ("plot", by default)
        type: The plot type ("auto", "manual", "curve" or "image")
        axes_synchronised: If True, the axes are synchronised
        force_colorbar_enabled: If True, the colorbar is always enabled
        show_axes_tab: If True, the axes tab is shown in the parameters dialog
        autoscale_margin_percent: The percentage margin added when autoscaling
         (0.2% by default)
    """

    title: str | None = None
    xlabel: str | tuple[str, str] | None = None
    ylabel: str | tuple[str, str] | None = None
    zlabel: str | None = None
    xunit: str | tuple[str, str] | None = None
    yunit: str | tuple[str, str] | None = None
    zunit: str | None = None
    yreverse: bool | None = None
    aspect_ratio: float = 1.0
    lock_aspect_ratio: bool | None = None
    curve_antialiasing: bool | None = None
    gridparam: GridParam | None = None
    section: str = "plot"
    type: str | PlotType = "auto"
    axes_synchronised: bool = False
    force_colorbar_enabled: bool = False
    show_axes_tab: bool = True
    autoscale_margin_percent: float = 0.2

    def __post_init__(self) -> None:
        """Check arguments"""
        # Check type
        if isinstance(self.type, str):
            if self.type not in ["auto", "manual", "curve", "image"]:
                raise ValueError("type must be 'auto', 'manual', 'curve' or 'image'")
            self.type = PlotType[self.type.upper()]
        elif not isinstance(self.type, PlotType):
            raise TypeError("type must be a string or a PlotType")
        # Check aspect ratio
        if self.aspect_ratio <= 0:
            raise ValueError("aspect_ratio must be strictly positive")
        # Check autoscale margin percentage
        if self.autoscale_margin_percent < 0:
            raise ValueError("autoscale_margin_percent must be non-negative")
        if self.autoscale_margin_percent > 50:
            raise ValueError("autoscale_margin_percent must be <= 50%")
        # Show a warning if force_colorbar_enabled is True and type is "curve"
        if self.force_colorbar_enabled and self.type == "curve":
            warnings.warn(
                "force_colorbar_enabled is True but type is 'curve', "
                "so the colorbar will not be displayed",
                RuntimeWarning,
            )

    def copy(self, other_options: dict[str, Any]) -> BasePlotOptions:
        """Copy the options and replace some of them with the given dictionary

        Args:
            other_options: The dictionary

        Returns:
            BasePlotOptions: The new options
        """
        return dataclasses.replace(self, **other_options)


class BasePlot(qwt.QwtPlot):
    """Enhanced QwtPlot class providing methods for handling items and axes better

    It distinguishes activatable items from basic QwtPlotItems.

    Activatable items must support IBasePlotItem interface and should
    be added to the plot using add_item methods.

    Args:
        parent: parent widget
        options: plot options
    """

    Y_LEFT, Y_RIGHT, X_BOTTOM, X_TOP = cst.Y_LEFT, cst.Y_RIGHT, cst.X_BOTTOM, cst.X_TOP
    AXIS_IDS = (Y_LEFT, Y_RIGHT, X_BOTTOM, X_TOP)
    AXIS_NAMES = {"left": Y_LEFT, "right": Y_RIGHT, "bottom": X_BOTTOM, "top": X_TOP}
    AXIS_TYPES = {
        "lin": qwt.QwtLinearScaleEngine,
        "log": qwt.QwtLogScaleEngine,
        "datetime": qwt.QwtDateTimeScaleEngine,
    }
    AXIS_CONF_OPTIONS = ("axis", "axis", "axis", "axis")
    DEFAULT_ACTIVE_XAXIS = X_BOTTOM
    DEFAULT_ACTIVE_YAXIS = Y_LEFT

    AUTOSCALE_TYPES = (CurveItem, BaseImageItem, PolygonMapItem)

    #: Signal emitted by plot when an IBasePlotItem object was moved
    #:
    #: Args:
    #:     item: the moved item
    #:     x0 (float): the old x position
    #:     y0 (float): the old y position
    #:     x1 (float): the new x position
    #:     y1 (float): the new y position
    SIG_ITEM_MOVED = QC.Signal(object, float, float, float, float)

    #: Signal emitted by plot when an IBasePlotItem handle was moved
    #:
    #: Args:
    #:     item: the moved item
    SIG_ITEM_HANDLE_MOVED = QC.Signal(object)

    #: Signal emitted by plot when an IBasePlotItem object was resized
    #:
    #: Args:
    #:     item: the resized item
    #:     zoom_dx (float): the zoom factor along the x axis
    #:     zoom_dy (float): the zoom factor along the y axis
    SIG_ITEM_RESIZED = QC.Signal(object, float, float)

    #: Signal emitted by plot when an IBasePlotItem object was rotated
    #:
    #: Args:
    #:     item: the rotated item
    #:     angle (float): the new angle (in radians)
    SIG_ITEM_ROTATED = QC.Signal(object, float)

    #: Signal emitted by plot when a shape.Marker position changes
    #:
    #: Args:
    #:     marker: the moved marker
    SIG_MARKER_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when a shape.Axes position (or the angle) changes
    #:
    #: Args:
    #:     axes: the moved axes
    SIG_AXES_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when an annotation.AnnotatedShape position changes
    #:
    #: Args:
    #:     annotation: the moved annotation
    SIG_ANNOTATION_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when the a shape.XRangeSelection range changes
    #:
    #: Args:
    #:     selection: the selection item
    #:     xmin (float): the new minimum x value
    #:     xmax (float): the new maximum x value
    SIG_RANGE_CHANGED = QC.Signal(object, float, float)

    #: Signal emitted by plot when item list has changed (item removed, added, ...)
    #:
    #: Args:
    #:     plot: the plot
    SIG_ITEMS_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when item parameters have changed (through the item's
    #: parameters dialog, or when setting colormap using the dedicated tool)
    #:
    #: Args:
    #:     item: the item
    SIG_ITEM_PARAMETERS_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when axis parameters have changed (through the axis
    #: parameters dialog)
    #:
    #: Args:
    #:     axis_id: the axis id (0: left, 1: right, 2: bottom, 3: top)
    SIG_AXIS_PARAMETERS_CHANGED = QC.Signal(int)

    #: Signal emitted by plot when selected item has changed
    #:
    #: Args:
    #:     plot: the plot
    SIG_ACTIVE_ITEM_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when an item was deleted from the item list or using the
    #: delete item tool
    #:
    #: Args:
    #:     item: the deleted item
    SIG_ITEM_REMOVED = QC.Signal(object)

    #: Signal emitted by plot when an item is selected
    #:
    #: Args:
    #:     item: the selected item
    SIG_ITEM_SELECTION_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when plot's title or any axis label has changed
    #:
    #: Args:
    #:     plot: the plot
    SIG_PLOT_LABELS_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when any plot axis direction has changed
    #:
    #: Args:
    #:     plot: the plot
    #:     axis_id: the axis id ("left", "right", "bottom", "top")
    SIG_AXIS_DIRECTION_CHANGED = QC.Signal(object, object)

    #: Signal emitted by plot when LUT has been changed by the user
    #:
    #: Args:
    #:     plot: the plot
    SIG_LUT_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when image mask has changed
    #:
    #: Args:
    #:     plot: the plot
    SIG_MASK_CHANGED = QC.Signal(object)

    #: Signal emitted by cross section plot when cross section curve data has changed
    #:
    #: Args:
    #:     plot: the plot
    SIG_CS_CURVE_CHANGED = QC.Signal(object)

    #: Signal emitted by plot when plot axis has changed, e.g. when panning/zooming
    #:
    #: Args:
    #:     plot: the plot
    SIG_PLOT_AXIS_CHANGED = QC.Signal(object)

    EPSILON_ASPECT_RATIO = 1e-6

    def __init__(
        self,
        parent: QW.QWidget | None = None,
        options: BasePlotOptions | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)
        if isinstance(options, dict):
            options = BasePlotOptions(**options)
        self.options = options = options if options is not None else BasePlotOptions()

        self.__autoscale_excluded_items: list[itf.IBasePlotItem] = []
        self.autoscale_margin_percent = options.autoscale_margin_percent
        self.lock_aspect_ratio = options.lock_aspect_ratio
        self.__autoLockAspectRatio = False
        if self.lock_aspect_ratio is None:
            if self.options.type == PlotType.IMAGE:
                self.lock_aspect_ratio = True
            elif self.options.type in (PlotType.CURVE, PlotType.MANUAL):
                self.lock_aspect_ratio = False
            else:  # PlotType.AUTO
                self.lock_aspect_ratio = False
                self.__autoLockAspectRatio = True

        self.__autoYReverse = False
        if options.yreverse is None:
            if self.options.type == PlotType.IMAGE:
                options.yreverse = True
            elif self.options.type in (PlotType.CURVE, PlotType.MANUAL):
                options.yreverse = False
            else:  # PlotType.AUTO
                options.yreverse = False
                self.__autoYReverse = True

        self.colormap_axis = cst.Y_RIGHT

        self.__autoColorBarEnabled = False
        if options.force_colorbar_enabled or self.options.type == PlotType.IMAGE:
            self.enableAxis(self.colormap_axis)
            self.axisWidget(self.colormap_axis).setColorBarEnabled(True)
        elif self.options.type == PlotType.AUTO:
            self.__autoColorBarEnabled = True

        if options.zlabel is not None:
            if options.ylabel is not None and not isinstance(options.ylabel, str):
                options.ylabel = options.ylabel[0]
            options.ylabel = (options.ylabel, options.zlabel)
        if options.zunit is not None:
            if options.yunit is not None and not isinstance(options.yunit, str):
                options.yunit = options.yunit[0]
            options.yunit = (options.yunit, options.zunit)

        self._start_autoscaled = True
        self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)
        self.manager = None
        self.plot_id = None  # id assigned by it's manager
        self.filter = StatefulEventFilter(self)
        self.items: list[itf.IBasePlotItem] = []
        self.active_item: qwt.QwtPlotItem = None
        self.last_selected = {}  # a mapping from item type to last selected item
        self.axes_styles = [
            AxeStyleParam(_("Left")),
            AxeStyleParam(_("Right")),
            AxeStyleParam(_("Bottom")),
            AxeStyleParam(_("Top")),
        ]
        self._active_xaxis = self.DEFAULT_ACTIVE_XAXIS
        self._active_yaxis = self.DEFAULT_ACTIVE_YAXIS
        self.read_axes_styles(options.section, self.AXIS_CONF_OPTIONS)
        self.font_title = get_font(CONF, options.section, "title")
        canvas: qwt.QwtPlotCanvas = self.canvas()
        canvas.setFocusPolicy(QC.Qt.FocusPolicy.StrongFocus)
        canvas.setFocusIndicator(qwt.QwtPlotCanvas.ItemFocusIndicator)

        self.SIG_ITEM_MOVED.connect(self._move_selected_items_together)
        self.SIG_ITEM_RESIZED.connect(self._resize_selected_items_together)
        self.SIG_ITEM_ROTATED.connect(self._rotate_selected_items_together)
        self.legendDataChanged.connect(
            lambda item, _legdata: item.update_item_parameters()
        )

        self.axes_reverse = [False] * 4

        self.set_titles(
            title=options.title,
            xlabel=options.xlabel,
            ylabel=options.ylabel,
            xunit=options.xunit,
            yunit=options.yunit,
        )

        self.antialiased = False
        antial = options.curve_antialiasing or CONF.get(options.section, "antialiasing")
        self.set_antialiasing(antial)

        self.axes_synchronised = options.axes_synchronised

        # Installing our own event filter:
        # (qwt's event filter does not fit our needs)
        canvas.installEventFilter(self.filter)
        canvas.setMouseTracking(True)

        self.cross_marker = Marker()
        self.curve_marker = Marker(
            label_cb=self.get_coordinates_str, constraint_cb=self.on_active_curve
        )
        self.__marker_stay_visible = False
        self.cross_marker.set_style(options.section, "marker/cross")
        self.curve_marker.set_style(options.section, "marker/curve")
        self.cross_marker.setVisible(False)
        self.curve_marker.setVisible(False)
        self.cross_marker.attach(self)
        self.curve_marker.attach(self)

        # Background color
        self.setCanvasBackground(QC.Qt.GlobalColor.white)

        self.curve_pointer = False
        self.canvas_pointer = False

        # Setting up grid
        if options.gridparam is None:
            options.gridparam = GridParam(title=_("Grid"), icon="grid.png")
            options.gridparam.read_config(CONF, options.section, "grid")
        self.grid = GridItem(options.gridparam)
        self.add_item(self.grid, z=-1)

        self.__aspect_ratio = None
        self.set_axis_direction("left", options.yreverse)
        self.set_aspect_ratio(options.aspect_ratio, options.lock_aspect_ratio)
        self.replot()  # Workaround for the empty image widget bug

    # ---- Private API ----------------------------------------------------------
    def __del__(self):
        # Sometimes, an obscure exception happens when we quit an application
        # because if we don't remove the eventFilter it can still be called
        # after the filter object has been destroyed by Python.
        canvas: qwt.QwtPlotCanvas = self.canvas()
        if canvas:
            try:
                canvas.removeEventFilter(self.filter)
            except RuntimeError as exc:
                # Depending on which widget owns the plot,
                # Qt may have already deleted the canvas when
                # the plot is deleted.
                if "C++ object" not in str(exc):
                    raise
            except ValueError:
                # This happens when object has already been deleted
                pass

    def update_color_mode(self) -> None:
        """Color mode was updated, update plot widget accordingly"""
        self.grid.gridparam.read_config(CONF, self.options.section, "grid")
        self.grid.gridparam.update_grid(self.grid)
        self.replot()

    def on_active_curve(self, x: float, y: float) -> tuple[float, float]:
        """
        Callback called when the active curve is moved

        Args:
            x (float): the x position
            y (float): the y position
        """
        curve: CurveItem = self.get_last_active_item(itf.ICurveItemType)
        if curve:
            x, y = curve.get_closest_coordinates(x, y)
        return x, y

    def get_coordinates_str(self, x: float, y: float) -> str:
        """
        Return the coordinates string

        Args:
            x (float): the x position
            y (float): the y position

        Returns:
            str: the coordinates string
        """
        title = _("Grid")
        item: TrackableItem = self.get_last_active_item(itf.ITrackableItemType)
        if item:
            return item.get_coordinates_label(x, y)
        return self.format_coordinate_values(x, y, "bottom", "left", title)

    def format_coordinate_values(
        self, x: float, y: float, xaxis: str | int, yaxis: str | int, title: str
    ) -> str:
        """Format coordinate values with axis-aware formatting

        Args:
            x: The x coordinate value
            y: The y coordinate value
            xaxis: The x axis name ("bottom", "top") or axis ID
            yaxis: The y axis name ("left", "right") or axis ID
            title: The title to display in the coordinate string

        Returns:
            str: Formatted coordinate string with HTML markup
        """
        x_formatted = self.format_coordinate_value(x, xaxis)
        y_formatted = self.format_coordinate_value(y, yaxis)
        return f"<b>{title}</b><br>x = {x_formatted}<br>y = {y_formatted}"

    def format_coordinate_value(self, value: float, axis_id: str | int) -> str:
        """Format a coordinate value based on the axis scale type

        Args:
            value: The coordinate value to format
            axis_id: The axis name ("bottom", "top", "left", "right") or axis ID

        Returns:
            str: Formatted coordinate value
        """
        axis_id = self.get_axis_id(axis_id)

        # Check if this axis is using datetime scale
        if self.get_axis_scale(axis_id) == "datetime":
            try:
                scale_draw: qwt.QwtDateTimeScaleDraw = self.axisScaleDraw(axis_id)
                dt = datetime.fromtimestamp(value)
                return dt.strftime(scale_draw.get_format())
            except (ValueError, OSError, OverflowError):
                # Handle invalid timestamps, fall back to numeric display
                return f"{value:g}"
        else:
            # Standard numeric formatting
            return f"{value:g}"

    def set_marker_axes(self) -> None:
        """
        Set the axes of the markers
        """
        item: TrackableItem = self.get_last_active_item(itf.ITrackableItemType)
        if item:
            self.cross_marker.setAxes(item.xAxis(), item.yAxis())
            self.curve_marker.setAxes(item.xAxis(), item.yAxis())

    def do_move_marker(self, event: QG.QMouseEvent) -> None:
        """
        Move the marker

        Args:
            event (QMouseEvent): the event
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
            self.__marker_stay_visible = event.modifiers() & QC.Qt.ControlModifier
        elif (
            event.modifiers() & QC.Qt.KeyboardModifier.AltModifier
            or self.canvas_pointer
        ):
            self.cross_marker.setZ(self.get_max_z() + 1)
            self.cross_marker.setVisible(True)
            self.curve_marker.setVisible(False)
            self.cross_marker.move_local_point_to(0, pos)
            self.replot()
            self.__marker_stay_visible = event.modifiers() & QC.Qt.ControlModifier
        else:
            vis_cross = self.cross_marker.isVisible()
            vis_curve = self.curve_marker.isVisible()
            self.cross_marker.setVisible(False)
            self.curve_marker.setVisible(self.__marker_stay_visible)
            if vis_cross or vis_curve:
                self.replot()

    def __get_axes_to_update(
        self,
        dx: tuple[float, float, float, float],
        dy: tuple[float, float, float, float],
    ) -> list[tuple[float, float, float, float], int]:
        """
        Return the axes to update

        Args:
            dx (tuple[float, float, float, float]): the x axis 'state' tuple
            dy (tuple[float, float, float, float]): the y axis 'state' tuple

        Returns:
            list[tuple[float, float, float, float], int]: the axes to update
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

    def do_pan_view(
        self,
        dx: tuple[float, float, float, float],
        dy: tuple[float, float, float, float],
        replot: bool = True,
    ) -> None:
        """
        Translate the active axes according to dx, dy axis 'state' tuples

        Args:
            dx (tuple[float, float, float, float]): the x axis 'state' tuple
            dy (tuple[float, float, float, float]): the y axis 'state' tuple
            replot: if True, do a full replot else just update the axes to avoid a
             redraw (default: True)
        """
        # dx and dy are the output of the "DragHandler.get_move_state" method
        # (see module ``plotpy.events``)

        auto = self.autoReplot()
        self.setAutoReplot(False)
        axes_to_update = self.__get_axes_to_update(dx, dy)

        for (x1, x0, _start, _width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            i_lbound = self.transform(axis_id, lbound)
            i_hbound = self.transform(axis_id, hbound)
            delta = x1 - x0
            vmin = self.invTransform(axis_id, i_lbound - delta)
            vmax = self.invTransform(axis_id, i_hbound - delta)
            self.set_axis_limits(axis_id, vmin, vmax)

        self.setAutoReplot(auto)
        if replot:
            self.replot()
        else:
            self.updateAxes()
        # the signal MUST be emitted after replot, otherwise
        # we receiver won't see the new bounds (don't know why?)
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

    def do_zoom_view(
        self,
        dx: tuple[float, float, float, float],
        dy: tuple[float, float, float, float],
        lock_aspect_ratio: bool | None = None,
        replot: bool = True,
    ) -> None:
        """
        Change the scale of the active axes (zoom/dezoom) according to dx, dy
        axis 'state' tuples

        We try to keep initial pos fixed on the canvas as the scale changes

        Args:
            dx (tuple[float, float, float, float]): the x axis 'state' tuple
            dy (tuple[float, float, float, float]): the y axis 'state' tuple
            lock_aspect_ratio: if True, the aspect ratio is locked
            replot: if True, do a full replot else just update the axes to avoid a
             redraw (default: True)
        """
        # dx and dy are the output of the "DragHandler.get_move_state" method
        # (see module ``plotpy.events``):
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
        axes_to_update = self.__get_axes_to_update(dx, dy)

        for (direction, x1, x0, start, width), axis_id in axes_to_update:
            lbound, hbound = self.get_axis_limits(axis_id)
            if not lock_aspect_ratio:
                F = 1 + 3 * direction * float(x1 - x0) / width
            if F * (hbound - lbound) == 0:
                continue
            if self.get_axis_scale(axis_id) in ("lin", "datetime"):
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
        if replot:
            self.replot()
        else:
            self.updateAxes()
        # the signal MUST be emitted after replot, otherwise
        # we receiver won't see the new bounds (don't know why?)
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

    def do_zoom_rect_view(self, start: QC.QPointF, end: QC.QPointF) -> None:
        """
        Zoom to rectangle defined by start and end points

        Args:
            start (QPointF): the start point
            end (QPointF): the end point
        """
        # TODO: Implement the case when axes are synchronised
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

    def get_default_item(self) -> itf.IBasePlotItem | None:
        """Return default item, depending on plot's default item type
        (e.g. for a curve plot, this is a curve item type).

        Return nothing if there is more than one item matching
        the default item type.

        Returns:
            IBasePlotItem: the default item
        """
        if self.options.type == PlotType.IMAGE:
            items = self.get_items(item_type=itf.IImageItemType)
        elif self.options.type == PlotType.CURVE:
            items = self.get_items(item_type=itf.ICurveItemType)
        else:
            items = [
                item
                for item in self.items
                if itf.IImageItemType in item.types()
                or itf.ICurveItemType in item.types()
            ]
        if len(items) == 1:
            return items[0]

    # ---- QWidget API ---------------------------------------------------------
    def mouseDoubleClickEvent(self, event: QG.QMouseEvent) -> None:
        """Reimplement QWidget method"""
        for axis_id in self.AXIS_IDS:
            widget = self.axisWidget(axis_id)
            if widget.geometry().contains(event.pos()):
                self.edit_axis_parameters(axis_id)
                break
        else:
            qwt.QwtPlot.mouseDoubleClickEvent(self, event)

    # ---- QwtPlot API ---------------------------------------------------------
    def showEvent(self, event) -> None:
        """Reimplement Qwt method"""
        if self.lock_aspect_ratio:
            self._start_autoscaled = True
        qwt.QwtPlot.showEvent(self, event)
        if self._start_autoscaled:
            self.do_autoscale()

    def resizeEvent(self, event):
        """Reimplement Qt method to resize widget"""
        qwt.QwtPlot.resizeEvent(self, event)
        if self.lock_aspect_ratio:
            self.apply_aspect_ratio()
            self.replot()

    # ---- Public API ----------------------------------------------------------
    def _move_selected_items_together(
        self, item: itf.IBasePlotItem, x0: float, y0: float, x1: float, y1: float
    ) -> None:
        """Selected items move together

        Args:
            item (IBasePlotItem): the item
            x0 (float): the old x position
            y0 (float): the old y position
            x1 (float): the new x position
            y1 (float): the new y position
        """
        for selitem in self.get_selected_items():
            if selitem is not item and selitem.can_move():
                selitem.move_with_selection(x1 - x0, y1 - y0)

    def _resize_selected_items_together(
        self, item: itf.IBasePlotItem, zoom_dx: float, zoom_dy: float
    ) -> None:
        """Selected items resize together

        Args:
            item (IBasePlotItem): the item
            zoom_dx (float): the zoom factor along the x axis
            zoom_dy (float): the zoom factor along the y axis
        """
        for selitem in self.get_selected_items():
            if (
                selitem is not item
                and selitem.can_resize()
                and itf.IBaseImageItem in selitem.__implements__
            ):
                if zoom_dx != 0 or zoom_dy != 0:
                    selitem.resize_with_selection(zoom_dx, zoom_dy)

    def _rotate_selected_items_together(
        self, item: itf.IBasePlotItem, angle: float
    ) -> None:
        """Selected items rotate together

        Args:
            item (IBasePlotItem): the item
            angle (float): the new angle (in radians)
        """
        for selitem in self.get_selected_items():
            if (
                selitem is not item
                and selitem.can_rotate()
                and itf.IBaseImageItem in selitem.__implements__
            ):
                selitem.rotate_with_selection(angle)

    def set_manager(self, manager: PlotManager, plot_id: int) -> None:
        """Set the associated :py:class:`.plot.manager.PlotManager` instance

        Args:
            manager (PlotManager): the manager
            plot_id (int): the plot id
        """
        self.manager = manager
        self.plot_id = plot_id

    def sizeHint(self) -> QC.QSize:
        """Preferred size"""
        return QC.QSize(400, 300)

    def get_title(self) -> str:
        """Get plot title"""
        return str(self.title().text())

    def set_title(self, title: str) -> None:
        """Set plot title

        Args:
            title (str): the title
        """
        text = qwt.QwtText(title)
        text.setFont(self.font_title)
        self.setTitle(text)
        self.SIG_PLOT_LABELS_CHANGED.emit(self)

    def get_show_axes_tab(self) -> bool:
        """Get whether the axes tab is shown in the parameters dialog

        Returns:
            bool: True if the axes tab is shown
        """
        return self.options.show_axes_tab

    def set_show_axes_tab(self, show: bool) -> None:
        """Set whether the axes tab is shown in the parameters dialog

        Args:
            show (bool): True to show the axes tab
        """
        self.options.show_axes_tab = show

    def get_axis_id(self, axis_name: str | int) -> int:
        """Return axis ID from axis name
        If axis ID is passed directly, check the ID

        Args:
            axis_name (str | int): the axis name or ID

        Returns:
            int: the axis ID
        """
        assert axis_name in self.AXIS_NAMES or axis_name in self.AXIS_IDS
        return self.AXIS_NAMES.get(axis_name, axis_name)

    def read_axes_styles(self, section: str, options: list[str, str, str, str]) -> None:
        """
        Read axes styles from section and options (one option
        for each axis in the order left, right, bottom, top)

        Skip axis if option is None

        Args:
            section (str): the section
            options (list[str, str, str, str]): the options
        """
        for prm, option in zip(self.axes_styles, options):
            if option is None:
                continue
            prm.read_config(CONF, section, option)
        self.update_all_axes_styles()

    def get_axis_title(self, axis_id: int) -> str:
        """Get axis title

        Args:
            axis_id (int): the axis id

        Returns:
            str: the axis title
        """
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].title

    def set_axis_title(self, axis_id: int, text: str) -> None:
        """Set axis title

        Args:
            axis_id (int): the axis id
            text (str): the axis title
        """
        axis_id = self.get_axis_id(axis_id)
        self.axes_styles[axis_id].title = text
        self.update_axis_style(axis_id)

    def get_axis_unit(self, axis_id: int) -> str:
        """Get axis unit

        Args:
            axis_id (int): the axis id

        Returns:
            str: the axis unit
        """
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].unit

    def set_axis_unit(self, axis_id: int, text: str) -> None:
        """Set axis unit

        Args:
            axis_id (int): the axis id
            text (str): the axis unit
        """
        axis_id = self.get_axis_id(axis_id)
        self.axes_styles[axis_id].unit = text
        self.update_axis_style(axis_id)

    def get_axis_font(self, axis_id: int) -> QG.QFont:
        """Get axis font

        Args:
            axis_id (int): the axis id

        Returns:
            QFont: the axis font
        """
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].title_font.build_font()

    def set_axis_font(self, axis_id: int, font: QG.QFont) -> None:
        """Set axis font

        Args:
            axis_id (int): the axis id
            font (QFont): the axis font
        """
        axis_id = self.get_axis_id(axis_id)
        self.axes_styles[axis_id].title_font.update_param(font)
        self.axes_styles[axis_id].ticks_font.update_param(font)
        self.update_axis_style(axis_id)

    def get_axis_color(self, axis_id: int) -> str:
        """Get axis color (color name, i.e. string)

        Args:
            axis_id (int): the axis id

        Returns:
            str: the axis color
        """
        axis_id = self.get_axis_id(axis_id)
        return self.axes_styles[axis_id].color

    def set_axis_color(self, axis_id: int, color: str | QG.QColor) -> None:
        """
        Set axis color

        Args:
            axis_id (int): the axis id
            color (str | QColor): the axis color
        """
        axis_id = self.get_axis_id(axis_id)
        if isinstance(color, str):
            color = QG.QColor(color)
        self.axes_styles[axis_id].color = str(color.name())
        self.update_axis_style(axis_id)

    def update_axis_style(self, axis_id: int) -> None:
        """Update axis style

        Args:
            axis_id (int): the axis id
        """
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

    def update_all_axes_styles(self) -> None:
        """Update all axes styles"""
        for axis_id in self.AXIS_IDS:
            self.update_axis_style(axis_id)

    def get_axis_limits(self, axis_id: int) -> tuple[float, float]:
        """Return axis limits (minimum and maximum values)

        Args:
            axis_id (int): the axis id

        Returns:
            tuple[float, float]: the axis limits
        """
        axis_id = self.get_axis_id(axis_id)
        sdiv = self.axisScaleDiv(axis_id)
        return sdiv.lowerBound(), sdiv.upperBound()

    def set_axis_limits(
        self, axis_id: int, vmin: float, vmax: float, stepsize: int = 0
    ) -> None:
        """Set axis limits (minimum and maximum values) and step size

        Args:
            axis_id (int): the axis id
            vmin (float): the minimum value
            vmax (float): the maximum value
            stepsize (int): the step size (optional, default=0)
        """
        axis_id = self.get_axis_id(axis_id)
        vmin, vmax = sorted([vmin, vmax])
        if self.get_axis_direction(axis_id):
            self.setAxisScale(axis_id, vmax, vmin, stepsize)
        else:
            self.setAxisScale(axis_id, vmin, vmax, stepsize)
        self._start_autoscaled = False

    def set_axis_ticks(
        self, axis_id: int, nmajor: int | None = None, nminor: int | None = None
    ) -> None:
        """Set axis maximum number of major ticks and maximum of minor ticks

        Args:
            axis_id (int): the axis id
            nmajor (int): the maximum number of major ticks
            nminor (int): the maximum number of minor ticks
        """
        axis_id = self.get_axis_id(axis_id)
        if nmajor is not None:
            self.setAxisMaxMajor(axis_id, nmajor)
        if nminor is not None:
            self.setAxisMaxMinor(axis_id, nminor)

    def get_axis_scale(self, axis_id: int) -> str:
        """Return the name ('lin', 'log', or 'datetime') of the scale used by axis

        Args:
            axis_id (int): the axis id

        Returns:
            str: the axis scale
        """
        axis_id = self.get_axis_id(axis_id)
        engine = self.axisScaleEngine(axis_id)

        # Check for most specific types first, since datetime inherits from linear
        if isinstance(engine, self.AXIS_TYPES["datetime"]):
            return "datetime"
        elif isinstance(engine, self.AXIS_TYPES["log"]):
            return "log"
        elif isinstance(engine, self.AXIS_TYPES["lin"]):
            return "lin"
        else:
            return "lin"  # unknown default to linear

    def set_axis_scale(self, axis_id: int, scale: str, autoscale: bool = True) -> None:
        """Set axis scale

        Args:
            axis_id (int): the axis id
            scale (str): the axis scale ('lin', 'log', or 'datetime')
            autoscale (bool): autoscale the axis (optional, default=True)

        Example:
            self.set_axis_scale(curve.yAxis(), 'lin')
            self.set_axis_scale('bottom', 'datetime')  # For time series data
        """
        axis_id = self.get_axis_id(axis_id)
        scale_engine = self.AXIS_TYPES[scale]()

        if scale != self.get_axis_scale(axis_id):
            if scale == "datetime":
                self.setAxisScaleDraw(axis_id, qwt.QwtDateTimeScaleDraw())
            else:
                self.setAxisScaleDraw(axis_id, qwt.QwtScaleDraw())

        self.setAxisScaleEngine(axis_id, scale_engine)
        if autoscale:
            self.do_autoscale(replot=False)

    def get_scales(self) -> tuple[str, str]:
        """Return active curve scales

        Example:
            self.get_scales() -> ('lin', 'lin')"""
        ax, ay = self.get_active_axes()
        return self.get_axis_scale(ax), self.get_axis_scale(ay)

    def set_scales(self, xscale: str, yscale: str) -> None:
        """Set active curve scales

        Args:
            xscale (str): the x axis scale ('lin', 'log' or 'datetime')
            yscale (str): the y axis scale ('lin' or 'log')

        Example:
            self.set_scales('lin', 'lin')"""
        ax, ay = self.get_active_axes()
        self.set_axis_scale(ax, xscale)
        self.set_axis_scale(ay, yscale)
        self.replot()

    def set_axis_datetime(
        self,
        axis_id: int | str,
        format: str = "%Y-%m-%d %H:%M:%S",
        rotate: float = -45,
        spacing: int = 4,
    ) -> None:
        """Configure an axis to display datetime labels

        This method sets up an axis to display Unix timestamps as formatted
        date/time strings.

        Args:
            axis_id: Axis ID (constants.Y_LEFT, constants.X_BOTTOM, ...)
                or string: 'bottom', 'left', 'top' or 'right'
            format: Format string for datetime display (default: "%Y-%m-%d %H:%M:%S").
                Uses Python datetime.strftime() format codes.
            rotate: Rotation angle for labels in degrees (default: -45)
            spacing: Spacing between labels (default: 4)

        Examples:
            >>> # Enable datetime on x-axis with default format
            >>> plot.set_axis_datetime("bottom")

            >>> # Enable datetime with time only
            >>> plot.set_axis_datetime("bottom", format="%H:%M:%S")

            >>> # Enable datetime with date only, no rotation
            >>> plot.set_axis_datetime("bottom", format="%Y-%m-%d", rotate=0)
        """
        axis_id = self.get_axis_id(axis_id)
        scale_draw = qwt.QwtDateTimeScaleDraw(format=format, spacing=spacing)
        self.setAxisScaleDraw(axis_id, scale_draw)
        scale_engine = qwt.QwtDateTimeScaleEngine()
        self.setAxisScaleEngine(axis_id, scale_engine)
        if rotate != 0:
            self.setAxisLabelRotation(axis_id, rotate)
            if rotate < 0:
                self.setAxisLabelAlignment(axis_id, QC.Qt.AlignLeft | QC.Qt.AlignBottom)
            else:
                self.setAxisLabelAlignment(
                    axis_id, QC.Qt.AlignRight | QC.Qt.AlignBottom
                )
        self.do_autoscale()

    def set_axis_limits_from_datetime(
        self,
        axis_id: int | str,
        dt_min: datetime,
        dt_max: datetime,
        stepsize: int = 0,
    ) -> None:
        """Set axis limits using datetime objects

        This is a convenience method to set axis limits for datetime axes without
        manually converting datetime objects to Unix timestamps.

        Args:
            axis_id: Axis ID (constants.Y_LEFT, constants.X_BOTTOM, ...)
                or string: 'bottom', 'left', 'top' or 'right'
            dt_min: Minimum datetime value
            dt_max: Maximum datetime value
            stepsize: The step size (optional, default=0)

        Examples:
            >>> from datetime import datetime
            >>> # Set x-axis limits to a specific date range
            >>> dt1 = datetime(2025, 10, 7, 10, 0, 0)
            >>> dt2 = datetime(2025, 10, 7, 18, 0, 0)
            >>> plot.set_axis_limits_from_datetime("bottom", dt1, dt2)
        """
        if not isinstance(dt_min, datetime) or not isinstance(dt_max, datetime):
            raise TypeError("dt_min and dt_max must be datetime objects")

        # Convert datetime objects to Unix timestamps
        epoch = datetime(1970, 1, 1)
        timestamp_min = (dt_min - epoch).total_seconds()
        timestamp_max = (dt_max - epoch).total_seconds()

        # Set the axis limits using the timestamps
        self.set_axis_limits(axis_id, timestamp_min, timestamp_max, stepsize)

    def get_autoscale_margin_percent(self) -> float:
        """Get autoscale margin percentage

        Returns:
            float: the autoscale margin percentage
        """
        return self.autoscale_margin_percent

    def set_autoscale_margin_percent(self, margin_percent: float) -> None:
        """Set autoscale margin percentage

        Args:
            margin_percent (float): the autoscale margin percentage (0-50)

        Raises:
            ValueError: if margin_percent is not in valid range
        """
        if margin_percent < 0:
            raise ValueError("autoscale_margin_percent must be non-negative")
        if margin_percent > 50:
            raise ValueError("autoscale_margin_percent must be <= 50%")

        self.autoscale_margin_percent = margin_percent
        # Trigger an autoscale to apply the new margin immediately
        self.do_autoscale(replot=True)

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
        if self.options.type == PlotType.IMAGE or self.options.force_colorbar_enabled:
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

    def get_items(
        self,
        z_sorted: bool = False,
        item_type: type[itf.IItemType | itf.IBasePlotItem] | None = None,
    ) -> list[itf.IBasePlotItem]:
        """Return widget's item list
        (items are based on IBasePlotItem's interface)

        Args:
            z_sorted (bool): sort items by z order (optional, default=False)
            item_type (IItemType): the item type (optional, default=None)

        Returns:
            list[IBasePlotItem]: the item list
        """
        if z_sorted:
            items = sorted(self.items, reverse=True, key=lambda x: x.z())
        else:
            items = self.items
        if item_type is None:
            return items
        else:
            assert issubclass(item_type, itf.IItemType)
            return [item for item in items if item_type in item.types()]

    def get_public_items(
        self, z_sorted: bool = False, item_type: itf.IBasePlotItem | None = None
    ) -> list[itf.IBasePlotItem]:
        """Return widget's public item list
        (items are based on IBasePlotItem's interface)

        Args:
            z_sorted (bool): sort items by z order (optional, default=False)
            item_type (IItemType): the item type (optional, default=None)

        Returns:
            list[IBasePlotItem]: the item list
        """
        return [
            item
            for item in self.get_items(z_sorted=z_sorted, item_type=item_type)
            if not item.is_private()
        ]

    def get_private_items(
        self, z_sorted: bool = False, item_type: itf.IBasePlotItem | None = None
    ) -> list[itf.IBasePlotItem]:
        """Return widget's private item list
        (items are based on IBasePlotItem's interface)

        Args:
            z_sorted (bool): sort items by z order (optional, default=False)
            item_type (IItemType): the item type (optional, default=None)

        Returns:
            list[IBasePlotItem]: the item list
        """
        return [
            item
            for item in self.get_items(z_sorted=z_sorted, item_type=item_type)
            if item.is_private()
        ]

    def copy_to_clipboard(self) -> None:
        """Copy widget's window to clipboard"""
        clipboard = QW.QApplication.clipboard()
        pixmap = self.grab()
        clipboard.setPixmap(pixmap)

    def save_widget(self, fname: str) -> None:
        """Grab widget's window and save it to filename (/*.png, /*.pdf)

        Args:
            fname (str): the filename
        """
        fname = str(fname)
        if fname.lower().endswith(".pdf"):
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setPageOrientation(QG.QPageLayout.Landscape)
            printer.setOutputFileName(fname)
            printer.setCreator("plotpy")
            self.print_(printer)
        elif fname.lower().endswith(".png"):
            pixmap = self.grab()
            pixmap.save(fname, "PNG")
        else:
            raise RuntimeError(_("Unknown file extension"))

    def get_selected_items(
        self, z_sorted=False, item_type: itf.IBasePlotItem | None = None
    ) -> list[itf.IBasePlotItem]:
        """Return selected items

        Args:
            z_sorted (bool): sort items by z order (optional, default=False)
            item_type (IItemType): the item type (optional, default=None)

        Returns:
            list[IBasePlotItem]: the selected items
        """
        return [
            item
            for item in self.get_items(item_type=item_type, z_sorted=z_sorted)
            if item.selected
        ]

    def get_max_z(self) -> int:
        """
        Return maximum z-order for all items registered in plot
        If there is no item, return 0

        Returns:
            int: the maximum z-order
        """
        if self.items:
            return max([_it.z() for _it in self.items])
        else:
            return 0

    def add_item(
        self, item: itf.IBasePlotItem, z: int | None = None, autoscale: bool = True
    ) -> None:
        """
        Add a plot item instance to this plot widget

        Args:
            item (IBasePlotItem): the item
            z (int): the z order (optional, default=None)
            autoscale (bool): autoscale the plot (optional, default=True)
        """
        if not hasattr(item, "__implements__"):
            raise TypeError("item must implement IBasePlotItem interface")
        assert itf.IBasePlotItem in item.__implements__

        if isinstance(item, qwt.QwtPlotCurve):
            item.setRenderHint(qwt.QwtPlotItem.RenderAntialiased, self.antialiased)

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
            parent = self.parentWidget()
            if parent is not None:
                parent.setUpdatesEnabled(False)
            self.update_colormap_axis(item)
            if autoscale:
                self.do_autoscale()
            if parent is not None:
                parent.setUpdatesEnabled(True)

    def add_item_with_z_offset(self, item: itf.IBasePlotItem, zoffset: int) -> None:
        """
        Add a plot item instance within a specified z range, over an offset

        Args:
            item (IBasePlotItem): the item
            zoffset (int): the z offset
        """
        zlist = sorted(
            [_it.z() for _it in self.items if _it.z() >= zoffset] + [zoffset - 1]
        )
        dzlist = np.argwhere(np.diff(zlist) > 1).flatten()
        if len(dzlist) == 0:
            z = max(zlist) + 1
        else:
            z = zlist[int(dzlist[0])] + 1
        self.add_item(item, z=z)

    def __clean_item_references(self, item: itf.IBasePlotItem) -> None:
        """Remove all reference to this item (active,
        last_selected

        Args:
            item (IBasePlotItem): the item
        """
        if item is self.active_item:
            self.active_item: qwt.QwtPlotItem = None
            self._active_xaxis = self.DEFAULT_ACTIVE_XAXIS
            self._active_yaxis = self.DEFAULT_ACTIVE_YAXIS
        for key, it in list(self.last_selected.items()):
            if item is it:
                del self.last_selected[key]

    def del_items(self, items: list[itf.IBasePlotItem]) -> None:
        """Remove item from widget

        Args:
            items (list[IBasePlotItem]): the items
        """
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

    def del_item(self, item: itf.IBasePlotItem) -> None:
        """
        Remove item from widget
        Convenience function (see 'del_items')

        Args:
            item (IBasePlotItem): the item
        """
        try:
            self.del_items([item])
        except ValueError:
            raise ValueError("item not in plot")

    def set_item_visible(
        self,
        item: itf.IBasePlotItem,
        state: bool,
        notify: bool = True,
        replot: bool = True,
    ) -> None:
        """Show/hide *item* and emit a SIG_ITEMS_CHANGED signal

        Args:
            item (IBasePlotItem): the item
            state (bool): the visibility state
            notify (bool): notify the item list (optional, default=True)
            replot (bool): replot the widget (optional, default=True)
        """
        item.setVisible(state)
        if item is self.active_item and not state:
            self.set_active_item(None)  # Notify the item list (see baseplot)
        if notify:
            self.SIG_ITEMS_CHANGED.emit(self)
        if replot:
            self.replot()

    def __set_items_visible(
        self,
        state: bool,
        items: list[itf.IBasePlotItem] | None = None,
        item_type: itf.IBasePlotItem | None = None,
    ) -> None:
        """Show/hide items (if *items* is None, show/hide all items)

        Args:
            state (bool): the visibility state
            items (list[IBasePlotItem]): the items (optional, default=None)
            item_type (IBasePlotItem): the item type (optional, default=None)
        """
        if items is None:
            items = self.get_items(item_type=item_type)
        for item in items:
            self.set_item_visible(item, state, notify=False, replot=False)
        self.SIG_ITEMS_CHANGED.emit(self)
        self.replot()

    def show_items(
        self,
        items: list[itf.IBasePlotItem] | None = None,
        item_type: itf.IBasePlotItem | None = None,
    ) -> None:
        """Show items (if *items* is None, show all items)

        Args:
            items (list[IBasePlotItem]): the items (optional, default=None)
            item_type (IBasePlotItem): the item type (optional, default=None)
        """
        self.__set_items_visible(True, items, item_type=item_type)

    def hide_items(
        self,
        items: list[itf.IBasePlotItem] | None = None,
        item_type: itf.IBasePlotItem | None = None,
    ) -> None:
        """Hide items (if *items* is None, hide all items)

        Args:
            items (list[IBasePlotItem]): the items (optional, default=None)
            item_type (IBasePlotItem): the item type (optional, default=None)
        """
        self.__set_items_visible(False, items, item_type=item_type)

    def save_items(self, iofile: str | IO[str], selected: bool = False) -> None:
        """
        Save (serializable) items to file using the :py:mod:`pickle` protocol

        Args:
            iofile (str | IO[str]): the file object or filename
            selected (bool): if True, will save only selected items
             (optional, default=False)

        See also :py:meth:`.BasePlot.restore_items`
        """
        if selected:
            items = self.get_selected_items()
        else:
            items = self.items[:]
        items = [item for item in items if itf.ISerializableType in item.types()]

        pickle.dump(items, iofile)

    def restore_items(self, iofile: str | IO[str]) -> None:
        """
        Restore items from file using the :py:mod:`pickle` protocol

        Args:
            iofile (str | IO[str]): the file object or filename

        See also :py:meth:`.BasePlot.save_items`
        """
        items = pickle.load(iofile)
        for item in items:
            self.add_item(item)

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer

        See also :py:meth:`.BasePlot.restore_items`
        """
        items = [item for item in self.items if itf.ISerializableType in item.types()]
        io.save_items(writer, items)

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader

        See also :py:meth:`.BasePlot.save_items`
        """
        for item in io.load_items(reader):
            self.add_item(item)

    def set_items(self, *args: itf.IBasePlotItem) -> None:
        """Utility function used to quickly setup a plot
        with a set of items

        Args:
            args: the items

        Example:
            self.set_items(item1, item2, item3)
        """
        self.del_all_items()
        for item in args:
            self.add_item(item)

    def del_all_items(self, except_grid: bool = True) -> None:
        """Del all items, eventually (default) except grid

        Args:
            except_grid (bool): if True, don't delete grid (optional, default=True)
        """
        items = [
            item for item in self.items if not except_grid or item is not self.grid
        ]
        self.del_items(items)

    def __swap_items_z(self, item1: qwt.QwtPlotItem, item2: qwt.QwtPlotItem) -> None:
        """Swap items z-order

        Args:
            item1 (QwtPlotItem): the first item
            item2 (QwtPlotItem): the second item
        """
        old_item1_z, old_item2_z = item1.z(), item2.z()
        item1.setZ(max([_it.z() for _it in self.items]) + 1)
        item2.setZ(old_item1_z)
        item1.setZ(old_item2_z)

    def move_up(self, item_list: list[itf.IBasePlotItem] | itf.IBasePlotItem) -> bool:
        """Move item(s) up, i.e. to the foreground
        (swap item with the next item in z-order)

        Args:
            item_list (list[IBasePlotItem] | IBasePlotItem): the item(s)

        Returns:
            bool: True if items have been moved effectively
        """
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

    def move_down(self, item_list: list[itf.IBasePlotItem] | itf.IBasePlotItem) -> bool:
        """Move item(s) down, i.e. to the background
        (swap item with the previous item in z-order)

        Args:
            item_list (list[IBasePlotItem] | IBasePlotItem): the item(s)

        Returns:
            bool: True if items have been moved effectively
        """
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

    def set_items_readonly(self, state: bool) -> None:
        """Set all items readonly state to *state*
        Default item's readonly state: False (items may be deleted)

        Args:
            state (bool): the readonly state
        """
        for item in self.get_items():
            item.set_readonly(state)
        self.SIG_ITEMS_CHANGED.emit(self)

    def select_item(self, item: itf.IBasePlotItem) -> None:
        """Select item

        Args:
            item (IBasePlotItem): the item
        """
        item.select()
        for itype in item.types():
            self.last_selected[itype] = item
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def unselect_item(self, item: itf.IBasePlotItem) -> None:
        """Unselect item

        Args:
            item (IBasePlotItem): the item
        """
        item.unselect()
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def get_last_active_item(
        self, item_type: type[itf.IItemType]
    ) -> itf.IBasePlotItem | None:
        """Return last active item corresponding to passed `item_type`

        Args:
            item_type (IItemType): the item type

        Returns:
            IBasePlotItem: the item
        """
        assert issubclass(item_type, itf.IItemType)
        return self.last_selected.get(item_type)

    def select_all(self) -> None:
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

    def unselect_all(self) -> None:
        """Unselect all selected items"""
        for item in self.items:
            if item.can_select():
                item.unselect()
        self.set_active_item(None)
        self.SIG_ITEM_SELECTION_CHANGED.emit(self)

    def select_some_items(self, items: list[itf.IBasePlotItem]) -> None:
        """Select items

        Args:
            items (list[IBasePlotItem]): the items
        """
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

    def set_active_item(self, item: itf.IBasePlotItem, select: bool = True) -> None:
        """Set active item, and unselect the old active item. For CurveItems,
        the grid axes are changed according to the selected item

        Args:
            item: the item
            select: select item after setting it as active (optional, default=True)
        """
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

        if not select and item is not None:
            self.unselect_item(item)

    def get_active_axes(self) -> tuple[int, int]:
        """Return active axes

        Returns:
            tuple[int, int]: the active axes IDs
        """
        item = self.active_item
        if item is not None:
            self._active_xaxis = item.xAxis()
            self._active_yaxis = item.yAxis()
        return self._active_xaxis, self._active_yaxis

    def get_active_item(self, force: bool = False) -> itf.IBasePlotItem | None:
        """
        Return active item
        Force item activation if there is no active item

        Args:
            force (bool): force item activation (optional, default=False)

        Returns:
            IBasePlotItem: the active item or None
        """
        if force and not self.active_item:
            for item in self.get_items():
                if item.can_select():
                    self.set_active_item(item)
                    break
        return self.active_item

    def get_nearest_object(
        self, pos: QC.QPointF, close_dist: int = 0
    ) -> tuple[itf.IBasePlotItem | None, float, int | None, bool]:
        """
        Return nearest item from position 'pos'

        Args:
            pos (QPointF): the position
            close_dist (int): the distance (optional, default=0)

        Returns:
            tuple[IBasePlotItem | None, float, int | None, bool]: the nearest item

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

    def get_nearest_object_in_z(
        self, pos: QC.QPointF
    ) -> tuple[itf.IBasePlotItem | None, int, bool | None, int | None]:
        """
        Return nearest item for which position 'pos' is inside of it
        (iterate over items with respect to their 'z' coordinate)

        Args:
            pos (QPointF): the position

        Returns:
            tuple[IBasePlotItem | None, int, bool | None, int | None]: the nearest item
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

    def get_context_menu(self) -> QW.QMenu:
        """Return widget context menu

        Returns:
            QMenu: the context menu
        """
        return self.manager.get_context_menu(self)

    def get_plot_parameters_status(self, key: str) -> bool:
        """
        Return True if the plot parameters are available

        Args:
            key (str): the parameter key

        Returns:
            bool: True if the plot parameters are available
        """
        if key == "item":
            return self.get_active_item() is not None
        else:
            return True

    def get_selected_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Return a list of DataSets for selected items parameters
        the datasets will be edited and passed back to set_plot_parameters

        Args:
            itemparams (ItemParameters): the item parameters
        """
        for item in self.get_selected_items():
            item.get_item_parameters(itemparams)
        # Retrieving active_item's parameters after every other item:
        # this way, the common datasets will be based on its parameters
        active_item = self.get_active_item()
        active_item.get_item_parameters(itemparams)

    def get_axesparam_class(self, item: itf.IBasePlotItem) -> AxesParam:
        """Return AxesParam dataset class associated to item's type

        Args:
            item (IBasePlotItem): the item

        Returns:
            AxesParam: the AxesParam dataset class
        """
        if isinstance(item, BaseImageItem):
            return ImageAxesParam
        else:
            return AxesParam

    def get_plot_parameters(self, key: str, itemparams: ItemParameters) -> None:
        """
        Return a list of DataSets for a given parameter key
        the datasets will be edited and passed back to set_plot_parameters

        this is a generic interface to help building context menus
        using the BasePlotMenuTool

        Args:
            key (str): the parameter key
            itemparams (ItemParameters): the item parameters
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
            if self.get_show_axes_tab():
                Param = self.get_axesparam_class(active_item)
                axesparam = Param(
                    title=_("Axes"),
                    icon="lin_lin.png",
                    comment=_("Axes associated to selected item"),
                )
                axesparam.update_param(active_item)
                itemparams.add("AxesParam", self, axesparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """Set item (plot, here) parameters

        Args:
            itemparams (ItemParameters): the item parameters
        """
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
            if active_item is not None:
                # active_item may be None when dealing with non-selectable items only
                dataset.update_item(active_item)

    def edit_plot_parameters(self, key: str) -> None:
        """
        Edit plot parameters

        Args:
            key (str): the parameter key
        """
        multiselection = len(self.get_selected_items()) > 1
        itemparams = ItemParameters(multiselection=multiselection)
        self.get_plot_parameters(key, itemparams)
        title, icon = PARAMETERS_TITLE_ICON[key]
        itemparams.edit(self, title, icon)

    def edit_axis_parameters(self, axis_id: int) -> None:
        """Edit axis parameters

        Args:
            axis_id (int): the axis ID
        """
        if axis_id != self.colormap_axis:
            if axis_id in (cst.Y_LEFT, cst.Y_RIGHT):
                title = _("Y Axis")
            else:
                title = _("X Axis")
            param = AxisParam(title=title)
            param.update_param(self, axis_id)
            if param.edit(parent=self):
                param.update_axis(self, axis_id)
                self.replot()

    def add_autoscale_types(self, item_types: tuple[type]) -> None:
        """
        Add item types to autoscale list

        Args:
            item_types (tuple[type]): the item types
        """
        self.AUTOSCALE_TYPES += item_types

    def add_autoscale_excludes(self, items: list[itf.IBasePlotItem]) -> None:
        """Add items to autoscale excludes list

        Args:
            items (list[IBasePlotItem]): the items
        """
        current_list = self.get_auto_scale_excludes()
        for item in items:
            if item not in current_list:
                self.__autoscale_excluded_items.append(weakref.ref(item))

    def remove_autoscale_excludes(self, items: list[itf.IBasePlotItem]) -> None:
        """Remove items from autoscale excludes list

        Args:
            items (list[IBasePlotItem]): the items
        """
        current_list = self.get_auto_scale_excludes()
        for item in items:
            if item in current_list:
                self.__autoscale_excluded_items.remove(weakref.ref(item))

    def get_auto_scale_excludes(self) -> list[itf.IBasePlotItem]:
        """Return autoscale excludes

        Returns:
            list[IBasePlotItem]: the items
        """
        # Update the list of excluded items, removing the items that have been
        # deleted since the last call to this method
        self.__autoscale_excluded_items = [
            item_ref
            for item_ref in self.__autoscale_excluded_items
            if item_ref() is not None
        ]
        return [item_ref() for item_ref in self.__autoscale_excluded_items]

    def do_autoscale(self, replot: bool = True, axis_id: int | None = None) -> None:
        """Do autoscale on all axes

        Args:
            replot (bool): replot the widget (optional, default=True)
            axis_id (int | None): the axis ID (optional, default=None)
        """
        auto = self.autoReplot()
        self.setAutoReplot(False)
        # TODO: Implement the case when axes are synchronised
        for axis_id in self.AXIS_IDS if axis_id is None else [axis_id]:
            vmin, vmax = None, None
            if not self.axisEnabled(axis_id):
                continue
            for item in self.get_items():
                if (
                    isinstance(item, self.AUTOSCALE_TYPES)
                    and not item.is_empty()
                    and item.isVisible()
                    and item not in self.get_auto_scale_excludes()
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
                margin = self.autoscale_margin_percent / 100.0
                vmin -= margin * dv
                vmax += margin * dv
            elif vmin > 0 and vmax > 0:  # log scale
                dv = np.log10(vmax) - np.log10(vmin)
                margin = self.autoscale_margin_percent / 100.0
                vmin = 10 ** (np.log10(vmin) - margin * dv)
                vmax = 10 ** (np.log10(vmax) + margin * dv)
            self.set_axis_limits(axis_id, vmin, vmax)
        self.setAutoReplot(auto)
        self.updateAxes()
        if self.lock_aspect_ratio:
            self.apply_aspect_ratio(full_scale=True)
        if replot:
            self.replot()
        self.SIG_PLOT_AXIS_CHANGED.emit(self)

    def disable_autoscale(self) -> None:
        """Re-apply the axis scales so as to disable autoscaling
        without changing the view"""
        for axis_id in self.AXIS_IDS:
            vmin, vmax = self.get_axis_limits(axis_id)
            self.set_axis_limits(axis_id, vmin, vmax)

    def invalidate(self) -> None:
        """Invalidate paint cache and schedule redraw
        use instead of replot when only the content
        of the canvas needs redrawing (axes, shouldn't change)
        """
        self.canvas().replot()
        self.update()

    def get_axis_direction(self, axis_id: int | str) -> bool:
        """
        Return axis direction of increasing values

        Args:
            axis_id: axis id (constants.Y_LEFT, constants.X_BOTTOM, ...)
             or string: 'bottom', 'left', 'top' or 'right'

        Returns:
            False (default)
        """
        axis_id = self.get_axis_id(axis_id)
        return self.axes_reverse[axis_id]

    def set_axis_direction(self, axis_id: int | str, reverse: bool = False) -> None:
        """
        Set axis direction of increasing values

        Args:
            axis_id: axis id (constants.Y_LEFT, constants.X_BOTTOM, ...)
             or string: 'bottom', 'left', 'top' or 'right'
            reverse (bool): False (default)

        If reverse is False:

            - x-axis values increase from left to right
            - y-axis values increase from bottom to top

        If reverse is True:

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

    def set_titles(
        self,
        title: str | None = None,
        xlabel: str | tuple[str, str] | None = None,
        ylabel: str | tuple[str, str] | None = None,
        xunit: str | tuple[str, str] | None = None,
        yunit: str | tuple[str, str] | None = None,
    ) -> None:
        """
        Set plot and axes titles at once

        Args:
            title (str): plot title
            xlabel (str | tuple[str, str]): (bottom axis title, top axis title)
             or bottom axis title only
            ylabel (str | tuple[str, str]): (left axis title, right axis title)
             or left axis title only
            xunit (str | tuple[str, str]): (bottom axis unit, top axis unit)
             or bottom axis unit only
            yunit (str | tuple[str, str]): (left axis unit, right axis unit)
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

    def set_pointer(self, pointer_type: str | None) -> None:
        """
        Set pointer.

        Args:
            pointer_type (str): pointer type (None, 'canvas', 'curve')

        Meaning of pointer_type:

            * None: disable pointer
            * 'canvas': enable canvas pointer
            * 'curve': enable on-curve pointer
        """
        self.canvas_pointer = False
        self.curve_pointer = False
        if pointer_type == "canvas":
            self.canvas_pointer = True
        elif pointer_type == "curve":
            self.curve_pointer = True

    def set_antialiasing(self, checked: bool) -> None:
        """Toggle curve antialiasing

        Args:
            checked (bool): True to enable antialiasing
        """
        self.antialiased = checked
        for curve in self.itemList():
            if isinstance(curve, qwt.QwtPlotCurve):
                curve.setRenderHint(qwt.QwtPlotItem.RenderAntialiased, self.antialiased)

    def set_plot_limits(
        self,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        xaxis: str | int = "bottom",
        yaxis: str | int = "left",
    ) -> None:
        """Set plot scale limits

        Args:
            x0 (float): x min
            x1 (float): x max
            y0 (float): y min
            y1 (float): y max
            xaxis (str | int): x axis name or id (optional, default='bottom')
            yaxis (str | int): y axis name or id (optional, default='left')
        """
        self.set_axis_limits(yaxis, y0, y1)
        self.set_axis_limits(xaxis, x0, x1)
        self.updateAxes()
        self.SIG_AXIS_DIRECTION_CHANGED.emit(self, self.get_axis_id(yaxis))
        self.SIG_AXIS_DIRECTION_CHANGED.emit(self, self.get_axis_id(xaxis))

    def get_plot_limits(
        self, xaxis: str | int = "bottom", yaxis: str | int = "left"
    ) -> tuple[float, float, float, float]:
        """Return plot scale limits

        Args:
            xaxis (str | int): x axis name or id (optional, default='bottom')
            yaxis (str | int): y axis name or id (optional, default='left')

        Returns:
            tuple[float, float, float, float]: x0, x1, y0, y1
        """
        x0, x1 = self.get_axis_limits(xaxis)
        y0, y1 = self.get_axis_limits(yaxis)
        return x0, x1, y0, y1

    # ---- Image scale/aspect ratio -related API -------------------------------
    def get_current_aspect_ratio(self) -> float | None:
        """Return current aspect ratio

        Returns:
            The current aspect ratio or None if the aspect ratio cannot be computed
            (this happens when the plot has been shrunk to a size so that the
            width is zero)
        """
        dx = self.axisScaleDiv(cst.X_BOTTOM).range()
        dy = self.axisScaleDiv(cst.Y_LEFT).range()
        h = self.canvasMap(cst.Y_LEFT).pDist()
        w = self.canvasMap(cst.X_BOTTOM).pDist()
        try:
            return fabs((h * dx) / (w * dy))
        except ZeroDivisionError:
            return None

    def get_aspect_ratio(self) -> float:
        """Return aspect ratio

        Returns:
            float: the aspect ratio
        """
        return self.__aspect_ratio

    def set_aspect_ratio(
        self, ratio: float | None = None, lock: bool | None = None
    ) -> None:
        """Set aspect ratio

        Args:
            ratio (float): the aspect ratio (optional, default=None)
            lock (bool): lock aspect ratio (optional, default=None)
        """
        if ratio is not None:
            self.__aspect_ratio = ratio
        if lock is not None:
            self.lock_aspect_ratio = lock
        self.apply_aspect_ratio()

    def apply_aspect_ratio(self, full_scale: bool = False) -> None:
        """
        Apply aspect ratio

        Args:
            full_scale: if True, the aspect ratio is applied to the full scale
             (this argument is True only when doing autoscale, i.e. in method
             :py:meth:`do_autoscale`: it is necessary to ensure that the whole
             image items are visible after autoscale, whatever their aspect ratio)
        """
        if not self.isVisible():
            return
        current_aspect = self.get_current_aspect_ratio()
        if current_aspect is None or (
            abs(current_aspect - self.__aspect_ratio) < self.EPSILON_ASPECT_RATIO
        ):
            return
        ymap = self.canvasMap(cst.Y_LEFT)
        xmap = self.canvasMap(cst.X_BOTTOM)
        h = ymap.pDist()
        w = xmap.pDist()
        dx1, dy1 = xmap.sDist(), fabs(ymap.sDist())
        x0, y0 = xmap.s1(), ymap.s1()
        x1, y1 = xmap.s2(), ymap.s2()
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0

        if w == 0 or h == 0:
            return  # avoid division by zero

        # Compute new Y limits, keeping the same X limits and aspect ratio
        dy2 = (h * dx1) / (w * self.__aspect_ratio)

        # Compute new X limits, keeping the same Y limits and aspect ratio
        dx2 = (w * dy1 * self.__aspect_ratio) / h

        if full_scale and dy2 <= dy1:
            # If the new Y limits are smaller than the current ones,
            # *and* if we are doing autoscale, we keep the current Y limits.
            # Why? Because, if the new Y limits are smaller than the current ones,
            # it means that the image items would not be entirely visible after
            # autoscale, and we don't want that.
            delta_x = 0.5 * (dx2 - dx1)
            x0 -= delta_x
            x1 += delta_x
        else:
            # If we are not doing autoscale, then we only change the Y limits (that
            # is a choice, we could also change the X limits).
            # If we are doing autoscale, then we change the Y limits only if the
            # new Y limits are larger than the current ones, in order to ensure
            # that the image items are entirely visible after autoscale.
            delta_y = 0.5 * (dy2 - dy1)
            y0 -= delta_y
            y1 += delta_y

        self.set_plot_limits(x0, x1, y0, y1)

    # ---- LUT/colormap-related API --------------------------------------------
    def notify_colormap_changed(self) -> None:
        """Levels histogram range has changed"""
        item = self.get_last_active_item(itf.IColormapImageItemType)
        if item is not None:
            self.update_colormap_axis(item)
        self.replot()
        self.SIG_LUT_CHANGED.emit(self)
        self.SIG_ACTIVE_ITEM_CHANGED.emit(self)

    def update_colormap_axis(self, item: itf.IColormapImageItemType) -> None:
        """
        Update colormap axis

        Args:
            item (IColormapImageItemType): the item
        """
        if itf.IColormapImageItemType not in item.types():
            return
        zaxis = self.colormap_axis
        axiswidget: QwtScaleWidget = self.axisWidget(zaxis)
        self.setAxisScale(zaxis, item.min, item.max)
        # XXX: The colormap can't be displayed if min>max, to fix this
        # we should pass an inverted colormap along with _max, _min values
        axiswidget.setColorMap(
            qwt.QwtInterval(item.min, item.max), item.get_color_map()
        )
        self.updateAxes()

    # # Keep this around to debug too many replots
    # def replot(self):
    #     import traceback

    #     traceback.print_stack()
    #     qwt.QwtPlot.replot(self)

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


# Register PolygonShape and annotated shape classes.
# It's not possible to simply register AnnotatedShape class
# because their is no warranty that SHAPE_CLASS implements all methods.
BasePlot.register_autoscale_type(PolygonShape)
BasePlot.register_autoscale_type(AnnotatedRectangle)
BasePlot.register_autoscale_type(AnnotatedCircle)
BasePlot.register_autoscale_type(AnnotatedEllipse)
BasePlot.register_autoscale_type(AnnotatedObliqueRectangle)
BasePlot.register_autoscale_type(AnnotatedSegment)
BasePlot.register_autoscale_type(AnnotatedPoint)
BasePlot.register_autoscale_type(AnnotatedPolygon)
