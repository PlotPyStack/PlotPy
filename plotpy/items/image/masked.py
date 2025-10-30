# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

import guidata.io
import numpy as np
import numpy.ma as ma
from qtpy import QtCore as QC

from plotpy import io
from plotpy._scaler import INTERP_NEAREST, _scale_rect, _scale_xy
from plotpy.config import _
from plotpy.interfaces import (
    IBaseImageItem,
    IBasePlotItem,
    IExportROIImageItemType,
    IHistDataSource,
    IVoiImageItemType,
)
from plotpy.items.image.standard import ImageItem, XYImageItem
from plotpy.styles.image import MaskedImageParam, MaskedXYImageParam

if TYPE_CHECKING:
    import guidata.io
    import qwt.scale_map
    from qtpy.QtCore import QRectF
    from qtpy.QtGui import QPainter

    from plotpy.plot import BasePlot


class MaskedArea:
    """Defines masked areas for a masked image item

    Args:
        geometry: Geometry of the area ('rectangular' or anything else for circular)
        x0: X coordinate of first point
        y0: Y coordinate of first point
        x1: X coordinate of second point
        y1: Y coordinate of second point
        inside: True if the area is inside the geometry, False if it is outside
    """

    def __init__(
        self,
        geometry: str | None = None,
        x0: float | None = None,
        y0: float | None = None,
        x1: float | None = None,
        y1: float | None = None,
        inside: bool | None = None,
    ) -> None:
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

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        for name in ("geometry", "inside", "x0", "y0", "x1", "y1"):
            writer.write(getattr(self, name), name)

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.geometry = reader.read("geometry")
        self.inside = reader.read("inside")
        for name in ("x0", "y0", "x1", "y1"):
            setattr(self, name, reader.read(name, func=reader.read_float))


class MaskedImageMixin:
    """Masked image mixin

    This class is a mixin providing array mask features to image items. It is used by
    :py:class:`.MaskedImageItem` and :py:class:`.MaskedXYImageItem` classes.

    Args:
        mask: 2D masked array
    """

    def __init__(self, mask: ma.MaskedArray | None = None) -> None:
        self.orig_data: np.ndarray | None = None
        self._mask: ma.MaskedArray | None = mask
        self._mask_filename: str | None = None
        self._masked_areas: list[MaskedArea] = []
        # ImageItem and XYImageItem attributes:
        self.data: ma.MaskedArray | None = None
        self.param: MaskedImageParam | MaskedXYImageParam | None = None

    # ---- Pickle methods -------------------------------------------------------
    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        writer.write(self.get_mask_filename(), group_name="mask_fname")
        writer.write_object_list(self._masked_areas, "masked_areas")

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        mask_fname = reader.read(group_name="mask_fname", func=reader.read_unicode)
        masked_areas = reader.read_object_list("masked_areas", MaskedArea)
        if mask_fname:
            self.set_mask_filename(mask_fname)
            self.load_mask_data()
        elif masked_areas and self.data is not None:
            self.set_masked_areas(masked_areas)
            self.apply_masked_areas()

    # ---- Public API -----------------------------------------------------------
    def update_mask(self) -> None:
        """Update mask"""
        if isinstance(self.data, np.ma.MaskedArray):
            # Casting filling_value to data dtype, otherwise this may raise an error
            # in future versions of NumPy (at the time of writing, this raises a
            # DeprecationWarning "NumPy will stop allowing conversion of out-of-bound
            # Python integers to integer arrays.")
            val = np.array(self.param.filling_value).astype(self.data.dtype)

            self.data.set_fill_value(val)

    def set_mask(self, mask: ma.MaskedArray) -> None:
        """Set image mask

        Args:
            mask: 2D masked array
        """
        self.data.mask = mask

    def get_mask(self) -> ma.MaskedArray | None:
        """Get image mask

        Returns:
            2D masked array
        """
        return self.data.mask

    def set_mask_filename(self, fname: str) -> None:
        """Set mask filename

        Args:
            fname: Mask filename

        There are two ways for pickling mask data of `MaskedImageItem` objects:

            1. using the mask filename (as for data itself)
            2. using the mask areas (`MaskedArea` instance, see set_mask_areas)

        When saving objects, the first method is tried and then, if no
        filename has been defined for mask data, the second method is used.
        """
        self._mask_filename = fname

    def get_mask_filename(self) -> str:
        """Get mask filename

        Returns:
            Mask filename
        """
        return self._mask_filename

    def load_mask_data(self) -> None:
        """Load mask data from file"""
        data = io.imread(self.get_mask_filename(), to_grayscale=True)
        self.set_mask(data)
        self._mask_changed()

    def set_masked_areas(self, areas: list[MaskedArea]) -> None:
        """Set masked areas

        Args:
            areas: List of masked areas

        .. seealso:: :py:meth:`.set_mask_filename`
        """
        self._masked_areas = areas

    def get_masked_areas(self) -> list[MaskedArea]:
        """Get masked areas

        Returns:
            List of masked areas
        """
        return self._masked_areas

    def add_masked_area(
        self, geometry: str, x0: float, y0: float, x1: float, y1: float, inside: bool
    ) -> None:
        """Add masked area

        Args:
            geometry: Area geometry
            x0: top left x coordinate
            y0: top left y coordinate
            x1: bottom right x coordinate
            y1: bottom right y coordinate
            inside: Inside or outside
        """
        area = MaskedArea(geometry=geometry, x0=x0, y0=y0, x1=x1, y1=y1, inside=inside)
        for _area in self._masked_areas:
            if area == _area:
                return
        self._masked_areas.append(area)

    def _mask_changed(self) -> None:
        """Emit the :py:data:`.baseplot.BasePlot.SIG_MASK_CHANGED` signal"""
        plot: BasePlot = self.plot()
        if plot is not None:
            plot.SIG_MASK_CHANGED.emit(self)

    def apply_masked_areas(self) -> None:
        """Apply masked areas"""
        for area in self._masked_areas:
            if area.geometry == "rectangular":
                self.mask_rectangular_area(
                    area.x0,
                    area.y0,
                    area.x1,
                    area.y1,
                    area.inside,
                    trace=False,
                    do_signal=False,
                )
            else:
                self.mask_circular_area(
                    area.x0,
                    area.y0,
                    area.x1,
                    area.y1,
                    area.inside,
                    trace=False,
                    do_signal=False,
                )
        self._mask_changed()

    def mask_all(self) -> None:
        """Mask all pixels"""
        self.data.mask = True
        self._mask_changed()

    def unmask_all(self) -> None:
        """Unmask all pixels"""
        self.data.mask = np.ma.nomask
        self.set_masked_areas([])
        self._mask_changed()

    def mask_rectangular_area(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        inside: bool = True,
        trace: bool = True,
        do_signal: bool = True,
    ) -> None:
        """Mask rectangular area

        Args:
            x0: top left x coordinate
            y0: top left y coordinate
            x1: bottom right x coordinate
            y1: bottom right y coordinate
            inside: if True (default), mask the inside of the area, otherwise
             mask the outside
            trace: if True (default), add the area to the list of masked areas
            do_signal: if True (default), emit the
             :py:data:`.baseplot.BasePlot.SIG_MASK_CHANGED` signal
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        if inside:
            self.data[iy0:iy1, ix0:ix1] = np.ma.masked
        else:
            indexes = np.ones(self.data.shape, dtype=bool)
            indexes[iy0:iy1, ix0:ix1] = False
            self.data[indexes] = np.ma.masked
        if trace:
            self.add_masked_area("rectangular", x0, y0, x1, y1, inside)
        if do_signal:
            self._mask_changed()

    def mask_circular_area(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        inside: bool = True,
        trace: bool = True,
        do_signal: bool = True,
    ) -> None:
        """Mask circular area (as a circle inscribed in a rectangle)

        Args:
            x0: top left x coordinate
            y0: top left y coordinate
            x1: bottom right x coordinate
            y1: bottom right y coordinate
            inside: if True (default), mask the inside of the area, otherwise
             mask the outside
            trace: if True (default), add the area to the list of masked areas
            do_signal: if True (default), emit the
             :py:data:`.baseplot.BasePlot.SIG_MASK_CHANGED` signal
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        xc, yc = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        radius = 0.5 * (x1 - x0)
        xdata, ydata = self.get_x_values(ix0, ix1), self.get_y_values(iy0, iy1)

        for ix in range(ix0, ix1):
            for iy in range(iy0, iy1):
                distance = np.sqrt(
                    (xdata[ix - ix0] - xc) ** 2 + (ydata[iy - iy0] - yc) ** 2
                )
                if inside:
                    if distance <= radius:
                        self.data[iy, ix] = np.ma.masked
                elif distance > radius:
                    self.data[iy, ix] = np.ma.masked

        if not inside:
            self.mask_rectangular_area(x0, y0, x1, y1, inside, trace=False)
        if trace:
            self.add_masked_area("circular", x0, y0, x1, y1, inside)
        if do_signal:
            self._mask_changed()

    def is_mask_visible(self) -> bool:
        """Return mask visibility

        Returns:
            True if mask is visible, False otherwise
        """
        return self.param.show_mask

    def set_mask_visible(self, state: bool) -> None:
        """Set mask visibility

        Args:
            state: True to show mask, False to hide it
        """
        self.param.show_mask = state
        plot = self.plot()
        if plot is not None:
            plot.replot()

    def _set_data(self, data: np.ndarray) -> None:
        """Set image data

        Args:
            data: 2D NumPy array
        """
        self.orig_data = data
        self.data = data.view(np.ma.MaskedArray)
        self.set_mask(self._mask)
        self._mask = None  # removing reference to this temporary array
        if self.param.filling_value is None:
            self.param.filling_value = self.data.get_fill_value()
        self.update_mask()


class MaskedImageItem(ImageItem, MaskedImageMixin):
    """Masked image item

    Args:
        data: 2D NumPy array
        mask: 2D NumPy array
        param: image parameters
    """

    __implements__ = (
        IBasePlotItem,
        IBaseImageItem,
        IHistDataSource,
        IVoiImageItemType,
        IExportROIImageItemType,
    )

    def __init__(
        self,
        data: np.ndarray | None = None,
        mask: np.ndarray | None = None,
        param: MaskedImageParam | None = None,
    ) -> None:
        self.orig_data = None
        MaskedImageMixin.__init__(self, mask=mask)
        ImageItem.__init__(self, data=data, param=param)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self) -> MaskedImageParam:
        """Return instance of the default MaskedImageParam DataSet"""
        return MaskedImageParam(_("Image"))

    # ---- Pickle methods -------------------------------------------------------
    def __reduce__(self) -> tuple:
        """Reduce object to pickled state"""
        fname = self.get_filename()
        if fname is None:
            fn_or_data = self.data
        else:
            fn_or_data = fname
        state = (
            self.param,
            self.get_lut_range(),
            fn_or_data,
            self.z(),
            self.get_mask_filename(),
            self.get_masked_areas(),
        )
        res = (self.__class__, (), state)
        return res

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
        param, lut_range, fn_or_data, z, mask_fname, old_masked_areas = state
        if old_masked_areas and isinstance(old_masked_areas[0], MaskedArea):
            masked_areas = old_masked_areas
        else:
            # Compatibility with old format
            masked_areas = []
            for geometry, x0, y0, x1, y1, inside in old_masked_areas:
                area = MaskedArea(
                    geometry=geometry, x0=x0, y0=y0, x1=x1, y1=y1, inside=inside
                )
                masked_areas.append(area)
        self.param = param
        if isinstance(fn_or_data, str):
            self.set_filename(fn_or_data)
            self.load_data(lut_range)
        elif fn_or_data is not None:  # should happen only with previous API
            self.set_data(fn_or_data, lut_range=lut_range)
        self.setZ(z)
        self.param.update_item(self)
        if mask_fname is not None:
            self.set_mask_filename(mask_fname)
            self.load_mask_data()
        elif masked_areas and self.data is not None:
            self.set_masked_areas(masked_areas)
            self.apply_masked_areas()

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        ImageItem.serialize(self, writer)
        MaskedImageMixin.serialize(self, writer)

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        ImageItem.deserialize(self, reader)
        MaskedImageMixin.deserialize(self, reader)

    # ---- BaseImageItem API ----------------------------------------------------
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
        ImageItem.draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap)
        if self.data is None:
            return
        if self.is_mask_visible():
            _a, _b, bg, _cmap = self.lut
            # pylint: disable=too-many-function-args
            alpha_masked = (
                np.uint32(255 * self.param.alpha_masked + 0.5).clip(0, 255) << 24
            )
            alpha_unmasked = (
                np.uint32(255 * self.param.alpha_unmasked + 0.5).clip(0, 255) << 24
            )
            cmap = np.array(
                [
                    np.uint32(0x000000 & 0xFFFFFF) | alpha_unmasked,
                    np.uint32(0xFFFFFF & 0xFFFFFF) | alpha_masked,
                ],
                dtype=np.uint32,
            )
            lut = (1, 0, bg, cmap)
            shown_data = np.ma.getmaskarray(self.data)
            src2 = self._rescale_src_rect(src_rect)
            dst_rect = tuple([int(i) for i in dst_rect])
            dest = _scale_rect(
                shown_data, src2, self._offscreen, dst_rect, lut, (INTERP_NEAREST,)
            )
            qrect = QC.QRectF(
                QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3])
            )
            painter.drawImage(qrect, self._image, qrect)

    # ---- RawImageItem API -----------------------------------------------------
    def set_data(
        self, data: np.ndarray, lut_range: list[float, float] | None = None
    ) -> None:
        """Set image data

        Args:
            data: 2D NumPy array
            lut_range: LUT range -- tuple (levelmin, levelmax) (Default value = None)
        """
        super().set_data(data, lut_range)
        MaskedImageMixin._set_data(self, data)


class MaskedXYImageItem(XYImageItem, MaskedImageMixin):
    """XY masked image item

    Args:
        x: 1D NumPy array, must be increasing
        y: 1D NumPy array, must be increasing
        data: 2D NumPy array
        mask: 2D NumPy array
        param: image parameters
    """

    __implements__ = (
        IBasePlotItem,
        IBaseImageItem,
        IHistDataSource,
        IVoiImageItemType,
        IExportROIImageItemType,
    )

    def __init__(
        self,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        data: np.ndarray | None = None,
        mask: np.ndarray | None = None,
        param: MaskedXYImageParam | None = None,
    ) -> None:
        self.orig_data = None
        MaskedImageMixin.__init__(self, mask=mask)
        XYImageItem.__init__(self, x=x, y=y, data=data, param=param)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self) -> MaskedXYImageParam:
        """Return instance of the default MaskedXYImageParam DataSet"""
        return MaskedXYImageParam(_("Image"))

    # ---- Pickle methods -------------------------------------------------------
    def __reduce__(self) -> tuple:
        """Reduce object to pickled state"""
        fname = self.get_filename()
        if fname is None:
            fn_or_data = self.data
        else:
            fn_or_data = fname
        state = (
            self.param,
            self.get_lut_range(),
            fn_or_data,
            self.x,
            self.y,
            self.z(),
            self.get_mask_filename(),
            self.get_masked_areas(),
        )
        res = (self.__class__, (), state)
        return res

    def __setstate__(self, state: tuple) -> None:
        """Set object state from pickled state"""
        param, lut_range, fn_or_data, x, y, z, mask_fname, old_masked_areas = state
        if old_masked_areas and isinstance(old_masked_areas[0], MaskedArea):
            masked_areas = old_masked_areas
        else:
            # Compatibility with old format
            masked_areas = []
            for geometry, x0, y0, x1, y1, inside in old_masked_areas:
                area = MaskedArea(
                    geometry=geometry, x0=x0, y0=y0, x1=x1, y1=y1, inside=inside
                )
                masked_areas.append(area)
        self.param = param
        if isinstance(fn_or_data, str):
            self.set_filename(fn_or_data)
            self.load_data(lut_range)
        elif fn_or_data is not None:  # should happen only with previous API
            self.set_data(fn_or_data, lut_range=lut_range)
        self.set_xy(x, y)
        self.setZ(z)
        self.param.update_item(self)
        if mask_fname is not None:
            self.set_mask_filename(mask_fname)
            self.load_mask_data()
        elif masked_areas and self.data is not None:
            self.set_masked_areas(masked_areas)
            self.apply_masked_areas()

    def serialize(
        self,
        writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        XYImageItem.serialize(self, writer)
        MaskedImageMixin.serialize(self, writer)

    def deserialize(
        self,
        reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        XYImageItem.deserialize(self, reader)
        MaskedImageMixin.deserialize(self, reader)

    # ---- BaseImageItem API ----------------------------------------------------
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
        XYImageItem.draw_image(
            self, painter, canvasRect, src_rect, dst_rect, xMap, yMap
        )
        if self.data is None:
            return
        if self.is_mask_visible():
            _a, _b, bg, _cmap = self.lut
            # pylint: disable=too-many-function-args
            alpha_masked = (
                np.uint32(255 * self.param.alpha_masked + 0.5).clip(0, 255) << 24
            )
            alpha_unmasked = (
                np.uint32(255 * self.param.alpha_unmasked + 0.5).clip(0, 255) << 24
            )
            cmap = np.array(
                [
                    np.uint32(0x000000 & 0xFFFFFF) | alpha_unmasked,
                    np.uint32(0xFFFFFF & 0xFFFFFF) | alpha_masked,
                ],
                dtype=np.uint32,
            )
            lut = (1, 0, bg, cmap)
            shown_data = np.ma.getmaskarray(self.data)

            xytr = self.x, self.y, src_rect
            dst_rect = tuple([int(i) for i in dst_rect])
            dest = _scale_xy(
                shown_data, xytr, self._offscreen, dst_rect, lut, (INTERP_NEAREST,)
            )
            qrect = QC.QRectF(
                QC.QPointF(dest[0], dest[1]), QC.QPointF(dest[2], dest[3])
            )
            painter.drawImage(qrect, self._image, qrect)

    def set_data(
        self, data: np.ndarray, lut_range: list[float, float] | None = None
    ) -> None:
        """Set image data

        Args:
            data: 2D NumPy array
            lut_range: LUT range -- tuple (levelmin, levelmax) (Default value = None)
        """
        super().set_data(data, lut_range)
        MaskedImageMixin._set_data(self, data)
