# -*- coding: utf-8 -*-

# pylint: disable=C0103

"""

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

if TYPE_CHECKING:
    from plotpy.styles.base import ItemParameters


class HistDataSource:
    """An objects that provides an Histogram data source interface
    to a simple numpy array of data
    """

    __implements__ = (IHistDataSource,)

    def __init__(self, data):
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
    """A Qwt item representing histogram data"""

    __implements__ = (IBasePlotItem,)

    def __init__(self, curveparam=None, histparam=None):
        self.hist_count = None
        self.hist_bins = None
        self.bins = None
        self.old_bins = None
        self.source = None
        self.logscale = None
        self.old_logscale = None
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

    def set_hist_source(self, src):
        """Set histogram source

        Args:
            src (object): Object with method `get_histogram`, e.g. objects derived from
             :py:class:`.ImageItem`
        """
        self.source = weakref.ref(src)
        self.update_histogram()

    def get_hist_source(self):
        """Return histogram source

        Returns:
            object: Object with method `get_histogram`, e.g. objects derived from
             :py:class:`.ImageItem`
        """
        if self.source is not None:
            return self.source()

    def set_hist_data(self, data):
        """Set histogram data"""
        self.set_hist_source(HistDataSource(data))

    def set_logscale(self, state):
        """Sets whether we use a logarithm or linear scale
        for the histogram counts"""
        self.logscale = state
        self.update_histogram()

    def get_logscale(self):
        """Returns the status of the scale"""
        return self.logscale

    def set_bins(self, n_bins):
        """
        :param n_bins:
        """
        self.bins = n_bins
        self.update_histogram()

    def get_bins(self):
        """
        :return:
        """
        return self.bins

    def compute_histogram(self):
        """
        :return:
        """
        return self.get_hist_source().get_histogram(self.bins)

    def update_histogram(self):
        """
        :return:
        """
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
        """ """
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
