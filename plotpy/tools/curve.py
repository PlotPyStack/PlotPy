# -*- coding: utf-8 -*-
"""Curve tools"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import numpy as np
import scipy.integrate as spt
from guidata.dataset import ChoiceItem, DataSet, FloatItem, IntItem
from guidata.qthelpers import execenv
from guidata.widgets.arrayeditor import ArrayEditor
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.constants import SHAPE_Z_OFFSET
from plotpy.coords import axes_to_canvas, canvas_to_axes
from plotpy.events import (
    KeyEventMatch,
    QtDragHandler,
    StandardKeyMatch,
    StatefulEventFilter,
    setup_standard_tool_filter,
)
from plotpy.interfaces import ICurveItemType
from plotpy.items import Marker, XRangeSelection, YRangeSelection
from plotpy.items.curve.base import CurveItem
from plotpy.tools.base import (
    DefaultToolbarID,
    InteractiveTool,
    LastItemHolder,
    ToggleTool,
)
from plotpy.tools.cursor import BaseCursorTool

if TYPE_CHECKING:
    from plotpy.items.label import DataInfoLabel
    from plotpy.plot.base import BasePlot
    from plotpy.plot.manager import PlotManager


class BaseRangeCursorTool(BaseCursorTool):
    """Base range cursor tool

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use. Defaults to DefaultToolbarID.
        title: Tool name. Defaults to None.
        icon: Tool icon path. Defaults to None.
        tip: Available tip. Defaults to None.
        switch_to_default_tool: Wether to use as the default tool or not.
         Defaults to None.
    """

    TITLE = ""
    ICON = ""  # No icon by default, subclasses should set this
    SWITCH_TO_DEFAULT_TOOL = True
    LABELFUNCS: tuple[tuple[str, Callable[..., Any]], ...] | None = None
    SHAPECLASS: type[XRangeSelection | YRangeSelection] = XRangeSelection

    def __init__(
        self,
        manager: PlotManager,
        labelfuncs: tuple[tuple[str, Callable[..., Any]], ...] | None = None,
        toolbar_id: Any = DefaultToolbarID,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
    ) -> None:
        super().__init__(manager, toolbar_id, title=title, icon=icon, tip=tip)
        self.last_item_holder = LastItemHolder(ICurveItemType)
        self.label: DataInfoLabel | None = None
        self.labelfuncs = labelfuncs or self.LABELFUNCS

    def create_shape(self) -> XRangeSelection | YRangeSelection:
        """Create shape associated with the tool"""
        assert self.SHAPECLASS is not None, "SHAPECLASS must be set in subclasses"
        return self.SHAPECLASS(0, 0)

    def get_label_title(self) -> str | None:
        """Return label title"""
        return self.TITLE

    def get_computation_specs(self):
        """Return computation specs"""
        raise NotImplementedError

    def create_label(self) -> DataInfoLabel:
        """Create label associated with the tool"""
        # The following import is here to avoid circular imports
        # pylint: disable=import-outside-toplevel
        from plotpy.builder import make

        plot = self.manager.get_plot()
        title = self.get_label_title()
        specs = self.get_computation_specs()
        label = make.computations(self.shape, "TL", specs, title)
        label.attach(plot)
        label.setZ(plot.get_max_z() + 1)
        label.setVisible(True)
        return label

    def move(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        super().move(filter, event)
        if self.label is None:
            self.label = self.create_label()

    def end_move(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """End shape move

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        super().end_move(filter, event)
        if self.label is not None:
            filter.plot.add_item_with_z_offset(self.label, SHAPE_Z_OFFSET)
            self.label = None


class CurveStatsTool(BaseRangeCursorTool):
    """X-range curve statistics tool

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use. Defaults to DefaultToolbarID.
        title: Tool name. Defaults to None.
        icon: Tool icon path. Defaults to None.
        tip: Available tip. Defaults to None.
        switch_to_default_tool: Wether to use as the default tool or not.
         Defaults to None.
    """

    TITLE = _("Signal statistics")
    ICON = "xrange.png"
    LABELFUNCS: tuple[tuple[str, Callable[..., Any]], ...] = (
        ("%g &lt; x &lt; %g", lambda *args: (args[0].min(), args[0].max())),
        ("%g &lt; y &lt; %g", lambda *args: (args[1].min(), args[1].max())),
        ("∆x=%g", lambda *args: args[0].max() - args[0].min()),
        ("∆y=%g", lambda *args: args[1].max() - args[1].min()),
        ("&lt;y&gt;=%g", lambda *args: args[1].mean()),
        ("σ(y)=%g", lambda *args: args[1].std()),
        ("∑(y)=%g", lambda *args: np.sum(args[1])),
        ("∫ydx=%g", lambda *args: spt.trapezoid(args[1], args[0])),
    )
    SHAPECLASS = XRangeSelection

    def set_labelfuncs(
        self, labelfuncs: tuple[tuple[str, Callable[..., Any]], ...]
    ) -> None:
        """Set label functions

        Args:
            labelfuncs: Label functions

        Example:

            .. code-block:: python

                labelfuncs = (
                    ("%g &lt; x &lt; %g", lambda *args: (args[0].min(), args[0].max())),
                    ("%g &lt; y &lt; %g", lambda *args: (args[1].min(), args[1].max())),
                    ("&lt;y&gt;=%g", lambda *args: args[1].mean()),
                    ("σ(y)=%g", lambda *args: args[1].std()),
                    ("∑(y)=%g", lambda *args: np.sum(args[1])),
                    ("∫ydx=%g", lambda *args: spt.trapezoid(args[1], args[0])),
                )
        """
        self.labelfuncs = labelfuncs

    def get_label_title(self) -> str | None:
        """Return label title"""
        curve = self.last_item_holder.get()
        return curve.title().text() if curve else None

    def get_computation_specs(self) -> list[tuple[CurveItem, str, Callable[..., Any]]]:
        """Return computation specs"""
        curve = self.last_item_holder.get()
        return [(curve, label, func) for label, func in self.labelfuncs]

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status

        Args:
            plot: BasePlot instance
        """
        item = self.last_item_holder.update_from_selection(plot)
        self.action.setEnabled(item is not None)


class YRangeCursorTool(BaseRangeCursorTool):
    """Y-range cursor tool

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use. Defaults to DefaultToolbarID.
        title: Tool name. Defaults to None.
        icon: Tool icon path. Defaults to None.
        tip: Available tip. Defaults to None.
        switch_to_default_tool: Wether to use as the default tool or not.
         Defaults to None.
    """

    TITLE = _("Y-range")
    ICON = "yrange.png"
    LABELFUNCS: tuple[tuple[str, Callable[..., Any]], ...] = (
        ("%g &lt; y &lt; %g", lambda ymin, ymax: (ymin, ymax)),
        ("∆y=%g", lambda ymin, ymax: ymax - ymin),
    )
    SHAPECLASS = YRangeSelection

    def set_labelfuncs(
        self, labelfuncs: tuple[tuple[str, Callable[..., Any]], ...]
    ) -> None:
        """Set label functions

        Args:
            labelfuncs: Label functions

        Example:

            .. code-block:: python

                labelfuncs = (
                    ("%g &lt; y &lt; %g", lambda ymin, ymax: (ymin, ymax)),
                    ("∆y=%g", lambda ymin, ymax: ymax - ymin),
                )
        """
        self.labelfuncs = labelfuncs

    def get_computation_specs(self) -> list[tuple[str, Callable[..., Any]]]:
        """Return computation specs"""
        return [(label, func) for label, func in self.labelfuncs]


class AntiAliasingTool(ToggleTool):
    """Anti-aliasing tool

    Args:
        manager: PlotManager Instance
    """

    def __init__(self, manager: PlotManager) -> None:
        super().__init__(manager, _("Antialiasing (curves)"))

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """Activate tool"""
        plot.set_antialiasing(checked)
        plot.replot()

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status

        Args:
            plot: BasePlot instance
        """
        self.action.setChecked(plot.antialiased)


class SelectPointTool(InteractiveTool):
    """Curve point selection tool

    Args:
        manager: PlotManager Instance
        mode: Selection mode. Defaults to "reuse".
        on_active_item: Wether to use the active item or not. Defaults to False.
        title: Tool name. Defaults to None.
        icon: Tool icon path. Defaults to None.
        tip: Available tip. Defaults to None.
        end_callback: Callback function taking a Self instance as argument that will
         be passed when the user stops dragging the point. Defaults to None.
        toolbar_id: Toolbar Id to use. Defaults to DefaultToolbarID.
        marker_style: Marker style. Defaults to None.
        switch_to_default_tool: Wether to use as the default tool or not.
         Defaults to None.
    """

    TITLE = _("Point selection")
    ICON = "point_selection.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = QC.Qt.CursorShape.PointingHandCursor

    def __init__(
        self,
        manager: PlotManager,
        mode: str = "reuse",
        on_active_item: bool = False,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
        end_callback: Callable[[SelectPointTool], Any] | None = None,
        toolbar_id=DefaultToolbarID,
        marker_style=None,
        switch_to_default_tool=None,
    ) -> None:
        super().__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        assert mode in ("reuse", "create")
        self.mode = mode
        self.end_callback = end_callback
        self.marker = None
        self.last_pos = None
        self.on_active_item = on_active_item
        if marker_style is not None:
            self.marker_style_sect = marker_style[0]
            self.marker_style_key = marker_style[1]
        else:
            self.marker_style_sect = self.MARKER_STYLE_SECT
            self.marker_style_key = self.MARKER_STYLE_KEY

    def set_marker_style(self, marker: Marker) -> None:
        """Configure marker style

        Args:
            marker: Marker instance
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def setup_filter(self, baseplot: BasePlot) -> StatefulEventFilter:
        """Setup event filter

        Args:
            baseplot: BasePlot instance

        Returns:
            StatefulEventFilter instance
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        handler = QtDragHandler(
            filter, QC.Qt.MouseButton.LeftButton, start_state=start_state
        )
        handler.SIG_START_TRACKING.connect(self.start)
        handler.SIG_MOVE.connect(self.move)
        handler.SIG_STOP_NOT_MOVING.connect(self.stop)
        handler.SIG_STOP_MOVING.connect(self.stop)
        return setup_standard_tool_filter(filter, start_state)

    def start(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Start tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        if self.marker is None:
            title = ""
            if self.TITLE:
                title = f"<b>{self.TITLE}</b><br>"
            if self.on_active_item:
                constraint_cb = filter.plot.on_active_curve

                def label_cb(x, y):
                    return title + filter.plot.get_coordinates_str(x, y)

            else:
                constraint_cb = None

                def label_cb(x, y):
                    return f"{title}x = {x:g}<br>y = {y:g}"

            self.marker = Marker(label_cb=label_cb, constraint_cb=constraint_cb)
            self.set_marker_style(self.marker)
        self.marker.attach(filter.plot)
        self.marker.setZ(filter.plot.get_max_z() + 1)
        self.marker.setVisible(True)

    def stop(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Stop tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self.move(filter, event)
        if self.mode != "reuse":
            self.marker.detach()
            self.marker = None
        if self.end_callback:
            self.end_callback(self)

    def move(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        if self.marker is None:
            return  # something is wrong ...
        self.marker.move_local_point_to(0, event.pos())
        filter.plot.replot()
        self.last_pos = self.marker.xValue(), self.marker.yValue()

    def get_coordinates(self) -> tuple[float, float] | None:
        """Get last coordinates"""
        return self.last_pos


class SelectPointsTool(InteractiveTool):
    """Curve points selection tool

    Args:
        manager: PlotManager Instance
        mode: Selection mode. Defaults to "reuse".
        on_active_item: Wether to use the active item or not. Defaults to False.
        title: Tool name. Defaults to None.
        icon: Tool icon path. Defaults to None.
        tip: Available tip. Defaults to None.
        end_callback: Callback function taking a Self instance as argument that will
        be passed when the user stops dragging the point. Defaults to None.
        toolbar_id: Toolbar Id to use. Defaults to DefaultToolbarID.
        marker_style: Marker style. Defaults to None.
        switch_to_default_tool: Wether to use as the default tool or not.
         Defaults to None.
        max_select: Maximum number of points to select. Defaults to None.
    """

    TITLE = _("Multi-point selection")
    ICON = "multipoint_selection.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = QC.Qt.CursorShape.PointingHandCursor

    def __init__(
        self,
        manager,
        mode="reuse",
        on_active_item=True,
        title=None,
        icon=None,
        tip=None,
        end_callback: Callable[[SelectPointsTool], Any] | None = None,
        toolbar_id=DefaultToolbarID,
        marker_style=None,
        switch_to_default_tool=None,
        max_select: int | None = None,
    ) -> None:
        super().__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        assert mode in ("reuse", "create")
        self.mode = mode
        self.end_callback = end_callback
        self.current_location_marker: Marker | None = None
        self.markers: dict[tuple[float, float], Marker] = {}
        self.on_active_item = on_active_item
        self.max_select = max_select
        if marker_style is not None:
            self.marker_style_sect = marker_style[0]
            self.marker_style_key = marker_style[1]
        else:
            self.marker_style_sect = self.MARKER_STYLE_SECT
            self.marker_style_key = self.MARKER_STYLE_KEY

    def set_marker_style(self, marker: Marker) -> None:
        """Configure marker style

        Args:
            marker: Marker instance
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def setup_filter(self, baseplot: BasePlot) -> StatefulEventFilter:
        """Setup event filter

        Args:
            baseplot: BasePlot instance

        Returns:
            StatefulEventFilter instance
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        single_selection_handler = QtDragHandler(
            filter,
            QC.Qt.MouseButton.LeftButton,
            start_state=start_state,
        )
        single_selection_handler.SIG_START_TRACKING.connect(self.start_single_selection)
        single_selection_handler.SIG_MOVE.connect(self.move)
        single_selection_handler.SIG_STOP_NOT_MOVING.connect(self.stop_single_selection)
        single_selection_handler.SIG_STOP_MOVING.connect(self.stop_single_selection)

        multi_selection_handler = QtDragHandler(
            filter,
            QC.Qt.MouseButton.LeftButton,
            start_state=start_state,
            mods=QC.Qt.KeyboardModifier.ControlModifier,
        )
        multi_selection_handler.SIG_START_TRACKING.connect(self.start_multi_selection)
        multi_selection_handler.SIG_MOVE.connect(self.move)
        multi_selection_handler.SIG_STOP_NOT_MOVING.connect(self.stop_multi_selection)
        multi_selection_handler.SIG_STOP_MOVING.connect(self.stop_multi_selection)

        return setup_standard_tool_filter(filter, start_state)

    def _init_current_marker(
        self,
        filter: StatefulEventFilter,
        event: QG.QMouseEvent,
        force_new_marker=False,
        title: str = "",
    ) -> None:
        """Initialize current marker

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
            force_new_marker: Wether to force a new marker or not. Defaults to False.
            title: Marker title. Defaults to "".
        """
        plot = filter.plot
        if plot is None:
            return
        if force_new_marker or self.current_location_marker is None:
            title = title or f"<b>{self.TITLE} {len(self.markers)}</b><br>"
            constraint_cb = plot.on_active_curve if self.on_active_item else None

            label_cb = self.__new_label_cb(filter, title)
            self.current_location_marker = Marker(
                label_cb=label_cb, constraint_cb=constraint_cb
            )
        assert self.current_location_marker
        self.set_marker_style(self.current_location_marker)
        self.current_location_marker.attach(filter.plot)
        self.current_location_marker.setZ(plot.get_max_z() + 1)
        self.current_location_marker.setVisible(True)

    def start_single_selection(
        self, filter: StatefulEventFilter, event: QG.QMouseEvent
    ) -> None:
        """Start single selection

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self._init_current_marker(filter, event, force_new_marker=True)

    def start_multi_selection(
        self, filter: StatefulEventFilter, event: QG.QMouseEvent
    ) -> None:
        """Start multi selection

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self._init_current_marker(filter, event, force_new_marker=True)
        assert self.current_location_marker
        self.current_location_marker.label_cb = self.__new_label_cb(
            filter, index=len(self.markers) + 1
        )

    def move(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        plot = filter.plot
        if plot is None:
            return
        if self.current_location_marker is None:
            return  # something is wrong ...
        self.current_location_marker.move_local_point_to(0, event.pos())
        plot.replot()

    def common_stop(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Common stop action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self.move(filter, event)
        if self.mode != "reuse" and self.current_location_marker is not None:
            self.current_location_marker.detach()
            self.current_location_marker = None

    def stop_single_selection(
        self, filter: StatefulEventFilter, event: QG.QMouseEvent
    ) -> None:
        """Stop single selection

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        assert self.current_location_marker
        self.common_stop(filter, event)
        # self.clear_markers((self.current_location_marker,))
        self.clear_markers()
        self.toggle_marker(self.current_location_marker)
        self.update_labels(filter)
        if self.end_callback:
            self.end_callback(self)

    def stop_multi_selection(
        self, filter: StatefulEventFilter, event: QG.QMouseEvent
    ) -> None:
        """Stop multi selection

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        assert self.current_location_marker
        self.common_stop(filter, event)
        self.toggle_marker(self.current_location_marker)
        if self.max_select is not None and len(self.markers) > self.max_select:
            xy = next(iter(self.markers))
            self.markers.pop(xy).detach()
            self.update_labels(filter)
        if self.end_callback:
            self.end_callback(self)

    def toggle_marker(self, marker: Marker) -> bool:
        """Toggle marker

        Args:
            marker: Marker instance

        Returns:
            bool: Wether the marker was added or not
        """
        assert marker
        xy = marker.xValue(), marker.yValue()
        entry_marker = self.markers.setdefault(xy, marker)
        if entry_marker is not marker:
            self.markers.pop(xy).detach()
            entry_marker.detach()
            marker.detach()
            self.current_location_marker = None
            return False
        return True

    def clear_markers(self, exclude_detach: tuple[Marker, ...] | None = None) -> None:
        """Clear markers

        Args:
            exclude_detach: Markers to exclude from detachment. Defaults to None.
        """
        exclude_detach = exclude_detach or tuple()
        _ = list(
            map(
                lambda m: m.detach(),
                filter(
                    lambda m: m not in exclude_detach,
                    self.markers.values(),
                ),
            )
        )
        self.markers.clear()

    def update_labels(self, filter: StatefulEventFilter) -> None:
        """Update labels

        Args:
            filter: StatefulEventFilter instance
        """
        for i, marker in enumerate(self.markers.values()):
            marker.label_cb = self.__new_label_cb(filter, index=i + 1)

    def __new_label_cb(
        self, filter: StatefulEventFilter, title: str = "", index: int = 1
    ) -> Callable[[float, float], str]:
        """Create new label callback

        Args:
            filter: StatefulEventFilter instance
            title: Title. Defaults to "".
            index: Index. Defaults to 1.

        Returns:
            Label callback
        """
        title = title or f"<b>{self.TITLE} - {index}</b><br>"
        if self.on_active_item:

            def label_cb(x, y):  # type: ignore
                return title + filter.plot.get_coordinates_str(x, y)

        else:

            def label_cb(x, y):
                return f"{title}{' - ' if title else ''}{index} x = {x:g}<br>y = {y:g}"

        return label_cb

    def get_coordinates(self) -> tuple[tuple[float, float], ...]:
        """Get all selected coordinates"""
        return tuple(self.markers.keys())


class InsertionDataSet(DataSet):
    """Insertion parameters"""

    __index = IntItem(_("Insertion index"), min=0)
    index = __index
    value = FloatItem(_("New value"))
    index_offset = ChoiceItem(
        _("Location"), choices=[_("Before"), _("After")], default=0
    )

    @classmethod
    def set_max_index(cls, max_index: int):
        """Sets the maximum index value for the index field

        Args:
            max_index: max index value
        """
        cls.index.set_prop("data", max=max_index)


class EditPointTool(InteractiveTool):
    """Curve point edition tool

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use . Defaults to DefaultToolbarID.
        title: Tool name. Defaults to None.
        icon: Tool icon path. Defaults to None.
        tip: Available tip. Defaults to None.
        switch_to_default_tool: Wether to use as the default tool or not.
         Defaults to None.
        end_callback: Callback function taking a Self instance as argument that will
        be passed when the user stops dragging the point. Defaults to None.
    """

    TITLE = _("Edit point")
    ICON = "edit_point_selection.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = QC.Qt.CursorShape.PointingHandCursor

    def __init__(
        self,
        manager: PlotManager,
        toolbar_id=DefaultToolbarID,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
        switch_to_default_tool: bool | None = None,
        end_callback: Callable[[EditPointTool], Any] | None = None,
    ) -> None:
        super().__init__(manager, toolbar_id, title, icon, tip, switch_to_default_tool)
        self.__x: np.ndarray | None = None
        self.__y: np.ndarray | None = None
        self.__x_bkp: np.ndarray | None = None
        self.__y_bkp: np.ndarray | None = None
        self.__current_location_marker: Marker | None = None
        self.__idx: int = 0
        self.__dsampled_idx: int = 0
        self.__lower_upper_x_bounds: tuple[float, float] = 0, 0
        self.marker_style_sect = self.MARKER_STYLE_SECT
        self.marker_style_key = self.MARKER_STYLE_KEY
        self.__indexed_changes: dict[CurveItem, dict[int, tuple[float, float]]] = {}
        self.__selection_threshold: float = 0.0
        self.end_callback = end_callback
        self.__dsampling = 1  # synchronized with the active CurveItem
        self.__curve_item_array_backup: dict[
            CurveItem, tuple[np.ndarray, np.ndarray]
        ] = {}
        self.dragging_point = False

    def set_marker_style(self, marker: Marker) -> None:
        """Configure marker style

        Args:
            marker: Marker instance
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def __get_selection_threshold(self, filter: StatefulEventFilter) -> float:
        """Computes a distance threshold from the current point selected (self._x,
        self._y) and the previous and next curve points. This threshold can be used to
        know if the user is close enough to the selected point to be allowed to move it.
        The threshold will be larger if the curve points are far from each other and
        lower if they are closer (locally adjusted).

        Args:
            filter: StatefulEventFilter instance

        Returns:
            Selection threshold (distance)
        """
        curve_item = self.__get_active_curve_item(filter)
        # Check if a point has been selected
        if self.__x is not None and self.__y is not None:
            # get previous and next curve points coordinates with bound checking
            lower_index_bound = max(self.__dsampled_idx - 1, 0)
            higher_index_bound = min(
                self.downsampled_x.shape[0], self.__dsampled_idx + 2
            )

            # Get x and y arrays of neigboring points (at coordinates i-1, i, i+1)
            axes_x_points = self.downsampled_x[lower_index_bound:higher_index_bound]
            axes_y_points = self.downsampled_y[lower_index_bound:higher_index_bound]

            # Create empty array where axes coordinates will be converted to canvas
            # coordinates
            canva_x_points, canva_y_points = (
                np.zeros(axes_x_points.size),
                np.zeros(axes_x_points.size),
            )

            # Convert axes coordinates to canvas coordinates
            for i, (x, y) in enumerate(zip(axes_x_points, axes_y_points)):
                new_x, new_y = axes_to_canvas(curve_item, x, y) or (None, None)
                assert new_x is not None and new_y is not None
                canva_x_points[i], canva_y_points[i] = new_x, new_y
            # computes the delta between the current point and its neighbors
            dx, dy = np.ediff1d(canva_x_points), np.ediff1d(canva_y_points)
            # returns the mean distance between the current point and its neighbors
            return np.linalg.norm((dx, dy), axis=0).min() / 2
        return 0.0

    def setup_filter(self, baseplot: BasePlot) -> StatefulEventFilter:
        """Setup event filter

        Args:
            baseplot: BasePlot instance

        Returns:
            StatefulEventFilter instance
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()

        drag_handler = QtDragHandler(
            filter, btn=QC.Qt.MouseButton.LeftButton, start_state=start_state
        )
        drag_handler.SIG_START_TRACKING.connect(self.start)
        drag_handler.SIG_MOVE.connect(self.move_point)
        drag_handler.SIG_STOP_MOVING.connect(self.stop)
        drag_handler.SIG_STOP_NOT_MOVING.connect(self.stop)

        undo_key_match = StandardKeyMatch(QG.QKeySequence.StandardKey.Undo)
        filter.add_event(
            start_state, undo_key_match, self.undo_curve_modifications, start_state
        )

        insert_keys_match = KeyEventMatch(
            ((QC.Qt.Key.Key_I, QC.Qt.KeyboardModifier.ControlModifier),)
        )
        filter.add_event(
            start_state,
            insert_keys_match,
            self.insert_point_at_selection,
            start_state,
        )

        return setup_standard_tool_filter(filter, start_state)

    def undo_curve_modifications(
        self, filter: StatefulEventFilter, _event: QC.QEvent | None
    ) -> None:
        """Undo all curve modifications

        Args:
            filter: StatefulEventFilter instance
            _event: Event instance
        """
        curve_item = self.__get_active_curve_item(filter)
        x_arr, y_arr = self.__curve_item_array_backup.get(curve_item, (None, None))
        if (
            x_arr is not None
            and y_arr is not None
            and self.__x is not None
            and self.__y is not None
        ):
            self.__x, self.__y = x_arr, y_arr
            curve_item.set_data(x_arr, y_arr)
            filter.plot.replot()
            self.__get_current_marker(filter).detach()
            self.__current_location_marker = None
            self.__x = self.__y = None
            self.__indexed_changes.get(curve_item, {}).clear()
            self.__idx = self.__dsampled_idx = 0

    def trigger_insert_point_at_selection(self) -> None:
        """Trigger insert point at selection"""
        plot: BasePlot | None = self.get_active_plot()
        if plot is None:
            return
        self.insert_point_at_selection(plot.filter, None)

    def insert_point_at_selection(
        self, filter: StatefulEventFilter, _event: QC.QEvent | None = None
    ) -> None:
        """Insert point at selection

        Args:
            filter: StatefulEventFilter instance
            _event: Event instance
        """
        curve_item = self.__get_active_curve_item(filter)
        if (
            self.__current_location_marker is None
            or self.__y is None
            or self.__x is None
        ):
            QW.QMessageBox.warning(
                filter.plot,
                _("Insert point"),
                _(
                    "Before inserting a new point, "
                    "please select an existing curve point."
                ),
            )
            return

        param = InsertionDataSet(title=_("Insert new value"), icon="insert.png")
        param.set_max_index(self.__x.size - 1)
        param.index = self.__idx
        param.value = self.__y[self.__idx - 1 : self.__idx + 1].mean()

        if param.edit() or execenv.unattended:
            insertion_index: int = param.index + param.index_offset  # type: ignore
            new_x: float = self.__x[insertion_index - 1 : insertion_index + 1].mean()
            self.__x = np.insert(self.__x, insertion_index, new_x)  # type: ignore
            self.__y = np.insert(self.__y, insertion_index, param.value)  # type: ignore
            curve_item.set_data(self.__x, self.__y)
            new_pos = axes_to_canvas(curve_item, new_x, param.value)  # type: ignore
            self.__current_location_marker.move_local_point_to(
                0,
                QC.QPointF(*new_pos),  # type: ignore
            )

    def __get_active_curve_item(self, filter: StatefulEventFilter) -> CurveItem:
        """Get active curve item. Simple method to avoid type checking errors.

        Args:
            filter: StatefulEventFilter instance

        Returns:
            curve item
        """
        assert isinstance(
            curve_item := filter.plot.get_last_active_item(ICurveItemType), CurveItem
        )
        return curve_item

    def __get_current_marker(self, filter: StatefulEventFilter) -> Marker:
        """Returns a marker instance. If the marker does not exist, it is created and
        returns it.

        Args:
            filter: StatefulEventFilter instance

        Returns:
            Marker instance
        """
        return self.__current_location_marker or self.__init_current_marker(filter)

    def __get_x_bounds(self, x_array: np.ndarray, index: int) -> tuple[float, float]:
        """Returns the x values of the previous and next points and performs an out
        of bound check in case the given index is the first or last of the array.

        Args:
            x_array: X array
            index: Index

        Returns:
            X bounds
        """
        lower_bound_index = max(index - 1, 0)
        upper_bound_index = min(x_array.size - 1, index + 1)
        return x_array[lower_bound_index], x_array[upper_bound_index]

    @property
    def downsampled_x(self) -> np.ndarray:
        """Downsampled x array"""
        assert self.__x is not None
        if self.__dsampling > 1:
            return self.__x[:: self.__dsampling]
        return self.__x

    @property
    def downsampled_y(self) -> np.ndarray:
        """Downsampled y array"""
        assert self.__y is not None
        if self.__dsampling > 1:
            return self.__y[:: self.__dsampling]
        return self.__y

    def start(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Start tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self.dragging_point = False
        curve_item = self.__get_active_curve_item(filter)
        if self.__current_location_marker is not None:
            self.__current_location_marker.detach()
            self.__current_location_marker = None
        if curve_item is not None:
            curve_x, curve_y = curve_item.get_data()
            self.__curve_item_array_backup.setdefault(curve_item, (curve_x, curve_y))
            if self.__x is not curve_x or self.__x is None or self.__y is not curve_y:
                self.__x, self.__y = curve_x.copy(), curve_y.copy()

            self.__dsampling: int = (
                1 if not curve_item.param.use_dsamp else curve_item.param.dsamp_factor
            )  # type: ignore
            self.__current_location_marker = self.__get_current_marker(filter)
            self.__current_location_marker.move_local_point_to(0, event.pos())
            x_value = self.__current_location_marker.xValue()
            self.__dsampled_idx = min(
                int(np.searchsorted(self.downsampled_x, x_value)),
                len(self.downsampled_x) - 1,
            )
            self.__idx = self.__dsampled_idx * self.__dsampling  # type: ignore
            self.__lower_upper_x_bounds = self.__get_x_bounds(curve_x, self.__idx)
            self.__selection_threshold = self.__get_selection_threshold(filter)
            filter.plot.replot()

    def move_point(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move point

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self.__current_location_marker = self.__get_current_marker(filter)
        curve_item = self.__get_active_curve_item(filter)
        drag_cursor_pos: QC.QPoint = event.pos()
        new_x, new_y = canvas_to_axes(curve_item, drag_cursor_pos) or (None, None)
        marker_canva_x, marker_canva_y = axes_to_canvas(
            curve_item, *self.__current_location_marker.get_pos()
        ) or (0.0, 0.0)

        cursor_distance_to_marker = float(
            np.linalg.norm(
                (
                    marker_canva_x - drag_cursor_pos.x(),
                    marker_canva_y - drag_cursor_pos.y(),
                )
            )
        )

        if (
            new_x is not None
            and new_y is not None
            and cursor_distance_to_marker < self.__selection_threshold
        ):
            self.dragging_point = True
            self.__selection_threshold = 10_000
            new_x = min(
                max(self.__lower_upper_x_bounds[0], new_x),
                self.__lower_upper_x_bounds[1],
            )

            assert self.__x is not None and self.__y is not None
            (
                self.downsampled_x[self.__dsampled_idx],
                self.downsampled_y[self.__dsampled_idx],
            ) = (new_x, new_y)
            curve_item.set_data(self.__x, self.__y)

            self.__current_location_marker.constraint_cb = (
                self.__current_location_marker.center_handle
            )
            marker_x, marker_y = axes_to_canvas(curve_item, new_x, new_y) or (0, 0)
            self.__current_location_marker.move_local_point_to(
                0, QC.QPointF(marker_x, marker_y)
            )
            filter.plot.replot()

    def stop(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Stop tool action and save new x and y coordinates.

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        if self.dragging_point:
            self.move_point(filter, event)
        self.dragging_point = False

        curve_item = self.__get_active_curve_item(filter)
        if not (isinstance(self.__x, np.ndarray) and isinstance(self.__y, np.ndarray)):
            return

        self.__x_bkp, self.__y_bkp = self.__curve_item_array_backup[curve_item]
        if self.__idx < self.__x_bkp.size and (
            self.__x[self.__idx] != self.__x_bkp[self.__idx]
            or self.__y[self.__idx] != self.__y_bkp[self.__idx]
        ):
            self.__indexed_changes.setdefault(curve_item, {})[self.__idx] = (
                self.__x[self.__idx],
                self.__y[self.__idx],
            )
        if self.end_callback is not None:
            self.end_callback(self)

    def __init_current_marker(
        self,
        filter: StatefulEventFilter,
    ) -> Marker:
        """Initialize current marker

        Args:
            filter: StatefulEventFilter instance

        Returns:
            Marker instance
        """
        plot = filter.plot
        marker = Marker(
            label_cb=lambda x, y: f"{x=:.4f}, {y=:.4f}",
            constraint_cb=plot.on_active_curve,
        )
        marker.set_style(self.marker_style_sect, self.marker_style_key)
        marker.attach(filter.plot)
        marker.setZ(plot.get_max_z() + 1)
        marker.setVisible(True)
        return marker

    def get_changes(self) -> dict[CurveItem, dict[int, tuple[float, float]]]:
        """Get changes"""
        return self.__indexed_changes

    def get_arrays(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Get arrays"""
        return self.__x, self.__y

    def get_initial_arrays(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Get initial arrays"""
        return self.__x_bkp, self.__y_bkp

    def reset_arrays(self) -> None:
        """Reset tool arrays to initial values and reset curve item data"""
        self.__x = self.__y = None
        for curve_item, (x_arr, y_arr) in self.__curve_item_array_backup.items():
            curve_item.set_data(x_arr, y_arr)
        self.__indexed_changes.clear()


class DownSamplingTool(ToggleTool):
    """Downsample curve tool

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use . Defaults to DefaultToolbarID.
    """

    def __init__(self, manager: PlotManager) -> None:
        super().__init__(manager, _("Downsample"))
        # No icon here, on purpose (because, on Windows, the toggle state is not
        # clearly visible with the icon in the context menu)

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """Activate tool

        Args:
            plot: BasePlot instance
            checked: Wether the tool is checked or not
        """
        curve_item: CurveItem | None = plot.get_last_active_item(ICurveItemType)
        if curve_item is not None:
            curve_item.param.use_dsamp = checked
            curve_item.update_params()

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status

        Args:
            plot: BasePlot instance
        """
        item: CurveItem | None = plot.get_last_active_item(ICurveItemType)
        self.action.setEnabled(item is not None)
        if item is not None and self.action is not None:
            self.action.setChecked(item.param.use_dsamp)


def export_curve_data(item: CurveItem) -> None:
    """Export curve item data to text file

    Args:
        item: curve item
    """
    item_data = item.get_data()
    if len(item_data) > 2:
        x, y, dx, dy = item_data
        array_list = [x, y]
        if dx is not None:
            array_list.append(dx)
        if dy is not None:
            array_list.append(dy)
        data = np.array(array_list).T
    else:
        x, y = item_data
        data = np.array([x, y]).T
    plot = item.plot()
    title = _("Export")
    if item.param.label:
        title += f" ({item.param.label})"
    fname, _f = QW.QFileDialog.getSaveFileName(
        plot, title, "", _("Text file") + " (*.txt)"
    )
    if fname:
        try:
            np.savetxt(str(fname), data, delimiter=",")
        except RuntimeError as error:
            QW.QMessageBox.critical(
                plot,
                _("Export"),
                _("Unable to export item data.")
                + "<br><br>"
                + _("Error message:")
                + "<br>"
                + str(error),
            )


def edit_curve_data(item: CurveItem) -> None:
    """Edit curve item data in array editor

    Args:
        item: curve item
    """
    item_data = item.get_data()
    if len(item_data) > 2:
        x, y, dx, dy = item_data
        array_list = [x, y]
        if dx is not None:
            array_list.append(dx)
        if dy is not None:
            array_list.append(dy)
        data = np.array(array_list).T
    else:
        x, y = item_data
        data = np.array([x, y]).T

    dialog = ArrayEditor(item.plot())
    dialog.setup_and_check(data)
    if dialog.exec_():
        if data.shape[1] > 2:
            if data.shape[1] == 3:
                x, y, tmp = data.T
                if dx is not None:
                    dx = tmp
                else:
                    dy = tmp
            else:
                x, y, dx, dy = data.T
            item.set_data(x, y, dx, dy)
        else:
            x, y = data.T
            item.set_data(x, y)
