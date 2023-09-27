# -*- coding: utf-8 -*-
import weakref

import numpy as np
from guidata.widgets.objecteditor import oedit
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.events import QtDragHandler, setup_standard_tool_filter
from plotpy.interfaces.common import ICurveItemType
from plotpy.items import Marker, XRangeSelection
from plotpy.tools.base import (
    SHAPE_Z_OFFSET,
    DefaultToolbarID,
    InteractiveTool,
    ToggleTool,
)
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
                label_cb = lambda x, y: title + filter.plot.get_coordinates_str(x, y)
            else:
                constraint_cb = None
                label_cb = lambda x, y: f"{title}x = {x:g}<br>y = {y:g}"
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
    """Edit curve item data to text file"""
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

    if oedit(data) is not None:
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
