# -*- coding: utf-8 -*-
# pylint: disable=C0103

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC

from plotpy import io
from plotpy._scaler import INTERP_AA
from plotpy.config import _
from plotpy.constants import LUTAlpha
from plotpy.coords import canvas_to_axes, pixelround
from plotpy.interfaces import (
    IBaseImageItem,
    IBasePlotItem,
    IColormapImageItemType,
    ICSImageItemType,
    IExportROIImageItemType,
    IHistDataSource,
    IImageItemType,
    ISerializableType,
    ITrackableItemType,
    IVoiImageItemType,
)
from plotpy.items.image.base import RawImageItem
from plotpy.items.image.filter import XYImageFilterItem, to_bins
from plotpy.mathutils.arrayfuncs import get_nan_range
from plotpy.styles.image import ImageParam, RGBImageParam, XYImageParam

if TYPE_CHECKING:
    import guidata.io
    import qwt.color_map
    import qwt.scale_map
    from qtpy.QtCore import QPointF, QRectF
    from qtpy.QtGui import QColor, QPainter

    from plotpy.interfaces import IItemType
    from plotpy.widgets.colormap.widget import EditableColormap

try:
    from plotpy._scaler import INTERP_NEAREST, _scale_rect, _scale_xy
except ImportError:
    print(
        ("Module 'plotpy.items.image': missing C extension"),
        file=sys.stderr,
    )
    print(
        ("try running :" "python setup.py build_ext --inplace -c mingw32"),
        file=sys.stderr,
    )
    raise


# ==============================================================================
# Image item
# ==============================================================================
class ImageItem(RawImageItem):
    """Image item

    Args:
        data: 2D NumPy array
        param: Image parameters
    """

    _can_move = True
    _can_resize = True

    __implements__ = (
        IBasePlotItem,
        IBaseImageItem,
        IHistDataSource,
        IVoiImageItemType,
        IExportROIImageItemType,
    )

    def __init__(
        self, data: np.ndarray | None = None, param: ImageParam | None = None
    ) -> None:
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self._log_data = None
        self._lin_lut_range = None
        self._is_zaxis_log = False
        super().__init__(data=data, param=param)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self) -> ImageParam:
        """Return instance of the default image param DataSet"""
        return ImageParam(_("Image"))

    # ---- Serialization methods -----------------------------------------------
    def __reduce__(self) -> tuple:
        """Reduce object to be pickled"""
        fname = self.get_filename()
        if fname is None:
            fn_or_data = self.data
        else:
            fn_or_data = fname
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        state = (
            self.param,
            self.get_lut_range(),
            fn_or_data,
            self.z(),
            xmin,
            xmax,
            ymin,
            ymax,
        )
        res = (self.__class__, (), state)
        return res

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
        param, lut_range, fn_or_data, z, xmin, xmax, ymin, ymax = state
        self.set_xdata(xmin, xmax)
        self.set_ydata(ymin, ymax)
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
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        super().serialize(writer)
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        writer.write(xmin, group_name="xmin")
        writer.write(xmax, group_name="xmax")
        writer.write(ymin, group_name="ymin")
        writer.write(ymax, group_name="ymax")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        super().deserialize(reader)
        for attr in ("xmin", "xmax", "ymin", "ymax"):
            # Note: do not be tempted to write the symetric code in `serialize`
            # because calling `get_xdata` and `get_ydata` is necessary
            setattr(self, attr, reader.read(attr, func=reader.read_float))

    # ---- Public API ----------------------------------------------------------
    def get_xdata(self, aligned=True) -> tuple[float, float]:
        """Get X data range

        Args:
            aligned: True if aligned (Default value = True)

        Returns:
            (xmin, xmax) tuple
        """
        xmin, xmax = self.xmin, self.xmax
        if xmin is None:
            xmin = 0.0
        if xmax is None:
            xmax = self.data.shape[1]
        if aligned:
            dx = 0.5 * (xmax - xmin) / self.data.shape[1]
            xmin -= dx
            xmax -= dx
        return xmin, xmax

    def get_ydata(self, aligned=True) -> tuple[float, float]:
        """Get Y data range

        Args:
            aligned: True if aligned (Default value = True)

        Returns:
            (ymin, ymax) tuple
        """
        ymin, ymax = self.ymin, self.ymax
        if ymin is None:
            ymin = 0.0
        if ymax is None:
            ymax = self.data.shape[0]
        if aligned:
            dy = 0.5 * (ymax - ymin) / self.data.shape[0]
            ymin -= dy
            ymax -= dy
        return ymin, ymax

    def set_xdata(self, xmin: float | None = None, xmax: float | None = None) -> None:
        """Set X data range

        Args:
            xmin: Minimum X value
            xmax: Maximum X value
        """
        self.xmin, self.xmax = xmin, xmax

    def set_ydata(self, ymin: float | None = None, ymax: float | None = None) -> None:
        """Set Y data range

        Args:
            ymin: Minimum Y value
            ymax: Maximum Y value
        """
        self.ymin, self.ymax = ymin, ymax

    def update_bounds(self) -> None:
        """Update image bounds to fit image shape"""
        if self.data is None:
            return
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        self.bounds = QC.QRectF(QC.QPointF(xmin, ymin), QC.QPointF(xmax, ymax))

    def get_zaxis_log_state(self):
        """Reimplement image.ImageItem method"""
        return self._is_zaxis_log

    def set_zaxis_log_state(self, state):
        """Reimplement image.ImageItem method"""
        self._is_zaxis_log = state
        plot = self.plot()
        if state:
            self._lin_lut_range = self.get_lut_range()
            if self._log_data is None:
                self._log_data = np.array(np.log10(self.data.clip(1)), dtype=np.float64)
            self.set_lut_range(get_nan_range(self._log_data))
            dtype = self._log_data.dtype
        else:
            self._log_data = None
            self.set_lut_range(self._lin_lut_range)
            dtype = self.data.dtype
        if self.interpolate[0] == INTERP_AA:
            self.interpolate = (INTERP_AA, self.interpolate[1].astype(dtype))
        plot.update_colormap_axis(self)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_pixel_coordinates(self, xplot: float, yplot: float) -> tuple[float, float]:
        """Get pixel coordinates from plot coordinates

        Args:
            xplot: X plot coordinate
            yplot: Y plot coordinate

        Returns:
            Pixel coordinates
        """
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        xpix = self.data.shape[1] * (xplot - xmin) / float(xmax - xmin)
        ypix = self.data.shape[0] * (yplot - ymin) / float(ymax - ymin)
        return xpix, ypix

    def get_plot_coordinates(self, xpixel: float, ypixel: float) -> tuple[float, float]:
        """Get plot coordinates from pixel coordinates

        Args:
            xpixel: X pixel coordinate
            ypixel: Y pixel coordinate

        Returns:
            Plot coordinates
        """
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        xplot = xmin + (xmax - xmin) * xpixel / float(self.data.shape[1])
        yplot = ymin + (ymax - ymin) * ypixel / float(self.data.shape[0])
        return xplot, yplot

    def get_x_values(self, i0: int, i1: int) -> np.ndarray:
        """Get X values from pixel indexes

        Args:
            i0: First index
            i1: Second index

        Returns:
            X values corresponding to the given pixel indexes
        """
        xmin, xmax = self.get_xdata()

        def xfunc(index):
            return xmin + (xmax - xmin) * index / float(self.data.shape[1])

        return np.linspace(xfunc(i0), xfunc(i1), i1 - i0, endpoint=False)

    def get_y_values(self, j0: int, j1: int) -> np.ndarray:
        """Get Y values from pixel indexes

        Args:
            j0: First index
            j1: Second index

        Returns:
            Y values corresponding to the given pixel indexes
        """
        ymin, ymax = self.get_ydata()

        def yfunc(index):
            return ymin + (ymax - ymin) * index / float(self.data.shape[0])

        return np.linspace(yfunc(j0), yfunc(j1), j1 - j0, endpoint=False)

    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """
        xmin, xmax = self.get_xdata(aligned=False)
        ymin, ymax = self.get_ydata(aligned=False)
        i, j = self.get_closest_indexes(x, y)
        xpix = np.linspace(xmin, xmax, self.data.shape[1] + 1)
        ypix = np.linspace(ymin, ymax, self.data.shape[0] + 1)
        return xpix[i], ypix[j]

    def _rescale_src_rect(
        self, src_rect: tuple[float, float, float, float]
    ) -> tuple[float, float, float, float]:
        """Rescale source rectangle

        Args:
            src_rect: Source rectangle

        Returns:
            Rescaled source rectangle
        """
        sxl, syt, sxr, syb = src_rect
        xl, yt, xr, yb = self.boundingRect().getCoords()
        H, W = self.data.shape[:2]
        if xr - xl != 0:
            x0 = W * (sxl - xl) / (xr - xl)
            x1 = W * (sxr - xl) / (xr - xl)
        else:
            x0 = x1 = 0
        if yb - yt != 0:
            y0 = H * (syt - yt) / (yb - yt)
            y1 = H * (syb - yt) / (yb - yt)
        else:
            y0 = y1 = 0
        return x0, y0, x1, y1

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
        if self.data is None:
            return
        if self.warn_if_non_linear_scale(painter, canvasRect):
            return

        src2 = self._rescale_src_rect(src_rect)
        dst_rect = tuple([int(i) for i in dst_rect])

        # Not the most efficient way to do it, but it works...
        # --------------------------------------------------------------------------
        if self.get_zaxis_log_state():
            data = self._log_data
        else:
            data = self.data
        # --------------------------------------------------------------------------

        try:
            dest = _scale_rect(
                data, src2, self._offscreen, dst_rect, self.lut, self.interpolate
            )
        except ValueError:
            # This exception is raised when zooming unreasonably inside a pixel
            return
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
        _scale_rect(
            self.data,
            self._rescale_src_rect(src_rect),
            dst_image,
            dst_rect,
            (a, b, None),
            interp,
        )

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        nx, ny = canvas_to_axes(self, pos)
        xmin, xmax = self.get_xdata()
        ymin, ymax = self.get_ydata()

        handle_x = [xmin, xmax, xmax, xmin][handle]
        handle_y = [ymin, ymin, ymax, ymax][handle]
        sign_xmin = [1, -1, -1, 1][handle]
        sign_xmax = [-1, 1, 1, -1][handle]
        sign_ymin = [1, 1, -1, -1][handle]
        sign_ymax = [-1, -1, 1, 1][handle]

        delta_x = nx - handle_x
        delta_y = ny - handle_y

        self.set_xdata(xmin + delta_x * sign_xmin, xmax + delta_x * sign_xmax)
        self.set_ydata(ymin + delta_y * sign_ymin, ymax + delta_y * sign_ymax)
        self.update_bounds()
        self.update_border()

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        nx, ny = canvas_to_axes(self, new_pos)
        ox, oy = canvas_to_axes(self, old_pos)
        xmin, xmax = self.get_xdata()
        ymin, ymax = self.get_ydata()
        self.set_xdata(xmin + nx - ox, xmax + nx - ox)
        self.set_ydata(ymin + ny - oy, ymax + ny - oy)
        self.update_bounds()
        self.update_border()
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, ox, oy, nx, ny)

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        xmin, xmax = self.get_xdata()
        ymin, ymax = self.get_ydata()
        self.set_xdata(xmin + delta_x, xmax + delta_x)
        self.set_ydata(ymin + delta_x, ymax + delta_y)
        self.update_bounds()
        self.update_border()


assert_interfaces_valid(ImageItem)


class XYImageItem(RawImageItem):
    """XY image item (non-linear axes)

    Args:
        x: 1D NumPy array, must be increasing
        y: 1D NumPy array, must be increasing
        data: 2D NumPy array
        param: image parameters
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, ISerializableType)

    def __init__(
        self,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        data: np.ndarray | None = None,
        param: XYImageParam | None = None,
    ) -> None:
        # if x and y are not increasing arrays, sort them and data accordingly
        if x is not None and not np.all(np.diff(x) >= 0):
            x_idx = np.argsort(x)
            x = x[x_idx]
            data = data[:, x_idx]
        if y is not None and not np.all(np.diff(y) >= 0):
            y_idx = np.argsort(y)
            y = y[y_idx]
            data = data[y_idx, :]
        super().__init__(data, param)
        self.x = None
        self.y = None
        if x is not None and y is not None:
            self.set_xy(x, y)

    # ---- Public API ----------------------------------------------------------

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self) -> XYImageParam:
        """Return instance of the default image param DataSet"""
        return XYImageParam(_("Image"))

    # ---- Pickle methods ------------------------------------------------------
    def __reduce__(self) -> tuple:
        """Reduce object to be pickled"""
        fname = self.get_filename()
        if fname is None:
            fn_or_data = self.data
        else:
            fn_or_data = fname
        state = (self.param, self.get_lut_range(), self.x, self.y, fn_or_data, self.z())
        res = (self.__class__, (), state)
        return res

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
        param, lut_range, x, y, fn_or_data, z = state
        self.param = param
        if isinstance(fn_or_data, str):
            self.set_filename(fn_or_data)
            self.load_data(lut_range)
        elif fn_or_data is not None:  # should happen only with previous API
            self.set_data(fn_or_data, lut_range=lut_range)
        self.set_xy(x, y)
        self.setZ(z)
        self.param.update_item(self)

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        super().serialize(writer)
        writer.write(self.x, group_name="Xdata")
        writer.write(self.y, group_name="Ydata")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        super().deserialize(reader)
        x = reader.read(group_name="Xdata", func=reader.read_array)
        y = reader.read(group_name="Ydata", func=reader.read_array)
        self.set_xy(x, y)

    # ---- Public API ----------------------------------------------------------
    def set_xy(self, x: np.ndarray | list[float], y: np.ndarray | list[float]) -> None:
        """Set X and Y data

        Args:
            x: 1D NumPy array, must be increasing
            y: 1D NumPy array, must be increasing

        Raises:
            ValueError: If X or Y are not increasing
            IndexError: If X or Y are not of the right length
        """
        ni, nj = self.data.shape
        x = np.array(x, float)
        y = np.array(y, float)
        if not np.all(np.diff(x) >= 0):
            raise ValueError("x must be an increasing 1D array")
        if not np.all(np.diff(y) >= 0):
            raise ValueError("y must be an increasing 1D array")
        if x.shape[0] == nj:
            self.x = to_bins(x)
        elif x.shape[0] == nj + 1:
            self.x = x
        else:
            raise IndexError(f"x must be a 1D array of length {nj:d} or {nj + 1:d}")
        if y.shape[0] == ni:
            self.y = to_bins(y)
        elif y.shape[0] == ni + 1:
            self.y = y
        else:
            raise IndexError(f"y must be a 1D array of length {ni:d} or {ni + 1:d}")
        self.bounds = QC.QRectF(
            QC.QPointF(self.x[0], self.y[0]), QC.QPointF(self.x[-1], self.y[-1])
        )
        self.update_border()

    # --- BaseImageItem API ----------------------------------------------------
    def get_filter(self, filterobj, filterparam):
        """Provides a filter object over this image's content"""
        return XYImageFilterItem(self, filterobj, filterparam)

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
        if self.warn_if_non_linear_scale(painter, canvasRect):
            return
        xytr = self.x, self.y, src_rect
        dst_rect = tuple([int(i) for i in dst_rect])
        dest = _scale_xy(
            self.data, xytr, self._offscreen, dst_rect, self.lut, self.interpolate
        )
        qrect = QC.QRectF(QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)

    def get_pixel_coordinates(self, xplot: float, yplot: float) -> tuple[float, float]:
        """Get pixel coordinates from plot coordinates

        Args:
            xplot: X plot coordinate
            yplot: Y plot coordinate

        Returns:
            Pixel coordinates
        """
        return self.x.searchsorted(xplot), self.y.searchsorted(yplot)

    def get_plot_coordinates(self, xpixel: float, ypixel: float) -> tuple[float, float]:
        """Get plot coordinates from pixel coordinates

        Args:
            xpixel: X pixel coordinate
            ypixel: Y pixel coordinate

        Returns:
            Plot coordinates
        """
        return self.x[int(pixelround(xpixel))], self.y[int(pixelround(ypixel))]

    def get_x_values(self, i0: int, i1: int) -> np.ndarray:
        """Get X values from pixel indexes

        Args:
            i0: First index
            i1: Second index

        Returns:
            X values corresponding to the given pixel indexes
        """
        return self.x[i0:i1]

    def get_y_values(self, j0: int, j1: int) -> np.ndarray:
        """Get Y values from pixel indexes

        Args:
            j0: First index
            j1: Second index

        Returns:
            Y values corresponding to the given pixel indexes
        """
        return self.y[j0:j1]

    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """
        i, j = self.get_closest_indexes(x, y)
        return self.x[i], self.y[j]

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
            ISerializableType,
            ICSImageItemType,
        )

    # ---- IBaseImageItem API --------------------------------------------------
    def can_sethistogram(self) -> bool:
        """
        Returns True if this item can be associated with a levels histogram

        Returns:
            bool: True if item can be associated with a levels histogram,
             False otherwise
        """
        return True


assert_interfaces_valid(XYImageItem)


# ==============================================================================
# RGB Image with alpha channel
# ==============================================================================
class RGBImageItem(ImageItem):
    """RGB image item

    Args:
        data: 3D NumPy array (shape: NxMx[34] -- 3: RGB, 4: RGBA)
        param: image parameters
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, ISerializableType)

    def __init__(
        self, data: np.ndarray | None = None, param: RGBImageParam | None = None
    ) -> None:
        self.orig_data = None
        super().__init__(data, param)
        self.lut = None

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self) -> RGBImageParam:
        """Return instance of the default image param DataSet"""
        return RGBImageParam(_("Image"))

    # ---- Public API ----------------------------------------------------------
    def recompute_alpha_channel(self) -> None:
        """Recompute alpha channel"""
        data = self.orig_data
        if self.orig_data is None:
            return
        H, W, NC = data.shape
        R = data[..., 0].astype(np.uint32)
        G = data[..., 1].astype(np.uint32)
        B = data[..., 2].astype(np.uint32)
        use_alpha = self.param.alpha_function != LUTAlpha.NONE.value
        alpha = self.param.alpha
        if NC > 3 and use_alpha:
            A = data[..., 3].astype(np.uint32)
        else:
            A = np.zeros((H, W), np.uint32)
            A[:, :] = int(255 * alpha)
        self.data[:, :] = (A << 24) + (R << 16) + (G << 8) + B

    # --- BaseImageItem API ----------------------------------------------------
    # Override lut/bg handling
    def set_lut_range(self, lut_range: tuple[float, float]) -> None:
        """
        Set the current active lut range

        .. warning::

            This method is not implemented for this item type.
        """
        pass

    def set_background_color(self, qcolor: QColor | str) -> None:
        """Set background color

        Args:
            qcolor: Background color

        .. warning::

            This method is not implemented for this item type.
        """
        self.lut = None

    def set_color_map(
        self, name_or_table: str | EditableColormap, invert: bool | None = None
    ) -> None:
        """Set colormap

        Args:
            name_or_table: Colormap name or colormap
            invert: True to invert colormap, False otherwise (Default value = None,
             i.e. do not change the default behavior)
        """
        self.lut = None

    # ---- RawImageItem API ----------------------------------------------------
    def load_data(self) -> None:
        """Load data from item filename attribute"""
        data = io.imread(self.get_filename(), to_grayscale=False)
        self.set_data(data)

    def set_data(self, data: np.ndarray) -> None:
        """Set image data

        Args:
            data: 2D NumPy array
        """
        H, W, NC = data.shape
        self.orig_data = data
        self.data = np.empty((H, W), np.uint32)
        self.recompute_alpha_channel()
        self.update_bounds()
        self.update_border()
        self.lut = None

    # ---- IBasePlotItem API ---------------------------------------------------
    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (IImageItemType, ITrackableItemType, ISerializableType)

    # ---- IBaseImageItem API --------------------------------------------------
    def can_sethistogram(self) -> bool:
        """
        Returns True if this item can be associated with a levels histogram

        Returns:
            bool: True if item can be associated with a levels histogram,
             False otherwise
        """
        return False


assert_interfaces_valid(RGBImageItem)
