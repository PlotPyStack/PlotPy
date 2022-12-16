# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103

"""
plotpy.gui.widgets.items.image
------------------------------

The `image` module provides image-related objects and functions:

    * :py:class:`.image.ImageItem`: simple images
    * :py:class:`.image.TrImageItem`: images supporting arbitrary
      affine transform
    * :py:class:`.image.XYImageItem`: images with non-linear X/Y axes
    * :py:class:`.image.Histogram2DItem`: 2D histogram
    * :py:class:`.image.ImageFilterItem`: rectangular filtering area
      that may be resized and moved onto the processed image
    * :py:func:`.image.assemble_imageitems`
    * :py:func:`.image.get_plot_qrect`
    * :py:func:`.image.get_image_from_plot`

``ImageItem``, ``TrImageItem``, ``XYImageItem``, ``Histogram2DItem`` and
``ImageFilterItem`` objects are plot items (derived from QwtPlotItem) that
may be displayed on a :py:class:`.baseplot.BasePlot` plotting widget.

.. seealso::

    Module :py:mod:`plotpy.gui.widgets.items.curve`
        Module providing curve-related plot items

    Module :py:mod:`plotpy.gui.widgets.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Examples
~~~~~~~~

Create a basic image plotting widget:

    * before creating any widget, a `QApplication` must be instantiated (that
      is a `Qt` internal requirement):

>>> import plotpy.gui
>>> app = plotpy.gui.qapplication()

    * that is mostly equivalent to the following (the only difference is that
      the `plotpy` helper function also installs the `Qt` translation
      corresponding to the system locale):

>>> from PyQt5.QtWidgets import QApplication
>>> app = QApplication([])

    * now that a `QApplication` object exists, we may create the plotting
      widget:

>>> from plotpy.gui.widgets.baseplot import BasePlot, PlotType
>>> plot = BasePlot(title="Example", type=PlotType.IMAGE)

Generate random data for testing purpose:

>>> import numpy as np
>>> data = np.random.rand(100, 100)

Create a simple image item:

    * from the associated plot item class (e.g. `XYImageItem` to create
      an image with non-linear X/Y axes): the item properties are then
      assigned by creating the appropriate style parameters object
      (e.g. :py:class:`.styles.ImageParam`)

>>> from plotpy.gui.widgets.items.image import ImageItem
>>> from plotpy.gui.widgets.styles import ImageParam
>>> param = ImageParam()
>>> param.label = 'My image'
>>> image = ImageItem(param)
>>> image.set_data(data)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.gui.widgets.builder import make
>>> image = make.image(data, title='My image')

Attach the image to the plotting widget:

>>> plot.add_item(image)

Display the plotting widget:

>>> plot.show()
>>> app.exec_()

Reference
~~~~~~~~~

.. autoclass:: BaseImageItem
   :members:
   :inherited-members:
.. autoclass:: RawImageItem
   :members:
   :inherited-members:
.. autoclass:: ImageItem
   :members:
   :inherited-members:
.. autoclass: TransformImageMixin
.. autoclass:: TrImageItem
   :members:
   :inherited-members:
.. autoclass:: XYImageItem
   :members:
   :inherited-members:
.. autoclass:: RGBImageItem
   :members:
   :inherited-members:
.. autoclass:: MaskedImageItem
   :members:
   :inherited-members:
.. autoclass:: MaskedXYImageItem
   :members:
   :inherited-members:
.. autoclass:: ImageFilterItem
   :members:
   :inherited-members:
.. autoclass:: XYImageFilterItem
   :members:
   :inherited-members:
.. autoclass:: Histogram2DItem
   :members:
   :inherited-members:
.. autoclass:: QuadGridItem
   :members:
   :inherited-members:

.. autofunction:: assemble_imageitems
.. autofunction:: get_plot_qrect
.. autofunction:: get_image_from_plot
"""

# FIXME: traceback in scaler when adding here 'from __future__ import division'

from __future__ import print_function, unicode_literals

import os.path as osp
import sys
from os import getcwd

import numpy as np

from plotpy.core.dataset.dataitems import DirectoryItem
from plotpy.core.utils.dataset import update_dataset
from plotpy.gui.utils.gui import assert_interfaces_valid
from plotpy.gui.utils.misc import get_icon
from plotpy.gui.widgets import io
from plotpy.gui.widgets.colormap import FULLRANGE, get_cmap, get_cmap_name
from plotpy.gui.widgets.config import _
from plotpy.gui.widgets.ext_gui_lib import (
    QBrush,
    QColor,
    QIcon,
    QImage,
    QPen,
    QPointF,
    QRect,
    QRectF,
    QwtPlot,
    QwtPlotItem,
)
from plotpy.gui.widgets.geometry import colvector, rotate, scale, translate
from plotpy.gui.widgets.interfaces import (
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
from plotpy.gui.widgets.io import iohandler
from plotpy.gui.widgets.items.shapes import RectangleShape
from plotpy.gui.widgets.items.utils import axes_to_canvas, canvas_to_axes
from plotpy.gui.widgets.styles import (
    ImageParam,
    MaskedImageParam,
    MaskedXYImageParam,
    QuadGridParam,
    RawImageParam,
    RGBImageParam,
    TrImageParam,
    XYImageParam,
)

stderr = sys.stderr
try:
    from plotpy._scaler import (
        INTERP_AA,
        INTERP_LINEAR,
        INTERP_NEAREST,
        _histogram,
        _scale_quads,
        _scale_rect,
        _scale_tr,
        _scale_xy,
    )
    from plotpy.histogram2d import histogram2d, histogram2d_func
except ImportError:
    print(
        ("Module 'plotpy.gui.widgets.items.image': missing C extension"),
        file=sys.stderr,
    )
    print(
        ("try running :" "python setup.py build_ext --inplace -c mingw32"),
        file=sys.stderr,
    )
    raise

LUT_SIZE = 1024
LUT_MAX = float(LUT_SIZE - 1)


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

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        super(ImageItem, self).serialize(writer)
        (xmin, xmax), (ymin, ymax) = self.get_xdata(), self.get_ydata()
        writer.write(xmin, group_name="xmin")
        writer.write(xmax, group_name="xmax")
        writer.write(ymin, group_name="ymin")
        writer.write(ymax, group_name="ymax")

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
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
        self.bounds = QRectF(QPointF(xmin, ymin), QPointF(xmax, ymax))

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
        xfunc = lambda index: xmin + (xmax - xmin) * index / float(self.data.shape[1])
        return np.linspace(xfunc(i0), xfunc(i1), i1 - i0, endpoint=False)

    def get_y_values(self, j0, j1):
        """

        :param j0:
        :param j1:
        :return:
        """
        ymin, ymax = self.get_ydata()
        yfunc = lambda index: ymin + (ymax - ymin) * index / float(self.data.shape[0])
        return np.linspace(yfunc(j0), yfunc(j1), j1 - j0, endpoint=False)

    def get_closest_coordinates(self, x, y):
        """Return closest image pixel coordinates"""
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
        qrect = QRectF(QPointF(dest[0], dest[1]), QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)

    def export_roi(
        self,
        src_rect,
        dst_rect,
        dst_image,
        apply_lut=False,
        apply_interpolation=False,
        original_resolution=False,
        force_interp_mode=None,
        force_interp_size=None,
    ):
        """Export Region Of Interest to array"""
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

    def move_local_point_to(self, handle, pos, ctrl=None):
        """Move a handle as returned by hit_test to the new position pos
        ctrl: True if <Ctrl> button is being pressed, False otherwise"""

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

    def move_local_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in canvas coordinates"""
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

    def move_with_selection(self, delta_x, delta_y):
        """
        Translate the shape together with other selected items
        delta_x, delta_y: translation in plot coordinates
        """
        xmin, xmax = self.get_xdata()
        ymin, ymax = self.get_ydata()
        self.set_xdata(xmin + delta_x, xmax + delta_x)
        self.set_ydata(ymin + delta_x, ymax + delta_y)
        self.update_bounds()
        self.update_border()


assert_interfaces_valid(ImageItem)


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
            "plotpy.gui.widgets.items.image.assemble_imageitems: since v2.2, "
            "the `align` option is ignored",
            file=sys.stderr,
        )
    align = 1  # XXX: byte alignment is disabled until further notice!
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
    return QRectF(p0x, p0y, p1x - p0x, p1y - p0y)


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
        from plotpy.gui.widgets import io

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
        QPointF(xc0, yc0),
        QPointF(xc1, yc1),
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

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        super(XYImageItem, self).serialize(writer)
        writer.write(self.x, group_name="Xdata")
        writer.write(self.y, group_name="Ydata")

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
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
        qrect = QRectF(QPointF(dest[0], dest[1]), QPointF(dest[2], dest[3]))
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

    def get_closest_coordinates(self, x, y):
        """Return closest image pixel coordinates"""
        i, j = self.get_closest_indexes(x, y)
        xi, yi = self.x[i], self.y[j]
        v = self.itr * colvector(xi, yi)
        x, y, _ = v[:, 0].A.ravel()
        return x, y

    # ---- IBasePlotItem API ---------------------------------------------------
    def types(self):
        """

        :return:
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
    def can_setfullscale(self):
        """

        :return:
        """
        return True

    def can_sethistogram(self):
        """

        :return:
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
        use_alpha = self.param.alpha_mask
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
    def types(self):
        """

        :return:
        """
        return (IImageItemType, ITrackableItemType, ISerializableType)

    # ---- IBaseImageItem API --------------------------------------------------
    def can_setfullscale(self):
        """

        :return:
        """
        return True

    def can_sethistogram(self):
        """

        :return:
        """
        return False


assert_interfaces_valid(RGBImageItem)


# ==============================================================================
# Masked Image
# ==============================================================================
class MaskedArea(object):
    """Defines masked areas for a masked image item"""

    def __init__(self, geometry=None, x0=None, y0=None, x1=None, y1=None, inside=None):
        self.geometry = geometry
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.inside = inside

    def __eq__(self, other):
        return (
            self.geometry == other.geometry
            and self.x0 == other.x0
            and self.y0 == other.y0
            and self.x1 == other.x1
            and self.y1 == other.y1
            and self.inside == other.inside
        )

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        for name in ("geometry", "inside", "x0", "y0", "x1", "y1"):
            writer.write(getattr(self, name), name)

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
        self.geometry = reader.read("geometry")
        self.inside = reader.read("inside")
        for name in ("x0", "y0", "x1", "y1"):
            setattr(self, name, reader.read(name, func=reader.read_float))
