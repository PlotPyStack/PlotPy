# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
plotpy.widgets.histogram
----------------------------

"""

from guidata.dataset.dataitems import FloatItem
from guidata.dataset.datatypes import DataSet
from qtpy import QtCore as QC

from plotpy.config import CONF, _
from plotpy.core.interfaces.common import IVoiImageItemType
from plotpy.core.items.histogram import HistogramItem
from plotpy.core.items.shapes.range import XRangeSelection
from plotpy.core.plot.base import BasePlot, PlotType
from plotpy.core.plot.histogram.utils import lut_range_threshold
from plotpy.core.styles.curve import CurveParam
from plotpy.core.styles.histogram import HistogramParam


class LevelsHistogram(BasePlot):
    """Image levels histogram widget"""

    #: Signal emitted by LevelsHistogram when LUT range of some items was changed.
    #: For now, this signal is private. The public counterpart is emitted by
    #: the base plot class (see :py:attr:`.BasePlot.SIG_LUT_CHANGED`).
    SIG_VOI_CHANGED = QC.Signal()

    def __init__(self, parent=None):
        super(LevelsHistogram, self).__init__(
            parent=parent, title="", section="histogram", type=PlotType.CURVE
        )
        self.antialiased = False

        # a dict of dict : plot -> selected items -> HistogramItem
        self._tracked_items = {}
        self.param = CurveParam(_("Curve"), icon="curve.png")
        self.param.read_config(CONF, "histogram", "curve")

        self.histparam = HistogramParam(_("Histogram"), icon="histogram.png")
        self.histparam.logscale = False
        self.histparam.n_bins = 256

        self.range = XRangeSelection(0, 1)
        self.range_mono_color = self.range.shapeparam.sel_line.color
        self.range_multi_color = CONF.get("histogram", "range/multi/color", "red")

        self.add_item(self.range, z=5)
        self.SIG_RANGE_CHANGED.connect(self.range_changed)
        self.set_active_item(self.range)

        self.setMinimumHeight(80)
        self.setAxisMaxMajor(self.Y_LEFT, 5)
        self.setAxisMaxMinor(self.Y_LEFT, 0)

        if parent is None:
            self.set_axis_title("bottom", "Levels")

    def connect_plot(self, plot):
        """

        :param plot:
        :return:
        """
        if plot.type == PlotType.CURVE:
            # Connecting only to image plot widgets (allow mixing image and
            # curve widgets for the same plot manager -- e.g. in pyplot)
            return
        self.SIG_VOI_CHANGED.connect(plot.notify_colormap_changed)
        plot.SIG_ITEM_SELECTION_CHANGED.connect(self.selection_changed)
        plot.SIG_ITEM_REMOVED.connect(self.item_removed)
        plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)

    def tracked_items_gen(self):
        """ """
        for plot, items in list(self._tracked_items.items()):
            for item in list(items.items()):
                yield item  # tuple item,curve

    def __del_known_items(self, known_items, items):
        del_curves = []
        for item in list(known_items.keys()):
            if item not in items:
                curve = known_items.pop(item)
                del_curves.append(curve)
        self.del_items(del_curves)

    def selection_changed(self, plot):
        """

        :param plot:
        :return:
        """
        items = plot.get_selected_items(item_type=IVoiImageItemType)
        known_items = self._tracked_items.setdefault(plot, {})

        if items:
            self.__del_known_items(known_items, items)
            if len(items) == 1:
                # Removing any cached item for other plots
                for other_plot, _items in list(self._tracked_items.items()):
                    if other_plot is not plot:
                        if not other_plot.get_selected_items(
                            item_type=IVoiImageItemType
                        ):
                            other_known_items = self._tracked_items[other_plot]
                            self.__del_known_items(other_known_items, [])
        else:
            # if all items are deselected we keep the last known
            # selection (for one plot only)
            for other_plot, _items in list(self._tracked_items.items()):
                if other_plot.get_selected_items(item_type=IVoiImageItemType):
                    self.__del_known_items(known_items, [])
                    break

        for item in items:
            if item not in known_items:
                imin, imax = item.get_lut_range_full()
                delta = int(imax - imin)
                if delta > 0 and delta < 256:
                    self.histparam.n_bins = delta
                else:
                    self.histparam.n_bins = 256
                curve = HistogramItem(self.param, self.histparam)
                curve.set_hist_source(item)
                self.add_item(curve, z=0)
                known_items[item] = curve

        nb_selected = len(list(self.tracked_items_gen()))
        if not nb_selected:
            self.replot()
            return
        self.param.shade = 1.0 / nb_selected
        for item, curve in self.tracked_items_gen():
            self.param.update_item(curve)
            self.histparam.update_hist(curve)

        self.active_item_changed(plot)

        # Rescaling histogram plot axes for better visibility
        ymax = None
        for item in known_items:
            curve = known_items[item]
            _x, y = curve.get_data()
            ymax0 = y.mean() + 3 * y.std()
            if ymax is None or ymax0 > ymax:
                ymax = ymax0
        ymin, _ymax = self.get_axis_limits("left")
        if ymax is not None:
            self.set_axis_limits("left", ymin, ymax)
            self.replot()

    def item_removed(self, item):
        """

        :param item:
        """
        for plot, items in list(self._tracked_items.items()):
            if item in items:
                curve = items.pop(item)
                self.del_items([curve])
                self.replot()
                break

    def active_item_changed(self, plot):
        """

        :param plot:
        :return:
        """
        items = plot.get_selected_items(item_type=IVoiImageItemType)
        if not items:
            # XXX: workaround
            return

        active = plot.get_last_active_item(IVoiImageItemType)
        if active:
            active_range = active.get_lut_range()
        else:
            active_range = None

        multiple_ranges = False
        for item, curve in self.tracked_items_gen():
            if active_range != item.get_lut_range():
                multiple_ranges = True
        if active_range is not None:
            _m, _M = active_range
            self.set_range_style(multiple_ranges)
            self.range.set_range(_m, _M, dosignal=False)
        self.replot()

    def set_range_style(self, multiple_ranges):
        """

        :param multiple_ranges:
        """
        if multiple_ranges:
            self.range.shapeparam.sel_line.color = self.range_multi_color
        else:
            self.range.shapeparam.sel_line.color = self.range_mono_color
        self.range.shapeparam.update_range(self.range)

    def set_range(self, _min, _max):
        """

        :param _min:
        :param _max:
        :return:
        """
        if _min < _max:
            self.set_range_style(False)
            self.range.set_range(_min, _max)
            self.replot()
            return True
        else:
            # Range was not changed
            return False

    def range_changed(self, _rangesel, _min, _max):
        """

        :param _rangesel:
        :param _min:
        :param _max:
        """
        for item, curve in self.tracked_items_gen():
            item.set_lut_range([_min, _max])
        self.SIG_VOI_CHANGED.emit()

    def set_full_range(self):
        """Set range bounds to image min/max levels"""
        _min = _max = None
        for item, curve in self.tracked_items_gen():
            imin, imax = item.get_lut_range_full()
            if _min is None or _min > imin:
                _min = imin
            if _max is None or _max < imax:
                _max = imax
        if _min is not None:
            self.set_range(_min, _max)

    def apply_min_func(self, item, curve, min):
        """

        :param item:
        :param curve:
        :param min:
        :return:
        """
        _min, _max = item.get_lut_range()
        return min, _max

    def apply_max_func(self, item, curve, max):
        """

        :param item:
        :param curve:
        :param max:
        :return:
        """
        _min, _max = item.get_lut_range()
        return _min, max

    def reduce_range_func(self, item, curve, percent):
        """

        :param item:
        :param curve:
        :param percent:
        :return:
        """
        return lut_range_threshold(item, curve.bins, percent)

    def apply_range_function(self, func, *args, **kwargs):
        """

        :param func:
        :param args:
        :param kwargs:
        """
        item = None
        for item, curve in self.tracked_items_gen():
            _min, _max = func(item, curve, *args, **kwargs)
            item.set_lut_range([_min, _max])
        self.SIG_VOI_CHANGED.emit()
        if item is not None:
            self.active_item_changed(item.plot())

    def eliminate_outliers(self, percent):
        """
        Eliminate outliers:
        eliminate percent/2*N counts on each side of the histogram
        (where N is the total count number)
        """
        self.apply_range_function(self.reduce_range_func, percent)

    def set_min(self, _min):
        """

        :param _min:
        """
        self.apply_range_function(self.apply_min_func, _min)

    def set_max(self, _max):
        """

        :param _max:
        """
        self.apply_range_function(self.apply_max_func, _max)


class EliminateOutliersParam(DataSet):
    percent = FloatItem(
        _("Eliminate outliers") + " (%)", default=2.0, min=0.0, max=100.0 - 1e-6
    )
