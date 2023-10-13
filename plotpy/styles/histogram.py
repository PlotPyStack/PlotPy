# -*- coding: utf-8 -*-

from guidata.dataset import (
    BoolItem,
    ChoiceItem,
    ColorItem,
    DataSet,
    GetAttrProp,
    IntItem,
    StringItem,
)

from plotpy.config import _
from plotpy.styles.base import ItemParameters
from plotpy.styles.image import BaseImageParam


class HistogramParam(DataSet):
    n_bins = IntItem(_("Bins"), default=100, min=1, help=_("Number of bins"))
    logscale = BoolItem(_("logarithmic"), _("Y-axis scale"), default=False)

    def update_param(self, obj):
        """

        :param obj:
        """
        self.n_bins = obj.get_bins()
        self.logscale = obj.get_logscale()

    def update_hist(self, hist):
        """

        :param hist:
        """
        hist.set_bins(self.n_bins)
        hist.set_logscale(self.logscale)


class Histogram2DParam(BaseImageParam):
    """Histogram"""

    _multiselection = False
    label = StringItem(_("Title"), default=_("Histogram")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    nx_bins = IntItem(
        _("X-axis bins"), default=100, min=1, help=_("Number of bins along x-axis")
    )
    ny_bins = IntItem(
        _("Y-axis bins"), default=100, min=1, help=_("Number of bins along y-axis")
    )
    logscale = BoolItem(_("logarithmic"), _("Z-axis scale"), default=False)

    computation = ChoiceItem(
        _("Computation"),
        [
            (-1, _("Bin count")),
            (0, _("Maximum value")),
            (1, _("Mininum value")),
            (2, _("Sum")),
            (3, _("Product")),
            (4, _("Average")),
        ],
        default=-1,
        help=_(
            "Bin count : counts the number of points per bin,\n"
            "For max, min, sum, product, average, compute the "
            "function of a third parameter (one by default)"
        ),
    )
    auto_lut = BoolItem(
        _("Automatic LUT range"),
        default=True,
        help=_("Automatically adapt color scale " "when panning, zooming"),
    )
    background = ColorItem(
        _("Background color"),
        default="transparent",
        help=_("Background color when no data is present"),
    )

    def update_param(self, obj):
        """

        :param obj:
        """
        super().update_param(obj)
        self.logscale = obj.logscale
        self.nx_bins, self.ny_bins = obj.nx_bins, obj.ny_bins

    def update_histogram(self, histogram):
        """

        :param histogram:
        """
        histogram.logscale = int(self.logscale)
        histogram.set_background_color(self.background)
        histogram.set_bins(self.nx_bins, self.ny_bins)
        self.update_item(histogram)


class Histogram2DParam_MS(Histogram2DParam):
    _multiselection = True


ItemParameters.register_multiselection(Histogram2DParam, Histogram2DParam_MS)
