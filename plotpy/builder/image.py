# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Image Item builder
------------------

This module provides a set of factory functions to simplify the creation
of image items.
"""

# Note: when adding method to builder classes, please do not forget to update the
# documentation (see builder.rst file). Because of class inheritance, the methods
# are not automatically documented (otherwise, they would be sorted alphabetically,
# due to a limitation of sphinx auto-doc).

from __future__ import annotations

import os.path as osp
from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy  # only to help intersphinx finding numpy doc
import numpy as np

from plotpy import io
from plotpy.config import _, make_title
from plotpy.constants import LUTAlpha
from plotpy.items import (
    ContourItem,
    Histogram2DItem,
    ImageItem,
    MaskedImageItem,
    MaskedXYImageItem,
    QuadGridItem,
    RGBImageItem,
    TrImageItem,
    XYImageItem,
    create_contour_items,
)
from plotpy.styles import (
    Histogram2DParam,
    ImageFilterParam,
    ImageParam,
    MaskedImageParam,
    MaskedXYImageParam,
    QuadGridParam,
    RGBImageParam,
    TrImageParam,
    XYImageParam,
)

if TYPE_CHECKING:  # pragma: no cover
    from plotpy.items.image.filter import ImageFilterItem

IMAGE_COUNT = 0
HISTOGRAM2D_COUNT = 0


class ImageBuilder:
    """Class regrouping a set of factory functions to simplify the creation
    of image items."""

    def __set_image_param(
        self,
        param: ImageParam,
        title: str | None,
        alpha_function: LUTAlpha | str | None,
        alpha: float | None,
        interpolation: str,
        **kwargs,
    ) -> None:
        if title:
            param.label = title
        else:
            global IMAGE_COUNT
            IMAGE_COUNT += 1
            param.label = make_title(_("Image"), IMAGE_COUNT)
        if alpha_function is not None:
            if isinstance(alpha_function, str):
                alpha_function = LUTAlpha.get_member_from_name(alpha_function)
            assert isinstance(alpha_function, LUTAlpha)
            param.alpha_function = alpha_function.value
        if alpha is not None:
            assert 0.0 <= alpha <= 1.0
            param.alpha = alpha
        interp_methods = {"nearest": 0, "linear": 1, "antialiasing": 5}
        param.interpolation = interp_methods[interpolation]
        for key, val in list(kwargs.items()):
            if val is not None:
                setattr(param, key, val)

    def _get_image_data(
        self,
        data: numpy.ndarray,
        filename: str | None,
        title: str | None,
        to_grayscale: bool,
    ) -> tuple[numpy.ndarray, str | None, str | None]:
        if data is None:
            assert filename is not None
            data = io.imread(filename, to_grayscale=to_grayscale)
        if title is None and filename is not None:
            title = osp.basename(filename)
        return data, filename, title

    @staticmethod
    def compute_bounds(
        data: numpy.ndarray,
        pixel_size: float | tuple[float, float],
        center_on: tuple[float, float] | None = None,
    ) -> tuple[float, float, float, float]:
        """Return image bounds from *pixel_size* (scalar or tuple)

        Args:
            data: image data
            pixel_size: pixel size
            center_on: center coordinates. Default is None

        Returns:
            tuple: xmin, xmax, ymin, ymax
        """
        if not isinstance(pixel_size, (tuple, list)):
            pixel_size = [pixel_size, pixel_size]
        dx, dy = pixel_size
        xmin, ymin = 0.0, 0.0
        xmax, ymax = data.shape[1] * dx, data.shape[0] * dy
        if center_on is not None:
            xc, yc = center_on
            dx, dy = 0.5 * (xmax - xmin) - xc, 0.5 * (ymax - ymin) - yc
            xmin -= dx
            xmax -= dx
            ymin -= dy
            ymax -= dy
        return xmin, xmax, ymin, ymax

    def image(
        self,
        data: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        xdata: list[float] = [None, None],
        ydata: list[float] = [None, None],
        pixel_size: float | tuple[float, float] | None = None,
        center_on: tuple[float, float] | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        x: numpy.ndarray | None = None,
        y: numpy.ndarray | None = None,
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = True,
    ) -> ImageItem | XYImageItem | RGBImageItem:
        """Make an image `plot item` from data

        Args:
            data: data. Default is None
            filename: image filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is None
            background_color: background color name. Default is None
            colormap: colormap name. Default is None
            xdata: x data. Default is [None, None]
            ydata: y data. Default is [None, None]
            pixel_size: pixel size. Default is None
            center_on: center on. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            x: x data. Default is None
            y: y data. Default is None
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.ImageItem` object or
            :py:class:`.XYImageItem` object if `x` and `y` are specified or
            :py:class:`.RGBImageItem` object if data has 3 dimensions
        """
        if x is not None or y is not None:
            assert pixel_size is None and center_on is None, (
                "Ambiguous parameters:"
                "both `x`/`y` and `pixel_size`/`center_on`/`xdata`/`ydata`"
                " were specified"
            )
            return self.xyimage(
                x,
                y,
                data,
                title=title,
                alpha_function=alpha_function,
                alpha=alpha,
                background_color=background_color,
                colormap=colormap,
                interpolation=interpolation,
                eliminate_outliers=eliminate_outliers,
                xformat=xformat,
                yformat=yformat,
                zformat=zformat,
                lut_range=lut_range,
                lock_position=lock_position,
            )

        assert isinstance(xdata, (tuple, list)) and len(xdata) == 2
        assert isinstance(ydata, (tuple, list)) and len(ydata) == 2
        param = ImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=True
        )

        if isinstance(filename, str) and filename.lower().endswith(".dcm"):
            # pylint: disable=import-outside-toplevel
            # pylint: disable=import-error
            from pydicom import dicomio  # type:ignore

            template = dicomio.read_file(filename, stop_before_pixels=True, force=True)
            ipp = getattr(template, "ImagePositionPatient", ["0", "0", "0"])
            pxs = getattr(template, "PixelSpacing", ["1", "1"])
            ipx, ipy = float(ipp[0]), float(ipp[1])
            pixel_size = dy, dx = float(pxs[0]), float(pxs[1])
            xc = (0.5 * data.shape[1] - 1) * dx + ipx
            yc = (0.5 * data.shape[0] - 1) * dy + ipy
            center_on = xc, yc

        if data.ndim == 3:
            return self.rgbimage(
                data=data,
                filename=filename,
                title=title,
                alpha_function=alpha_function,
                alpha=alpha,
            )
        assert data.ndim == 2, "Data must have 2 dimensions"
        if pixel_size is None:
            assert (
                center_on is None
            ), "Argument `pixel_size` must be specified when `center_on`"
            xmin, xmax = xdata
            ymin, ymax = ydata
        else:
            xmin, xmax, ymin, ymax = self.compute_bounds(data, pixel_size, center_on)
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = ImageItem(data, param)
        image.set_filename(filename)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_threshold(eliminate_outliers)
        return image

    def maskedimage(
        self,
        data: numpy.ndarray | None = None,
        mask: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float = 1.0,
        xdata: list[float] = [None, None],
        ydata: list[float] = [None, None],
        pixel_size: float | tuple[float, float] | None = None,
        center_on: tuple[float, float] | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        show_mask: bool = False,
        fill_value: float | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        x: numpy.ndarray | None = None,
        y: numpy.ndarray | None = None,
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = True,
    ) -> MaskedImageItem | MaskedXYImageItem:
        """Make a masked image `plot item` from data

        Args:
            data: data. Default is None
            mask: mask. Default is None
            filename: image filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is 1.0
            xdata: x data. Default is [None, None]
            ydata: y data. Default is [None, None]
            pixel_size: pixel size. Default is None
            center_on: center on. Default is None
            background_color: background color. Default is None
            colormap: colormap. Default is None
            show_mask: show mask. Default is False
            fill_value: fill value. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            x: x data. Default is None
            y: y data. Default is None
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.MaskedImageItem` object or :py:class:`.MaskedXYImageItem` object
        """
        if x is not None or y is not None:
            assert pixel_size is None and center_on is None, (
                "Ambiguous parameters:"
                "both `x`/`y` and `pixel_size`/`center_on`/`xdata`/`ydata`"
                " were specified"
            )
            return self.maskedxyimage(
                x,
                y,
                data,
                mask=mask,
                title=title,
                alpha_function=alpha_function,
                alpha=alpha,
                background_color=background_color,
                colormap=colormap,
                show_mask=show_mask,
                fill_value=fill_value,
                interpolation=interpolation,
                eliminate_outliers=eliminate_outliers,
                xformat=xformat,
                yformat=yformat,
                zformat=zformat,
                lut_range=lut_range,
                lock_position=lock_position,
            )

        assert isinstance(xdata, (tuple, list)) and len(xdata) == 2
        assert isinstance(ydata, (tuple, list)) and len(ydata) == 2
        param = MaskedImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=True
        )
        assert data.ndim == 2, "Data must have 2 dimensions"
        if pixel_size is None:
            assert center_on is None, (
                "Ambiguous parameters: both `center_on`"
                " and `xdata`/`ydata` were specified"
            )
            xmin, xmax = xdata
            ymin, ymax = ydata
        else:
            xmin, xmax, ymin, ymax = self.compute_bounds(data, pixel_size, center_on)
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            show_mask=show_mask,
            fill_value=fill_value,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = MaskedImageItem(data, mask, param)
        image.set_filename(filename)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_threshold(eliminate_outliers)
        return image

    def maskedxyimage(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        data: numpy.ndarray,
        mask: numpy.ndarray | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float = 1.0,
        background_color: str | None = None,
        colormap: str | None = None,
        show_mask: bool = False,
        fill_value: float | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = True,
    ) -> MaskedXYImageItem:
        """Make a masked XY image `plot item` from data

        Args:
            x: x data
            y: y data
            data: data
            mask: mask. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is 1.0
            background_color: background color. Default is None
            colormap: colormap. Default is None
            show_mask: show mask. Default is False
            fill_value: fill value. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.MaskedXYImageItem` object
        """

        if isinstance(x, (list, tuple)):
            x = np.array(x)
        if isinstance(y, (list, tuple)):
            y = np.array(y)

        param = MaskedXYImageParam(title=_("Image"), icon="image.png")
        assert data.ndim == 2, "Data must have 2 dimensions"

        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            show_mask=show_mask,
            fill_value=fill_value,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = MaskedXYImageItem(x, y, data, mask, param)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_threshold(eliminate_outliers)
        return image

    def rgbimage(
        self,
        data: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float = 1.0,
        xdata: list | tuple = [None, None],
        ydata: list | tuple = [None, None],
        pixel_size: float | None = None,
        center_on: tuple | None = None,
        interpolation: str = "linear",
        lock_position: bool = True,
    ) -> RGBImageItem:
        """Make a RGB image `plot item` from data

        Args:
            data: data
            filename: filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is 1.0
            xdata: x data. Default is [None, None]
            ydata: y data. Default is [None, None]
            pixel_size: pixel size. Default is None
            center_on: center on. Default is None
            interpolation: interpolation method. Default is 'linear'
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.RGBImageItem` object
        """
        assert isinstance(xdata, (tuple, list)) and len(xdata) == 2
        assert isinstance(ydata, (tuple, list)) and len(ydata) == 2
        param = RGBImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=False
        )
        assert data.ndim == 3, "RGB data must have 3 dimensions"
        if pixel_size is None:
            assert center_on is None, (
                "Ambiguous parameters: both `center_on`"
                " and `xdata`/`ydata` were specified"
            )
            xmin, xmax = xdata
            ymin, ymax = ydata
        else:
            xmin, xmax, ymin, ymax = self.compute_bounds(data, pixel_size, center_on)
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            lock_position=lock_position,
        )
        image = RGBImageItem(data, param)
        image.set_filename(filename)
        return image

    def quadgrid(
        self,
        X: numpy.ndarray,
        Y: numpy.ndarray,
        Z: numpy.ndarray,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float | None = None,
        colormap: str | None = None,
        interpolation: str = "linear",
        lock_position: bool = True,
    ) -> QuadGridItem:
        """Make a pseudocolor `plot item` of a 2D array

        Args:
            X: x data
            Y: y data
            Z: data
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is None
            colormap: colormap. Default is None
            interpolation: interpolation method. Default is 'linear'
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.QuadGridItem` object
        """
        param = QuadGridParam(title=_("Image"), icon="image.png")
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            colormap=colormap,
            lock_position=lock_position,
        )
        image = QuadGridItem(X, Y, Z, param)
        return image

    def pcolor(self, *args, **kwargs) -> QuadGridItem:
        """Make a pseudocolor `plot item` of a 2D array
        based on MATLAB-like syntax

        Args:
            args: non-keyword arguments
            kwargs: keyword arguments

        Returns:
            :py:class:`.QuadGridItem` object

        Examples::
            pcolor(C)
            pcolor(X, Y, C)
        """  # noqa: E501
        if len(args) == 1:
            (Z,) = args
            M, N = Z.shape
            X, Y = np.meshgrid(np.arange(N, dtype=Z.dtype), np.arange(M, dtype=Z.dtype))
        elif len(args) == 3:
            X, Y, Z = args
        else:
            raise RuntimeError("1 or 3 non-keyword arguments expected")
        return self.quadgrid(X, Y, Z, **kwargs)

    def trimage(
        self,
        data: numpy.ndarray | None = None,
        filename: str | None = None,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        x0: float = 0.0,
        y0: float = 0.0,
        angle: float = 0.0,
        dx: float = 1.0,
        dy: float = 1.0,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = False,
    ) -> TrImageItem:
        """Make a transformable image `plot item` (image with an arbitrary
        affine transform)

        Args:
            data: data
            filename: filename. Default is None
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is None
            background_color: background color. Default is None
            colormap: colormap. Default is None
            x0: x position. Default is 0.0
            y0: y position. Default is 0.0
            angle: angle (radians). Default is 0.0
            dx: pixel size along X axis. Default is 1.0
            dy: pixel size along Y axis. Default is 1.0
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is False

        Returns:
            :py:class:`.TrImageItem` object
        """
        param = TrImageParam(title=_("Image"), icon="image.png")
        data, filename, title = self._get_image_data(
            data, filename, title, to_grayscale=True
        )
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            pos_x0=x0,
            pos_y0=y0,
            angle=angle,
            dx=dx,
            dy=dy,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        image = TrImageItem(data, param)
        image.set_filename(filename)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_threshold(eliminate_outliers)
        return image

    def xyimage(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        data: numpy.ndarray,
        title: str | None = None,
        alpha_function: LUTAlpha | str | None = None,
        alpha: float | None = None,
        background_color: str | None = None,
        colormap: str | None = None,
        interpolation: str = "linear",
        eliminate_outliers: float | None = None,
        xformat: str = "%.1f",
        yformat: str = "%.1f",
        zformat: str = "%.1f",
        lut_range: tuple[float, float] | None = None,
        lock_position: bool = False,
    ) -> XYImageItem:
        """Make an xyimage `plot item` (image with non-linear X/Y axes) from data

        Args:
            x: X coordinates
            y: Y coordinates
            data: data
            title: image title. Default is None
            alpha_function: function for LUT alpha channel.
             Default is :py:attr:`.LUTAlpha.NONE`
             (valid string values are 'none', 'constant', 'linear', 'sigmoid', 'tanh')
            alpha: alpha value. Default is None
            background_color: background color. Default is None
            colormap: colormap. Default is None
            interpolation: interpolation method. Default is 'linear'
            eliminate_outliers: eliminate outliers. Default is None
            xformat: x format. Default is '%.1f'
            yformat: y format. Default is '%.1f'
            zformat: z format. Default is '%.1f'
            lut_range: LUT range. Default is None
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.XYImageItem` object
        """
        param = XYImageParam(title=_("Image"), icon="image.png")
        self.__set_image_param(
            param,
            title,
            alpha_function,
            alpha,
            interpolation,
            background=background_color,
            colormap=colormap,
            xformat=xformat,
            yformat=yformat,
            zformat=zformat,
            lock_position=lock_position,
        )
        if isinstance(x, (list, tuple)):
            x = np.array(x)
        if isinstance(y, (list, tuple)):
            y = np.array(y)
        image = XYImageItem(x, y, data, param)
        if lut_range is not None:
            assert eliminate_outliers is None, (
                "Ambiguous parameters: both `lut_range`"
                " and `eliminate_outliers` were specified"
            )
            image.set_lut_range(lut_range)
        elif eliminate_outliers is not None:
            image.set_lut_threshold(eliminate_outliers)
        return image

    def imagefilter(
        self,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        imageitem: ImageItem,
        filter: Callable,
        title: str | None = None,
    ) -> ImageFilterItem:
        """Make a rectangular area image filter `plot item`

        Args:
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            imageitem: image item
            filter: filter function
            title: filter title. Default is None

        Returns:
            :py:class:`.ImageFilterItem` object
        """
        param = ImageFilterParam(_("Filter"), icon="funct.png")
        param.xmin, param.xmax, param.ymin, param.ymax = xmin, xmax, ymin, ymax
        if title is not None:
            param.label = title
        filt = imageitem.get_filter(filter, param)
        _m, _M = imageitem.get_lut_range()
        filt.set_lut_range([_m, _M])
        return filt

    def contours(
        self,
        Z: np.ndarray,
        levels: float | np.ndarray,
        X: np.ndarray | None = None,
        Y: np.ndarray | None = None,
    ) -> list[ContourItem]:
        """Make a contour curves

        Args:
            Z: The height values over which the contour is drawn.
            levels : Determines the number and positions of the contour lines/regions.
             If a float, draw contour lines at this specified levels
             If array-like, draw contour lines at the specified levels.
             The values must be in increasing order.
            X: The coordinates of the values in *Z*.
             *X* must be 2-D with the same shape as *Z* (e.g. created via
             ``numpy.meshgrid``), or it must both be 1-D such that ``len(X) == M``
             is the number of columns in *Z*.
             If none, they are assumed to be integer indices, i.e. ``X = range(M)``.
            Y: The coordinates of the values in *Z*.
             *Y* must be 2-D with the same shape as *Z* (e.g. created via
             ``numpy.meshgrid``), or it must both be 1-D such that ``len(Y) == N``
             is the number of rows in *Z*.
             If none, they are assumed to be integer indices, i.e. ``Y = range(N)``.

        Returns:
            list of :py:class:`.ContourItem` objects
        """
        return create_contour_items(Z, levels, X, Y)

    def histogram2D(
        self,
        X: numpy.ndarray,
        Y: numpy.ndarray,
        NX: int | None = None,
        NY: int | None = None,
        logscale: bool | None = None,
        title: str | None = None,
        transparent: bool | None = None,
        Z: numpy.ndarray | None = None,
        computation: int = -1,
        interpolation: int = 0,
        lock_position: bool = True,
    ) -> Histogram2DItem:
        """Make a 2D Histogram `plot item`

        Args:
            X: X data
            Y: Y data
            NX: number of bins along x-axis. Default is None
            NY: number of bins along y-axis. Default is None
            logscale: Z-axis scale. Default is None
            title: item title. Default is None
            transparent: enable transparency. Default is None
            Z: Z data. Default is None
            computation: computation mode. Default is -1
            interpolation: interpolation mode. Default is 0
            lock_position: lock position. Default is True

        Returns:
            :py:class:`.Histogram2DItem` object
        """
        basename = _("2D Histogram")
        param = Histogram2DParam(title=basename, icon="histogram2d.png")
        if NX is not None:
            param.nx_bins = NX
        if NY is not None:
            param.ny_bins = NY
        if logscale is not None:
            param.logscale = int(logscale)
        if title is not None:
            param.label = title
        else:
            global HISTOGRAM2D_COUNT
            HISTOGRAM2D_COUNT += 1
            param.label = make_title(basename, HISTOGRAM2D_COUNT)
        if transparent is not None:
            param.transparent = transparent
        param.computation = computation
        param.interpolation = interpolation
        param.lock_position = lock_position
        return Histogram2DItem(X, Y, param, Z=Z)
