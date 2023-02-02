# -*- coding: utf-8 -*-
import numpy as np
from guidata.dataset.dataitems import (
    BoolItem,
    ChoiceItem,
    ColorItem,
    FloatItem,
    ImageChoiceItem,
    IntItem,
    StringItem,
)
from guidata.dataset.datatypes import BeginGroup, DataSet, EndGroup, GetAttrProp
from qtpy import QtGui as QG

from plotpy._scaler import INTERP_AA, INTERP_LINEAR, INTERP_NEAREST
from plotpy.config import _
from plotpy.widgets.colormap import build_icon_from_cmap_name, get_colormap_list
from plotpy.widgets.styles.base import ItemParameters


def _create_choices():
    choices = []
    for cmap_name in get_colormap_list():
        choices.append((cmap_name, cmap_name, build_icon_from_cmap_name))
    return choices


class BaseImageParam(DataSet):
    _multiselection = False
    label = StringItem(_("Image title"), default=_("Image")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    alpha_mask = BoolItem(
        _("Use image level as alpha"), _("Alpha channel"), default=False
    )
    alpha = FloatItem(
        _("Global alpha"), default=1.0, min=0, max=1, help=_("Global alpha value")
    )
    _hide_colormap = False
    colormap = ImageChoiceItem(
        _("Colormap"), _create_choices(), default="jet"
    ).set_prop("display", hide=GetAttrProp("_hide_colormap"))

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

    def update_param(self, image):
        """

        :param image:
        """
        self.label = str(image.title().text())
        self.colormap = image.get_color_map_name()
        interpolation = image.get_interpolation()
        mode = interpolation[0]

        if mode == INTERP_NEAREST:
            self.interpolation = 0
        elif mode == INTERP_LINEAR:
            self.interpolation = 1
        else:
            size = interpolation[1].shape[0]
            self.interpolation = size

    def update_item(self, image):
        """

        :param image:
        """
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.setTitle(self.label)
        image.set_color_map(self.colormap)
        size = self.interpolation

        if size == 0:
            mode = INTERP_NEAREST
        elif size == 1:
            mode = INTERP_LINEAR
        else:
            mode = INTERP_AA
        image.set_interpolation(mode, size)
        if plot is not None:
            plot.blockSignals(False)


class TransformParamMixin(DataSet):

    lock_position = BoolItem(
        _("Lock position"),
        _("Position"),
        default=True,
        help=_("Locked images are not movable with the mouse"),
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

    def _update_transform(self, image):
        """

        :param image:
        """
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        try:
            image.set_transform(*self.get_transform())
        except Exception:
            pass
        if plot is not None:
            plot.blockSignals(False)

    def get_transform(self):
        """
        Return the transformation parameters

        :return: tuple (x0, y0, angle, dx, dy, hflip, yflip)
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

    def set_transform(self, x0, y0, angle, dx=1.0, dy=1.0, hflip=False, vflip=False):
        """
        Set the transformation

        :param x0: X translation
        :param y0: Y translation
        :param angle: rotation angle in radians
        :param dx: X-scaling factor
        :param dy: Y-scaling factor
        :param hflip: True if image if flip horizontally
        :param vflip: True if image is flip vertically
        """
        self.pos_x0 = x0
        self.pos_y0 = y0
        self.pos_angle = angle * 180 / np.pi
        self.dx = dx
        self.dy = dy
        self.hflip = hflip
        self.vflip = vflip


class ImageParamMixin(DataSet):
    """Mixin allowing to use all not trimage as previously in guidata/guiqwt
    without having to modify existing code"""

    dx = 1.0
    dy = 1.0
    pos_x0 = 0.0
    hflip = False
    pos_y0 = 0.0
    vflip = False
    pos_angle = 0.0

    def _update_transform(self, image):
        """

        :param image:
        """
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        try:
            image.set_transform(*self.get_transform())
        except Exception:
            pass
        if plot is not None:
            plot.blockSignals(False)

    def get_transform(self):
        """
        Return the transformation parameters

        :return: tuple (x0, y0, angle, dx, dy, hflip, yflip)
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

    def set_transform(self, x0, y0, angle, dx=1.0, dy=1.0, hflip=False, vflip=False):
        """
        Set the transformation

        :param x0: X translation
        :param y0: Y translation
        :param angle: rotation angle in radians
        :param dx: X-scaling factor
        :param dy: Y-scaling factor
        :param hflip: True if image if flip horizontally
        :param vflip: True if image is flip vertically
        """
        self.pos_x0 = x0
        self.pos_y0 = y0
        self.pos_angle = angle * 180 / np.pi
        self.dx = dx
        self.dy = dy
        self.hflip = hflip
        self.vflip = vflip


class QuadGridParam(ImageParamMixin):
    _multiselection = False
    label = StringItem(_("Image title"), default=_("Image")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    alpha_mask = BoolItem(
        _("Use image level as alpha"), _("Alpha channel"), default=False
    )
    alpha = FloatItem(
        _("Global alpha"), default=1.0, min=0, max=1, help=_("Global alpha value")
    )
    _hide_colormap = False
    colormap = ImageChoiceItem(
        _("Colormap"), _create_choices(), default="jet"
    ).set_prop("display", hide=GetAttrProp("_hide_colormap"))

    interpolation = ChoiceItem(
        _("Interpolation"),
        [(0, _("Quadrangle interpolation")), (1, _("Flat"))],
        default=0,
        help=_(
            "Image interpolation type, "
            "Flat mode use fixed u,v "
            "interpolation parameters"
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

    def update_param(self, image):
        """

        :param image:
        """
        self.label = str(image.title().text())
        self.colormap = image.get_color_map_name()
        interp, uflat, vflat = image.interpolate
        self.interpolation = interp
        self.uflat = uflat
        self.vflat = vflat
        self.grid = image.grid

    def update_item(self, image):
        """

        :param image:
        """
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.setTitle(self.label)
        image.set_color_map(self.colormap)
        image.interpolate = (self.interpolation, self.uflat, self.vflat)
        image.grid = self.grid
        # TODO : gridcolor
        if plot is not None:
            plot.blockSignals(False)

        self._update_transform(image)


class RawImageParam(BaseImageParam):
    _hide_background = False
    background = ColorItem(_("Background color"), default="#000000").set_prop(
        "display", hide=GetAttrProp("_hide_background")
    )

    def update_param(self, image):
        """

        :param image:
        """
        super(RawImageParam, self).update_param(image)
        self.background = str(QG.QColor(image.bg_qcolor).name())

    def update_item(self, image):
        """

        :param image:
        """
        super(RawImageParam, self).update_item(image)
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.set_background_color(self.background)
        if plot is not None:
            plot.blockSignals(False)


class RawImageParam_MS(RawImageParam):
    _multiselection = True


ItemParameters.register_multiselection(RawImageParam, RawImageParam_MS)


class XYImageParam(RawImageParam, ImageParamMixin):
    def update_item(self, image):
        """

        :param image:
        """
        super().update_item(image)
        self._update_transform(image)


class XYImageParam_MS(XYImageParam):
    _multiselection = True


ItemParameters.register_multiselection(XYImageParam, XYImageParam_MS)


class ImageParam(RawImageParam):
    lock_position = BoolItem(
        _("Lock position"),
        _("Position"),
        default=True,
        help=_("Locked images are not movable with the mouse"),
    )
    _xdata = BeginGroup(_("Image placement along X-axis"))
    xmin = FloatItem(_("x|min"), default=None)
    xmax = FloatItem(_("x|max"), default=None)
    _end_xdata = EndGroup(_("Image placement along X-axis"))
    _ydata = BeginGroup(_("Image placement along Y-axis"))
    ymin = FloatItem(_("y|min"), default=None)
    ymax = FloatItem(_("y|max"), default=None)
    _end_ydata = EndGroup(_("Image placement along Y-axis"))

    def update_param(self, image):
        """

        :param image:
        """
        super(ImageParam, self).update_param(image)
        self.xmin = image.xmin
        if self.xmin is None:
            self.xmin = 0.0
        self.ymin = image.ymin
        if self.ymin is None:
            self.ymin = 0.0
        if image.is_empty():
            shape = (0, 0)
        else:
            shape = image.data.shape
        self.xmax = image.xmax
        if self.xmax is None:
            self.xmax = float(shape[1])
        self.ymax = image.ymax
        if self.ymax is None:
            self.ymax = float(shape[0])

    def update_item(self, image):
        """

        :param image:
        """
        super(ImageParam, self).update_item(image)
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.xmin = self.xmin
        image.xmax = self.xmax
        image.ymin = self.ymin
        image.ymax = self.ymax
        image.update_bounds()
        image.update_border()
        if plot is not None:
            plot.blockSignals(False)


class ImageParam_MS(ImageParam):
    _multiselection = True


ItemParameters.register_multiselection(ImageParam, ImageParam_MS)


class RGBImageParam(ImageParam):
    _hide_background = True
    _hide_colormap = True

    def update_item(self, image):
        """

        :param image:
        """
        super(RGBImageParam, self).update_item(image)
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.recompute_alpha_channel()
        if plot is not None:
            plot.blockSignals(False)


class RGBImageParam_MS(RGBImageParam):
    _multiselection = True


ItemParameters.register_multiselection(RGBImageParam, RGBImageParam_MS)


class MaskedImageParamMixin(DataSet):

    g_mask = BeginGroup(_("Mask"))
    filling_value = FloatItem(_("Filling value"))
    show_mask = BoolItem(_("Show image mask"), default=False)
    alpha_masked = FloatItem(_("Masked area alpha"), default=0.7, min=0, max=1)
    alpha_unmasked = FloatItem(_("Unmasked area alpha"), default=0.0, min=0, max=1)
    _g_mask = EndGroup(_("Mask"))

    def _update_item(self, image):
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.update_mask()
        if plot is not None:
            plot.blockSignals(False)


class MaskedImageParam(ImageParam, MaskedImageParamMixin):
    def update_item(self, image):
        """

        :param image:
        """
        super(MaskedImageParam, self).update_item(image)
        self._update_item(image)


class MaskedXYImageParam(XYImageParam, MaskedImageParamMixin):
    def update_item(self, image):
        """

        :param image:
        """
        super(MaskedXYImageParam, self).update_item(image)
        self._update_item(image)


class MaskedImageParam_MS(MaskedImageParam):
    _multiselection = True


class MaskedXYImageParam_MS(MaskedXYImageParam):
    _multiselection = True


ItemParameters.register_multiselection(MaskedImageParam, MaskedImageParam_MS)
ItemParameters.register_multiselection(MaskedXYImageParam, MaskedXYImageParam_MS)


class ImageFilterParam(BaseImageParam):
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

    def update_param(self, obj):
        """

        :param obj:
        """
        self.xmin, self.ymin, self.xmax, self.ymax = obj.border_rect.get_rect()
        self.use_source_cmap = obj.use_source_cmap
        super(ImageFilterParam, self).update_param(obj)

    def update_imagefilter(self, imagefilter):
        """

        :param imagefilter:
        """
        m, M = imagefilter.get_lut_range()
        set_range = False
        if not self.use_source_cmap and imagefilter.use_source_cmap:
            set_range = True
        imagefilter.use_source_cmap = self.use_source_cmap
        if set_range:
            imagefilter.set_lut_range([m, M])
        self.update_item(imagefilter)
        imagefilter.border_rect.set_rect(self.xmin, self.ymin, self.xmax, self.ymax)


class TrImageParam(RawImageParam):
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

    def update_param(self, image):
        """

        :param image:
        """
        super(TrImageParam, self).update_param(image)
        # we don't get crop info from the image because
        # its not easy to extract from the transform
        # and TrImageItem keeps it's crop information
        # directly in this DataSet

    def update_item(self, image):
        """

        :param image:
        """
        RawImageParam.update_item(self, image)
        plot = image.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        image.set_transform(*self.get_transform())
        if plot is not None:
            plot.blockSignals(False)

    def get_transform(self):
        """

        :return:
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

    def set_transform(self, x0, y0, angle, dx=1.0, dy=1.0, hflip=False, vflip=False):
        """

        :param x0:
        :param y0:
        :param angle:
        :param dx:
        :param dy:
        :param hflip:
        :param vflip:
        """
        self.pos_x0 = x0
        self.pos_y0 = y0
        self.pos_angle = angle * 180 / np.pi
        self.dx = dx
        self.dy = dy
        self.hflip = hflip
        self.vflip = vflip

    def set_crop(self, left, top, right, bottom):
        """

        :param left:
        :param top:
        :param right:
        :param bottom:
        """
        self.crop_left = left
        self.crop_right = right
        self.crop_top = top
        self.crop_bottom = bottom

    def get_crop(self):
        """

        :return:
        """
        return (self.crop_left, self.crop_top, self.crop_right, self.crop_bottom)


class TrImageParam_MS(TrImageParam):
    _multiselection = True


ItemParameters.register_multiselection(TrImageParam, TrImageParam_MS)
