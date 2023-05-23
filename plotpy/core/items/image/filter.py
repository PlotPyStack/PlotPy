# -*- coding: utf-8 -*-
import sys

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import assert_interfaces_valid, update_dataset
from qtpy import QtCore as QC

from plotpy.core.interfaces.common import (
    IBaseImageItem,
    IBasePlotItem,
    IColormapImageItemType,
    IImageItemType,
    ITrackableItemType,
    IVoiImageItemType,
)
from plotpy.core.items.image.base import BaseImageItem
from plotpy.core.items.utils import canvas_to_axes

try:
    from plotpy._scaler import _scale_xy
except ImportError:
    print(
        ("Module 'plotpy.core.items.image.filter': missing C extension"),
        file=sys.stderr,
    )
    print(
        ("try running :" "python setup.py build_ext --inplace -c mingw32"),
        file=sys.stderr,
    )
    raise


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

        * image: :py:class:`.image.RawImageItem` instance
        * filter: function (x, y, data) --> data
        * param: image filter parameters
          (:py:class:`.styles.ImageFilterParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem)
    _can_select = True
    _can_resize = True
    _can_move = True

    def __init__(self, image, filter, param):
        self.use_source_cmap = None
        self.image = None  # BaseImageItem constructor will try to set this
        # item's color map using the method 'set_color_map'
        super(ImageFilterItem, self).__init__(param=param)
        self.border_rect.set_style("plot", "shape/imagefilter")
        self.image = image
        self.filter = filter

        self.imagefilterparam = param
        self.imagefilterparam.update_imagefilter(self)
        self.setIcon(get_icon("funct.png"))

    # ---- Public API -----------------------------------------------------------
    def set_image(self, image):
        """
        Set the image item on which the filter will be applied

            * image: :py:class:`.image.RawImageItem` instance
        """
        self.image = image

    def set_filter(self, filter):
        """
        Set the filter function

            * filter: function (x, y, data) --> data
        """
        self.filter = filter

    # ---- QwtPlotItem API ------------------------------------------------------
    def boundingRect(self):
        """

        :return:
        """
        x0, y0, x1, y1 = self.border_rect.get_rect()
        return QC.QRectF(x0, y0, x1 - x0, y1 - y0)

    # ---- IBasePlotItem API ----------------------------------------------------
    def update_item_parameters(self):
        """ """
        BaseImageItem.update_item_parameters(self)
        self.imagefilterparam.update_param(self)

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        BaseImageItem.get_item_parameters(self, itemparams)
        self.update_item_parameters()
        itemparams.add("ImageFilterParam", self, self.imagefilterparam)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        update_dataset(
            self.imagefilterparam, itemparams.get("ImageFilterParam"), visible_only=True
        )
        self.imagefilterparam.update_imagefilter(self)
        BaseImageItem.set_item_parameters(self, itemparams)

    def move_local_point_to(self, handle, pos, ctrl=None):
        """Move a handle as returned by hit_test to the new position pos
        ctrl: True if <Ctrl> button is being pressed, False otherwise"""
        npos = canvas_to_axes(self, pos)
        self.border_rect.move_point_to(handle, npos)

    def move_local_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in canvas coordinates"""
        old_pt = canvas_to_axes(self, old_pos)
        new_pt = canvas_to_axes(self, new_pos)
        self.border_rect.move_shape(old_pt, new_pt)
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, *(old_pt + new_pt))

    def move_with_selection(self, delta_x, delta_y):
        """
        Translate the shape together with other selected items
        delta_x, delta_y: translation in plot coordinates
        """
        self.border_rect.move_with_selection(delta_x, delta_y)

    def set_color_map(self, name_or_table):
        """

        :param name_or_table:
        """
        if self.use_source_cmap:
            if self.image is not None:
                self.image.set_color_map(name_or_table)
        else:
            BaseImageItem.set_color_map(self, name_or_table)

    def get_color_map(self):
        """

        :return:
        """
        if self.use_source_cmap:
            return self.image.get_color_map()
        else:
            return BaseImageItem.get_color_map(self)

    def get_lut_range(self):
        """

        :return:
        """
        if self.use_source_cmap:
            return self.image.get_lut_range()
        else:
            return BaseImageItem.get_lut_range(self)

    def set_lut_range(self, lut_range):
        """

        :param lut_range:
        """
        if self.use_source_cmap:
            self.image.set_lut_range(lut_range)
        else:
            BaseImageItem.set_lut_range(self, lut_range)

    # ---- IBaseImageItem API ---------------------------------------------------
    def types(self):
        """

        :return:
        """
        return (
            IImageItemType,
            IVoiImageItemType,
            IColormapImageItemType,
            ITrackableItemType,
        )

    def can_setfullscale(self):
        """

        :return:
        """
        return False

    def can_sethistogram(self):
        """

        :return:
        """
        return True


class XYImageFilterItem(ImageFilterItem):
    """
    Construct a rectangular area image filter item

        * image: :py:class:`.image.XYImageItem` instance
        * filter: function (x, y, data) --> data
        * param: image filter parameters
          (:py:class:`.styles.ImageFilterParam` instance)
    """

    def __init__(self, image, filter, param):
        ImageFilterItem.__init__(self, image, filter, param)

    def set_image(self, image):
        """
        Set the image item on which the filter will be applied

            * image: :py:class:`.image.XYImageItem` instance
        """
        ImageFilterItem.set_image(self, image)

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
        bounds = self.boundingRect()

        filt_qrect = bounds & self.image.boundingRect()
        x0, y0, x1, y1 = filt_qrect.getCoords()
        i0, i1 = xMap.transform(x0), xMap.transform(x1)
        j0, j1 = yMap.transform(y0), yMap.transform(y1)

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

        x0, y0, x1, y1 = src_rect
        cx = canvasRect.left()
        cy = canvasRect.top()
        sx = (x1 - x0) / (W - 1)
        sy = (y1 - y0) / (H - 1)
        # tr1 = tr(x0,y0)*scale(sx,sy)*tr(-cx,-cy)
        tr = np.matrix([[sx, 0, x0 - cx * sx], [0, sy, y0 - cy * sy], [0, 0, 1]], float)
        mat = self.image.tr * tr

        xytr = x - self.image.x[0], y - self.image.y[0], src_rect

        dest = _scale_xy(
            new_data,
            xytr,
            mat,
            self._offscreen,
            dstRect.getCoords(),
            lut,
            self.interpolate,
        )
        qrect = QC.QRectF(QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)


assert_interfaces_valid(ImageFilterItem)
