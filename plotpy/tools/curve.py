# -*- coding: utf-8 -*-

"""Curve tools"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any, Callable

import numpy as np
from guidata.dataset import ChoiceItem, DataSet, FloatItem, IntItem
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
from plotpy.items import Marker, XRangeSelection
from plotpy.items.curve.base import CurveItem
from plotpy.plot.base import BasePlot
from plotpy.tools.base import DefaultToolbarID, InteractiveTool, ToggleTool
from plotpy.tools.cursor import BaseCursorTool

if TYPE_CHECKING:
    from plotpy.plot.manager import PlotManager


class CurveStatsTool(BaseCursorTool):
    """Curve statistics tool

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
    SWITCH_TO_DEFAULT_TOOL = True

    def __init__(
        self, manager, toolbar_id=DefaultToolbarID, title=None, icon=None, tip=None
    ):
        super().__init__(manager, toolbar_id, title=title, icon=icon, tip=tip)
        self._last_item = None
        self.label = None

    def get_last_item(self) -> CurveItem | None:
        """Get last item on which the tool was used"""
        if self._last_item is not None:
            return self._last_item()
        return None

    def create_shape(self) -> XRangeSelection:
        """Create shape associated with the tool"""
        return XRangeSelection(0, 0)

    def move(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        super().move(filter, event)

        # The following import is here to avoid circular imports
        # pylint: disable=import-outside-toplevel
        from plotpy.builder import make

        if self.label is None:
            plot = filter.plot
            curve = self.get_associated_item(plot)

            self.label = make.computations(
                self.shape,
                "TL",
                [
                    (
                        curve,
                        "%g &lt; x &lt; %g",
                        lambda *args: (args[0].min(), args[0].max()),
                    ),
                    (
                        curve,
                        "%g &lt; y &lt; %g",
                        lambda *args: (args[1].min(), args[1].max()),
                    ),
                    (curve, "&lt;y&gt;=%g", lambda *args: args[1].mean()),
                    (curve, "σ(y)=%g", lambda *args: args[1].std()),
                    (curve, "∑(y)=%g", lambda *args: np.trapz(args[1])),
                    (curve, "∫ydx=%g", lambda *args: np.trapz(args[1], args[0])),
                ],
            )
            self.label.attach(plot)
            self.label.setZ(plot.get_max_z() + 1)
            self.label.setVisible(True)

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

    def get_associated_item(self, plot: BasePlot) -> CurveItem | None:
        """Get associated item

        Args:
            plot: BasePlot instance

        Returns:
            curve item or None
        """
        items = plot.get_selected_items(item_type=ICurveItemType)
        if len(items) == 1:
            self._last_item = weakref.ref(items[0])
        return self.get_last_item()

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status

        Args:
            plot: BasePlot instance
        """
        item = self.get_associated_item(plot)
        self.action.setEnabled(item is not None)


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
    """Curve points selection tool"""

    TITLE = _("Multi-point selection")
    ICON = "multipoint_selection2.png"
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
    ):
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
        if not isinstance(plot, BasePlot):
            return None
        if force_new_marker or self.current_location_marker is None:
            title = title or f"<b>{self.TITLE} {len(self.markers)}</b><br>"
            constraint_cb = plot.on_active_curve if self.on_active_item else None

            label_cb = self._new_label_cb(filter, title)
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
        self.current_location_marker.label_cb = self._new_label_cb(
            filter, index=len(self.markers) + 1
        )

    def move(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        plot = filter.plot
        if not isinstance(plot, BasePlot):
            return None
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
            marker.label_cb = self._new_label_cb(filter, index=i + 1)

    def _new_label_cb(
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

    def get_coordinates(self) -> tuple[tuple[float, float], ...] | None:
        """Get all selected coordinates"""
        return tuple(self.markers.keys())


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
    ICON = "edit_point_selection2.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = QC.Qt.CursorShape.PointingHandCursor

    class InsertionDataSet(DataSet):
        """Insertion parameters"""

        __index = IntItem(_("Insertion index"), min=0)
        index = __index
        value = FloatItem(_("New value"))
        index_offset = ChoiceItem(_("Location"), choices=["Before", "After"], default=0)

        @classmethod
        def set_max_index(cls, max_index: int):
            cls.index.set_prop("data", max=max_index)

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
        self._x: np.ndarray | None = None
        self._y: np.ndarray | None = None
        self._x_bkp: np.ndarray | None = None
        self._y_bkp: np.ndarray | None = None
        self._current_location_marker: Marker | None = None
        self._index: int = 0
        self._downsampled_index: int = 0
        self._lower_upper_x_bounds: tuple[float, float] = 0, 0
        self.marker_style_sect = self.MARKER_STYLE_SECT
        self.marker_style_key = self.MARKER_STYLE_KEY
        self._indexed_changes: dict[CurveItem, dict[int, tuple[float, float]]] = {}
        self._selection_threshold: float = 0.0
        self.end_callback = end_callback
        self._downsampling = 1  # synchronized with the active CurveItem
        self._curve_item_array_backup: dict[
            CurveItem, tuple[np.ndarray, np.ndarray]
        ] = {}
        self.dragging_point = False

    def set_marker_style(self, marker: Marker) -> None:
        """Configure marker style

        Args:
            marker: Marker instance
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def _get_selection_threshold(self, filter: StatefulEventFilter) -> float:
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
        curve_item = self._get_active_curve_item(filter)
        # Check if a point has been selected
        if self._x is not None and self._y is not None:
            # get previous and next curve points coordinates with bound checking
            lower_index_bound = max(self._downsampled_index - 1, 0)
            higher_index_bound = min(
                self.downsampled_x.shape[0], self._downsampled_index + 2
            )

            # Get x and y arrays of neigboring points (at coordinates i-1, i, i+1)
            axes_x_points = self.downsampled_x[lower_index_bound:higher_index_bound]
            axes_y_points = self.downsampled_y[lower_index_bound:higher_index_bound]

            # Create empty array where axes coordinates will be converted to canvas
            # coordinates
            canva_x_points, canva_y_points = np.zeros(axes_x_points.size), np.zeros(
                axes_x_points.size
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
        curve_item = self._get_active_curve_item(filter)
        x_arr, y_arr = self._curve_item_array_backup.get(curve_item, (None, None))
        if (
            x_arr is not None
            and y_arr is not None
            and self._x is not None
            and self._y is not None
        ):
            self._x, self._y = x_arr, y_arr
            curve_item.set_data(x_arr, y_arr)
            self._get_plot(filter).replot()
            self._get_current_marker(filter).detach()
            self._current_location_marker = None
            self._x = self._y = None
            self._indexed_changes.get(curve_item, {}).clear()
            self._index = self._downsampled_index = 0

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
        curve_item = self._get_active_curve_item(filter)
        if self._current_location_marker is None or self._y is None or self._x is None:
            QW.QMessageBox.warning(
                self._get_plot(filter),
                "Point not selected",
                "Please select a curve point with a left click.",
            )
            return

        insertion_dataset = self.InsertionDataSet(
            title=_("Insert new value"), icon="insert.png"
        )
        insertion_dataset.set_max_index(self._x.size - 1)
        insertion_dataset.index = self._index
        insertion_dataset.value = self._y[self._index - 1 : self._index + 1].mean()
        insertion_dataset.edit()

        insertion_index: int = insertion_dataset.index + insertion_dataset.index_offset  # type: ignore
        new_x: float = self._x[insertion_index - 1 : insertion_index + 1].mean()
        self._x = np.insert(self._x, insertion_index, new_x)  # type: ignore
        self._y = np.insert(
            self._y, insertion_index, insertion_dataset.value  # type: ignore
        )
        curve_item.set_data(self._x, self._y)
        new_pos = axes_to_canvas(curve_item, new_x, insertion_dataset.value)  # type: ignore
        self._current_location_marker.move_local_point_to(
            0, QC.QPointF(*new_pos)  # type: ignore
        )

    def _get_plot(self, filter: StatefulEventFilter) -> BasePlot:
        """Get plot. Simple method to avoid type checking errors

        Args:
            filter: StatefulEventFilter instance

        Returns:
            BasePlot instance
        """
        assert isinstance(plot := filter.plot, BasePlot)
        return plot

    def _get_active_curve_item(self, filter: StatefulEventFilter) -> CurveItem:
        """Get active curve item. Simple method to avoid type checking errors.

        Args:
            filter: StatefulEventFilter instance

        Returns:
            curve item
        """
        plot = self._get_plot(filter)
        assert isinstance(
            curve_item := plot.get_last_active_item(ICurveItemType), CurveItem
        )
        return curve_item

    def _get_current_marker(self, filter: StatefulEventFilter) -> Marker:
        """Returns a marker instance. If the marker does not exist, it is created and
        returns it.

        Args:
            filter: StatefulEventFilter instance

        Returns:
            Marker instance
        """
        return self._current_location_marker or self._init_current_marker(filter)

    def _get_x_bounds(self, x_array: np.ndarray, index: int) -> tuple[float, float]:
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
        assert self._x is not None
        if self._downsampling > 1:
            return self._x[:: self._downsampling]
        return self._x

    @property
    def downsampled_y(self) -> np.ndarray:
        """Downsampled y array"""
        assert self._y is not None
        if self._downsampling > 1:
            return self._y[:: self._downsampling]
        return self._y

    def start(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Start tool action

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self.dragging_point = False
        curve_item = self._get_active_curve_item(filter)
        if self._current_location_marker is not None:
            self._current_location_marker.detach()
            self._current_location_marker = None
        if curve_item is not None:
            curve_x, curve_y = curve_item.get_data()
            self._curve_item_array_backup.setdefault(curve_item, (curve_x, curve_y))
            if self._x is not curve_x or self._x is None or self._y is not curve_y:
                self._x, self._y = curve_x.copy(), curve_y.copy()

            self._downsampling: int = (
                1
                if not curve_item.param.use_downsampling
                else curve_item.param.downsampling_factor
            )  # type: ignore
            self._current_location_marker = self._get_current_marker(filter)
            self._current_location_marker.move_local_point_to(0, event.pos())
            x_value = self._current_location_marker.xValue()
            self._downsampled_index = int(np.searchsorted(self.downsampled_x, x_value))
            self._index = self._downsampled_index * self._downsampling  # type: ignore
            self._lower_upper_x_bounds = self._get_x_bounds(curve_x, self._index)
            self._selection_threshold = self._get_selection_threshold(filter)
            self._get_plot(filter).replot()

    def move_point(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Move point

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        self._current_location_marker = self._get_current_marker(filter)
        curve_item = self._get_active_curve_item(filter)
        drag_cursor_pos: QC.QPoint = event.pos()
        new_x, new_y = canvas_to_axes(curve_item, drag_cursor_pos) or (None, None)
        marker_canva_x, marker_canva_y = axes_to_canvas(
            curve_item, *self._current_location_marker.get_pos()
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
            and cursor_distance_to_marker < self._selection_threshold
        ):
            self.dragging_point = True
            self._selection_threshold = 10_000
            new_x = min(
                max(self._lower_upper_x_bounds[0], new_x), self._lower_upper_x_bounds[1]
            )

            assert self._x is not None and self._y is not None
            (
                self.downsampled_x[self._downsampled_index],
                self.downsampled_y[self._downsampled_index],
            ) = (new_x, new_y)
            curve_item.set_data(self._x, self._y)

            self._current_location_marker.constraint_cb = (
                self._current_location_marker.center_handle
            )
            marker_x, marker_y = axes_to_canvas(curve_item, new_x, new_y) or (0, 0)
            self._current_location_marker.move_local_point_to(
                0, QC.QPointF(marker_x, marker_y)
            )
            self._get_plot(filter).replot()

    def stop(self, filter: StatefulEventFilter, event: QG.QMouseEvent) -> None:
        """Stop tool action and save new x and y coordinates.

        Args:
            filter: StatefulEventFilter instance
            event: Qt mouse event
        """
        if self.dragging_point:
            self.move_point(filter, event)
        self.dragging_point = False

        curve_item = self._get_active_curve_item(filter)
        if not (isinstance(self._x, np.ndarray) and isinstance(self._y, np.ndarray)):
            return

        backup_x_arr, backup_y_arr = self._curve_item_array_backup[curve_item]
        if self._index < backup_x_arr.size and (
            self._x[self._index] != backup_x_arr[self._index]
            or self._y[self._index] != backup_y_arr[self._index]
        ):
            self._indexed_changes.setdefault(curve_item, {})[self._index] = (
                self._x[self._index],
                self._y[self._index],
            )
        if self.end_callback is not None:
            self.end_callback(self)

    def _init_current_marker(
        self,
        filter: StatefulEventFilter,
    ) -> Marker:
        """Initialize current marker

        Args:
            filter: StatefulEventFilter instance

        Returns:
            Marker instance
        """
        plot = self._get_plot(filter)
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
        return self._indexed_changes

    def get_arrays(self) -> tuple[np.ndarray| None, np.ndarray | None]:
        """Get arrays"""
        return self._x, self._y

    def get_initial_arrays(self) -> tuple[np.ndarray| None, np.ndarray | None]:
        """Get initial arrays"""
        return self._x_bkp, self._y_bkp

    def reset_arrays(self) -> None:
        """Reset tool arrays to initial values and reset curve item data"""
        self._x = self._y = None
        for curve_item, (x_arr, y_arr) in self._curve_item_array_backup.items():
            curve_item.set_data(x_arr, y_arr)
        self._indexed_changes.clear()


class DownSampleCurveTool(ToggleTool):
    """Downsample curve tool

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use . Defaults to DefaultToolbarID.
    """

    def __init__(self, manager, toolbar_id=DefaultToolbarID) -> None:
        super().__init__(
            manager,
            _("Downsample curves"),
            icon="curve_downsample2.png",
            toolbar_id=toolbar_id,
        )

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """Activate tool

        Args:
            plot: BasePlot instance
            checked: Wether the tool is checked or not
        """
        curve_item: CurveItem | None = plot.get_last_active_item(
            ICurveItemType
        )  # type: ignore
        if curve_item is not None:
            curve_item.param.use_downsampling = checked
            curve_item.update_data()
            plot.replot()

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status

        Args:
            plot: BasePlot instance
        """
        curve_item: CurveItem | None = plot.get_last_active_item(
            ICurveItemType
        )  # type: ignore
        if curve_item is not None and self.action is not None:
            self.action.setChecked(curve_item.param.use_downsampling)
            curve_item.update_data()
            plot.replot()


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
