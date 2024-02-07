# -*- coding: utf-8 -*-

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any

from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import CONF, _
from plotpy.constants import LUT_MAX, PlotType
from plotpy.interfaces import ICSImageItemType
from plotpy.panels.csection.csitem import (
    LineCrossSectionItem,
    ObliqueCrossSectionItem,
    XCrossSectionItem,
    YCrossSectionItem,
)
from plotpy.plot.base import BasePlot, BasePlotOptions
from plotpy.styles.curve import CurveParam

LUT_AXIS_TITLE = _("LUT scale") + (" (0-%d)" % LUT_MAX)


if TYPE_CHECKING:  # pragma: no cover
    from qtpy.QtWidgets import QWidget

    from plotpy.items import BaseImageItem
    from plotpy.panels.csection.csitem import CrossSectionItem


class BaseCrossSectionPlot(BasePlot):
    """Cross section plot base class

    Args:
        parent: Parent widget. Defaults to None.
    """

    CURVE_LABEL = _("Cross section")
    LABEL_TEXT = ""  # to be overridden in subclasses
    _HEIGHT = None
    _WIDTH = None
    CS_AXIS = None
    Z_AXIS = None
    Z_MAX_MAJOR = 5
    SHADE = 0.2

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            parent=parent,
            options=BasePlotOptions(title="", section="cross_section", type="curve"),
        )
        self.perimage_mode = True
        self.autoscale_mode = True
        self.autorefresh_mode = True
        self.apply_lut = False
        self.single_source = False
        self.lockscales = True

        self.last_obj = None
        self.known_items = {}
        self._shapes = {}

        self.param = CurveParam(_("Curve"), icon="curve.png")
        self.set_curve_style("cross_section", "curve")

        if self._HEIGHT is not None:
            self.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum)
        elif self._WIDTH is not None:
            self.setSizePolicy(QW.QSizePolicy.Minimum, QW.QSizePolicy.Expanding)

        # The following import is here to avoid circular imports
        # pylint: disable=import-outside-toplevel
        from plotpy.builder import make

        self.label = make.label(self.LABEL_TEXT, "C", (0, 0), "C")
        self.label.set_readonly(True)
        self.add_item(self.label)

        self.setAxisMaxMajor(self.Z_AXIS, self.Z_MAX_MAJOR)
        self.setAxisMaxMinor(self.Z_AXIS, 0)

    def set_curve_style(self, section: str, option: str) -> None:
        """Set curve style

        Args:
            section: Configuration section name
            option: Configuration option name
        """
        self.param.read_config(CONF, section, option)
        self.param.label = self.CURVE_LABEL

    def connect_plot(self, plot: BasePlot) -> None:
        """Connect plot to cross section plot

        Args:
            plot: Plot to connect (containing the image items to be used for)
        """
        if plot.options.type == PlotType.CURVE:
            # Connecting only to image plot widgets (allow mixing image and
            # curve widgets for the same plot manager -- e.g. in pyplot)
            return
        plot.SIG_ITEMS_CHANGED.connect(self.items_changed)
        plot.SIG_LUT_CHANGED.connect(self.lut_changed)
        plot.SIG_MASK_CHANGED.connect(lambda item: self.update_plot())
        plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)
        plot.SIG_ANNOTATION_CHANGED.connect(self.shape_changed)
        plot.SIG_PLOT_LABELS_CHANGED.connect(self.plot_labels_changed)
        plot.SIG_AXIS_DIRECTION_CHANGED.connect(self.axis_dir_changed)
        plot.SIG_PLOT_AXIS_CHANGED.connect(self.plot_axis_changed)
        self.plot_labels_changed(plot)
        for axis_id in plot.AXIS_IDS:
            self.axis_dir_changed(plot, axis_id)
        self.items_changed(plot)

    def register_shape(self, plot: BasePlot, shape: Any, refresh: bool = True) -> None:
        """Register shape associated to cross section plot

        Args:
            plot: Plot containing the shape and the associated image items
            shape: Shape to register, and to be used for cross section
            refresh: Whether to refresh the plot
        """
        known_shapes = self._shapes.get(plot, [])
        if shape in known_shapes:
            return
        self._shapes[plot] = known_shapes + [shape]
        self.update_plot(shape, refresh=refresh and self.autorefresh_mode)

    def unregister_shape(self, shape: Any) -> None:
        """Unregister shape associated to cross section plot

        Args:
            shape: Shape to unregister
        """
        for plot in self._shapes:
            shapes = self._shapes[plot]
            if shape in shapes:
                shapes.pop(shapes.index(shape))
                if len(shapes) == 0 or shape is self.get_last_obj():
                    for curve in self.get_cross_section_curves():
                        curve.clear_data()
                    self.replot()
                break

    def create_cross_section_item(self) -> CrossSectionItem:
        """Create cross section item"""
        raise NotImplementedError

    def add_cross_section_item(self, source: BaseImageItem) -> None:
        """Add cross section item

        Args:
            source: Source image item to add cross section item for
        """
        curve = self.create_cross_section_item()
        curve.set_source_image(source)
        curve.set_readonly(True)
        self.add_item(curve, z=0)
        self.known_items[source] = curve

    def get_cross_section_curves(self) -> list[CrossSectionItem]:
        """Return cross section curves"""
        return list(self.known_items.values())

    def items_changed(self, plot: BasePlot) -> None:
        """Items have changed in the plot

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        # Del obsolete cross section items
        new_sources = plot.get_items(item_type=ICSImageItemType)
        for source in self.known_items.copy():
            if source not in new_sources:
                curve = self.known_items.pop(source)
                curve.clear_data()  # useful to emit SIG_CS_CURVE_CHANGED
                # (eventually notify other panels that the
                #  cross section curve is now empty)
                self.del_item(curve)

        # Update plot only to show/hide cross section curves according to
        # the associated image item visibility state (hence `refresh=False`)
        self.update_plot(refresh=False)

        self.plot_axis_changed(plot)

        if not new_sources:
            self.replot()
            return

        self.param.shade = self.SHADE / len(new_sources)
        for source in new_sources:
            if source not in self.known_items and source.isVisible():
                if not self.single_source or not self.known_items:
                    self.add_cross_section_item(source=source)

    def active_item_changed(self, plot: BasePlot) -> None:
        """Active item has just changed

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        self.shape_changed(plot.get_active_item())

    def plot_labels_changed(self, plot: BasePlot) -> None:
        """Plot labels have changed

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        raise NotImplementedError

    def axis_dir_changed(self, plot: BasePlot, axis_id: str) -> None:
        """An axis direction has changed

        Args:
            plot: Plot containing the image items to be used for cross section
            axis_id: Axis ID
        """
        pass

    def plot_axis_changed(self, plot: BasePlot) -> None:
        """Plot was just zoomed/panned

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        if self.lockscales:
            self.do_autoscale(replot=False, axis_id=self.Z_AXIS)
            vmin, vmax = plot.get_axis_limits(self.CS_AXIS)
            self.set_axis_limits(self.CS_AXIS, vmin, vmax)

    def is_shape_known(self, shape: Any) -> bool:
        """Return whether shape is known

        Args:
            shape: Shape to check

        Returns:
            bool: Whether shape is known
        """
        for shapes in list(self._shapes.values()):
            if shape in shapes:
                return True
        else:
            return False

    def shape_changed(self, shape: Any) -> None:
        """Shape has changed

        Args:
            shape: Shape that has changed
        """
        if self.autorefresh_mode:
            if self.is_shape_known(shape):
                self.update_plot(shape)

    def get_last_obj(self) -> BaseImageItem | None:
        """Return last active object"""
        if self.last_obj is not None:
            return self.last_obj()

    def update_plot(self, obj: Any = None, refresh: bool = True) -> None:
        """
        Update cross section curves

        Args:
            obj: Object to update cross section curves for
             (may be a marker or a rectangular shape, or None to update)
            refresh: Whether to refresh the plot
        """
        if obj is None:
            obj = self.get_last_obj()
            if obj is None:
                return
        else:
            self.last_obj = weakref.ref(obj)
        if obj.plot() is None:
            self.unregister_shape(obj)
            return
        if self.label.isVisible():
            self.label.hide()
        items = list(self.known_items.items())
        for item, curve in iter(items):
            if not item.isVisible():
                curve.hide()
            else:
                curve.show()
                curve.perimage_mode = self.perimage_mode
                curve.autoscale_mode = self.autoscale_mode
                curve.apply_lut = self.apply_lut
                if refresh:
                    curve.update_item(obj)
        if self.autoscale_mode:
            self.do_autoscale(replot=True)
        elif self.lockscales:
            self.do_autoscale(replot=True, axis_id=self.Z_AXIS)

    def toggle_perimage_mode(self, state: bool) -> None:
        """Toggle the per item mode

        Args:
            state: State to toggle to
        """
        self.perimage_mode = state
        self.update_plot()

    def toggle_autoscale(self, state: bool) -> None:
        """Toggle the autoscale mode

        Args:
            state: State to toggle to
        """
        self.autoscale_mode = state
        self.update_plot()

    def toggle_autorefresh(self, state: bool) -> None:
        """Toggle the autorefresh mode

        Args:
            state: State to toggle to
        """
        self.autorefresh_mode = state
        if state:
            self.update_plot()

    def toggle_apply_lut(self, state: bool) -> None:
        """Toggle the apply LUT mode

        Args:
            state: State to toggle to
        """
        self.apply_lut = state
        self.update_plot()
        if self.apply_lut:
            self.set_axis_title(self.Z_AXIS, LUT_AXIS_TITLE)
            self.set_axis_color(self.Z_AXIS, "red")
        else:
            obj = self.get_last_obj()
            if obj is not None and obj.plot() is not None:
                self.plot_labels_changed(obj.plot())

    def toggle_lockscales(self, state: bool)-> None:
        """Toggle the lock scales mode

        Args:
            state: State to toggle to
        """
        self.lockscales = state
        obj = self.get_last_obj()
        if obj is not None and obj.plot() is not None:
            self.plot_axis_changed(obj.plot())

    def lut_changed(self, plot: BasePlot) -> None:
        """LUT has changed

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        if self.apply_lut:
            self.update_plot()


class HorizontalCrossSectionPlot(BaseCrossSectionPlot):
    CS_AXIS = BasePlot.X_BOTTOM
    Z_AXIS = BasePlot.Y_LEFT

    def plot_labels_changed(self, plot: BasePlot) -> None:
        """Plot labels have changed

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        self.set_axis_title("left", plot.get_axis_title("right"))
        self.set_axis_title("bottom", plot.get_axis_title("bottom"))
        self.set_axis_color("left", plot.get_axis_color("right"))
        self.set_axis_color("bottom", plot.get_axis_color("bottom"))

    def axis_dir_changed(self, plot: BasePlot, axis_id: str) -> None:
        """An axis direction has changed

        Args:
            plot: Plot containing the image items to be used for cross section
            axis_id: Axis ID
        """
        if axis_id == plot.X_BOTTOM:
            self.set_axis_direction("bottom", plot.get_axis_direction("bottom"))
            self.replot()


class VerticalCrossSectionPlot(BaseCrossSectionPlot):
    CS_AXIS = BasePlot.Y_LEFT
    Z_AXIS = BasePlot.X_BOTTOM
    Z_MAX_MAJOR = 3

    def plot_labels_changed(self, plot: BasePlot) -> None:
        """Plot labels have changed

        Args:
            plot: Plot containing the image items to be used for cross section
        """
        self.set_axis_title("bottom", plot.get_axis_title("right"))
        self.set_axis_title("left", plot.get_axis_title("left"))
        self.set_axis_color("bottom", plot.get_axis_color("right"))
        self.set_axis_color("left", plot.get_axis_color("left"))

    def axis_dir_changed(self, plot: BasePlot, axis_id: str) -> None:
        """An axis direction has changed

        Args:
            plot: Plot containing the image items to be used for cross section
            axis_id: Axis ID
        """
        if axis_id == plot.Y_LEFT:
            self.set_axis_direction("left", plot.get_axis_direction("left"))
            self.replot()


class XYCrossSectionMixin:

    LABEL_TEXT = _("Enable a marker")

    def connect_plot(self, plot: BasePlot) -> None:
        """Connect plot to cross section plot

        Args:
            plot: Plot to connect (containing the image items to be used for)
        """
        BaseCrossSectionPlot.connect_plot(self, plot)
        plot.SIG_MARKER_CHANGED.connect(
            lambda marker: BaseCrossSectionPlot.update_plot(self, marker)
        )


class XCrossSectionPlot(HorizontalCrossSectionPlot, XYCrossSectionMixin):
    """X-axis cross section plot"""

    _HEIGHT = 130

    def sizeHint(self) -> QC.QSize:
        """Reimplemented from QWidget.sizeHint"""
        return QC.QSize(self.width(), self._HEIGHT)

    def create_cross_section_item(self) -> XCrossSectionItem:
        """Create cross section item"""
        return XCrossSectionItem(self.param)


class YCrossSectionPlot(VerticalCrossSectionPlot, XYCrossSectionMixin):
    """Y-axis cross section plot"""

    _WIDTH = 140

    def sizeHint(self) -> QC.QSize:
        """Reimplemented from QWidget.sizeHint"""
        return QC.QSize(self._WIDTH, self.height())

    def create_cross_section_item(self) -> YCrossSectionItem:
        """Create cross section item"""
        return YCrossSectionItem(self.param)


# Oblique cross section plot
class ObliqueCrossSectionPlot(HorizontalCrossSectionPlot):
    """Oblique averaged cross section plot"""

    PLOT_TITLE = _("Oblique averaged cross section")
    CURVE_LABEL = _("Oblique averaged cross section")
    LABEL_TEXT = _("Activate the oblique cross section tool")
    SHADE = 0.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_title(self.PLOT_TITLE)
        self.single_source = True

    def create_cross_section_item(self) -> ObliqueCrossSectionItem:
        """Create cross section item"""
        return ObliqueCrossSectionItem(self.param)



# Line cross section plot
class LineCrossSectionPlot(HorizontalCrossSectionPlot):
    """Line cross section plot"""

    PLOT_TITLE = _("Line cross section")
    CURVE_LABEL = _("Line cross section")
    LABEL_TEXT = _("Activate the line cross section tool")
    SHADE = 0.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_title(self.PLOT_TITLE)
        self.single_source = True

    def create_cross_section_item(self) -> LineCrossSectionItem:
        """Create cross section item"""
        return LineCrossSectionItem(self.param)
