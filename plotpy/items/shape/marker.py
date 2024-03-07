# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qwt import QwtPlotMarker

from plotpy.config import CONF, _
from plotpy.coords import canvas_to_axes
from plotpy.interfaces import IBasePlotItem, IShapeItemType
from plotpy.styles.base import MARKERSTYLES
from plotpy.styles.shape import MarkerParam

if TYPE_CHECKING:
    from collections.abc import Callable

    import guidata.dataset.io
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QPainter

    from plotpy.interfaces import IItemType
    from plotpy.styles.base import ItemParameters


class Marker(QwtPlotMarker):
    """Marker shape

    Args:
        label_cb: Label callback (must return a string, takes x and y as arguments)
        constraint_cb: Constraint callback (must return a tuple (x, y),
         takes x and y as arguments)
        markerparam: Marker parameters

    .. note::

        Marker class derives from QwtPlotMarker, which is a QwtPlotItem. That is
        why AbstractShape methods are re-implemented here.
    """

    __implements__ = (IBasePlotItem,)
    _readonly = False
    _private = False
    _can_select = True
    _can_resize = True
    _can_rotate = False
    _can_move = True

    def __init__(
        self,
        label_cb: Callable | None = None,
        constraint_cb: Callable | None = None,
        markerparam: MarkerParam = None,
    ) -> None:
        super().__init__()
        self._pending_center_handle = None
        self.selected = False
        self.label_cb = label_cb
        if constraint_cb is None:
            constraint_cb = self.center_handle
        self.constraint_cb = constraint_cb
        if markerparam is None:
            self.markerparam = MarkerParam(_("Marker"))
            self.markerparam.read_config(CONF, "plot", "marker/cursor")
        else:
            self.markerparam = markerparam
        self.markerparam.update_marker(self)
        self.setIcon(get_icon("marker.png"))

    def __reduce__(self) -> tuple[type, tuple, tuple]:
        """Return state information for pickling"""
        self.markerparam.update_param(self)
        state = (self.markerparam, self.xValue(), self.yValue(), self.z())
        return (Marker, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Restore state information from pickled state"""
        self.markerparam, xvalue, yvalue, z = state
        self.setXValue(xvalue)
        self.setYValue(yvalue)
        self.setZ(z)
        self.markerparam.update_marker(self)

    def serialize(
        self,
        writer: (
            guidata.dataset.io.HDF5Writer
            | guidata.dataset.io.INIWriter
            | guidata.dataset.io.JSONWriter
        ),
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        self.markerparam.update_param(self)
        writer.write(self.markerparam, group_name="markerparam")
        writer.write(self.xValue(), group_name="x")
        writer.write(self.yValue(), group_name="y")
        writer.write(self.z(), group_name="z")

    def deserialize(
        self,
        reader: (
            guidata.dataset.io.HDF5Reader
            | guidata.dataset.io.INIReader
            | guidata.dataset.io.JSONReader
        ),
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.markerparam = MarkerParam(_("Marker"), icon="marker.png")
        reader.read("markerparam", instance=self.markerparam)
        self.markerparam.update_marker(self)
        self.setXValue(reader.read("x"))
        self.setYValue(reader.read("y"))
        self.setZ(reader.read("z"))

    # ------QwtPlotItem API------------------------------------------------------
    def draw(
        self,
        painter: QPainter,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        canvasRect: QRectF,
    ) -> None:
        """Draw the item

        Args:
            painter: Painter
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Canvas rectangle
        """
        if self._pending_center_handle:
            x, y = self.center_handle(self.xValue(), self.yValue())
            self.setValue(x, y)
        self.update_label()
        QwtPlotMarker.draw(self, painter, xMap, yMap, canvasRect)

    # ------IBasePlotItem API----------------------------------------------------
    def set_selectable(self, state: bool) -> None:
        """Set item selectable state

        Args:
            state: True if item is selectable, False otherwise
        """
        self._can_select = state

    def set_resizable(self, state: bool) -> None:
        """Set item resizable state
        (or any action triggered when moving an handle, e.g. rotation)

        Args:
            state: True if item is resizable, False otherwise
        """
        self._can_resize = state

    def set_movable(self, state: bool) -> None:
        """Set item movable state

        Args:
            state: True if item is movable, False otherwise
        """
        self._can_move = state

    def set_rotatable(self, state: bool) -> None:
        """Set item rotatable state

        Args:
            state: True if item is rotatable, False otherwise
        """
        self._can_rotate = state

    def can_select(self) -> bool:
        """
        Returns True if this item can be selected

        Returns:
            bool: True if item can be selected, False otherwise
        """
        return self._can_select

    def can_resize(self) -> bool:
        """
        Returns True if this item can be resized

        Returns:
            bool: True if item can be resized, False otherwise
        """
        return self._can_resize

    def can_rotate(self) -> bool:
        """
        Returns True if this item can be rotated

        Returns:
            bool: True if item can be rotated, False otherwise
        """
        return self._can_rotate

    def can_move(self) -> bool:
        """
        Returns True if this item can be moved

        Returns:
            bool: True if item can be moved, False otherwise
        """
        return self._can_move

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType,)

    def set_readonly(self, state: bool) -> None:
        """Set object readonly state

        Args:
            state: True if object is readonly, False otherwise
        """
        self._readonly = state

    def is_readonly(self) -> bool:
        """Return object readonly state

        Returns:
            bool: True if object is readonly, False otherwise
        """
        return self._readonly

    def set_private(self, state: bool) -> None:
        """Set object as private

        Args:
            state: True if object is private, False otherwise
        """
        self._private = state

    def is_private(self) -> bool:
        """Return True if object is private

        Returns:
            bool: True if object is private, False otherwise
        """
        return self._private

    def select(self) -> None:
        """
        Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        if self.selected:
            # Already selected
            return
        self.selected = True
        self.markerparam.update_marker(self)
        self.invalidate_plot()

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        self.selected = False
        self.markerparam.update_marker(self)
        self.invalidate_plot()

    def hit_test(self, pos: QPointF) -> tuple[float, float, bool, None]:
        """Return a tuple (distance, attach point, inside, other_object)

        Args:
            pos: Position

        Returns:
            tuple: Tuple with four elements: (distance, attach point, inside,
             other_object).

        Description of the returned values:

        * distance: distance in pixels (canvas coordinates) to the closest
           attach point
        * attach point: handle of the attach point
        * inside: True if the mouse button has been clicked inside the object
        * other_object: if not None, reference of the object which will be
           considered as hit instead of self
        """
        plot = self.plot()
        xc, yc = pos.x(), pos.y()
        x = plot.transform(self.xAxis(), self.xValue())
        y = plot.transform(self.yAxis(), self.yValue())
        ms = self.markerparam.markerstyle
        # The following assert has no purpose except reminding that the
        # markerstyle is one of the MARKERSTYLES dictionary values, in case
        # this dictionary evolves in the future (this should not fail):
        assert ms in list(MARKERSTYLES.values())
        if ms == "NoLine":
            return math.sqrt((x - xc) ** 2 + (y - yc) ** 2), 0, False, None
        elif ms == "HLine":
            return math.sqrt((y - yc) ** 2), 0, False, None
        elif ms == "VLine":
            return math.sqrt((x - xc) ** 2), 0, False, None
        elif ms == "Cross":
            return math.sqrt(min((x - xc) ** 2, (y - yc) ** 2)), 0, False, None

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.markerparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        self.update_item_parameters()
        itemparams.add("MarkerParam", self, self.markerparam)

    def set_item_parameters(self, itemparams):
        """
        Change the appearance of this item according
        to the parameter set provided

        params is a list of Datasets of the same types as those returned
        by get_item_parameters
        """
        update_dataset(
            self.markerparam, itemparams.get("MarkerParam"), visible_only=True
        )
        self.markerparam.update_marker(self)
        if self.selected:
            self.select()

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        x, y = canvas_to_axes(self, pos)
        self.set_pos(x, y)

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        # This methods is never called because marker is not a shape (but a point)

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        # This methods is never called because marker is not a shape (but a point)

    # ------Public API-----------------------------------------------------------
    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        self.markerparam.read_config(CONF, section, option)
        self.markerparam.update_marker(self)

    def set_pos(self, x: float | None = None, y: float | None = None) -> None:
        """Set marker position

        Args:
            x: X value (if None, use current value)
            y: Y value (if None, use current value)
        """
        if x is None:
            x = self.xValue()
        if y is None:
            y = self.yValue()
        if self.constraint_cb:
            x, y = self.constraint_cb(x, y)
        self.setValue(x, y)
        if self.plot():
            self.plot().SIG_MARKER_CHANGED.emit(self)

    def get_pos(self) -> tuple[float, float]:
        """Get marker position

        Returns:
            Tuple with two elements (x, y)
        """
        return self.xValue(), self.yValue()

    def set_markerstyle(self, style: str | int | None) -> None:
        """Set marker style

        Args:
            style: Marker style
        """
        param = self.markerparam
        param.set_markerstyle(style)
        param.update_marker(self)

    def is_vertical(self) -> bool:
        """Is it a vertical cursor?

        Returns:
            True if this is a vertical cursor
        """
        return self.lineStyle() == QwtPlotMarker.VLine

    def is_horizontal(self) -> bool:
        """Is it a horizontal cursor?

        Returns:
            True if this is a horizontal cursor
        """
        return self.lineStyle() == QwtPlotMarker.HLine

    def center_handle(self, x: float, y: float) -> tuple[float, float]:
        r"""Center cursor handle depending on marker style (\|, -)

        Args:
            x: X value
            y: Y value

        Returns:
            Tuple with two elements (x, y)
        """
        plot = self.plot()
        if plot is None:
            self._pending_center_handle = True
        else:
            self._pending_center_handle = False
            if self.is_vertical():
                ymap = plot.canvasMap(self.yAxis())
                y_top, y_bottom = ymap.s1(), ymap.s2()
                y = 0.5 * (y_top + y_bottom)
            elif self.is_horizontal():
                xmap = plot.canvasMap(self.xAxis())
                x_left, x_right = xmap.s1(), xmap.s2()
                x = 0.5 * (x_left + x_right)
        return x, y

    def invalidate_plot(self) -> None:
        """Invalidate the plot to force a redraw"""
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def update_label(self) -> None:
        """Update label"""
        x, y = self.xValue(), self.yValue()
        if self.label_cb:
            label = self.label_cb(x, y)
            if label is None:
                return
        elif self.is_vertical():
            label = f"x = {x:g}"
        elif self.is_horizontal():
            label = f"y = {y:g}"
        else:
            label = f"x = {x:g}<br>y = {y:g}"
        text = self.label()
        text.setText(label)
        self.setLabel(text)
        plot = self.plot()
        if plot is not None:
            xaxis = plot.axisScaleDiv(self.xAxis())
            if x < (xaxis.upperBound() + xaxis.lowerBound()) / 2:
                hor_alignment = QC.Qt.AlignRight
            else:
                hor_alignment = QC.Qt.AlignLeft
            yaxis = plot.axisScaleDiv(self.yAxis())
            ymap = plot.canvasMap(self.yAxis())
            y_top, y_bottom = ymap.s1(), ymap.s2()
            if y < 0.5 * (yaxis.upperBound() + yaxis.lowerBound()):
                if y_top > y_bottom:
                    ver_alignment = QC.Qt.AlignBottom
                else:
                    ver_alignment = QC.Qt.AlignTop
            else:
                if y_top > y_bottom:
                    ver_alignment = QC.Qt.AlignTop
                else:
                    ver_alignment = QC.Qt.AlignBottom
            self.setLabelAlignment(hor_alignment | ver_alignment)


assert_interfaces_valid(Marker)
