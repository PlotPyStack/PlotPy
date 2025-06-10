# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.dataset import (
    BoolItem,
    ChoiceItem,
    ColorItem,
    DataSet,
    FloatItem,
    GetAttrProp,
    IntItem,
    StringItem,
)

from plotpy.config import _
from plotpy.styles.base import ItemParameters
from plotpy.styles.image import BaseImageParam

if TYPE_CHECKING:
    from plotpy.items import Histogram2DItem, HistogramItem


class HistogramParam(DataSet):
    n_bins = IntItem(_("Bins"), default=100, min=1, help=_("Number of bins"))
    bin_min = FloatItem(_("Min"), default=None, help=_("Minimum value"), check=False)
    bin_max = FloatItem(_("Max"), default=None, help=_("Maximum value"), check=False)
    logscale = BoolItem(_("logarithmic"), _("Y-axis scale"), default=False)

    def update_param(self, item: HistogramItem) -> None:
        """Update the histogram parameters from the plot item

        Args:
            item: Histogram item
        """
        self.n_bins = item.get_bins()
        self.bin_min, self.bin_max = item.get_bin_range()
        self.logscale = item.get_logscale()

    def update_hist(self, item: HistogramItem) -> None:
        """Update the histogram plot item from the parameters

        Args:
            item: Histogram item
        """
        if self.bin_min is None or self.bin_max is None:
            item.bin_range = None
        else:
            item.bin_range = (self.bin_min, self.bin_max)
        item.bins = self.n_bins
        item.logscale = self.logscale
        item.update_histogram()


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
        help=_("Automatically adapt color scale when panning, zooming"),
    )
    background = ColorItem(
        _("Background color"),
        default="transparent",
        help=_("Background color when no data is present"),
    )

    def update_param(self, item: Histogram2DItem) -> None:
        """Update the histogram parameters from the plot item

        Args:
            item: 2D Histogram item
        """
        super().update_param(item)
        self.logscale = item.logscale
        self.nx_bins, self.ny_bins = item.nx_bins, item.ny_bins

    def update_histogram(self, item: Histogram2DItem) -> None:
        """Update the histogram plot item from the parameters

        Args:
            item: 2D Histogram item
        """
        item.logscale = int(self.logscale)
        item.set_background_color(self.background)
        item.set_bins(self.nx_bins, self.ny_bins)
        self.update_item(item)


class Histogram2DParam_MS(Histogram2DParam):
    _multiselection = True


ItemParameters.register_multiselection(Histogram2DParam, Histogram2DParam_MS)
