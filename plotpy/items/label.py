# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
plotpy.widgets.label
--------------------

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotItem

from plotpy.config import CONF, _
from plotpy.interfaces import IBasePlotItem, ISerializableType, IShapeItemType
from plotpy.items.curve.base import CurveItem
from plotpy.styles.label import LabelParam

if TYPE_CHECKING:
    from collections.abc import Callable

    import guidata.io
    import qwt.scale_map
    import qwt.symbol
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QBrush, QPainter, QPen, QTextDocument

    from plotpy.interfaces import IItemType
    from plotpy.items import ImageItem, RectangleShape, XRangeSelection
    from plotpy.styles.base import ItemParameters

ANCHORS = {
    "TL": lambda r: (r.left(), r.top()),
    "TR": lambda r: (r.right(), r.top()),
    "BL": lambda r: (r.left(), r.bottom()),
    "BR": lambda r: (r.right(), r.bottom()),
    "L": lambda r: (r.left(), (r.top() + r.bottom()) / 2.0),
    "R": lambda r: (r.right(), (r.top() + r.bottom()) / 2.0),
    "T": lambda r: ((r.left() + r.right()) / 2.0, r.top()),
    "B": lambda r: ((r.left() + r.right()) / 2.0, r.bottom()),
    "C": lambda r: ((r.left() + r.right()) / 2.0, (r.top() + r.bottom()) / 2.0),
}


class AbstractLabelItem(QwtPlotItem):
    """Abstract label plot item

    Draws a label on the canvas at position :
    G+C where G is a point in plot coordinates and C a point
    in canvas coordinates.
    G can also be an anchor string as in ANCHORS in which case
    the label will keep a fixed position wrt the canvas rect

    Args:
        labelparam: Label parameters
    """

    _readonly = False
    _private = False

    def __init__(self, labelparam: LabelParam = None) -> None:
        super().__init__()
        self.selected = False
        self.anchor = None
        self.G = None
        self.C = None
        self.border_pen = None
        self.bg_brush = None
        if labelparam is None:
            self.labelparam = LabelParam(_("Label"), icon="label.png")
        else:
            self.labelparam = labelparam
            self.labelparam.update_label(self)
        self._can_select = True
        self._can_resize = False
        self._can_move = True
        self._can_rotate = False

    def set_style(self, section: str, option: str) -> None:
        """Set style for this item

        Args:
            section: Section
            option: Option
        """
        self.labelparam.read_config(CONF, section, option)
        self.labelparam.update_label(self)

    def __reduce__(self) -> tuple[type, tuple]:
        """Return a tuple containing the constructor and its arguments"""
        return (self.__class__, (self.labelparam,))

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        self.labelparam.update_param(self)
        writer.write(self.labelparam, group_name="labelparam")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.labelparam = LabelParam(_("Label"), icon="label.png")
        reader.read("labelparam", instance=self.labelparam)
        self.labelparam.update_label(self)
        if isinstance(self.G, np.ndarray):
            self.G = tuple(self.G)

    def get_text_rect(self) -> QC.QRectF:
        """Return the text rectangle

        Returns:
            Text rectangle
        """
        return QC.QRectF(0.0, 0.0, 10.0, 10.0)

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType,)

    def set_text_style(
        self, font: QG.QFont | None = None, color: str | None = None
    ) -> None:
        """Set label text style

        Args:
            font: Font
            color: Color
        """
        raise NotImplementedError

    def get_top_left(
        self,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        canvasRect: QC.QRectF,
    ) -> tuple[float, float]:
        """Return the top left corner of the text rectangle

        Args:
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Canvas rectangle

        Returns:
            tuple: Tuple with two elements: (x, y)
        """
        x0, y0 = self.get_origin(xMap, yMap, canvasRect)
        x0 += self.C[0]
        y0 += self.C[1]

        rect = self.get_text_rect()
        pos = ANCHORS[self.anchor](rect)
        x0 -= pos[0]
        y0 -= pos[1]
        return x0, y0

    def get_origin(
        self,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        canvasRect: QC.QRectF,
    ) -> tuple[float, float]:
        """Return the origin of the text rectangle

        Args:
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Canvas rectangle

        Returns:
            tuple: Tuple with two elements: (x, y)
        """
        if self.G in ANCHORS:
            return ANCHORS[self.G](canvasRect)
        else:
            x0 = xMap.transform(self.G[0])
            y0 = yMap.transform(self.G[1])
            return x0, y0

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

    def can_move(self) -> bool:
        """
        Returns True if this item can be moved

        Returns:
            bool: True if item can be moved, False otherwise
        """
        return self._can_move

    def can_rotate(self) -> bool:
        """
        Returns True if this item can be rotated

        Returns:
            bool: True if item can be rotated, False otherwise
        """
        return False  # TODO: Implement labels rotation?

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

    def invalidate_plot(self) -> None:
        """Invalidate the plot to force a redraw"""
        plot = self.plot()
        if plot:
            plot.invalidate()

    def select(self) -> None:
        """
        Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        if self.selected:
            # Already selected
            return
        self.selected = True
        w = self.border_pen.width()
        self.border_pen.setWidth(w + 1)
        self.invalidate_plot()

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        self.selected = False
        self.labelparam.update_label(self)
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
        if plot is None:
            return
        rect = self.get_text_rect()
        canvasRect = plot.canvas().contentsRect()
        xMap = plot.canvasMap(self.xAxis())
        yMap = plot.canvasMap(self.yAxis())
        x, y = self.get_top_left(xMap, yMap, canvasRect)
        rct = QC.QRectF(x, y, rect.width(), rect.height())
        inside = rct.contains(pos.x(), pos.y())
        if inside:
            return self.click_inside(pos.x() - x, pos.y() - y)
        else:
            return 1000.0, None, False, None

    def click_inside(self, locx: float, locy: float) -> tuple[float, float, bool, type]:
        """Called when the mouse button is clicked inside the object

        Args:
            locx: Local x coordinate
            locy: Local y coordinate

        Returns:
            tuple: Tuple with four elements: (distance, attach point, inside,
             other_object).
        """
        return 2.0, 1, True, None

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.labelparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        self.update_item_parameters()
        itemparams.add("LabelParam", self, self.labelparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(self.labelparam, itemparams.get("LabelParam"), visible_only=True)
        self.labelparam.update_label(self)
        if self.selected:
            self.select()

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        if handle != -1:
            return

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        if self.G in ANCHORS or not self.labelparam.move_anchor:
            # Move canvas offset
            lx, ly = self.C
            lx += new_pos.x() - old_pos.x()
            ly += new_pos.y() - old_pos.y()
            self.C = lx, ly
            self.labelparam.xc, self.labelparam.yc = lx, ly
        else:
            # Move anchor
            plot = self.plot()
            if plot is None:
                return
            lx0, ly0 = self.G
            cx = plot.transform(self.xAxis(), lx0)
            cy = plot.transform(self.yAxis(), ly0)
            cx += new_pos.x() - old_pos.x()
            cy += new_pos.y() - old_pos.y()
            lx1 = plot.invTransform(self.xAxis(), cx)
            ly1 = plot.invTransform(self.yAxis(), cy)
            self.G = lx1, ly1
            self.labelparam.xg, self.labelparam.yg = lx1, ly1
            plot.SIG_ITEM_MOVED.emit(self, lx0, ly0, lx1, ly1)

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        if self.G in ANCHORS or not self.labelparam.move_anchor:
            return
        lx0, ly0 = self.G
        lx1, ly1 = lx0 + delta_x, ly0 + delta_y
        self.G = lx1, ly1
        self.labelparam.xg, self.labelparam.yg = lx1, ly1

    def draw_frame(
        self, painter: QPainter, x: float, y: float, w: float, h: float
    ) -> None:
        """Draw the frame

        Args:
            painter: Painter
            x: X coordinate
            y: Y coordinate
            w: Width
            h: Height
        """
        rectf = QC.QRectF(x, y, w, h)
        if self.labelparam.bgalpha > 0.0:
            painter.fillRect(rectf, self.bg_brush)
        if self.border_pen.width() > 0:
            painter.setPen(self.border_pen)
            painter.drawRect(rectf)


class LabelItem(AbstractLabelItem):
    """Label plot item

    Args:
        text: Text
        labelparam: Label parameters
    """

    __implements__ = (IBasePlotItem, ISerializableType)

    def __init__(
        self, text: str | None = None, labelparam: LabelParam | None = None
    ) -> None:
        self.text_string = "" if text is None else text
        self.text = QG.QTextDocument()
        self.marker: qwt.symbol.QwtSymbol | None = None
        super().__init__(labelparam)
        self.setIcon(get_icon("label.png"))

    def __reduce__(self) -> tuple[type, tuple]:
        """Return a tuple containing the constructor and its arguments"""
        return (self.__class__, (self.text_string, self.labelparam))

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        super().serialize(writer)
        writer.write(self.text_string, group_name="text")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        super().deserialize(reader)
        self.set_text(reader.read("text", func=reader.read_unicode))

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType, ISerializableType)

    def set_pos(self, x: float, y: float) -> None:
        """Set position

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.G = x, y
        self.labelparam.abspos = False
        self.labelparam.xg, self.labelparam.yg = x, y

    def get_plain_text(self) -> str:
        """Get plain text

        Returns:
            str: Plain text
        """
        return str(self.text.toPlainText())

    def set_text(self, text: str | None = None) -> None:
        """Set text

        Args:
            text: Text
        """
        if text is not None:
            self.text_string = text
        self.text.setHtml(f"<div>{self.text_string}</div>")

    def set_text_style(
        self, font: QG.QFont | None = None, color: str | None = None
    ) -> None:
        """Set label text style

        Args:
            font: Font
            color: Color
        """
        if font is not None:
            self.text.setDefaultFont(font)
        if color is not None:
            self.text.setDefaultStyleSheet("div { color: %s; }" % color)
        self.set_text()

    def get_text_rect(self) -> QRectF:
        """Return the text rectangle

        Returns:
            Text rectangle
        """
        sz = self.text.size()
        return QC.QRectF(0, 0, sz.width(), sz.height())

    def update_text(self) -> None:
        """Update text"""
        pass

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
        self.update_text()
        x, y = self.get_top_left(xMap, yMap, canvasRect)
        x0, y0 = self.get_origin(xMap, yMap, canvasRect)
        painter.save()
        self.marker.drawSymbols(painter, [QC.QPointF(x0, y0)])
        painter.restore()
        sz = self.text.size()
        self.draw_frame(painter, int(x), int(y), int(sz.width()), int(sz.height()))
        painter.setPen(QG.QPen(QG.QColor(self.labelparam.color)))
        painter.translate(x, y)
        self.text.drawContents(painter)


assert_interfaces_valid(LabelItem)


LEGEND_WIDTH = 30  # Length of the sample line
LEGEND_SPACEH = 5  # Spacing between border, sample, text, border
LEGEND_SPACEV = 3  # Vertical space between items


class LegendBoxItem(AbstractLabelItem):
    """Legend box plot item

    Args:
        labelparam: Label parameters
    """

    __implements__ = (IBasePlotItem, ISerializableType)

    def __init__(self, labelparam: LabelParam = None) -> None:
        self.font = None
        self.color = None
        super().__init__(labelparam)
        # saves the last computed sizes
        self.sizes = 0.0, 0.0, 0.0, 0.0
        self.setIcon(get_icon("legend.png"))

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType, ISerializableType)

    def get_legend_items(
        self,
    ) -> list[tuple[QTextDocument, QPen, QBrush, qwt.symbol.QwtSymbol]]:
        """Return the legend items

        Returns:
            list: List of legend items (text, pen, brush, symbol)
        """
        plot = self.plot()
        if plot is None:
            return []
        text_items = []
        for item in plot.get_items():
            if not isinstance(item, CurveItem) or not self.include_item(item):
                continue
            text = QG.QTextDocument()
            text.setDefaultFont(self.font)
            text.setDefaultStyleSheet("div { color: %s; }" % self.color)
            text.setHtml(f"<div>{item.param.label}</div>")
            text_items.append((text, item.pen(), item.brush(), item.symbol()))
        return text_items

    def include_item(self, item: Any) -> bool:
        """Include item in legend box?

        Args:
            item: Item

        Returns:
            True if item is included, False otherwise
        """
        return item.isVisible()

    def get_legend_size(
        self, legenditems: list[tuple]
    ) -> tuple[float, float, float, float]:
        """Return the legend size

        Args:
            legenditems: Legend items

        Returns:
            tuple: Tuple with four elements: (TW, TH, width, height)
        """
        width = 0
        height = 0
        for text, _, _, _ in legenditems:  # noqa
            sz = text.size()
            if sz.width() > width:
                width = sz.width()
            if sz.height() > height:
                height = sz.height()

        TW = LEGEND_SPACEH * 3 + LEGEND_WIDTH + width
        TH = len(legenditems) * (height + LEGEND_SPACEV) + LEGEND_SPACEV
        self.sizes = TW, TH, width, height
        return self.sizes

    def set_text_style(
        self, font: QG.QFont | None = None, color: str | None = None
    ) -> None:
        """Set label text style

        Args:
            font: Font
            color: Color
        """
        if font is not None:
            self.font = font
        if color is not None:
            self.color = color

    def get_text_rect(self) -> QC.QRectF:
        """Return the text rectangle

        Returns:
            Text rectangle
        """
        items = self.get_legend_items()
        TW, TH, _width, _height = self.get_legend_size(items)
        return QC.QRectF(0.0, 0.0, TW, TH)

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
        items = self.get_legend_items()
        TW, TH, _width, height = self.get_legend_size(items)

        x, y = self.get_top_left(xMap, yMap, canvasRect)
        self.draw_frame(painter, int(x), int(y), int(TW), int(TH))

        y0 = int(y + LEGEND_SPACEV)
        x0 = int(x + LEGEND_SPACEH)
        for text, ipen, ibrush, isymbol in items:
            isymbol.drawSymbols(
                painter, [QC.QPointF(x0 + LEGEND_WIDTH / 2, y0 + height / 2)]
            )
            painter.save()
            painter.setPen(ipen)
            painter.setBrush(ibrush)
            painter.drawLine(
                x0, int(y0 + height / 2), int(x0 + LEGEND_WIDTH), int(y0 + height / 2)
            )
            x1 = x0 + LEGEND_SPACEH + LEGEND_WIDTH
            painter.translate(x1, y0)
            text.drawContents(painter)
            painter.restore()
            y0 += height + LEGEND_SPACEV

    def click_inside(self, locx: float, locy: float) -> tuple[float, float, bool, type]:
        """Called when the mouse button is clicked inside the object

        Args:
            locx: Local x coordinate
            locy: Local y coordinate

        Returns:
            tuple: Tuple with four elements: (distance, attach point, inside,
             other_object).
        """
        # hit_test already called get_text_rect for us...
        _TW, _TH, _width, height = self.sizes
        line = (locy - LEGEND_SPACEV) / (height + LEGEND_SPACEV)
        line = int(line)
        if LEGEND_SPACEH <= locx <= (LEGEND_WIDTH + LEGEND_SPACEH):
            # We hit a legend line, select the corresponding curve
            # and do as if we weren't hit...
            items = [
                item
                for item in self.plot().get_items()
                if self.include_item(item) and isinstance(item, CurveItem)
            ]
            if line < len(items):
                return 1000.0, None, False, items[line]
        return 2.0, 1, True, None

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.labelparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        self.update_item_parameters()
        itemparams.add("LegendParam", self, self.labelparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(
            self.labelparam, itemparams.get("LegendParam"), visible_only=True
        )
        self.labelparam.update_label(self)
        if self.selected:
            self.select()


assert_interfaces_valid(LegendBoxItem)


class SelectedLegendBoxItem(LegendBoxItem):
    """Selected legend box plot item

    Args:
        labelparam: Label parameters
        itemlist: List of items
    """

    def __init__(
        self, dataset: LabelParam = None, itemlist: list[Any] | None = None
    ) -> None:
        super().__init__(dataset)
        self.itemlist = [] if itemlist is None else itemlist

    def __reduce__(self) -> tuple[type, tuple]:
        """Return a tuple containing the constructor and its arguments"""
        # XXX Filter itemlist for picklabel items
        return (self.__class__, (self.labelparam, []))

    def include_item(self, item: Any) -> bool:
        """Include item in legend box?

        Args:
            item: Item

        Returns:
            True if item is included, False otherwise
        """
        return LegendBoxItem.include_item(self, item) and item in self.itemlist

    def add_item(self, item: Any) -> None:
        """Add item

        Args:
            item: Item
        """
        self.itemlist.append(item)


class ObjectInfo:
    """Base class for objects used to format text labels"""

    def get_text(self) -> str:
        """Return the text to be displayed"""
        return ""


class RangeInfo(ObjectInfo):
    """ObjectInfo handling XRangeSelection shape informations: x, dx

    Args:
        label: Formatted string
        xrangeselection: XRangeSelection object
        function: Input arguments are x, dx ; returns objects used to format the
         label. Default function is `lambda x, dx: (x, dx)`.

    Examples::
        x = linspace(-10, 10, 10)
        y = sin(sin(sin(x)))
        xrangeselection = make.range(-2, 2)
        RangeInfo(u"x = %.1f ± %.1f cm", xrangeselection, lambda x, dx: (x, dx))
        disp = make.info_label('BL', comp, title="titre")
    """

    def __init__(
        self,
        label: str,
        xrangeselection: XRangeSelection,
        function: Callable | None = None,
    ) -> None:
        self.label = str(label)
        self.range = xrangeselection
        if function is None:

            def function(x, dx):
                return x, dx

        self.func = function

    def get_text(self) -> str:
        """Return the text to be displayed"""
        x0, x1 = self.range.get_range()
        x = 0.5 * (x0 + x1)
        dx = 0.5 * (x1 - x0)
        return self.label % self.func(x, dx)


class RangeComputation(ObjectInfo):
    """ObjectInfo showing curve computations relative to a XRangeSelection
    shape

    Args:
        label: formatted string
        curve: CurveItem object
        xrangeselection: XRangeSelection object
        function: input arguments are x, y arrays (extraction of arrays
         corresponding to the xrangeselection X-axis range)
    """

    def __init__(
        self,
        label: str,
        curve: CurveItem,
        xrangeselection: XRangeSelection,
        function: Callable | None = None,
    ) -> None:
        self.label = str(label)
        self.curve = curve
        self.range = xrangeselection
        if function is None:

            def function(x, dx):
                return x, dx

        self.func = function

    def set_curve(self, curve: CurveItem) -> None:
        """Set curve item

        Args:
            curve: Curve item
        """
        self.curve = curve

    def get_text(self) -> str:
        """Return the text to be displayed"""
        x0, x1 = self.range.get_range()
        data = self.curve.get_data()
        X = data[0]
        i0 = X.searchsorted(x0)
        i1 = X.searchsorted(x1)
        if i0 > i1:
            i0, i1 = i1, i0
        vectors = []
        for vector in data:
            if vector is None:
                vectors.append(None)
            elif i0 == i1:
                vectors.append(np.array([np.NaN]))
            else:
                vectors.append(vector[i0:i1])
        return self.label % self.func(*vectors)


class RangeComputation2d(ObjectInfo):
    """ObjectInfo showing image computations relative to a rectangular area

    Args:
        label: formatted string
        image: ImageItem object
        rect: Rectangular area
        function: input arguments are x, y, z arrays (extraction of arrays
         corresponding to the rectangular area)
    """

    def __init__(
        self, label: str, image: ImageItem, rect: RectangleShape, function: Callable
    ) -> None:
        self.label = str(label)
        self.image = image
        self.rect = rect
        self.func = function

    def get_text(self) -> str:
        """Return the text to be displayed"""
        x0, y0, x1, y1 = self.rect.get_rect()
        x, y, z = self.image.get_data(x0, y0, x1, y1)
        res = self.func(x, y, z)
        return self.label % res


class DataInfoLabel(LabelItem):
    """Label item displaying informations relative to an annotation

    Args:
        labelparam: Label parameters
        infos: List of objects implementing the ``get_text`` method
    """

    __implements__ = (IBasePlotItem,)

    def __init__(
        self, labelparam: LabelParam | None = None, infos: list[Any] | None = None
    ) -> None:
        super().__init__(None, labelparam)
        if isinstance(infos, ObjectInfo):
            infos = [infos]
        self.infos = infos

    def __reduce__(self) -> tuple[type, tuple]:
        """Return a tuple containing the constructor and its arguments"""
        return (self.__class__, (self.labelparam, self.infos))

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IShapeItemType,)

    def update_text(self):
        """Update text"""
        title = self.labelparam.label
        if title:
            text = ["<b>%s</b>" % title]
        else:
            text = []
        for info in self.infos:
            text.append(info.get_text())
        self.set_text("<br/>".join(text))
