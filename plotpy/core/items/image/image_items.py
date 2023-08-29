# -*- coding: utf-8 -*-
# pylint: disable=C0103

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.core import io
from plotpy.core.coords import canvas_to_axes
from plotpy.core.interfaces.common import (
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
from plotpy.core.items.image.base import RawImageItem, pixelround
from plotpy.core.items.image.filter import XYImageFilterItem, to_bins
from plotpy.core.items.image.mixin import ImageMixin
from plotpy.core.styles.image import ImageParam, LUTAlpha, RGBImageParam, XYImageParam
from plotpy.utils.geometry import colvector

if TYPE_CHECKING:
    import guidata.dataset.io
    from qtpy.QtCore import QPointF

    from plotpy.core.interfaces.common import IItemType

try:
    from plotpy._scaler import INTERP_NEAREST, _scale_rect, _scale_xy
except ImportError:
    print(
        ("Module 'plotpy.core.items.image': missing C extension"),
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
    """
    Construct a simple image item

        * data: 2D NumPy array
        * param (optional): image parameters
          (:py:class:`.styles.ImageParam` instance)
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

    def __init__(self, data=None, param=None):
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        super(ImageItem, self).__init__(data=data, param=param)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self):
        """Return instance of the default imageparam DataSet"""
        return ImageParam(_("Image"))

    # ---- Serialization methods -----------------------------------------------
    def __reduce__(self):
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

    def __setstate__(self, state):
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
        writer: guidata.dataset.io.HDF5Writer
        | guidata.dataset.io.INIWriter
        | guidata.dataset.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        super(ImageItem, self).serialize(writer)
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        writer.write(xmin, group_name="xmin")
        writer.write(xmax, group_name="xmax")
        writer.write(ymin, group_name="ymin")
        writer.write(ymax, group_name="ymax")

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
        super(ImageItem, self).deserialize(reader)
        for attr in ("xmin", "xmax", "ymin", "ymax"):
            # Note: do not be tempted to write the symetric code in `serialize`
            # because calling `get_xdata` and `get_ydata` is necessary
            setattr(self, attr, reader.read(attr, func=reader.read_float))

    # ---- Public API ----------------------------------------------------------
    def get_xdata(self):
        """Return (xmin, xmax)"""
        xmin, xmax = self.xmin, self.xmax
        if xmin is None:
            xmin = 0.0
        if xmax is None:
            xmax = self.data.shape[1]
        return xmin, xmax

    def get_ydata(self):
        """Return (ymin, ymax)"""
        ymin, ymax = self.ymin, self.ymax
        if ymin is None:
            ymin = 0.0
        if ymax is None:
            ymax = self.data.shape[0]
        return ymin, ymax

    def set_xdata(self, xmin=None, xmax=None):
        """

        :param xmin:
        :param xmax:
        """
        self.xmin, self.xmax = xmin, xmax

    def set_ydata(self, ymin=None, ymax=None):
        """

        :param ymin:
        :param ymax:
        """
        self.ymin, self.ymax = ymin, ymax

    def update_bounds(self):
        """

        :return:
        """
        if self.data is None:
            return
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        self.bounds = QC.QRectF(QC.QPointF(xmin, ymin), QC.QPointF(xmax, ymax))

    # ---- BaseImageItem API ---------------------------------------------------
    def get_pixel_coordinates(self, xplot, yplot):
        """Return (image) pixel coordinates (from plot coordinates)"""
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        xpix = self.data.shape[1] * (xplot - xmin) / float(xmax - xmin)
        ypix = self.data.shape[0] * (yplot - ymin) / float(ymax - ymin)
        return xpix, ypix

    def get_plot_coordinates(self, xpixel, ypixel):
        """Return plot coordinates (from image pixel coordinates)"""
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        xplot = xmin + (xmax - xmin) * xpixel / float(self.data.shape[1])
        yplot = ymin + (ymax - ymin) * ypixel / float(self.data.shape[0])
        return xplot, yplot

    def get_x_values(self, i0, i1):
        """

        :param i0:
        :param i1:
        :return:
        """
        xmin, xmax = self.get_xdata()

        def xfunc(index):
            return xmin + (xmax - xmin) * index / float(self.data.shape[1])

        return np.linspace(xfunc(i0), xfunc(i1), i1 - i0, endpoint=False)

    def get_y_values(self, j0, j1):
        """

        :param j0:
        :param j1:
        :return:
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
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        i, j = self.get_closest_indexes(x, y)
        xpix = np.linspace(xmin, xmax, self.data.shape[1] + 1)
        ypix = np.linspace(ymin, ymax, self.data.shape[0] + 1)
        return xpix[i], ypix[j]

    def _rescale_src_rect(self, src_rect):
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

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        :return:
        """
        if self.data is None:
            return
        src2 = self._rescale_src_rect(src_rect)
        dst_rect = tuple([int(i) for i in dst_rect])
        dest = _scale_rect(
            self.data, src2, self._offscreen, dst_rect, self.lut, self.interpolate
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
        force_interp_mode: str = None,
        force_interp_size: int = None,
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


class XYImageItem(ImageMixin, RawImageItem):
    """
    Construct an image item with non-linear X/Y axes

        * x: 1D NumPy array, must be increasing
        * y: 1D NumPy array, must be increasing
        * data: 2D NumPy array
        * param (optional): image parameters
          (:py:class:`.styles.XYImageParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, ISerializableType)

    def __init__(self, x=None, y=None, data=None, param=None):
        # if x and y are not increasing arrays, sort them and data accordingly
        if x is not None and not np.all(np.diff(x) >= 0):
            x_idx = np.argsort(x)
            x = x[x_idx]
            data = data[:, x_idx]
        if y is not None and not np.all(np.diff(y) >= 0):
            y_idx = np.argsort(y)
            y = y[y_idx]
            data = data[y_idx, :]
        self.x = None
        self.y = None
        self.tr = np.eye(3, dtype=float)
        self.itr = np.eye(3, dtype=float)
        self.points = np.array([[0, 0, 2, 2], [0, 2, 2, 0], [1, 1, 1, 1]], float)
        super(XYImageItem, self).__init__(data, param)

        if x is not None and y is not None:
            self.set_xy(x, y)
        self.set_transform(0, 0, 0)

    # ---- Public API ----------------------------------------------------------

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self):
        """Return instance of the default imageparam DataSet"""
        return XYImageParam(_("Image"))

    # ---- Pickle methods ------------------------------------------------------
    def __reduce__(self):
        fname = self.get_filename()
        if fname is None:
            fn_or_data = self.data
        else:
            fn_or_data = fname
        state = (self.param, self.get_lut_range(), self.x, self.y, fn_or_data, self.z())
        res = (self.__class__, (), state)
        return res

    def __setstate__(self, state):
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
        self.set_transform(*self.get_transform())

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
        super(XYImageItem, self).serialize(writer)
        writer.write(self.x, group_name="Xdata")
        writer.write(self.y, group_name="Ydata")

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
        super(XYImageItem, self).deserialize(reader)
        x = reader.read(group_name="Xdata", func=reader.read_array)
        y = reader.read(group_name="Ydata", func=reader.read_array)
        self.set_xy(x, y)
        self.set_transform(*self.get_transform())

    # ---- Public API ----------------------------------------------------------
    def set_xy(self, x, y):
        """

        :param x:
        :param y:
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
        xmin = self.x[0]
        xmax = self.x[-1]
        ymin = self.y[0]
        ymax = self.y[-1]
        self.points = np.array(
            [[xmin, xmin, xmax, xmax], [ymin, ymax, ymax, ymin], [1, 1, 1, 1]], float
        )
        # self.compute_bounds()

    # --- BaseImageItem API ----------------------------------------------------
    def get_filter(self, filterobj, filterparam):
        """Provides a filter object over this image's content"""
        return XYImageFilterItem(self, filterobj, filterparam)

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        """

        W = canvasRect.width()
        H = canvasRect.height()
        if W <= 1 or H <= 1:
            return

        x0, y0, x1, y1 = src_rect
        cx = canvasRect.left()
        cy = canvasRect.top()
        sx = (x1 - x0) / (W - 1)
        sy = (y1 - y0) / (H - 1)
        # tr1 = tr(x0,y0)*scale(sx,sy)*tr(-cx,-cy)
        tr = np.matrix([[sx, 0, x0 - cx * sx], [0, sy, y0 - cy * sy], [0, 0, 1]], float)
        mat = self.tr * tr

        xytr = self.x, self.y, src_rect
        dst_rect = tuple([int(i) for i in dst_rect])
        dest = _scale_xy(
            self.data, xytr, mat, self._offscreen, dst_rect, self.lut, self.interpolate
        )
        qrect = QC.QRectF(QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)

    def get_pixel_coordinates(self, xplot, yplot):
        """Return (image) pixel coordinates (from plot coordinates)"""
        v = self.tr * colvector(xplot, yplot)
        xpixel, ypixel, _ = v[:, 0]
        return self.x.searchsorted(xpixel), self.y.searchsorted(ypixel)

    def get_plot_coordinates(self, xpixel, ypixel):
        """Return plot coordinates (from image pixel coordinates)"""
        return self.x[int(pixelround(xpixel))], self.y[int(pixelround(ypixel))]

    def get_x_values(self, i0, i1):
        """

        :param i0:
        :param i1:
        :return:
        """
        zeros = np.zeros(self.x.shape)
        ones = np.ones(self.x.shape)
        xv = np.dstack((self.x, zeros, ones))
        x = (self.itr * xv.T).A[0]
        return x[i0:i1]

    def get_y_values(self, j0, j1):
        """

        :param j0:
        :param j1:
        :return:
        """
        zeros = np.zeros(self.y.shape)
        ones = np.ones(self.y.shape)
        yv = np.dstack((zeros, self.y, ones))
        y = (self.itr * yv.T).A[1]
        return y[j0:j1]

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
        xi, yi = self.x[i], self.y[j]
        v = self.itr * colvector(xi, yi)
        x, y, _ = v[:, 0].A.ravel()
        return x, y

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
    """
    Construct a RGB/RGBA image item

        * data: NumPy array of uint8 (shape: NxMx[34] -- 3: RGB, 4: RGBA)
          (last dimension: 0: Red, 1: Green, 2: Blue {, 3:Alpha})
        * param (optional): image parameters
          (:py:class:`.styles.RGBImageParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, ISerializableType)

    def __init__(self, data=None, param=None):
        self.orig_data = None
        super(RGBImageItem, self).__init__(data, param)
        self.lut = None

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self):
        """Return instance of the default imageparam DataSet"""
        return RGBImageParam(_("Image"))

    # ---- Public API ----------------------------------------------------------
    def recompute_alpha_channel(self):
        """

        :return:
        """
        data = self.orig_data
        if self.orig_data is None:
            return
        H, W, NC = data.shape
        R = data[..., 0].astype(np.uint32)
        G = data[..., 1].astype(np.uint32)
        B = data[..., 2].astype(np.uint32)
        use_alpha = self.param.alpha_function != LUTAlpha.NONE
        alpha = self.param.alpha
        if NC > 3 and use_alpha:
            A = data[..., 3].astype(np.uint32)
        else:
            A = np.zeros((H, W), np.uint32)
            A[:, :] = int(255 * alpha)
        self.data[:, :] = (A << 24) + (R << 16) + (G << 8) + B

    # --- BaseImageItem API ----------------------------------------------------
    # Override lut/bg handling
    def set_lut_range(self, range):
        """

        :param range:
        """
        pass

    def set_background_color(self, qcolor):
        """

        :param qcolor:
        """
        self.lut = None

    def set_color_map(self, name_or_table):
        """

        :param name_or_table:
        """
        self.lut = None

    # ---- RawImageItem API ----------------------------------------------------
    def load_data(self):
        """
        Load data from *filename*
        *filename* has been set using method 'set_filename'
        """
        data = io.imread(self.get_filename(), to_grayscale=False)
        self.set_data(data)

    def set_data(self, data):
        """

        :param data:
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
