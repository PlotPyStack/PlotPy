# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Quiver plot item
================

This module provides the :py:class:`QuiverItem` class for displaying 2D vector
fields (quiver plots), similar to Matplotlib's :py:func:`matplotlib.pyplot.quiver`.

.. autoclass:: QuiverItem
   :members:
"""

from __future__ import annotations

import math
import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotItem

from plotpy.interfaces import IBasePlotItem, IDecoratorItemType

if TYPE_CHECKING:
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QPainter

    from plotpy.interfaces import IItemType
    from plotpy.styles.base import ItemParameters


class QuiverItem(QwtPlotItem):
    """Quiver (2D vector field) plot item

    Displays arrows at grid positions (X, Y) with direction and magnitude
    defined by (U, V) components, similar to Matplotlib's ``quiver``.

    Args:
        x: 1D or 2D array of arrow X positions
        y: 1D or 2D array of arrow Y positions
        u: 1D or 2D array of arrow X components
        v: 1D or 2D array of arrow Y components
        color: Arrow color (default: black)
        arrow_scale: Scale factor for arrow length in pixels (default: 30.0).
         Larger values produce longer arrows.
        arrow_head_size: Size of arrow heads in pixels (default: 6.0)
        headwidth: Arrow head width as a multiple of head size (default: 0.7)
    """

    __implements__ = (IBasePlotItem,)

    _readonly = True
    _private = False
    _can_select = True
    _can_resize = False
    _can_rotate = False
    _can_move = False
    _icon_name = "quiver.svg"

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        color: str | QG.QColor = "black",
        arrow_scale: float = 30.0,
        arrow_head_size: float = 6.0,
        headwidth: float = 0.7,
    ) -> None:
        super().__init__()
        self.setItemAttribute(QwtPlotItem.AutoScale, True)
        self.selected = False
        self.immutable = True
        self._set_data(x, y, u, v)
        self._color = QG.QColor(color)
        self._arrow_scale = arrow_scale
        self._arrow_head_size = arrow_head_size
        self._headwidth = headwidth

    # ---- Data handling ----------------------------------------------------------

    def _set_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
    ) -> None:
        """Set and validate vector field data.

        Args:
            x: Arrow X positions (1D or 2D)
            y: Arrow Y positions (1D or 2D)
            u: Arrow X direction components (1D or 2D)
            v: Arrow Y direction components (1D or 2D)
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        u = np.asarray(u, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)

        # If X, Y are 1D and U, V are 2D, expand via meshgrid
        if x.ndim == 1 and y.ndim == 1 and u.ndim == 2:
            x, y = np.meshgrid(x, y)

        # Flatten all arrays for uniform processing
        self._x = x.ravel()
        self._y = y.ravel()
        self._u = u.ravel()
        self._v = v.ravel()

        if not (self._x.size == self._y.size == self._u.size == self._v.size):
            raise ValueError("x, y, u, v arrays must have the same number of elements")

    def set_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
    ) -> None:
        """Set vector field data and trigger replot.

        Args:
            x: Arrow X positions (1D or 2D)
            y: Arrow Y positions (1D or 2D)
            u: Arrow X direction components (1D or 2D)
            v: Arrow Y direction components (1D or 2D)
        """
        self._set_data(x, y, u, v)
        plot = self.plot()
        if plot is not None:
            plot.replot()

    def get_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return the vector field data.

        Returns:
            Tuple of (x, y, u, v) arrays
        """
        return self._x, self._y, self._u, self._v

    # ---- Style accessors -------------------------------------------------------

    def set_color(self, color: str | QG.QColor) -> None:
        """Set arrow color.

        Args:
            color: Color name string or QColor
        """
        self._color = QG.QColor(color)

    def get_color(self) -> QG.QColor:
        """Return arrow color.

        Returns:
            Arrow color
        """
        return self._color

    # ---- QwtPlotItem interface -------------------------------------------------

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the data.

        The bounding rectangle is expanded by a margin to ensure arrows at
        the edges of the field remain visible when the plot auto-scales.

        Returns:
            Bounding rectangle in data coordinates
        """
        if self._x.size == 0:
            return QC.QRectF()
        xmin, xmax = float(self._x.min()), float(self._x.max())
        ymin, ymax = float(self._y.min()), float(self._y.max())
        # Add margin to account for arrow length extending beyond base points.
        # Use 10% of the data range, or fall back to a fraction of the min
        # absolute coordinate value for degenerate cases (e.g., single column).
        dx = xmax - xmin
        dy = ymax - ymin
        margin_x = dx * 0.1 if dx > 0 else abs(xmin) * 0.1 + 1.0
        margin_y = dy * 0.1 if dy > 0 else abs(ymin) * 0.1 + 1.0
        return QC.QRectF(
            xmin - margin_x,
            ymin - margin_y,
            dx + 2 * margin_x,
            dy + 2 * margin_y,
        )

    def is_empty(self) -> bool:
        """Return True if the item has no data.

        Returns:
            True if the item is empty, False otherwise
        """
        return self._x.size == 0

    def draw(
        self,
        painter: QPainter,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        canvasRect: QRectF,
    ) -> None:
        """Draw the vector field.

        Args:
            painter: QPainter instance
            xMap: X axis scale map (data -> pixel)
            yMap: Y axis scale map (data -> pixel)
            canvasRect: Canvas rectangle in pixel coordinates
        """
        if self._x.size == 0:
            return

        painter.save()
        painter.setRenderHint(QG.QPainter.Antialiasing)

        # Compute magnitudes and normalize direction vectors
        mag = np.sqrt(self._u**2 + self._v**2)
        max_mag = mag.max()
        if max_mag == 0:
            painter.restore()
            return

        # Normalize to [0, 1] range
        norm_mag = mag / max_mag

        pen_width = 1.5 if not self.selected else 2.5
        color = self._color
        if self.selected:
            color = QG.QColor("red")

        pen = QG.QPen(color, pen_width)
        pen.setCapStyle(QC.Qt.RoundCap)
        pen.setJoinStyle(QC.Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QG.QBrush(color))

        arrow_head_size = self._arrow_head_size
        head_angle = math.pi / 6  # 30 degrees
        headwidth = self._headwidth

        for i in range(self._x.size):
            if mag[i] < 1e-12:
                continue

            # Transform base point to canvas coordinates
            px = xMap.transform(self._x[i])
            py = yMap.transform(self._y[i])

            # Arrow direction (in pixel space, note Y is inverted)
            dx = self._u[i] / max_mag
            dy = -self._v[i] / max_mag  # Negate for screen coordinates

            # Scale arrow length
            length = norm_mag[i] * self._arrow_scale
            end_x = px + dx * length
            end_y = py + dy * length

            # Draw shaft
            painter.drawLine(QC.QPointF(px, py), QC.QPointF(end_x, end_y))

            # Draw arrow head
            if length < 2.0:
                continue  # Too small for a head

            angle = math.atan2(end_y - py, end_x - px)

            h1x = end_x - arrow_head_size * math.cos(angle - head_angle * headwidth)
            h1y = end_y - arrow_head_size * math.sin(angle - head_angle * headwidth)
            h2x = end_x - arrow_head_size * math.cos(angle + head_angle * headwidth)
            h2y = end_y - arrow_head_size * math.sin(angle + head_angle * headwidth)

            head = QG.QPolygonF(
                [
                    QC.QPointF(end_x, end_y),
                    QC.QPointF(h1x, h1y),
                    QC.QPointF(h2x, h2y),
                ]
            )
            painter.drawPolygon(head)

        painter.restore()

    # ---- IBasePlotItem interface -----------------------------------------------

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.

        Returns:
            Tuple of class objects inheriting from IItemType
        """
        return (IDecoratorItemType,)

    def set_readonly(self, state: bool) -> None:
        """Set object readonly state.

        Args:
            state: True if object is readonly, False otherwise
        """
        self._readonly = state

    def is_readonly(self) -> bool:
        """Return object readonly state.

        Returns:
            True if object is readonly, False otherwise
        """
        return self._readonly

    def set_private(self, state: bool) -> None:
        """Set object as private.

        Args:
            state: True if object is private, False otherwise
        """
        self._private = state

    def is_private(self) -> bool:
        """Return True if object is private.

        Returns:
            True if object is private, False otherwise
        """
        return self._private

    def get_icon_name(self) -> str:
        """Return the icon name.

        Returns:
            Icon name
        """
        return self._icon_name

    def set_icon_name(self, icon_name: str) -> None:
        """Set the icon name.

        Args:
            icon_name: Icon name
        """
        self._icon_name = icon_name

    def set_selectable(self, state: bool) -> None:
        """Set item selectable state.

        Args:
            state: True if item is selectable, False otherwise
        """
        self._can_select = state

    def set_resizable(self, state: bool) -> None:
        """Set item resizable state.

        Args:
            state: True if item is resizable, False otherwise
        """
        self._can_resize = state

    def set_movable(self, state: bool) -> None:
        """Set item movable state.

        Args:
            state: True if item is movable, False otherwise
        """
        self._can_move = state

    def set_rotatable(self, state: bool) -> None:
        """Set item rotatable state.

        Args:
            state: True if item is rotatable, False otherwise
        """
        self._can_rotate = state

    def can_select(self) -> bool:
        """Returns True if this item can be selected.

        Returns:
            True if item can be selected, False otherwise
        """
        return self._can_select

    def can_resize(self) -> bool:
        """Returns True if this item can be resized.

        Returns:
            True if item can be resized, False otherwise
        """
        return self._can_resize

    def can_rotate(self) -> bool:
        """Returns True if this item can be rotated.

        Returns:
            True if item can be rotated, False otherwise
        """
        return self._can_rotate

    def can_move(self) -> bool:
        """Returns True if this item can be moved.

        Returns:
            True if item can be moved, False otherwise
        """
        return self._can_move

    def select(self) -> None:
        """Select the object and highlight it."""
        self.selected = True
        plot = self.plot()
        if plot is not None:
            plot.replot()

    def unselect(self) -> None:
        """Unselect the object and restore its appearance."""
        self.selected = False
        plot = self.plot()
        if plot is not None:
            plot.replot()

    def hit_test(self, pos: QPointF) -> tuple[float, float, bool, None]:
        """Return a tuple (distance, attach point, inside, other_object).

        Args:
            pos: Position in canvas coordinates

        Returns:
            Tuple with four elements (distance, attach point, inside, other_object)
        """
        plot = self.plot()
        if plot is None or self._x.size == 0:
            return sys.maxsize, 0, False, None

        # Convert click position to data coordinates
        cx, cy = pos.x(), pos.y()

        # Find the closest arrow base point
        dist = sys.maxsize
        for i in range(self._x.size):
            px = plot.transform(self.xAxis(), self._x[i])
            py = plot.transform(self.yAxis(), self._y[i])
            d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
            if d < dist:
                dist = d

        # Consider "inside" if within the bounding rect on canvas
        rect = self.boundingRect()
        x0 = plot.transform(self.xAxis(), rect.left())
        y0 = plot.transform(self.yAxis(), rect.top())
        x1 = plot.transform(self.xAxis(), rect.right())
        y1 = plot.transform(self.yAxis(), rect.bottom())
        canvas_rect = QC.QRectF(
            QC.QPointF(min(x0, x1), min(y0, y1)),
            QC.QPointF(max(x0, x1), max(y0, y1)),
        )
        inside = canvas_rect.contains(QC.QPointF(cx, cy))

        return dist, 0, inside, None

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties."""

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """Appends datasets to the list of DataSets describing the parameters.

        Args:
            itemparams: Item parameters
        """

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """Change the appearance of this item according to the parameter set.

        Args:
            itemparams: Item parameters
        """

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position.

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos.

        Args:
            old_pos: Old position
            new_pos: New position
        """

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items.

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """


assert_interfaces_valid(QuiverItem)
