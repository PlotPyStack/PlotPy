# -*- coding: utf-8 -*-
import weakref
from email.mime import base
from sre_parse import State
from turtle import update
from typing import Callable

import numpy as np
from guidata.widgets.arrayeditor import ArrayEditor
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.constants import SHAPE_Z_OFFSET
from plotpy.events import QtDragHandler, StatefulEventFilter, setup_standard_tool_filter
from plotpy.interfaces import ICurveItemType
from plotpy.items import Marker, XRangeSelection
from plotpy.plot.base import BasePlot
from plotpy.tools.base import DefaultToolbarID, InteractiveTool, ToggleTool
from plotpy.tools.cursor import BaseCursorTool


class CurveStatsTool(BaseCursorTool):
    """ """

    TITLE = _("Signal statistics")
    ICON = "xrange.png"
    SWITCH_TO_DEFAULT_TOOL = True

    def __init__(
        self, manager, toolbar_id=DefaultToolbarID, title=None, icon=None, tip=None
    ):
        super().__init__(manager, toolbar_id, title=title, icon=icon, tip=tip)
        self._last_item = None
        self.label = None

    def get_last_item(self):
        """

        :return:
        """
        if self._last_item is not None:
            return self._last_item()

    def create_shape(self):
        """

        :return:
        """

        return XRangeSelection(0, 0)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
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

    def end_move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        super().end_move(filter, event)
        if self.label is not None:
            filter.plot.add_item_with_z_offset(self.label, SHAPE_Z_OFFSET)
            self.label = None

    def get_associated_item(self, plot):
        """

        :param plot:
        :return:
        """
        items = plot.get_selected_items(item_type=ICurveItemType)
        if len(items) == 1:
            self._last_item = weakref.ref(items[0])
        return self.get_last_item()

    def update_status(self, plot):
        """

        :param plot:
        """
        item = self.get_associated_item(plot)
        self.action.setEnabled(item is not None)


class AntiAliasingTool(ToggleTool):
    """ """

    def __init__(self, manager):
        super().__init__(manager, _("Antialiasing (curves)"))

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.set_antialiasing(checked)
        plot.replot()

    def update_status(self, plot):
        """

        :param plot:
        """
        self.action.setChecked(plot.antialiased)


class SelectPointTool(InteractiveTool):
    """ """

    TITLE = _("Point selection")
    ICON = "point_selection.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = QC.Qt.CursorShape.PointingHandCursor

    def __init__(
        self,
        manager,
        mode="reuse",
        on_active_item=False,
        title=None,
        icon=None,
        tip=None,
        end_callback=None,
        toolbar_id=DefaultToolbarID,
        marker_style=None,
        switch_to_default_tool=None,
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
        self.marker = None
        self.last_pos = None
        self.on_active_item = on_active_item
        if marker_style is not None:
            self.marker_style_sect = marker_style[0]
            self.marker_style_key = marker_style[1]
        else:
            self.marker_style_sect = self.MARKER_STYLE_SECT
            self.marker_style_key = self.MARKER_STYLE_KEY

    def set_marker_style(self, marker):
        """

        :param marker:
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
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

    def start(self, filter, event):
        """

        :param filter:
        :param event:
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

    def stop(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.move(filter, event)
        if self.mode != "reuse":
            self.marker.detach()
            self.marker = None
        if self.end_callback:
            self.end_callback(self)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        :return:
        """
        if self.marker is None:
            return  # something is wrong ...
        self.marker.move_local_point_to(0, event.pos())
        filter.plot.replot()
        self.last_pos = self.marker.xValue(), self.marker.yValue()

    def get_coordinates(self):
        """

        :return:
        """
        return self.last_pos


class SelectPointsTool(InteractiveTool):
    """ """

    TITLE = _("Multi-point selection")
    ICON = "point_selection.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = QC.Qt.CursorShape.PointingHandCursor

    def __init__(
        self,
        manager,
        mode="reuse",
        on_active_item=False,
        title=None,
        icon=None,
        tip=None,
        end_callback=None,
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

    def set_marker_style(self, marker):
        """

        :param marker:
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def setup_filter(self, baseplot: BasePlot):
        """

        :param baseplot:
        :return:
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
        event: QC.QEvent,
        force_new_marker=False,
        title: str = "",
    ):
        if force_new_marker or self.current_location_marker is None:
            title = title or f"<b>{self.TITLE} {len(self.markers)}</b><br>"
            if self.on_active_item:
                constraint_cb = filter.plot.on_active_curve

            else:
                constraint_cb = None

            label_cb = self._new_label_cb(filter, title)
            self.current_location_marker = Marker(
                label_cb=label_cb, constraint_cb=constraint_cb
            )
        assert self.current_location_marker
        self.set_marker_style(self.current_location_marker)
        self.current_location_marker.attach(filter.plot)
        self.current_location_marker.setZ(filter.plot.get_max_z() + 1)
        self.current_location_marker.setVisible(True)

    def start_single_selection(self, filter: StatefulEventFilter, event: QC.QEvent):
        """

        :param filter:
        :param event:
        """
        self._init_current_marker(filter, event, force_new_marker=True)

    def start_multi_selection(self, filter: StatefulEventFilter, event: QC.QEvent):
        """

        :param filter:
        :param event:
        """
        self._init_current_marker(filter, event, force_new_marker=True)
        assert self.current_location_marker
        self.current_location_marker.label_cb = self._new_label_cb(
            filter, index=len(self.markers) + 1
        )

    def move(self, filter: StatefulEventFilter, event: QC.QEvent):
        """

        :param filter:
        :param event:
        :return:
        """
        if self.current_location_marker is None:
            return  # something is wrong ...
        self.current_location_marker.move_local_point_to(0, event.pos())
        filter.plot.replot()

    def common_stop(self, filter: StatefulEventFilter, event: QC.QEvent):
        self.move(filter, event)
        if self.mode != "reuse":
            self.current_location_marker.detach()
            self.current_location_marker = None

    def stop_single_selection(self, filter: StatefulEventFilter, event: QC.QEvent):
        """

        :param filter:
        :param event:
        """
        assert self.current_location_marker
        self.common_stop(filter, event)
        # self.clear_markers((self.current_location_marker,))
        self.clear_markers()
        self.toggle_marker(self.current_location_marker)
        self.update_labels(filter)
        if self.end_callback:
            self.end_callback(self)

    def stop_multi_selection(self, filter: StatefulEventFilter, event: QC.QEvent):
        """

        :param filter:
        :param event:
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

    def clear_markers(self, exclude_detach: tuple[Marker, ...] | None = None):
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

    def update_labels(self, filter: StatefulEventFilter):
        for i, marker in enumerate(self.markers.values()):
            marker.label_cb = self._new_label_cb(filter, index=i + 1)

    def _new_label_cb(
        self, filter: StatefulEventFilter, title: str = "", index: int = 1
    ) -> Callable[[float, float], str]:
        title = title or f"<b>{self.TITLE} - {index}</b><br>"
        if self.on_active_item:

            def label_cb(x, y):
                return title + filter.plot.get_coordinates_str(x, y)

        else:

            def label_cb(x, y):
                return f"{title}{' - ' if title else ''}{index} x = {x:g}<br>y = {y:g}"

        return label_cb

    def get_coordinates(self):
        return tuple(self.markers.keys())


def export_curve_data(item):
    """Export curve item data to text file"""
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


def edit_curve_data(item):
    """Edit curve item data in array editor"""
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
