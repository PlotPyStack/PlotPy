# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import numpy as np
from guidata.dataset import (
    BeginGroup,
    BoolItem,
    ChoiceItem,
    ColorItem,
    DataSet,
    EndGroup,
    FloatItem,
    GetAttrProp,
    ImageChoiceItem,
    IntItem,
    StringItem,
)
from qtpy import QtGui as QG

from plotpy._scaler import INTERP_AA, INTERP_LINEAR, INTERP_NEAREST
from plotpy.config import _
from plotpy.constants import LUTAlpha
from plotpy.mathutils.colormap import (
    ALL_COLORMAPS,
    LARGE_ICON_HEIGHT,
    LARGE_ICON_ORIENTATION,
    LARGE_ICON_WIDTH,
    build_icon_from_cmap_name,
)
from plotpy.styles.base import ItemParameters

if TYPE_CHECKING:
    from guidata.dataset import DataSet

    from plotpy.items import (
        BaseImageItem,
        ImageFilterItem,
        ImageItem,
        MaskedImageItem,
        MaskedXYImageItem,
        RawImageItem,
        RGBImageItem,
        TrImageItem,
    )
    from plotpy.plot import BasePlot


def _create_choices(
    dataset: DataSet, item: ImageChoiceItem, value: Any
) -> list[tuple[str, str, Callable[[str], QG.QIcon]]]:
    """Create the list of choices for the colormap item."""
    choices: list[tuple[str, str, Callable[[str], QG.QIcon]]] = []
    for cmap in ALL_COLORMAPS.values():
        choices.append(
            (
                cmap.name,
                cmap.name,
                lambda name: build_icon_from_cmap_name(
                    name,
                    LARGE_ICON_WIDTH,
                    LARGE_ICON_HEIGHT,
                    LARGE_ICON_ORIENTATION,
                    1,
                ),
            )
        )
    return choices


# TODO: Use an "enum" like LUTAlpha for the interpolation mode as well
# (and eventually for other parameters)


class BaseImageParam(DataSet):
    """Base class for image parameters."""

    _multiselection = False
    label = StringItem(_("Image title"), default=_("Image")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    alpha_function = ChoiceItem(
        _("Alpha function"),
        LUTAlpha.get_choices(),
        default=LUTAlpha.NONE.value,
        help=LUTAlpha.get_help(),
    )
    alpha = FloatItem(
        _("Global alpha"), default=1.0, min=0, max=1, help=_("Global alpha value")
    )
    _hide_colormap = False
    colormap = (
        ImageChoiceItem(_("Colormap"), _create_choices, default="jet")
        .set_prop("display", hide=GetAttrProp("_hide_colormap"))
        .set_prop("display", size=(LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT))
    )
    invert_colormap = BoolItem(_("Invert colormap"), default=False)

    keep_lut_range = BoolItem(
        _("Lock LUT range when updating data"),
        default=False,
        help=_(
            "If enabled, the LUT range is not updated when the image data changes."
            "<br>This allows to keep the same color scale for different successive "
            "images. <br><br>"
            "<u>Note:</u> It has no effect when a new image is added to the plot."
        ),
    )

    interpolation = ChoiceItem(
        _("Interpolation"),
        [
            (0, _("None (nearest pixel)")),
            (1, _("Linear interpolation")),
            (2, _("2x2 antialiasing filter")),
            (3, _("3x3 antialiasing filter")),
            (5, _("5x5 antialiasing filter")),
        ],
        default=0,
        help=_("Image interpolation type"),
    )

    _formats = BeginGroup(_("Statistics string formatting"))
    xformat = StringItem(_("X-Axis"), default=r"%.1f")
    yformat = StringItem(_("Y-Axis"), default=r"%.1f")
    zformat = StringItem(_("Z-Axis"), default=r"%.1f")
    _end_formats = EndGroup(_("Statistics string formatting"))

    def get_units(self) -> tuple[str, str, str]:
        """Get the units for the x, y and z axes.

        Returns:
            The units for the x, y and z axes.
        """
        try:
            xunit = self.xformat.split()[1]
        except IndexError:
            xunit = ""
        try:
            yunit = self.yformat.split()[1]
        except IndexError:
            yunit = ""
        try:
            zunit = self.zformat.split()[1]
        except IndexError:
            zunit = ""
        return xunit, yunit, zunit

    def update_param(self, item: BaseImageItem) -> None:
        """Update the parameters from the given image item.

        Args:
            item: The image item to update the parameters from.
        """
        self.label = str(item.title().text())
        cmap = item.get_color_map()
        if cmap is not None:
            self.colormap = cmap.name
            self.invert_colormap = cmap.invert
        interpolation = item.get_interpolation()
        mode = interpolation[0]

        if mode == INTERP_NEAREST:
            self.interpolation = 0
        elif mode == INTERP_LINEAR:
            self.interpolation = 1
        else:
            size = interpolation[1].shape[0]
            self.interpolation = size

    def update_item(self, item: BaseImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        if isinstance(self.alpha_function, LUTAlpha):
            self.alpha_function = self.alpha_function.value
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.setTitle(self.label)
        item.set_color_map(self.colormap, self.invert_colormap)
        size = self.interpolation

        if size == 0:
            mode = INTERP_NEAREST
        elif size == 1:
            mode = INTERP_LINEAR
        else:
            mode = INTERP_AA
        item.set_interpolation(mode, size)
        if plot is not None:
            plot.blockSignals(False)


class QuadGridParam(DataSet):
    """Parameters for the grid of a quad item."""

    _multiselection = False
    label = StringItem(_("Image title"), default=_("Image")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    alpha_function = ChoiceItem(
        _("Alpha function"),
        LUTAlpha.get_choices(),
        default=LUTAlpha.NONE.value,
        help=LUTAlpha.get_help(),
    )
    alpha = FloatItem(
        _("Global alpha"), default=1.0, min=0, max=1, help=_("Global alpha value")
    )
    _hide_colormap = False
    colormap = ImageChoiceItem(_("Colormap"), _create_choices, default="jet").set_prop(
        "display", hide=GetAttrProp("_hide_colormap")
    )
    invert_colormap = BoolItem(_("Invert colormap"), default=False)

    interpolation = ChoiceItem(
        _("Interpolation"),
        [(0, _("Quadrangle interpolation")), (1, _("Flat"))],
        default=0,
        help=_(
            "Image interpolation type, Flat mode use fixed u,v interpolation parameters"
        ),
    )
    uflat = FloatItem(
        _("Fixed U interpolation parameter"),
        default=0.5,
        min=0.0,
        max=1.0,
        help=_("For flat mode only"),
    )
    vflat = FloatItem(
        _("Fixed V interpolation parameter"),
        default=0.5,
        min=0.0,
        max=1.0,
        help=_("For flat mode only"),
    )
    grid = BoolItem(_("Show grid"), default=False)
    gridcolor = ColorItem(_("Grid lines color"), default="black")

    def update_param(self, item: BaseImageItem) -> None:
        """Update the parameters from the given image item.

        Args:
            item: The image item to update the parameters from.
        """
        self.label = str(item.title().text())
        cmap = item.get_color_map()
        if cmap is not None:
            self.colormap = cmap.name
            self.invert_colormap = cmap.invert
        interp, uflat, vflat = item.interpolate
        self.interpolation = interp
        self.uflat = uflat
        self.vflat = vflat
        self.grid = item.grid

    def update_item(self, item: BaseImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        if isinstance(self.alpha_function, LUTAlpha):
            self.alpha_function = self.alpha_function.value
        plot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.setTitle(self.label)
        item.set_color_map(self.colormap, self.invert_colormap)
        item.interpolate = (self.interpolation, self.uflat, self.vflat)
        item.grid = self.grid
        if plot is not None:
            plot.blockSignals(False)


class RawImageParam(BaseImageParam):
    """Parameters for a raw image."""

    _hide_background = False
    background = ColorItem(_("Background color"), default="#000000").set_prop(
        "display", hide=GetAttrProp("_hide_background")
    )

    def update_param(self, item: RawImageItem) -> None:
        """Update the parameters from the given image item.

        Args:
            item: The image item from which to update the parameters.
        """
        super().update_param(item)
        self.background = str(QG.QColor(item.bg_qcolor).name())

    def update_item(self, item: RawImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        super().update_item(item)
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.set_background_color(self.background)
        if plot is not None:
            plot.blockSignals(False)


class RawImageParam_MS(RawImageParam):
    """Parameters for a raw image (multiselection)."""

    _multiselection = True


ItemParameters.register_multiselection(RawImageParam, RawImageParam_MS)


class XYImageParam(RawImageParam):
    """Parameters for an XY image."""

    pass


class XYImageParam_MS(XYImageParam):
    """Parameters for an XY image (multiselection)."""

    _multiselection = True


ItemParameters.register_multiselection(XYImageParam, XYImageParam_MS)


class ImageParam(RawImageParam):
    """Parameters for an image."""

    lock_position = BoolItem(
        _("Lock position"),
        _("Position"),
        default=True,
        help=_("Locked images are not movable with the mouse"),
    )
    _xdata = BeginGroup(_("Image placement along X-axis"))
    xmin = FloatItem(_("x|min"), default=None, check=False)
    xmax = FloatItem(_("x|max"), default=None, check=False)
    _end_xdata = EndGroup(_("Image placement along X-axis"))
    _ydata = BeginGroup(_("Image placement along Y-axis"))
    ymin = FloatItem(_("y|min"), default=None, check=False)
    ymax = FloatItem(_("y|max"), default=None, check=False)
    _end_ydata = EndGroup(_("Image placement along Y-axis"))

    def update_param(self, item: ImageItem) -> None:
        """Update the parameters from the given image item.

        Args:
            item: The image item from which to update the parameters.
        """
        super().update_param(item)
        self.xmin = item.xmin
        self.ymin = item.ymin
        self.xmax = item.xmax
        self.ymax = item.ymax

    def update_item(self, item: ImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        super().update_item(item)
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.xmin = self.xmin
        item.xmax = self.xmax
        item.ymin = self.ymin
        item.ymax = self.ymax
        item.update_bounds()
        item.update_border()
        if plot is not None:
            plot.blockSignals(False)


class ImageParam_MS(ImageParam):
    """Parameters for an image (multiselection)."""

    _multiselection = True


ItemParameters.register_multiselection(ImageParam, ImageParam_MS)


class RGBImageParam(ImageParam):
    """Parameters for an RGB image."""

    _hide_background = True
    _hide_colormap = True

    def update_item(self, item: RGBImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        super().update_item(item)
        plot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.recompute_alpha_channel()
        if plot is not None:
            plot.blockSignals(False)


class RGBImageParam_MS(RGBImageParam):
    """Parameters for an RGB image (multiselection)."""

    _multiselection = True


ItemParameters.register_multiselection(RGBImageParam, RGBImageParam_MS)


class MaskedImageParamMixin(DataSet):
    """Mixin for masked image parameters."""

    g_mask = BeginGroup(_("Mask"))
    filling_value = FloatItem(_("Filling value"))
    show_mask = BoolItem(_("Show image mask"), default=False)
    alpha_masked = FloatItem(_("Masked area alpha"), default=0.7, min=0, max=1)
    alpha_unmasked = FloatItem(_("Unmasked area alpha"), default=0.0, min=0, max=1)
    _g_mask = EndGroup(_("Mask"))

    def _update_item(self, item: MaskedImageItem) -> None:
        """Update the given masked image item from the parameters.

        Args:
            item: The masked image item to update.
        """
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.update_mask()
        if plot is not None:
            plot.blockSignals(False)


class MaskedImageParam(ImageParam, MaskedImageParamMixin):
    """Parameters for a masked image."""

    def update_item(self, item: MaskedImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        super().update_item(item)
        self._update_item(item)


class MaskedXYImageParam(XYImageParam, MaskedImageParamMixin):
    """Parameters for a masked XY image."""

    def update_item(self, item: MaskedXYImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        super().update_item(item)
        self._update_item(item)


class MaskedImageParam_MS(MaskedImageParam):
    """Parameters for a masked image (multiselection)."""

    _multiselection = True


class MaskedXYImageParam_MS(MaskedXYImageParam):
    """Parameters for a masked XY image (multiselection)."""

    _multiselection = True


ItemParameters.register_multiselection(MaskedImageParam, MaskedImageParam_MS)
ItemParameters.register_multiselection(MaskedXYImageParam, MaskedXYImageParam_MS)


class ImageFilterParam(BaseImageParam):
    """Parameters for an image filter."""

    label = StringItem(_("Title"), default=_("Filter"))
    g1 = BeginGroup(_("Bounds"))
    xmin = FloatItem(_("x|min"))
    xmax = FloatItem(_("x|max"))
    ymin = FloatItem(_("y|min"))
    ymax = FloatItem(_("y|max"))
    _g1 = EndGroup("sub-group")
    use_source_cmap = BoolItem(
        _("Use image colormap and level"), _("Color map"), default=True
    )

    def update_param(self, item: ImageFilterItem) -> None:
        """Update the parameters from the given image filter item.

        Args:
            item: The image filter item from which to update the parameters.
        """
        self.xmin, self.ymin, self.xmax, self.ymax = item.border_rect.get_rect()
        self.use_source_cmap = item.use_source_cmap
        super().update_param(item)

    def update_imagefilter(self, item: ImageFilterItem) -> None:
        """Update the given image filter item from the parameters.

        Args:
            item: The image filter item to update.
        """
        m, M = item.get_lut_range()
        set_range = False
        if not self.use_source_cmap and item.use_source_cmap:
            set_range = True
        item.use_source_cmap = self.use_source_cmap
        if set_range:
            item.set_lut_range([m, M])
        self.update_item(item)
        item.border_rect.set_rect(self.xmin, self.ymin, self.xmax, self.ymax)


class TrImageParam(RawImageParam):
    """Parameters for a transformed image."""

    lock_position = BoolItem(
        _("Lock position"),
        _("Position"),
        default=False,
        help=_("Locked images are not movable with the mouse"),
    )

    _crop = BeginGroup(_("Crop")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    crop_left = IntItem(_("Left"), default=0)
    crop_right = IntItem(_("Right"), default=0)
    crop_top = IntItem(_("Top"), default=0)
    crop_bottom = IntItem(_("Bottom"), default=0)
    _end_crop = EndGroup(_("Cropping")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    _ps = BeginGroup(_("Pixel size")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    dx = FloatItem(_("Width (dx)"), default=1.0)
    dy = FloatItem(_("Height (dy)"), default=1.0)
    _end_ps = EndGroup(_("Pixel size")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    _pos = BeginGroup(_("Translate, rotate and flip"))
    pos_x0 = FloatItem(_("x<sub>CENTER</sub>"), default=0.0).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    hflip = BoolItem(_("Flip horizontally"), default=False).set_prop("display", col=1)
    pos_y0 = FloatItem(_("y<sub>CENTER</sub>"), default=0.0).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    vflip = BoolItem(_("Flip vertically"), default=False).set_prop("display", col=1)
    pos_angle = FloatItem(_("θ (°)"), default=0.0).set_prop("display", col=0)
    _end_pos = EndGroup(_("Translate, rotate and flip"))

    def update_param(self, item: TrImageItem) -> None:
        """Update the parameters from the given image item.

        Args:
            item: The image item from which to update the parameters.
        """
        super().update_param(item)
        # we don't get crop info from the image because
        # its not easy to extract from the transform
        # and TrImageItem keeps it's crop information
        # directly in this DataSet

    def update_item(self, item: TrImageItem) -> None:
        """Update the given image item from the parameters.

        Args:
            item: The image item to update.
        """
        RawImageParam.update_item(self, item)
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.set_transform(*self.get_transform())
        if plot is not None:
            plot.blockSignals(False)

    def get_transform(self) -> tuple[float, float, float, float, float, bool, bool]:
        """Get the transformation parameters.

        Returns:
            The transformation parameters: x0, y0, angle, dx, dy, hflip, vflip.
        """
        return (
            self.pos_x0,
            self.pos_y0,
            self.pos_angle * np.pi / 180,
            self.dx,
            self.dy,
            self.hflip,
            self.vflip,
        )

    def set_transform(
        self,
        x0: float,
        y0: float,
        angle: float,
        dx: float = 1.0,
        dy: float = 1.0,
        hflip: bool = False,
        vflip: bool = False,
    ) -> None:
        """Set the transformation parameters.

        Args:
            x0: The x-coordinate of the center of the image.
            y0: The y-coordinate of the center of the image.
            angle: The rotation angle in degrees.
            dx: The width of the image.
            dy: The height of the image.
            hflip: Flip the image horizontally.
            vflip: Flip the image vertically.
        """
        self.pos_x0 = x0
        self.pos_y0 = y0
        self.pos_angle = angle * 180 / np.pi
        self.dx = dx
        self.dy = dy
        self.hflip = hflip
        self.vflip = vflip

    def set_crop(self, left: int, top: int, right: int, bottom: int) -> None:
        """Set the crop parameters.

        Args:
            left: The left crop.
            top: The top crop.
            right: The right crop.
            bottom: The bottom crop.
        """
        self.crop_left = left
        self.crop_right = right
        self.crop_top = top
        self.crop_bottom = bottom

    def get_crop(self) -> tuple[int, int, int, int]:
        """Get the crop parameters.

        Returns:
            The crop parameters: left, top, right, bottom.
        """
        return (self.crop_left, self.crop_top, self.crop_right, self.crop_bottom)


class TrImageParam_MS(TrImageParam):
    """Parameters for a transformed image (multiselection)."""

    _multiselection = True


ItemParameters.register_multiselection(TrImageParam, TrImageParam_MS)
