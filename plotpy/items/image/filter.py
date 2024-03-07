# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC

from plotpy.coords import canvas_to_axes
from plotpy.interfaces import (
    IBaseImageItem,
    IBasePlotItem,
    IColormapImageItemType,
    IImageItemType,
    ITrackableItemType,
    IVoiImageItemType,
)
from plotpy.items.image.base import BaseImageItem

try:
    from plotpy._scaler import _scale_xy
except ImportError:
    print(
        ("Module 'plotpy.items.image.filter': missing C extension"),
        file=sys.stderr,
    )
    print(
        ("try running :" "python setup.py build_ext --inplace -c mingw32"),
        file=sys.stderr,
    )
    raise

if TYPE_CHECKING:
    import qwt.color_map
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QPainter

    from plotpy.interfaces import IItemType
    from plotpy.items import RawImageItem, XYImageItem
    from plotpy.styles import ImageFilterParam, ItemParameters


# ==============================================================================
# Image with custom X, Y axes
# ==============================================================================
def to_bins(x):
    """Convert point center to point bounds"""
    bx = np.zeros((x.shape[0] + 1,), float)
    bx[1:-1] = (x[:-1] + x[1:]) / 2
    bx[0] = x[0] - (x[1] - x[0]) / 2
    bx[-1] = x[-1] + (x[-1] - x[-2]) / 2
    return bx


# TODO: Implement get_filter methods for image items other than XYImageItem!
class ImageFilterItem(BaseImageItem):
    """
    Construct a rectangular area image filter item

        * image: :py:class:`.RawImageItem` instance
        * filter: function (x, y, data) --> data
        * param: image filter parameters
          (:py:class:`.ImageFilterParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem)
    _can_select = True
    _can_resize = True
    _can_move = True

    def __init__(
        self, image: RawImageItem | None, filter: Callable, param: ImageFilterParam
    ) -> None:
        self.use_source_cmap = None

        # BaseImageItem constructor will try to set this item's color map
        # using the method 'set_color_map'
        self.image: RawImageItem | None = None

        super().__init__(param=param)
        self.border_rect.set_style("plot", "shape/imagefilter")
        self.image = image
        self.filter = filter

        self.imagefilterparam = param
        self.imagefilterparam.update_imagefilter(self)
        self.setIcon(get_icon("funct.png"))

    # ---- Public API -----------------------------------------------------------
    def set_image(self, image: RawImageItem | None) -> None:
        """
        Set the image item on which the filter will be applied

            * image: :py:class:`.RawImageItem` instance
        """
        self.image = image

    def set_filter(self, filter: Callable) -> None:
        """
        Set the filter function

            * filter: function (x, y, data) --> data
        """
        self.filter = filter

    # ---- QwtPlotItem API ------------------------------------------------------
    def boundingRect(self) -> QC.QRectF:
        """Return the bounding rectangle of the shape

        Returns:
            Bounding rectangle of the shape
        """
        x0, y0, x1, y1 = self.border_rect.get_rect()
        return QC.QRectF(x0, y0, x1 - x0, y1 - y0)

    # ---- IBasePlotItem API ----------------------------------------------------
    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        BaseImageItem.update_item_parameters(self)
        self.imagefilterparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        BaseImageItem.get_item_parameters(self, itemparams)
        self.update_item_parameters()
        itemparams.add("ImageFilterParam", self, self.imagefilterparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(
            self.imagefilterparam, itemparams.get("ImageFilterParam"), visible_only=True
        )
        self.imagefilterparam.update_imagefilter(self)
        BaseImageItem.set_item_parameters(self, itemparams)

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        npos = canvas_to_axes(self, pos)
        self.border_rect.move_point_to(handle, npos, ctrl)
        if self.plot():
            self.plot().SIG_ITEM_HANDLE_MOVED.emit(self)

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        old_pt = canvas_to_axes(self, old_pos)
        new_pt = canvas_to_axes(self, new_pos)
        self.border_rect.move_shape(old_pt, new_pt)
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, *(old_pt + new_pt))

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        self.border_rect.move_with_selection(delta_x, delta_y)

    def set_color_map(
        self, name_or_table: str | qwt.color_map.QwtLinearColorMap
    ) -> None:
        """Set colormap

        Args:
            name_or_table: Colormap name or colormap
        """
        if self.use_source_cmap:
            if self.image is not None:
                self.image.set_color_map(name_or_table)
        else:
            BaseImageItem.set_color_map(self, name_or_table)

    def get_color_map(self) -> qwt.color_map.QwtLinearColorMap:
        """Get colormap"""
        if self.use_source_cmap:
            return self.image.get_color_map()
        else:
            return BaseImageItem.get_color_map(self)

    def get_lut_range(self) -> tuple[float, float]:
        """Get the current active lut range

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        if self.use_source_cmap:
            return self.image.get_lut_range()
        else:
            return BaseImageItem.get_lut_range(self)

    def set_lut_range(self, lut_range: tuple[float, float]) -> None:
        """
        Set the current active lut range

        Args:
            lut_range: Lut range, tuple(min, max)

        Example:
            >>> item.set_lut_range((0.0, 1.0))
        """
        if self.use_source_cmap:
            self.image.set_lut_range(lut_range)
        else:
            BaseImageItem.set_lut_range(self, lut_range)

    # ---- IBaseImageItem API ---------------------------------------------------
    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (
            IImageItemType,
            IVoiImageItemType,
            IColormapImageItemType,
            ITrackableItemType,
        )

    def can_sethistogram(self) -> bool:
        """
        Returns True if this item can be associated with a levels histogram

        Returns:
            bool: True if item can be associated with a levels histogram,
             False otherwise
        """
        return True


class XYImageFilterItem(ImageFilterItem):
    """
    Construct a rectangular area image filter item

        * image: :py:class:`.XYImageItem` instance
        * filter: function (x, y, data) --> data
        * param: image filter parameters
          (:py:class:`.ImageFilterParam` instance)
    """

    def __init__(
        self, image: XYImageItem, filter: Callable, param: ImageFilterParam
    ) -> None:
        self.image: XYImageItem | None = None
        super().__init__(image, filter, param)

    def set_image(self, image):
        """
        Set the image item on which the filter will be applied

            * image: :py:class:`.XYImageItem` instance
        """
        ImageFilterItem.set_image(self, image)

    def draw_image(
        self,
        painter: QPainter,
        canvasRect: QRectF,
        src_rect: tuple[float, float, float, float],
        dst_rect: tuple[float, float, float, float],
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
    ) -> None:
        """Draw image

        Args:
            painter: Painter
            canvasRect: Canvas rectangle
            src_rect: Source rectangle
            dst_rect: Destination rectangle
            xMap: X axis scale map
            yMap: Y axis scale map
        """
        bounds = self.boundingRect()

        filt_qrect = bounds & self.image.boundingRect()
        x0, y0, x1, y1 = filt_qrect.getCoords()
        i0, i1 = int(xMap.transform(x0)), int(xMap.transform(x1))
        j0, j1 = int(yMap.transform(y0)), int(yMap.transform(y1))

        dstRect = QC.QRect(i0, j0, i1 - i0, j1 - j0)
        if not dstRect.intersects(canvasRect):
            return

        x, y, data = self.image.get_data(x0, y0, x1, y1)
        new_data = self.filter(x, y, data)
        self.data = new_data
        if self.use_source_cmap:
            lut = self.image.lut
        else:
            lut = self.lut

        W = canvasRect.width()
        H = canvasRect.height()
        if W <= 1 or H <= 1:
            return

        # x, y = x - self.image.x[0], y - self.image.y[0]
        dest = _scale_xy(
            new_data,
            (x, y, src_rect),
            self._offscreen,
            dstRect.getCoords(),
            lut,
            self.interpolate,
        )
        qrect = QC.QRectF(QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)


assert_interfaces_valid(ImageFilterItem)
