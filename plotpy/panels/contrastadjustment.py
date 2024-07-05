# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Contrast adjustment
^^^^^^^^^^^^^^^^^^^

The `contrast adjustment` panel is a widget which displays the image levels
histogram and allows to manipulate it in order to adjust the image contrast.

.. autoclass:: ContrastAdjustment
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon, get_image_layout
from guidata.dataset import DataSet, FloatItem
from guidata.qthelpers import add_actions, create_action
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import CONF, IS_DARK, _
from plotpy.constants import ID_CONTRAST, PlotType
from plotpy.interfaces import IPanel, IVoiImageItemType
from plotpy.items import HistogramItem, XRangeSelection
from plotpy.lutrange import lut_range_threshold
from plotpy.panels.base import PanelWidget
from plotpy.plot.base import BasePlot, BasePlotOptions
from plotpy.styles import CurveParam, HistogramParam
from plotpy.tools import AntiAliasingTool, BasePlotMenuTool, SelectPointTool, SelectTool

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from qtpy.QtGui import QCloseEvent
    from qtpy.QtWidgets import QWidget

    from plotpy.items import BaseImageItem
    from plotpy.plot.manager import PlotManager


class LevelsHistogram(BasePlot):
    """Image levels histogram widget

    Args:
        parent: parent widget
    """

    DEFAULT_NBINS = 256  # Default number of bins for histogram

    #: Signal emitted by LevelsHistogram when LUT range of some items was changed.
    #: For now, this signal is private. The public counterpart is emitted by
    #: the base plot class (see :py:attr:`.BasePlot.SIG_LUT_CHANGED`).
    SIG_VOI_CHANGED = QC.Signal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(
            parent=parent,
            options=BasePlotOptions(title="", section="histogram", type="curve"),
        )
        self.antialiased = False

        # a dict of dict : plot -> selected items -> HistogramItem
        self._tracked_items: dict[BasePlot, dict[BaseImageItem, HistogramItem]] = {}
        self.param = CurveParam(_("Curve"), icon="curve.png")
        self.param.read_config(CONF, "histogram", "curve")

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

    def connect_plot(self, plot: BasePlot) -> None:
        """Connect plot to histogram widget

        Args:
            plot: plot to connect to
        """
        if plot.options.type == PlotType.CURVE:
            # Connecting only to image plot widgets (allow mixing image and
            # curve widgets for the same plot manager -- e.g. in pyplot)
            return
        self.SIG_VOI_CHANGED.connect(plot.notify_colormap_changed)
        plot.SIG_ITEM_SELECTION_CHANGED.connect(self.selection_changed)
        plot.SIG_ITEM_REMOVED.connect(self.item_removed)
        plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)
        plot.SIG_AXIS_PARAMETERS_CHANGED.connect(
            lambda axis_id: self.axis_parameters_changed(plot=plot, axis_id=axis_id)
        )

    def tracked_items_gen(
        self,
    ) -> Generator[tuple[BaseImageItem, HistogramItem], None, None]:
        """Generator of tracked items"""
        for _plot, items in list(self._tracked_items.items()):
            for item_curve_tuple in list(items.items()):
                yield item_curve_tuple  # tuple item,curve

    def __del_known_items(self, known_items: dict, items: list) -> None:
        """Delete known items

        Args:
            known_items: dict of known items
            items: list of items to delete
        """
        del_curves = []
        for item in list(known_items.keys()):
            if item not in items:
                curve = known_items.pop(item)
                del_curves.append(curve)
        self.del_items(del_curves)

    def selection_changed(self, plot: BasePlot) -> None:
        """Selection changed callback

        Args:
            plot: plot whose selection changed
        """
        items: list[BaseImageItem] = plot.get_selected_items(
            item_type=IVoiImageItemType
        )
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
                histparam = HistogramParam(_("Histogram"), icon="histogram.png")
                histparam.logscale = False
                histparam.n_bins = self.DEFAULT_NBINS
                curve = HistogramItem(self.param, histparam, keep_weakref=True)
                curve.set_hist_source(item)
                self.add_item(curve, z=0)
                known_items[item] = curve

        nb_selected = len(list(self.tracked_items_gen()))
        if not nb_selected:
            self.replot()
            return
        self.param.shade = 1.0 / nb_selected
        for item, curve in self.tracked_items_gen():
            if np.issubdtype(item.data.dtype, np.integer):
                # For integer data, we use the full range of data type
                info = np.iinfo(item.data.dtype)
                curve.histparam.bin_min = info.min
                curve.histparam.bin_max = info.max
                curve.histparam.n_bins = min(
                    info.max - info.min + 1, self.DEFAULT_NBINS
                )
            else:
                curve.histparam.bin_min = None
                curve.histparam.bin_max = None
                curve.histparam.n_bins = self.DEFAULT_NBINS
            self.param.update_item(curve)
            curve.histparam.update_hist(curve)

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

    def item_removed(self, item: BaseImageItem) -> None:
        """Item removed callback

        Args:
            item: item which was removed
        """
        replot = False
        for _plot, items_dict in list(self._tracked_items.items()):
            if item in items_dict:
                try:
                    self.del_item(items_dict[item])
                    replot = True
                except ValueError:
                    pass  # Histogram has not yet been created
                items_dict.pop(item)
                break
        if replot:
            self.replot()

    def active_item_changed(self, plot: BasePlot) -> None:
        """Active item changed callback

        Args:
            plot: plot whose active item changed
        """
        items = plot.get_selected_items(item_type=IVoiImageItemType)
        if not items:
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

    def axis_parameters_changed(self, plot: BasePlot, axis_id: int) -> None:
        """Plot axis parameters changed callback

        Args:
            axis_id: axis ID
        """
        if axis_id == BasePlot.Y_RIGHT:
            # Colormap bounds changed, we need to update the range accordingly:
            self.active_item_changed(plot)

    def set_range_style(self, multiple_ranges: bool) -> None:
        """Set range style

        Args:
            multiple_ranges: whether multiple ranges are selected
        """
        if multiple_ranges:
            self.range.shapeparam.sel_line.color = self.range_multi_color
        else:
            self.range.shapeparam.sel_line.color = self.range_mono_color
        self.range.shapeparam.update_item(self.range)

    def set_range(self, zmin: float, zmax: float) -> bool:
        """Set range

        Args:
            zmin: minimum value
            zmax: maximum value

        Returns:
            True if range was changed, False otherwise
        """
        if zmin < zmax:
            self.set_range_style(False)
            self.range.set_range(zmin, zmax)
            self.replot()
            return True
        else:
            # Range was not changed
            return False

    def range_changed(
        self, _rangesel: XRangeSelection, zmin: float, zmax: float
    ) -> None:
        """Range changed callback

        Args:
            _rangesel: range selection
            zmin: minimum value
            zmax: maximum value
        """
        for item, _curve in self.tracked_items_gen():
            item.set_lut_range([zmin, zmax])
        self.SIG_VOI_CHANGED.emit()

    @staticmethod
    def apply_full_range_func(
        item: BaseImageItem, _curve: HistogramItem
    ) -> tuple[float, float]:
        """Apply full range function

        Args:
            item: item to apply full range to
            _curve: histogram curve associated with item

        Returns:
            tuple of minimum and maximum values
        """
        return item.get_lut_range_full()

    @staticmethod
    def apply_min_func(
        item: BaseImageItem, _curve: HistogramItem, zmin: float
    ) -> tuple[float, float]:
        """Apply minimum function

        Args:
            item: item to apply minimum to
            _curve: histogram curve associated with item
            zmin: minimum value

        Returns:
            tuple of minimum and maximum values
        """
        _zmin, zmax = item.get_lut_range()
        return zmin, zmax

    @staticmethod
    def apply_max_func(
        item: BaseImageItem, _curve: HistogramItem, zmax: float
    ) -> tuple[float, float]:
        """Apply maximum function

        Args:
            item: item to apply maximum to
            _curve: histogram curve associated with item
            zmax: maximum value

        Returns:
            tuple of minimum and maximum values
        """
        zmin, _zmax = item.get_lut_range()
        return zmin, zmax

    @staticmethod
    def reduce_range_func(
        item: BaseImageItem, curve: HistogramItem, percent: float
    ) -> tuple[float, float]:
        """Reduce range function

        Args:
            item: item to reduce range of
            curve: histogram curve associated with item
            percent: percentage of range to reduce

        Returns:
            tuple of minimum and maximum values
        """
        return lut_range_threshold(item, curve.bins, percent)

    def apply_range_function(self, func: Callable, *args, **kwargs) -> None:
        """Apply range function

        Args:
            func: function to apply
            *args: arguments to pass to function
            **kwargs: keyword arguments to pass to function
        """
        item = None
        zmin, zmax = np.inf, -np.inf
        for item, curve in self.tracked_items_gen():
            zmin_i, zmax_i = func(item, curve, *args, **kwargs)
            zmin = min(zmin, zmin_i)
            zmax = max(zmax, zmax_i)
        if zmin != np.inf and zmax != -np.inf:
            self.set_range(zmin, zmax)

    def set_full_range(self) -> None:
        """Set range bounds to image min/max levels"""
        self.apply_range_function(self.apply_full_range_func)

    def eliminate_outliers(self, percent: float) -> None:
        """Eliminate outliers

        Args:
            percent: percentage of outliers to eliminate (eliminate percent/2
             on each side)
        """
        self.apply_range_function(self.reduce_range_func, percent)

    def set_min(self, zmin: float) -> None:
        """Set minimum value

        Args:
            zmin: minimum value
        """
        self.apply_range_function(self.apply_min_func, zmin)

    def set_max(self, zmax: float) -> None:
        """Set maximum value

        Args:
            zmax: maximum value
        """
        self.apply_range_function(self.apply_max_func, zmax)


class EliminateOutliersParam(DataSet):
    percent = FloatItem(
        _("Eliminate outliers") + " (%)", default=2.0, min=0.0, max=100.0 - 1e-6
    )


class ContrastAdjustment(PanelWidget):
    """Contrast adjustment tool

    Args:
        parent: parent widget
    """

    __implements__ = (IPanel,)
    PANEL_ID = ID_CONTRAST
    PANEL_TITLE = _("Contrast")
    PANEL_ICON = "contrast.png"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.local_manager = None  # local manager for the histogram plot
        self.manager = None  # manager for the associated image plot

        # Storing min/max markers for each active image
        self.min_markers = {}
        self.max_markers = {}

        # Select point tools
        self.min_select_tool = None
        self.max_select_tool = None

        color = "#444444" if not IS_DARK else "#bbbbbb"
        style = "<span style='color: %s'><b>{}</b></span>" % color
        layout, _label = get_image_layout(
            self.PANEL_ICON, style.format(self.PANEL_TITLE), alignment=QC.Qt.AlignLeft
        )
        layout.setAlignment(QC.Qt.AlignCenter)
        vlayout = QW.QVBoxLayout()
        vlayout.addLayout(layout)

        # Avoid circular import
        # pylint-disable=import-outside-toplevel
        from plotpy.plot.manager import PlotManager

        self.local_manager = PlotManager(self)
        self.histogram = LevelsHistogram(parent)
        vlayout.addWidget(self.histogram)
        self.local_manager.add_plot(self.histogram)
        hlayout = QW.QHBoxLayout()
        self.setLayout(hlayout)
        hlayout.addLayout(vlayout)

        self.toolbar = toolbar = QW.QToolBar(self)
        toolbar.setIconSize(QC.QSize(12, 12))
        toolbar.setOrientation(QC.Qt.Horizontal)
        toolbar.setToolButtonStyle(QC.Qt.ToolButtonTextBesideIcon)
        layout.addWidget(toolbar)

        # Add standard plot-related tools to the local manager
        lman = self.local_manager
        lman.add_tool(SelectTool)
        lman.add_tool(BasePlotMenuTool, "item")
        lman.add_tool(BasePlotMenuTool, "axes")
        lman.add_tool(BasePlotMenuTool, "grid")
        lman.add_tool(AntiAliasingTool)
        lman.get_default_tool().activate()

        self.outliers_param = EliminateOutliersParam(self.PANEL_TITLE)

    def register_panel(self, manager: PlotManager) -> None:
        """Register panel to plot manager

        Args:
            manager: plot manager to register to
        """
        self.manager = manager
        default_toolbar = self.manager.get_default_toolbar()
        self.manager.add_toolbar(self.toolbar, "contrast")
        self.manager.set_default_toolbar(default_toolbar)
        self.setup_actions()
        for plot in manager.get_plots():
            self.histogram.connect_plot(plot)

    def configure_panel(self) -> None:
        """Configure panel"""
        self.min_select_tool = self.manager.add_tool(
            SelectPointTool,
            title=_("Min."),
            on_active_item=True,
            mode="create",
            tip=_("Select minimum level on image"),
            toolbar_id="contrast",
            end_callback=self.apply_min_selection,
            switch_to_default_tool=True,
        )
        self.max_select_tool = self.manager.add_tool(
            SelectPointTool,
            title=_("Max."),
            on_active_item=True,
            mode="create",
            tip=_("Select maximum level on image"),
            toolbar_id="contrast",
            end_callback=self.apply_max_selection,
            switch_to_default_tool=True,
        )

    def get_plot(self) -> BasePlot:
        """Get active plot

        Returns:
            active plot
        """
        return self.manager.get_active_plot()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Reimplement Qt method"""
        self.hide()
        event.ignore()

    def setup_actions(self) -> None:
        """Setup actions"""
        fullrange_ac = create_action(
            self,
            _("Full range"),
            icon=get_icon("full_range.png"),
            triggered=self.histogram.set_full_range,
            tip=_("Scale the image's display range " "according to data range"),
        )
        outliers_ac = create_action(
            self,
            _("Eliminate %"),
            icon=get_icon("eliminate_outliers.png"),
            triggered=self.eliminate_outliers,
            tip=_(
                "Eliminate outliers from the image's display range, "
                "based on a percentage of the data range"
            ),
        )
        setrange_ac = create_action(
            self,
            _("Set range"),
            icon=get_icon("xrange.png"),
            triggered=self.set_range_manually,
            tip=_("Set the image's display range manually"),
        )
        add_actions(self.toolbar, [fullrange_ac, outliers_ac, setrange_ac])

    def eliminate_outliers(self) -> None:
        """Eliminate outliers"""

        def apply_callback(param: EliminateOutliersParam) -> None:
            """Apply callback"""
            self.histogram.eliminate_outliers(param.percent)

        zmin_0, zmax_0 = self.histogram.range.get_range()
        if self.outliers_param.edit(self, apply=apply_callback):
            apply_callback(self.outliers_param)
        else:
            self.histogram.set_range(zmin_0, zmax_0)

    def set_range_manually(self) -> None:
        """Set range manually"""

        class RangeParam(DataSet):
            """Range parameters"""

            zmin = FloatItem(_("Min. level"))
            zmax = FloatItem(_("Max. level"))

        def apply_callback(param: RangeParam) -> None:
            """Apply callback"""
            self.histogram.set_range(param.zmin, param.zmax)

        param = RangeParam(_("Set range"))
        zmin_0, zmax_0 = param.zmin, param.zmax = self.histogram.range.get_range()
        if param.edit(self, apply=apply_callback):
            apply_callback(param)
        else:
            self.histogram.set_range(zmin_0, zmax_0)

    def apply_min_selection(self, tool: SelectPointTool) -> None:
        """Apply minimum selection

        Args:
            tool: select point tool
        """
        item: BaseImageItem = self.get_plot().get_last_active_item(IVoiImageItemType)
        point = self.min_select_tool.get_coordinates()
        z = item.get_data(*point)
        self.histogram.set_min(z)
        tool.SIG_TOOL_JOB_FINISHED.emit()

    def apply_max_selection(self, tool: SelectPointTool) -> None:
        """Apply maximum selection

        Args:
            tool: select point tool
        """
        item: BaseImageItem = self.get_plot().get_last_active_item(IVoiImageItemType)
        point = self.max_select_tool.get_coordinates()
        z = item.get_data(*point)
        self.histogram.set_max(z)
        tool.SIG_TOOL_JOB_FINISHED.emit()

    def set_range(self, zmin: float, zmax: float) -> None:
        """Set contrast panel's histogram range

        Args:
            zmin: minimum value
            zmax: maximum value
        """
        self.histogram.set_range(zmin, zmax)
        # Update the levels histogram in case active item data has changed:
        self.histogram.selection_changed(self.get_plot())


assert_interfaces_valid(ContrastAdjustment)
