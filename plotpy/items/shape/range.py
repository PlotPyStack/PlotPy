# -*- coding: utf-8 -*-
"""Range selection shape items."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import guidata.io
import numpy as np
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt.text import QwtText

from plotpy.config import CONF, _
from plotpy.coords import canvas_to_axes
from plotpy.items.shape.base import AbstractShape
from plotpy.styles.shape import RangeShapeParam

if TYPE_CHECKING:
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QPainter
    from qwt import QwtSymbol

    from plotpy.plot import BasePlot
    from plotpy.styles.base import ItemParameters


class BaseRangeSelection(AbstractShape):
    """Range selection shape

    Args:
        _min: Minimum value
        _max: Maximum value
        shapeparam: Shape parameters
    """

    _icon_name = ""
    _horizontal = True  # True for X range, False for Y range
    _label_frac_key = ""  # serialization key for label position fraction

    def __init__(
        self,
        _min: float | None = None,
        _max: float | None = None,
        shapeparam: RangeShapeParam | None = None,
    ) -> None:
        super().__init__()
        self._min = _min
        self._max = _max
        self._label_frac: float = 0.5
        if shapeparam is None:
            self.shapeparam = RangeShapeParam(_("Range"), icon=self._icon_name)
            self.shapeparam.read_config(CONF, "histogram", "range")
            self.shapeparam.text.read_config(CONF, "plot", "marker/cursor/text")
            self.shapeparam.sel_text.read_config(CONF, "plot", "marker/cursor/sel_text")
        else:
            self.shapeparam: RangeShapeParam = shapeparam
        self.pen = None
        self.sel_pen = None
        self.brush = None
        self.handle = None
        self.symbol = None
        self.sel_symbol = None
        self.label_text: QwtText | None = None
        self.sel_label_text: QwtText | None = None
        if self._min is not None and self._max is not None:
            self.shapeparam.update_item(self)  # creates all the above QObjects

    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        self.shapeparam.read_config(CONF, section, option)
        # Override label text style from cursor marker config so that range
        # labels use the same style as cursor markers.
        self.shapeparam.text.read_config(CONF, "plot", "marker/cursor/text")
        self.shapeparam.sel_text.read_config(CONF, "plot", "marker/cursor/sel_text")
        self.shapeparam.update_item(self)

    def _make_label_qwt_text(self, label_str: str) -> QwtText:
        """Create a styled QwtText for the delta label.

        Args:
            label_str: Label string

        Returns:
            Styled QwtText using the item's label_text style.
        """
        text = QwtText(label_str)
        source = self.sel_label_text if self.selected else self.label_text
        if source is not None:
            text.setColor(source.color())
            text.setBackgroundBrush(source.backgroundBrush())
            text.setFont(source.font())
        return text

    def __reduce__(self) -> tuple[type, tuple, tuple]:
        """Return state information for pickling"""
        self.shapeparam.update_param(self)
        state = (self.shapeparam, self._min, self._max, self._label_frac)
        return (self.__class__, (), state)

    def __setstate__(self, state: tuple) -> None:
        """Restore state information from pickling"""
        defaults = (None, 0, 0, 0.5)
        state = state + defaults[len(state) :]
        self.shapeparam, self._min, self._max, self._label_frac = state
        self.shapeparam.update_item(self)

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        self.shapeparam.update_param(self)
        writer.write(self.shapeparam, group_name="shapeparam")
        writer.write(self._min, group_name="min")
        writer.write(self._max, group_name="max")
        writer.write(self._label_frac, group_name=self._label_frac_key)

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self._min = reader.read("min")
        self._max = reader.read("max")
        self.shapeparam = RangeShapeParam(_("Range"), icon=self._icon_name)
        reader.read("shapeparam", instance=self.shapeparam)
        self.shapeparam.update_item(self)
        self._label_frac = reader.read(self._label_frac_key, default=self._label_frac)

    def _primary_axis(self) -> int:
        """Return the primary axis ID (xAxis for horizontal, yAxis for vertical)."""
        return self.xAxis() if self._horizontal else self.yAxis()

    def get_handles_pos(self) -> tuple[float, float, float]:
        """Return the handles position

        Returns:
            Tuple with three elements: (p0, p1, fixed) where p0/p1 are the
            positions of the boundary handles and fixed is the cross-axis
            center position.
        """
        plot = self.plot()
        assert plot is not None, "Item must be attached to a plot"
        rct = plot.canvas().contentsRect()
        if self._horizontal:
            fixed = rct.center().y()
            p0 = plot.transform(self.xAxis(), self._min)
            p1 = plot.transform(self.xAxis(), self._max)
        else:
            fixed = rct.center().x()
            p0 = plot.transform(self.yAxis(), self._min)
            p1 = plot.transform(self.yAxis(), self._max)
        return p0, p1, fixed

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
        plot: BasePlot = self.plot()
        if not plot:
            return
        if self.selected:
            pen: QG.QPen = self.sel_pen
            sym: QwtSymbol = self.sel_symbol
        else:
            pen: QG.QPen = self.pen
            sym: QwtSymbol = self.symbol

        rct = QC.QRectF(plot.canvas().contentsRect())
        if self._horizontal:
            rct.setLeft(xMap.transform(self._min))
            rct.setRight(xMap.transform(self._max))
        else:
            rct.setTop(yMap.transform(self._max))
            rct.setBottom(yMap.transform(self._min))

        painter.fillRect(rct, self.brush)
        painter.setPen(pen)

        if self._horizontal:
            painter.drawLine(rct.topLeft(), rct.bottomLeft())
            painter.drawLine(rct.topRight(), rct.bottomRight())
        else:
            painter.drawLine(rct.topLeft(), rct.topRight())
            painter.drawLine(rct.bottomLeft(), rct.bottomRight())

        dash = QG.QPen(pen)
        dash.setStyle(QC.Qt.DashLine)
        dash.setWidth(1)
        painter.setPen(dash)
        if self._horizontal:
            cx = rct.center().x()
            painter.drawLine(QC.QPointF(cx, rct.top()), QC.QPointF(cx, rct.bottom()))
        else:
            cy = rct.center().y()
            painter.drawLine(QC.QPointF(rct.left(), cy), QC.QPointF(rct.right(), cy))

        if self.can_resize() and not self.is_readonly():
            painter.setPen(pen)
            p0, p1, fixed = self.get_handles_pos()
            if self._horizontal:
                sym.drawSymbol(painter, QC.QPointF(p0, fixed))
                sym.drawSymbol(painter, QC.QPointF(p1, fixed))
            else:
                sym.drawSymbol(painter, QC.QPointF(fixed, p0))
                sym.drawSymbol(painter, QC.QPointF(fixed, p1))

        self._draw_delta_label(painter, rct)

    def _format_label(self, plot: BasePlot) -> str:
        """Format the delta label text with bounds.

        Args:
            plot: Parent plot

        Returns:
            Formatted label string
        """
        delta = abs(self._max - self._min)
        v_min, v_max = self._min, self._max
        if self._horizontal:
            axis = self.xAxis()
            if plot.get_axis_scale(axis) == "datetime":
                return plot.format_coordinate_value(delta, axis)
            sym = "x"
        else:
            sym = "y"
        return (
            f"\u0394{sym} = {delta:g}\n{sym}\u2080 = {v_min:g}  {sym}\u2081 = {v_max:g}"
        )

    def _draw_delta_label(self, painter: QPainter, rct: QC.QRectF) -> None:
        """Draw the delta label at the center of the range.

        Args:
            painter: Painter
            rct: Rectangle of the range selection in canvas coordinates
        """
        plot: BasePlot = self.plot()
        if plot is None:
            return

        label_str = self._format_label(plot)
        text = self._make_label_qwt_text(label_str)
        text_size = text.textSize(text.font())
        canvas_rct = QC.QRectF(plot.canvas().contentsRect())

        if self._horizontal:
            label_y = canvas_rct.top() + self._label_frac * canvas_rct.height()
            label_x = rct.center().x() - text_size.width() / 2
            label_rect = QC.QRectF(
                label_x,
                label_y - text_size.height() / 2,
                text_size.width(),
                text_size.height(),
            )
        else:
            label_x = canvas_rct.left() + self._label_frac * canvas_rct.width()
            label_y = rct.center().y()
            label_rect = QC.QRectF(
                label_x - text_size.width() / 2,
                label_y - text_size.height() / 2,
                text_size.width(),
                text_size.height(),
            )

        painter.save()
        painter.translate(label_rect.topLeft())
        text.draw(
            painter,
            QC.QRectF(0, 0, label_rect.width(), label_rect.height()),
        )
        painter.restore()

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
        coord = pos.x() if self._horizontal else pos.y()
        p0, p1, _fixed = self.get_handles_pos()
        d0 = math.fabs(p0 - coord)
        d1 = math.fabs(p1 - coord)
        d2 = math.fabs((p0 + p1) / 2 - coord)
        z = np.array([d0, d1, d2])
        dist = z.min()
        handle = z.argmin()
        inside = bool(p0 < coord < p1) if p0 < p1 else bool(p1 < coord < p0)
        return dist, handle, inside, None

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        if ctrl:
            # Ctrl+drag: move delta label along the secondary axis
            plot = self.plot()
            if plot is not None:
                canvas = QC.QRectF(plot.canvas().contentsRect())
                if self._horizontal:
                    frac = (pos.y() - canvas.top()) / canvas.height()
                else:
                    frac = (pos.x() - canvas.left()) / canvas.width()
                self._label_frac = max(0.0, min(1.0, frac))
                plot.replot()
            return
        if self._horizontal:
            val, _ = canvas_to_axes(self, pos)
            self.move_point_to(handle, (val, 0), ctrl)
        else:
            _, val = canvas_to_axes(self, pos)
            self.move_point_to(handle, (0, val), ctrl)

    def move_point_to(
        self, handle: int, pos: tuple[float, float], ctrl: bool = False
    ) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        val = pos[0] if self._horizontal else pos[1]
        if handle == 0:
            self._min = val
        elif handle == 1:
            self._max = val
        elif handle == 2:
            move = val - (self._max + self._min) / 2
            self._min += move
            self._max += move
        self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)

    def move_shape(
        self, old_pos: tuple[float, float], new_pos: tuple[float, float]
    ) -> None:
        """Translate the shape such that old_pos becomes new_pos in axis coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        idx = 0 if self._horizontal else 1
        delta = new_pos[idx] - old_pos[idx]
        self._min += delta
        self._max += delta
        self.plot().SIG_RANGE_CHANGED.emit(self, self._min, self._max)
        self.plot().replot()

    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the shape

        Returns:
            Bounding rectangle of the shape
        """
        if self._horizontal:
            return QC.QRectF(self._min, 0, self._max - self._min, 0)
        return QC.QRectF(0, self._min, 0, self._max - self._min)

    def get_range(self) -> tuple[float, float]:
        """Return the range

        Returns:
            Tuple with two elements (min, max).
        """
        return self._min, self._max

    def set_range(self, _min: float, _max: float, dosignal: bool = True) -> None:
        """Set the range

        Args:
            _min: Minimum value
            _max: Maximum value
            dosignal: True to emit the SIG_RANGE_CHANGED signal
        """
        self._min = _min
        self._max = _max
        plot = self.plot()
        if dosignal and plot is not None:
            plot.SIG_RANGE_CHANGED.emit(self, self._min, self._max)

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.shapeparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        self.update_item_parameters()
        itemparams.add("ShapeParam", self, self.shapeparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(self.shapeparam, itemparams.get("ShapeParam"), visible_only=True)
        self.shapeparam.update_item(self)
        self.sel_brush = QG.QBrush(self.brush)


class XRangeSelection(BaseRangeSelection):
    """X range selection shape (horizontal)

    Args:
        _min: Minimum value
        _max: Maximum value
        shapeparam: Shape parameters
    """

    _icon_name = "xrange.png"
    _horizontal = True
    _label_frac_key = "label_y_frac"


assert_interfaces_valid(XRangeSelection)


class YRangeSelection(BaseRangeSelection):
    """Y range selection shape (vertical)

    Args:
        _min: Minimum value
        _max: Maximum value
        shapeparam: Shape parameters
    """

    _icon_name = "yrange.png"
    _horizontal = False
    _label_frac_key = "label_x_frac"


assert_interfaces_valid(YRangeSelection)
