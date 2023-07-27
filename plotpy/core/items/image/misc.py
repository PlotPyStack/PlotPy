# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.dataset.datatypes import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.core import io
from plotpy.core.coords import axes_to_canvas
from plotpy.core.interfaces.common import (
    IBaseImageItem,
    IBasePlotItem,
    IColormapImageItemType,
    ICSImageItemType,
    IExportROIImageItemType,
    IHistDataSource,
    IImageItemType,
    ITrackableItemType,
    IVoiImageItemType,
)
from plotpy.core.items.image.base import BaseImageItem, RawImageItem, _nanmax, _nanmin
from plotpy.core.items.image.mixin import ImageMixin
from plotpy.core.items.image.transform import TrImageItem
from plotpy.core.styles.image import ImageParam, QuadGridParam

try:
    from plotpy._scaler import _histogram, _scale_quads
    from plotpy.histogram2d import histogram2d, histogram2d_func
except ImportError:
    print(
        ("Module 'plotpy.core.items.image.base': missing C extension"),
        file=sys.stderr,
    )
    print(
        ("try running :" "python setup.py build_ext --inplace -c mingw32"),
        file=sys.stderr,
    )
    raise

if TYPE_CHECKING:
    from plotpy.core.interfaces.common import IItemType
    from plotpy.core.styles.base import ItemParameters


class QuadGridItem(ImageMixin, RawImageItem):
    """
    Construct a QuadGrid image

        * X, Y, Z: A structured grid of quadrilaterals
          each quad is defined by (X[i], Y[i]), (X[i], Y[i+1]),
          (X[i+1], Y[i+1]), (X[i+1], Y[i])
        * param (optional): image parameters (ImageParam instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, IHistDataSource, IVoiImageItemType)

    def __init__(self, X, Y, Z, param=None):
        assert X is not None
        assert Y is not None
        assert Z is not None
        self.X = X
        self.Y = Y
        assert X.shape == Y.shape
        assert Z.shape == X.shape
        self.tr = np.eye(3, dtype=float)
        self.itr = np.eye(3, dtype=float)
        self.points = np.array([[0, 0, 2, 2], [0, 2, 2, 0], [1, 1, 1, 1]], float)
        super(QuadGridItem, self).__init__(Z, param)
        self.set_data(Z)
        self.grid = 1
        self.interpolate = (0, 0.5, 0.5)
        self.param.update_item(self)

        self.set_transform(0, 0, 0)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self):
        """Return instance of the default imageparam DataSet"""
        return QuadGridParam(_("Quadrilaterals"))

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

    def set_data(self, data, X=None, Y=None, lut_range=None):
        """
        Set Image item data

            * data: 2D NumPy array
            * lut_range: LUT range -- tuple (levelmin, levelmax)
        """
        if lut_range is not None:
            _min, _max = lut_range
        else:
            _min, _max = _nanmin(data), _nanmax(data)

        self.data = data
        self.histogram_cache = None
        if X is not None:
            assert Y is not None
            self.X = X
            self.Y = Y

        xmin = self.X.min()
        xmax = self.X.max()
        ymin = self.Y.min()
        ymax = self.Y.max()
        self.points = np.array(
            [[xmin, xmin, xmax, xmax], [ymin, ymax, ymax, ymin], [1, 1, 1, 1]], float
        )
        self.update_bounds()
        self.update_border()
        self.set_lut_range([_min, _max])

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        """
        self._offscreen[...] = np.uint32(0)
        dest = _scale_quads(
            self.X,
            self.Y,
            self.data,
            src_rect,
            self.itr,
            self._offscreen,
            dst_rect,
            self.lut,
            self.interpolate,
            self.grid,
        )
        qrect = QC.QRectF(QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)
        xl, yt, xr, yb = dest
        self._offscreen[yt:yb, xl:xr] = 0

    def notify_new_offscreen(self):
        """ """
        # we always ensure the offscreen is clean before drawing
        self._offscreen[...] = 0


assert_interfaces_valid(QuadGridItem)


class Histogram2DItem(ImageMixin, BaseImageItem):
    """
    Construct a 2D histogram item

        * X: data (1-D array)
        * Y: data (1-D array)
        * param (optional): style parameters
          (:py:class:`.styles.Histogram2DParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, IHistDataSource, IVoiImageItemType)

    def __init__(self, X, Y, param=None, Z=None):
        if param is None:
            param = ImageParam(_("Image"))
        self._z = Z  # allows set_bins to
        self.tr = np.eye(3, dtype=float)
        self.itr = np.eye(3, dtype=float)
        self.points = np.array([[0, 0, 2, 2], [0, 2, 2, 0], [1, 1, 1, 1]], float)
        super(Histogram2DItem, self).__init__(param=param)

        # Set by parameters
        self.nx_bins = 0
        self.ny_bins = 0
        self.logscale = None

        # internal use
        self._x = None
        self._y = None

        # Histogram parameters
        self.histparam = param
        self.histparam.update_histogram(self)

        self.set_lut_range([0, 10.0])
        self.set_data(X, Y, Z)
        self.setIcon(get_icon("histogram2d.png"))
        self.set_transform(0, 0, 0)

    # ---- Public API -----------------------------------------------------------
    def set_bins(self, NX, NY):
        """Set histogram bins"""
        self.nx_bins = NX
        self.ny_bins = NY
        self.data = np.zeros((self.ny_bins, self.nx_bins), float)
        if self._z is not None:
            self.data_tmp = np.zeros((self.ny_bins, self.nx_bins), float)

    def set_data(self, X, Y, Z=None):
        """Set histogram data"""
        self._x = X
        self._y = Y
        self._z = Z
        xmin = self._x.min()
        xmax = self._x.max()
        ymin = self._y.min()
        ymax = self._y.max()
        self.points = np.array(
            [[xmin, xmin, xmax, xmax], [ymin, ymax, ymax, ymin], [1, 1, 1, 1]], float
        )
        self.compute_bounds()

    # ---- QwtPlotItem API ------------------------------------------------------
    fill_canvas = True

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        """
        computation = self.histparam.computation
        i1, j1, i2, j2 = src_rect

        if computation == -1 or self._z is None:
            self.data[:, :] = 0.0
            nmax = histogram2d(
                self._x, self._y, i1, i2, j1, j2, self.itr.A, self.data, self.logscale
            )
        else:
            self.data_tmp[:, :] = 0.0
            if computation in (2, 4):  # sum, avg
                self.data[:, :] = 0.0
            elif computation in (1, 5):  # min, argmin
                val = np.inf
                self.data[:, :] = val
            elif computation in (0, 6):  # max, argmax
                val = -np.inf
                self.data[:, :] = val
            elif computation == 3:
                self.data[:, :] = 1.0
            histogram2d_func(
                self._x,
                self._y,
                self._z,
                i1,
                i2,
                j1,
                j2,
                self.itr.A,
                self.data_tmp,
                self.data,
                computation,
            )
            if computation in (0, 1, 5, 6):
                self.data[self.data == val] = np.nan
            else:
                self.data[self.data_tmp == 0.0] = np.nan
        if self.histparam.auto_lut:
            nmin = _nanmin(self.data)
            nmax = _nanmax(self.data)
            self.set_lut_range([nmin, nmax])
            self.plot().update_colormap_axis(self)
        src_rect = (0, 0, self.nx_bins, self.ny_bins)

        def drawfunc(*args):
            return BaseImageItem.draw_image(self, *args)

        if self.fill_canvas:
            x1, y1, x2, y2 = canvasRect.getCoords()
            drawfunc(painter, canvasRect, src_rect, (x1, y1, x2, y2), xMap, yMap)
        else:
            dst_rect = tuple([int(i) for i in dst_rect])
            drawfunc(painter, canvasRect, src_rect, dst_rect, xMap, yMap)

    # ---- IBasePlotItem API ---------------------------------------------------
    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """
        return (
            IColormapImageItemType,
            IImageItemType,
            ITrackableItemType,
            IVoiImageItemType,
            IColormapImageItemType,
            ICSImageItemType,
        )

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""
        BaseImageItem.update_item_parameters(self)
        self.histparam.update_param(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        BaseImageItem.get_item_parameters(self, itemparams)
        itemparams.add("Histogram2DParam", self, self.histparam)

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """
        update_dataset(
            self.histparam, itemparams.get("Histogram2DParam"), visible_only=True
        )
        self.histparam = itemparams.get("Histogram2DParam")
        self.histparam.update_histogram(self)
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
        _min = _nanmin(self.data)
        _max = _nanmax(self.data)
        if self.data.dtype in (np.float64, np.float32):
            bins = np.unique(
                np.array(np.linspace(_min, _max, nbins + 1), dtype=self.data.dtype)
            )
        else:
            bins = np.arange(_min, _max + 2, dtype=self.data.dtype)
        res2 = np.zeros((bins.size + 1,), np.uint32)
        _histogram(self.data.flatten(), bins, res2)
        # toc("histo2")
        res = res2[1:-1], bins
        return res


assert_interfaces_valid(Histogram2DItem)


def assemble_imageitems(
    items,
    src_qrect,
    destw,
    desth,
    align=None,
    add_images=False,
    apply_lut=False,
    apply_interpolation=False,
    original_resolution=False,
    force_interp_mode=None,
    force_interp_size=None,
):
    """
    Assemble together image items in qrect (`QRectF` object)
    and return resulting pixel data

    .. warning::

        Does not support `XYImageItem` objects
    """
    # align width to 'align' bytes
    if align is not None:
        print(
            "plotpy.core.items.image.assemble_imageitems: since v2.2, "
            "the `align` option is ignored",
            file=sys.stderr,
        )
    align = 1  # XXX: Byte alignment is disabled until further notice!
    aligned_destw = int(align * ((int(destw) + align - 1) / align))
    aligned_desth = int(desth * aligned_destw / destw)

    try:
        output = np.zeros((aligned_desth, aligned_destw), np.float32)
    except ValueError:
        raise MemoryError
    if not add_images:
        dst_image = output

    dst_rect = (0, 0, aligned_destw, aligned_desth)

    src_rect = list(src_qrect.getCoords())
    # The source QRect is generally coming from a rectangle shape which is
    # adjusted to fit a given ROI on the image. So the rectangular area is
    # aligned with image pixel edges: to avoid any rounding error, we reduce
    # the rectangle area size by one half of a pixel, so that the area is now
    # aligned with the center of image pixels.
    pixel_width = src_qrect.width() / float(destw)
    pixel_height = src_qrect.height() / float(desth)
    src_rect[0] += 0.5 * pixel_width
    src_rect[1] += 0.5 * pixel_height
    src_rect[2] -= 0.5 * pixel_width
    src_rect[3] -= 0.5 * pixel_height

    for it in sorted(items, key=lambda obj: obj.z()):
        if it.isVisible() and src_qrect.intersects(it.boundingRect()):
            if add_images:
                dst_image = np.zeros_like(output)
            it.export_roi(
                src_rect=src_rect,
                dst_rect=dst_rect,
                dst_image=dst_image,
                apply_lut=apply_lut,
                apply_interpolation=apply_interpolation,
                original_resolution=original_resolution,
                force_interp_mode=force_interp_mode,
                force_interp_size=force_interp_size,
            )
            if add_images:
                output += dst_image
    return output


def get_plot_qrect(plot, p0, p1):
    """
    Return `QRectF` rectangle object in plot coordinates
    from top-left and bottom-right `QPointF` objects in canvas coordinates
    """
    ax, ay = plot.X_BOTTOM, plot.Y_LEFT
    p0x, p0y = plot.invTransform(ax, p0.x()), plot.invTransform(ay, p0.y())
    p1x, p1y = plot.invTransform(ax, p1.x() + 1), plot.invTransform(ay, p1.y() + 1)
    return QC.QRectF(p0x, p0y, p1x - p0x, p1y - p0y)


def get_items_in_rectangle(plot, p0, p1, item_type=None, intersect=True):
    """Return items which bounding rectangle intersects (p0, p1)
    item_type: default is `IExportROIImageItemType`"""
    if item_type is None:
        item_type = IExportROIImageItemType
    items = plot.get_items(item_type=item_type)
    src_qrect = get_plot_qrect(plot, p0, p1)
    if intersect:
        return [it for it in items if src_qrect.intersects(it.boundingRect())]
    else:  # contains
        return [it for it in items if src_qrect.contains(it.boundingRect())]


def compute_trimageitems_original_size(items, src_w, src_h):
    """Compute `TrImageItem` original size from max dx and dy"""
    trparams = [item.get_transform() for item in items if isinstance(item, TrImageItem)]
    if trparams:
        dx_max = max([dx for _x, _y, _angle, dx, _dy, _hf, _vf in trparams])
        dy_max = max([dy for _x, _y, _angle, _dx, dy, _hf, _vf in trparams])
        return src_w / dx_max, src_h / dy_max
    else:
        return src_w, src_h


def get_image_from_qrect(
    plot,
    p0,
    p1,
    src_size=None,
    adjust_range=None,
    item_type=None,
    apply_lut=False,
    apply_interpolation=False,
    original_resolution=False,
    add_images=False,
    force_interp_mode=None,
    force_interp_size=None,
):
    """Return image array from `QRect` area (p0 and p1 are respectively the
    top-left and bottom-right `QPointF` objects)

    adjust_range: None (return raw data, dtype=np.float32), 'original'
    (return data with original data type), 'normalize' (normalize range with
    original data type)"""
    assert adjust_range in (None, "normalize", "original")
    items = get_items_in_rectangle(plot, p0, p1, item_type=item_type)
    if not items:
        raise TypeError(_("There is no supported image item in current plot."))
    if src_size is None:
        _src_x, _src_y, src_w, src_h = get_plot_qrect(plot, p0, p1).getRect()
    else:
        # The only benefit to pass the src_size list is to avoid any
        # rounding error in the transformation computed in `get_plot_qrect`
        src_w, src_h = src_size
    destw, desth = compute_trimageitems_original_size(items, src_w, src_h)
    data = get_image_from_plot(
        plot,
        p0,
        p1,
        destw=destw,
        desth=desth,
        apply_lut=apply_lut,
        add_images=add_images,
        apply_interpolation=apply_interpolation,
        original_resolution=original_resolution,
        force_interp_mode=force_interp_mode,
        force_interp_size=force_interp_size,
    )
    if adjust_range is None:
        return data
    dtype = None
    for item in items:
        if dtype is None or item.data.dtype.itemsize > dtype.itemsize:
            dtype = item.data.dtype
    if adjust_range == "normalize":
        data = io.scale_data_to_dtype(data, dtype=dtype)
    else:
        data = np.array(data, dtype=dtype)
    return data


def get_image_in_shape(
    obj, norm_range=False, item_type=None, apply_lut=False, apply_interpolation=False
):
    """Return image array from rectangle shape"""
    x0, y0, x1, y1 = obj.get_rect()
    (x0, x1), (y0, y1) = sorted([x0, x1]), sorted([y0, y1])
    xc0, yc0 = axes_to_canvas(obj, x0, y0)
    xc1, yc1 = axes_to_canvas(obj, x1, y1)
    adjust_range = "normalize" if norm_range else "original"
    return get_image_from_qrect(
        obj.plot(),
        QC.QPointF(xc0, yc0),
        QC.QPointF(xc1, yc1),
        src_size=(x1 - x0, y1 - y0),
        adjust_range=adjust_range,
        item_type=item_type,
        apply_lut=apply_lut,
        apply_interpolation=apply_interpolation,
        original_resolution=True,
    )


def get_image_from_plot(
    plot,
    p0,
    p1,
    destw=None,
    desth=None,
    add_images=False,
    apply_lut=False,
    apply_interpolation=False,
    original_resolution=False,
    force_interp_mode=None,
    force_interp_size=None,
):
    """
    Return pixel data of a rectangular plot area (image items only)
    p0, p1: resp. top-left and bottom-right points (`QPointF` objects)
    apply_lut: apply contrast settings
    add_images: add superimposed images (instead of replace by the foreground)

    .. warning::

        Support only the image items implementing the `IExportROIImageItemType`
        interface, i.e. this does *not* support `XYImageItem` objects
    """
    if destw is None:
        destw = p1.x() - p0.x() + 1
    if desth is None:
        desth = p1.y() - p0.y() + 1
    items = plot.get_items(item_type=IExportROIImageItemType)
    qrect = get_plot_qrect(plot, p0, p1)
    return assemble_imageitems(
        items,
        qrect,
        destw,
        desth,  # align=4,
        add_images=add_images,
        apply_lut=apply_lut,
        apply_interpolation=apply_interpolation,
        original_resolution=original_resolution,
        force_interp_mode=force_interp_mode,
        force_interp_size=force_interp_size,
    )
