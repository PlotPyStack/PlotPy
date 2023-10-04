# -*- coding: utf-8 -*-

# pylint: disable=C0103

"""
Histogram item
"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.utils import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qwt import QwtPlotCurve

from plotpy.config import _
from plotpy.interfaces.common import IBasePlotItem, IHistDataSource
from plotpy.items.curve.base import CurveItem
from plotpy.styles.curve import CurveParam
from plotpy.styles.histogram import HistogramParam

if TYPE_CHECKING:  # pragma: no cover
    from plotpy.items.image.base import BaseImageItem
    from plotpy.styles.base import ItemParameters


class HistDataSource:
    """An objects that provides an Histogram data source interface
    to a simple numpy array of data
    """

    __implements__ = (IHistDataSource,)

    def __init__(self, data: np.ndarray) -> None:
        self.data = data

    def get_histogram(self, nbins: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Return a tuple (hist, bins) where hist is a list of histogram values

        Args:
            nbins (int): number of bins

        Returns:
            tuple: (hist, bins)
        """
        return np.histogram(self.data, nbins)


assert_interfaces_valid(HistDataSource)


class HistogramItem(CurveItem):
    """Histogram plot item

    Args:
        curveparam: Curve parameters
        histparam: Histogram parameters
    """

    __implements__ = (IBasePlotItem,)

    def __init__(
        self,
        curveparam: CurveParam | None = None,
        histparam: HistogramParam | None = None,
        keep_weakref: bool = False,
    ) -> None:
        self.hist_count = None
        self.hist_bins = None
        self.bins = None
        self.old_bins = None
        self.source: BaseImageItem | None = None
        self.logscale: bool | None = None
        self.old_logscale = None
        self.keep_weakref = keep_weakref
        if curveparam is None:
            curveparam = CurveParam(_("Curve"), icon="curve.png")
            curveparam.curvestyle = "Steps"
        if histparam is None:
            self.histparam = HistogramParam(title=_("Histogram"), icon="histogram.png")
        else:
            self.histparam = histparam
        CurveItem.__init__(self, curveparam)
        self.setCurveAttribute(QwtPlotCurve.Inverted)
        self.setIcon(get_icon("histogram.png"))

    def set_hist_source(self, src: BaseImageItem) -> None:
        """Set histogram source

        Args:
            src: Object with method `get_histogram`, e.g. objects derived from
             :py:class:`.ImageItem`
        """
        if self.keep_weakref:
            self.source = weakref.ref(src)
        else:
            self.source = src
        self.update_histogram()

    def get_hist_source(self) -> BaseImageItem | None:
        """Return histogram source

        Returns:
            object: Object with method `get_histogram`, e.g. objects derived from
             :py:class:`.ImageItem`
        """
        if self.source is not None:
            if self.keep_weakref:
                return self.source()
            return self.source

    def set_hist_data(self, data: np.ndarray) -> None:
        """Set histogram data

        Args:
            data: numpy array
        """
        self.set_hist_source(HistDataSource(data))

    def set_logscale(self, state: bool) -> None:
        """Sets whether we use a logarithm or linear scale
        for the histogram counts

        Args:
            state: True for logarithmic scale
        """
        self.logscale = state
        self.update_histogram()

    def get_logscale(self) -> bool | None:
        """Returns the status of the scale

        Returns:
            bool: True for logarithmic scale
        """
        return self.logscale

    def set_bins(self, n_bins: int) -> None:
        """Sets the number of bins

        Args:
            n_bins: number of bins
        """
        self.bins = n_bins
        self.update_histogram()

    def get_bins(self) -> int | None:
        """Returns the number of bins

        Returns:
            int: number of bins
        """
        return self.bins

    def compute_histogram(self) -> tuple[np.ndarray, np.ndarray]:
        """Compute histogram data

        Returns:
            tuple: (hist, bins)
        """
        return self.get_hist_source().get_histogram(self.bins)

    def update_histogram(self) -> None:
        """Update histogram data"""
        if self.get_hist_source() is None:
            return
        hist, bin_edges = self.compute_histogram()
        hist = np.concatenate((hist, [0]))
        if self.logscale:
            hist = np.log(hist + 1)

        self.set_data(bin_edges, hist)
        # Autoscale only if logscale/bins have changed
        if self.bins != self.old_bins or self.logscale != self.old_logscale:
            if self.plot():
                self.plot().do_autoscale()
        self.old_bins = self.bins
        self.old_logscale = self.logscale

        plot = self.plot()
        if plot is not None:
            plot.do_autoscale(replot=True)

    def update_params(self):
        """Update histogram parameters"""
        self.histparam.update_hist(self)
        CurveItem.update_params(self)

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """
        CurveItem.get_item_parameters(self, itemparams)
        itemparams.add("HistogramParam", self, self.histparam)

    def set_item_parameters(self, itemparams):
        """
        :param itemparams:
        """
        update_dataset(
            self.histparam, itemparams.get("HistogramParam"), visible_only=True
        )
        self.histparam.update_hist(self)
        CurveItem.set_item_parameters(self, itemparams)


assert_interfaces_valid(HistogramItem)
