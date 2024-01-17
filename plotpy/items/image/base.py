# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

from __future__ import annotations

import os
import os.path as osp
from typing import TYPE_CHECKING, Any

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotItem

from plotpy import io
from plotpy._scaler import (
    INTERP_AA,
    INTERP_LINEAR,
    INTERP_NEAREST,
    _histogram,
    _scale_rect,
)
from plotpy.config import _
from plotpy.constants import LUT_MAX, LUT_SIZE, LUTAlpha
from plotpy.coords import pixelround
from plotpy.interfaces import (
    IBaseImageItem,
    IBasePlotItem,
    IColormapImageItemType,
    ICSImageItemType,
    IExportROIImageItemType,
    IHistDataSource,
    IImageItemType,
    ISerializableType,
    IStatsImageItemType,
    ITrackableItemType,
    IVoiImageItemType,
)

# do not import rectangleshape from plotpy.items directly
from plotpy.items.shape.rectangle import RectangleShape
from plotpy.lutrange import lut_range_threshold
from plotpy.mathutils.arrayfuncs import get_nan_range
from plotpy.mathutils.colormaps import FULLRANGE, get_cmap
from plotpy.styles.image import RawImageParam

if TYPE_CHECKING:  # pragma: no cover
    import guidata.dataset.io
    import qwt.color_map
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QColor, QPainter

    from plotpy.interfaces import IItemType
    from plotpy.styles.base import ItemParameters
    from plotpy.widgets.colormap_widget import CustomQwtLinearColormap


class BaseImageItem(QwtPlotItem):
    """Base class for image items

    Args:
        data: Image data
        param: Image parameters
    """

    __implements__ = (
        IBasePlotItem,
        IBaseImageItem,
        IHistDataSource,
        IVoiImageItemType,
        ICSImageItemType,
        IStatsImageItemType,
        IExportROIImageItemType,
    )
    _can_select = True
    _can_resize = False
    _can_move = False
    _can_rotate = False
    _readonly = False
    _private = False

    def __init__(
        self, data: np.ndarray | None = None, param: Any | None = None
    ) -> None:
        super().__init__()

        self.bg_qcolor = QG.QColor()

        self.bounds = QC.QRectF()

        # BaseImageItem needs:
        # param.background
        # param.alpha_function
        # param.alpha
        # param.colormap
        if param is None:
            param = self.get_default_param()
        self.param = param

        self.selected = False

        self.data: np.ndarray | None = None

        self.min = 0.0
        self.max = 1.0
        self.cmap_table = None
        self.cmap = None
        self.colormap_axis = None
        self._image: QG.QImage | None = None

        self._offscreen = np.array((1, 1), np.uint32)

        # Linear interpolation is the default interpolation algorithm:
        # it's almost as fast as 'nearest pixel' method but far smoother
        self.interpolate = None
        self.set_interpolation(INTERP_LINEAR)

        x1, y1 = self.bounds.left(), self.bounds.top()
        x2, y2 = self.bounds.right(), self.bounds.bottom()
        self.border_rect = RectangleShape(x1, y1, x2, y2)
        self.border_rect.set_style("plot", "shape/imageborder")
        # A, B, Background, Colormap
        self.lut = (1.0, 0.0, None, np.zeros((LUT_SIZE,), np.uint32))
        self.set_lut_range((0.0, 255.0))
        self.setItemAttribute(QwtPlotItem.AutoScale)
        self.setItemAttribute(QwtPlotItem.Legend, True)
        self._filename = None  # The file this image comes from

        self.histogram_cache = None
        if data is not None:
            self.set_data(data)
        self.param.update_item(self)
        self.setIcon(get_icon("image.png"))

    # ---- Public API ----------------------------------------------------------
    def get_default_param(self) -> Any:
        """Return instance of the default image param DataSet"""
        raise NotImplementedError

    def set_filename(self, fname: str) -> None:
        """Set the filename of the image

        Args:
            fname: Filename
        """
        self._filename = fname

    def get_filename(self) -> str | None:
        """Get the filename of the image

        Returns:
            Filename
        """
        fname = self._filename
        if fname is not None and not osp.isfile(fname):
            other_try = osp.join(os.getcwd(), osp.basename(fname))
            if osp.isfile(other_try):
                self.set_filename(other_try)
                fname = other_try
        return fname

    def get_filter(self, filterobj, filterparam):
        """Provides a filter object over this image's content"""
        raise NotImplementedError

    def get_pixel_coordinates(self, xplot: float, yplot: float) -> tuple[float, float]:
        """Get pixel coordinates from plot coordinates

        Args:
            xplot: X plot coordinate
            yplot: Y plot coordinate

        Returns:
            Pixel coordinates
        """
        return xplot, yplot

    def get_plot_coordinates(self, xpixel: float, ypixel: float) -> tuple[float, float]:
        """Get plot coordinates from pixel coordinates

        Args:
            xpixel: X pixel coordinate
            ypixel: Y pixel coordinate

        Returns:
            Plot coordinates
        """
        return xpixel, ypixel

    def get_closest_indexes(
        self, x: float, y: float, corner: str | None = None
    ) -> tuple[int, int]:
        """Get closest image pixel indexes to the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate
            corner: None (not a corner), 'TL' (top-left corner),
             'BR' (bottom-right corner)

        Returns:
            Closest image pixel indexes
        """
        x, y = self.get_pixel_coordinates(x, y)
        i_max = self.data.shape[1] - 1
        j_max = self.data.shape[0] - 1
        if corner == "BR":
            i_max += 1
            j_max += 1
        i = max([0, min([i_max, int(pixelround(x, corner))])])
        j = max([0, min([j_max, int(pixelround(y, corner))])])
        return i, j

    def get_closest_index_rect(
        self, x0: float, y0: float, x1: float, y1: float
    ) -> tuple[int, int, int, int]:
        """Get closest image rectangular pixel area index bounds

        Args:
            x0: X coordinate of first point
            y0: Y coordinate of first point
            x1: X coordinate of second point
            y1: Y coordinate of second point

        Returns:
            Closest image rectangular pixel area index bounds

        .. note::

            Avoid returning empty rectangular area (return 1x1 pixel area instead).
            Handle reversed/not-reversed Y-axis orientation.
        """
        ix0, iy0 = self.get_closest_indexes(x0, y0, corner="TL")
        ix1, iy1 = self.get_closest_indexes(x1, y1, corner="BR")
        if ix0 > ix1:
            ix1, ix0 = ix0, ix1
        if iy0 > iy1:
            iy1, iy0 = iy0, iy1
        if ix0 == ix1:
            ix1 += 1
        if iy0 == iy1:
            iy1 += 1
        return ix0, iy0, ix1, iy1

    def align_rectangular_shape(self, shape: RectangleShape) -> None:
        """Align rectangular shape to image pixels

        Args:
            shape: Shape to align
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(*shape.get_rect())
        x0, y0 = self.get_plot_coordinates(ix0, iy0)
        x1, y1 = self.get_plot_coordinates(ix1, iy1)
        shape.set_rect(x0, y0, x1, y1)

    def get_closest_pixel_indexes(self, x: float, y: float) -> tuple[int, int]:
        """Get closest pixel indexes

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Closest pixel indexes

        .. note::

            Instead of returning indexes of an image pixel like the method
            'get_closest_indexes', this method returns the indexes of the
            closest pixel which is not necessarily on the image itself
            (i.e. indexes may be outside image index bounds: negative or
            superior than the image dimension)

        .. note::

            This is *not* the same as retrieving the canvas pixel coordinates
            (which depends on the zoom level)
        """
        x, y = self.get_pixel_coordinates(x, y)
        i = int(pixelround(x))
        j = int(pixelround(y))
        return i, j

    def get_x_values(self, i0: int, i1: int) -> np.ndarray:
        """Get X values from pixel indexes

        Args:
            i0: First index
            i1: Second index

        Returns:
            X values corresponding to the given pixel indexes
        """
        return np.arange(i0, i1)

    def get_y_values(self, j0: int, j1: int) -> np.ndarray:
        """Get Y values from pixel indexes

        Args:
            j0: First index
            j1: Second index

        Returns:
            Y values corresponding to the given pixel indexes
        """
        return np.arange(j0, j1)

    def get_r_values(self, i0, i1, j0, j1, flag_circle=False):
        """Get radial values from pixel indexes

        Args:
            i0: First index
            i1: Second index
            j0: Third index
            j1: Fourth index
            flag_circle: Flag circle (Default value = False)

        Returns:
            Radial values corresponding to the given pixel indexes
        """
        return self.get_x_values(i0, i1)

    def set_data(
        self, data: np.ndarray, lut_range: tuple[float, float] | None = None
    ) -> None:
        """Set image data

        Args:
            data: 2D NumPy array
            lut_range: LUT range -- tuple (levelmin, levelmax) (Default value = None)
        """
        if lut_range is not None:
            _min, _max = lut_range
        else:
            _min, _max = get_nan_range(data)

        self.data = data
        self.histogram_cache = None
        self.update_bounds()
        self.update_border()
        self.set_lut_range((_min, _max))

    def get_data(
        self, x0: float, y0: float, x1: float | None = None, y1: float | None = None
    ) -> float | tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get image data

        Args:
            x0: X coordinate of first point
            y0: Y coordinate of first point
            x1: X coordinate of second point (Default value = None)
            y1: Y coordinate of second point (Default value = None)

        Returns:
            Image level, or image levels in rectangular area (x0,y0,x1,y1)
             as a tuple (x, y, data) of arrays
        """
        i0, j0 = self.get_closest_indexes(x0, y0)
        if x1 is None or y1 is None:
            return self.data[j0, i0]
        else:
            i1, j1 = self.get_closest_indexes(x1, y1)
            i1 += 1
            j1 += 1
            return (
                self.get_x_values(i0, i1),
                self.get_y_values(j0, j1),
                self.data[j0:j1, i0:i1],
            )

    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """
        return self.get_closest_indexes(x, y)

    def get_coordinates_label(self, x: float, y: float) -> str:
        """
        Get the coordinates label for the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            str: Coordinates label
        """
        title = self.title().text()
        z = self.get_data(x, y)
        return f"{title}:<br>x = {int(x):d}<br>y = {int(y):d}<br>z = {z:g}"

    def set_background_color(self, qcolor: QColor | str) -> None:
        """Set background color

        Args:
            qcolor: Background color
        """
        # mask = np.uint32(255*self.param.alpha+0.5).clip(0,255) << 24
        self.bg_qcolor = qcolor
        a, b, _bg, cmap = self.lut
        if qcolor is None:
            self.lut = (a, b, None, cmap)
        else:
            self.lut = (a, b, np.uint32(QG.QColor(qcolor).rgb() & 0xFFFFFF), cmap)

    def set_color_map(self, name_or_table: str | CustomQwtLinearColormap) -> None:
        """Set colormap

        Args:
            name_or_table: Colormap name or colormap
        """
        if name_or_table is self.cmap_table:
            # This avoids rebuilding the LUT all the time
            return
        if isinstance(name_or_table, str):
            table = get_cmap(name_or_table)
        else:
            table = name_or_table
        self.cmap_table = table
        self.cmap = table.colorTable(FULLRANGE)
        cmap_a = self.lut[3]
        alpha = self.param.alpha
        alpha_function = self.param.alpha_function
        for i in range(LUT_SIZE):
            if alpha_function == LUTAlpha.NONE.value:
                pix_alpha = 1.0
            elif alpha_function == LUTAlpha.CONSTANT.value:
                pix_alpha = alpha
            else:
                x = i / float(LUT_SIZE - 1)
                if alpha_function == LUTAlpha.LINEAR.value:
                    pix_alpha = alpha * x
                elif alpha_function == LUTAlpha.SIGMOID.value:
                    pix_alpha = alpha / (1 + np.exp(-10 * x))
                elif alpha_function == LUTAlpha.TANH.value:
                    pix_alpha = alpha * np.tanh(5 * x)
                else:
                    raise ValueError(f"Invalid alpha function {alpha_function}")
            # pylint: disable=too-many-function-args
            alpha_channel = max(min(np.uint32(255 * pix_alpha + 0.5), 255), 0) << 24
            cmap_a[i] = (
                np.uint32((table.rgb(FULLRANGE, i / LUT_MAX)) & 0xFFFFFF)
                | alpha_channel
            )
        plot = self.plot()
        if plot:
            plot.update_colormap_axis(self)

    def get_color_map(self) -> CustomQwtLinearColormap | None:
        """Get colormap

        Returns:
            Colormap
        """
        return self.cmap_table

    def get_color_map_name(self) -> str | None:
        """Get the current colormap name if set. The output value should not directly
        be used to retrieve a colormap object from one of the global colormap
        dictionaries, as the colormap name may contain capital letters whereas the
        colormap string keys of the dictionaries are all lowercase.

        Returns:
            Colormap name
        """
        if self.cmap_table is None:
            return None
        return self.cmap_table.name

    def get_color_map_key_name(self) -> str | None:
        """Same as get_color_map_name, but returns the colormap name in lowercase. This
        is because the colormap string keys of the global colormap dictionaries are all
        lowercase.

        Returns:
            Colormap name
        """
        if self.cmap_table is None:
            return None
        return self.cmap_table.name.lower()

    def set_interpolation(self, interp_mode: int, size: int | None = None) -> None:
        """Set interpolation mode

        Args:
            interp_mode: INTERP_NEAREST, INTERP_LINEAR, INTERP_AA
            size: (for anti-aliasing only) AA matrix size (Default value = None)
        """
        if interp_mode in (INTERP_NEAREST, INTERP_LINEAR):
            self.interpolate = (interp_mode,)
        if interp_mode == INTERP_AA:
            aa = np.ones((size, size), self.data.dtype)
            self.interpolate = (interp_mode, aa)

    def get_interpolation(self) -> tuple[int] | tuple[int, np.ndarray]:
        """Get interpolation mode"""
        return self.interpolate

    def set_lut_range(self, lut_range: tuple[float, float]) -> None:
        """
        Set the current active lut range

        Args:
            lut_range: Lut range, tuple(min, max)

        Example:
            >>> item.set_lut_range((0.0, 1.0))
        """
        self.min, self.max = lut_range
        _a, _b, bg, cmap = self.lut
        if self.max == self.min:
            self.lut = (LUT_MAX, self.min, bg, cmap)
        else:
            fmin, fmax = float(self.min), float(self.max)  # avoid overflows
            self.lut = (
                LUT_MAX / (fmax - fmin),
                -LUT_MAX * fmin / (fmax - fmin),
                bg,
                cmap,
            )

    def get_lut_range(self) -> tuple[float, float]:
        """Get the current active lut range

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        return self.min, self.max

    def set_lut_threshold(self, threshold: float) -> None:
        """Set lut threshold value, eliminating the given percent of the histogram

        Args:
            threshold: Lut threshold value
        """
        self.set_lut_range(lut_range_threshold(self, 256, threshold))

    def get_lut_range_full(self) -> tuple[float, float]:
        """Return full dynamic range

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        return get_nan_range(self.data)

    def get_lut_range_max(self) -> tuple[float, float]:
        """Get maximum range for this dataset

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        kind = self.data.dtype.kind
        if kind in np.typecodes["AllFloat"]:
            info = np.finfo(self.data.dtype)
        else:
            info = np.iinfo(self.data.dtype)
        return info.min, info.max

    def update_bounds(self) -> None:
        """Update image bounds to fit image shape"""
        if self.data is None:
            return
        self.bounds = QC.QRectF(0, 0, self.data.shape[1], self.data.shape[0])

    def update_border(self) -> None:
        """Update image border rectangle to fit image shape"""
        bounds = self.boundingRect().getCoords()
        self.border_rect.set_rect(*bounds)

    def draw_border(
        self,
        painter: QPainter,
        xMap: qwt.scale_map.QwtScaleMap,
        yMap: qwt.scale_map.QwtScaleMap,
        canvasRect: QRectF,
    ) -> None:
        """Draw image border rectangle

        Args:
            painter: Painter
            xMap: X axis scale map
            yMap: Y axis scale map
            canvasRect: Canvas rectangle
        """
        self.border_rect.draw(painter, xMap, yMap, canvasRect)

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
        dest = _scale_rect(
            self.data, src_rect, self._offscreen, dst_rect, self.lut, self.interpolate
        )
        qrect = QC.QRectF(QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)

    def export_roi(
        self,
        src_rect: tuple[float, float, float, float],
        dst_rect: tuple[float, float, float, float],
        dst_image: np.ndarray,
        apply_lut: bool = False,
        apply_interpolation: bool = False,
        original_resolution: bool = False,
        force_interp_mode: str | None = None,
        force_interp_size: int | None = None,
    ) -> None:
        """
        Export a rectangular area of the image to another image

        Args:
            src_rect: Source rectangle
            dst_rect: Destination rectangle
            dst_image: Destination image
            apply_lut: Apply lut (Default value = False)
            apply_interpolation: Apply interpolation (Default value = False)
            original_resolution: Original resolution (Default value = False)
            force_interp_mode: Force interpolation mode (Default value = None)
            force_interp_size: Force interpolation size (Default value = None)
        """
        if apply_lut:
            a, b, _bg, _cmap = self.lut
        else:
            a, b = 1.0, 0.0
        interp = self.interpolate if apply_interpolation else (INTERP_NEAREST,)
        _scale_rect(self.data, src_rect, dst_image, dst_rect, (a, b, None), interp)

    # ---- QwtPlotItem API -----------------------------------------------------
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
        x1, y1, x2, y2 = canvasRect.getCoords()
        i1, i2 = xMap.invTransform(x1), xMap.invTransform(x2)
        j1, j2 = yMap.invTransform(y1), yMap.invTransform(y2)

        xl, yt, xr, yb = self.boundingRect().getCoords()
        dest = (
            xMap.transform(xl),
            yMap.transform(yt),
            xMap.transform(xr) + 1,
            yMap.transform(yb) + 1,
        )

        W = int(canvasRect.right())
        H = int(canvasRect.bottom())
        if self._offscreen.shape != (H, W):
            self._offscreen = np.empty((H, W), np.uint32)
            self._image = QG.QImage(self._offscreen, W, H, QG.QImage.Format_ARGB32)
            self._image.ndarray = self._offscreen
            self.notify_new_offscreen()
        self.draw_image(painter, canvasRect, (i1, j1, i2, j2), dest, xMap, yMap)
        self.draw_border(painter, xMap, yMap, canvasRect)

    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the data

        Returns:
            Bounding rectangle of the data
        """
        return self.bounds

    def notify_new_offscreen(self) -> None:
        """Notify that the offscreen image has changed"""
        # callback for those derived classes who need it
        pass

    def setVisible(self, enable: bool) -> None:
        """Set item visibility

        Args:
            enable: True if item is visible, False otherwise
        """
        if not enable:
            self.unselect()  # when hiding item, unselect it
        if enable:
            self.border_rect.show()
        else:
            self.border_rect.hide()
        QwtPlotItem.setVisible(self, enable)

    # ---- IBasePlotItem API ----------------------------------------------------
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
            ICSImageItemType,
            IExportROIImageItemType,
            IStatsImageItemType,
            IStatsImageItemType,
        )

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
        self.selected = True
        self.border_rect.select()

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        self.selected = False
        self.border_rect.unselect()

    def is_empty(self) -> bool:
        """Return True if the item is empty

        Returns:
            True if the item is empty, False otherwise
        """
        return self.data is None or self.data.size == 0

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
        return self._can_resize and not getattr(self.param, "lock_position", False)

    def can_move(self) -> bool:
        """
        Returns True if this item can be moved

        Returns:
            bool: True if item can be moved, False otherwise
        """
        return self._can_move and not getattr(self.param, "lock_position", False)

    def can_rotate(self) -> bool:
        """
        Returns True if this item can be rotated

        Returns:
            bool: True if item can be rotated, False otherwise
        """
        return self._can_rotate and not getattr(self.param, "lock_position", False)

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
        ax = self.xAxis()
        ay = self.yAxis()
        return self.border_rect.poly_hit_test(plot, ax, ay, pos)

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        pass

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        itemparams.add("ShapeParam", self, self.border_rect.shapeparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        self.border_rect.set_item_parameters(itemparams)

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        pass

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        pass

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        pass

    def resize_with_selection(self, zoom_dx, zoom_dy):
        """
        Resize the shape together with other selected items
        zoom_dx, zoom_dy : zoom factor for dx and dy
        """
        pass

    def rotate_with_selection(self, angle):
        """
        Rotate the shape together with other selected items
        angle : rotation angle
        """
        pass

    # ---- IBaseImageItem API --------------------------------------------------
    def can_sethistogram(self) -> bool:
        """
        Returns True if this item can be associated with a levels histogram

        Returns:
            bool: True if item can be associated with a levels histogram,
             False otherwise
        """
        return False

    def get_histogram(self, nbins: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Return a tuple (hist, bins) where hist is a list of histogram values

        Args:
            nbins (int): number of bins

        Returns:
            tuple: (hist, bins)
        """
        if self.data is None:
            return [0], [0, 1]
        if self.histogram_cache is None or nbins != self.histogram_cache[0].shape[0]:
            if True:
                # Note: np.histogram does not accept data with NaN
                res = np.histogram(self.data[~np.isnan(self.data)], nbins)
            else:
                # TODO: _histogram is faster, but caching is buggy in this version
                _min, _max = get_nan_range(self.data)
                if self.data.dtype in (np.float64, np.float32):
                    bins = np.unique(
                        np.array(
                            np.linspace(_min, _max, nbins + 1), dtype=self.data.dtype
                        )
                    )
                else:
                    bins = np.arange(_min, _max + 2, dtype=self.data.dtype)
                res2 = np.zeros((bins.size + 1,), np.uint32)
                _histogram(self.data.flatten(), bins, res2)
                res = res2[1:-1], bins
            self.histogram_cache = res
        else:
            res = self.histogram_cache
        return res

    def __process_cross_section(self, ydata, apply_lut):
        if apply_lut:
            a, b, _bg, _cmap = self.lut
            return (ydata * a + b).clip(0, LUT_MAX)
        else:
            return ydata

    def get_stats(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        show_surface: bool = False,
        show_integral: bool = False,
    ) -> str:
        """Return formatted string with stats on image rectangular area
        (output should be compatible with AnnotatedShape.get_infos)

        Args:
            x0: X0
            y0: Y0
            x1: X1
            y1: Y1
            show_surface: Show surface (Default value = False)
            show_integral: Show integral (Default value = False)
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        data = self.data[iy0:iy1, ix0:ix1]
        xfmt = self.param.xformat
        yfmt = self.param.yformat
        zfmt = self.param.zformat
        try:
            xunit = xfmt.split()[1]
        except IndexError:
            xunit = ""
        try:
            yunit = yfmt.split()[1]
        except IndexError:
            yunit = ""
        try:
            zunit = zfmt.split()[1]
        except IndexError:
            zunit = ""
        if show_integral:
            integral = data.sum()
        infos = "<br>".join(
            [
                "<b>%s</b>" % self.param.label,
                "%sx%s %s"
                % (self.data.shape[1], self.data.shape[0], str(self.data.dtype)),
                "",
                "%s ≤ x ≤ %s" % (xfmt % x0, xfmt % x1),
                "%s ≤ y ≤ %s" % (yfmt % y0, yfmt % y1),
                "%s ≤ z ≤ %s" % (zfmt % data.min(), zfmt % data.max()),
                "‹z› = " + zfmt % data.mean(),
                "σ(z) = " + zfmt % data.std(),
            ]
        )
        if show_surface and xunit == yunit:
            surfacefmt = xfmt.split()[0] + " " + xunit
            if xunit != "":
                surfacefmt = surfacefmt + "²"
            surface = abs((x1 - x0) * (y1 - y0))
            infos = infos + "<br>" + _("surface = %s") % (surfacefmt % surface)
        if show_integral:
            integral = data.sum()
            integral_fmt = r"%.3e " + zunit
            infos = infos + "<br>" + _("sum = %s") % (integral_fmt % integral)
        if (
            show_surface
            and xunit == yunit
            and xunit is not None
            and show_integral
            and zunit is not None
        ):
            if surface != 0:
                density = integral / surface
                densityfmt = r"%.3e " + zunit + "/" + xunit
                if xunit != "":
                    densityfmt = densityfmt + "²"
                infos = infos + "<br>" + _("density = %s") % (densityfmt % density)
            else:
                infos = infos + "<br>" + _("density not computed : surface is null !")
        return infos

    def get_xsection(self, y0: float | int, apply_lut: bool = False) -> np.ndarray:
        """Return cross section along x-axis at y=y0

        Args:
            y0: Y0
            apply_lut: Apply lut (Default value = False)

        Returns:
            Cross section along x-axis at y=y0
        """
        _ix, iy = self.get_closest_indexes(0, y0)
        return (
            self.get_x_values(0, self.data.shape[1]),
            self.__process_cross_section(self.data[iy, :], apply_lut),
        )

    def get_ysection(self, x0: float | int, apply_lut: bool = False) -> np.ndarray:
        """Return cross section along y-axis at x=x0

        Args:
            x0: X0
            apply_lut: Apply lut (Default value = False)

        Returns:
            Cross section along y-axis at x=x0
        """
        ix, _iy = self.get_closest_indexes(x0, 0)
        return (
            self.get_y_values(0, self.data.shape[0]),
            self.__process_cross_section(self.data[:, ix], apply_lut),
        )

    def get_average_xsection(
        self, x0: float, y0: float, x1: float, y1: float, apply_lut: bool = False
    ) -> np.ndarray:
        """Return average cross section along x-axis for the given rectangle

        Args:
            x0: X0 of top left corner
            y0: Y0 of top left corner
            x1: X1 of bottom right corner
            y1: Y1 of bottom right corner
            apply_lut: Apply lut (Default value = False)

        Returns:
            Average cross section along x-axis
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        ydata = self.data[iy0:iy1, ix0:ix1]
        if ydata.size == 0:
            return np.array([]), np.array([])
        ydata = ydata.mean(axis=0)
        return (
            self.get_x_values(ix0, ix1),
            self.__process_cross_section(ydata, apply_lut),
        )

    def get_average_ysection(
        self, x0: float, y0: float, x1: float, y1: float, apply_lut: bool = False
    ) -> np.ndarray:
        """Return average cross section along y-axis

        Args:
            x0: X0 of top left corner
            y0: Y0 of top left corner
            x1: X1 of bottom right corner
            y1: Y1 of bottom right corner
            apply_lut: Apply lut (Default value = False)

        Returns:
            Average cross section along y-axis
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        ydata = self.data[iy0:iy1, ix0:ix1]
        if ydata.size == 0:
            return np.array([]), np.array([])
        ydata = ydata.mean(axis=1)
        return (
            self.get_y_values(iy0, iy1),
            self.__process_cross_section(ydata, apply_lut),
        )


assert_interfaces_valid(BaseImageItem)


# ==============================================================================
# Raw Image item (image item without scale)
# ==============================================================================
class RawImageItem(BaseImageItem):
    """
    Construct a simple image item

        * data: 2D NumPy array
        * param: image parameters
          (:py:class:`.styles.RawImageParam` instance)
    """

    __implements__ = (
        IBasePlotItem,
        IBaseImageItem,
        IHistDataSource,
        IVoiImageItemType,
        ISerializableType,
    )

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self) -> RawImageParam:
        """Return instance of the default image param DataSet

        Returns:
            RawImageParam: Default image param DataSet
        """
        return RawImageParam(_("Image"))

    # ---- Serialization methods -----------------------------------------------
    def __reduce__(self) -> tuple:
        """Return state information for pickling"""
        fname = self.get_filename()
        if fname is None:
            fn_or_data = self.data
        else:
            fn_or_data = fname
        state = self.param, self.get_lut_range(), fn_or_data, self.z()
        res = (self.__class__, (), state)
        return res

    def __setstate__(self, state: tuple) -> None:
        """Restore state information for pickling"""
        param, lut_range, fn_or_data, z = state
        self.param = param
        if isinstance(fn_or_data, str):
            self.set_filename(fn_or_data)
            self.load_data()
        elif fn_or_data is not None:  # should happen only with previous API
            self.set_data(fn_or_data)
        self.set_lut_range(lut_range)
        self.setZ(z)
        self.param.update_item(self)

    def serialize(
        self,
        writer: guidata.dataset.io.HDF5Writer
        | guidata.dataset.io.INIWriter
        | guidata.dataset.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        fname = self.get_filename()
        load_from_fname = fname is not None
        data = None if load_from_fname else self.data
        writer.write(load_from_fname, group_name="load_from_fname")
        writer.write(fname, group_name="fname")
        writer.write(data, group_name="Zdata")
        writer.write(self.get_lut_range(), group_name="lut_range")
        writer.write(self.z(), group_name="z")
        self.param.update_param(self)
        writer.write(self.param, group_name="imageparam")

    def deserialize(
        self,
        reader: guidata.dataset.io.HDF5Reader
        | guidata.dataset.io.INIReader
        | guidata.dataset.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        lut_range = reader.read(group_name="lut_range")
        if reader.read(group_name="load_from_fname"):
            name = reader.read(group_name="fname", func=reader.read_unicode)
            name = io.iohandler.adapt_path(name)
            self.set_filename(name)
            self.load_data()
        else:
            data = reader.read(group_name="Zdata", func=reader.read_array)
            self.set_data(data)
        self.set_lut_range(lut_range)
        self.setZ(reader.read("z"))
        self.param = self.get_default_param()
        reader.read("imageparam", instance=self.param)
        self.param.update_item(self)

    # ---- Public API ----------------------------------------------------------
    def load_data(self, lut_range: list[float, float] | None = None) -> None:
        """Load data from item filename attribute
        and eventually apply specified lut_range

        Args:
            lut_range: Lut range (Default value = None)
        """
        data = io.imread(self.get_filename(), to_grayscale=True)
        self.set_data(data, lut_range=lut_range)

    # ---- IBasePlotItem API ---------------------------------------------------
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
            ICSImageItemType,
            ISerializableType,
            IExportROIImageItemType,
            IStatsImageItemType,
        )

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        self.param.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        BaseImageItem.get_item_parameters(self, itemparams)
        self.update_item_parameters()
        itemparams.add("ImageParam", self, self.param)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(self.param, itemparams.get("ImageParam"), visible_only=True)
        self.param.update_item(self)
        BaseImageItem.set_item_parameters(self, itemparams)

    # ---- IBaseImageItem API --------------------------------------------------
    def can_sethistogram(self) -> bool:
        """
        Returns True if this item can be associated with a levels histogram

        Returns:
            bool: True if item can be associated with a levels histogram,
             False otherwise
        """
        return True


assert_interfaces_valid(RawImageItem)
