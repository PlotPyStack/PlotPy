# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)
"""This module provides a basic widget to edit a colormap that contains a multi-slider
and a colorap representation.
"""
from __future__ import annotations

from typing import Sequence, TypeVar, Union

import numpy as np
import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW
from guidata.qthelpers import add_actions, create_action
from qwt import QwtInterval, QwtLinearColorMap, toQImage
from qwt.color_map import ColorStop

from plotpy.config import _
from plotpy.widgets._colormap_slider import QColorMapSlider

ColorTypeT = TypeVar("ColorTypeT", bound=Union[QG.QColor, int])
QColorInitTypes = Union[
    QG.QColor, int, tuple[int, int, int, int], str, QC.Qt.GlobalColor, None
]


class CustomQwtLinearColormap(QwtLinearColorMap):
    """Overload of the QwtLinearColorMap class to add some features. This class is
    temporary and should be removed when its features are added to QwtPython.

    Args:
        *args: QwtLinearColorMap arguments
        name: Optional str name given to the colormap. Useful for the interactions
        with the rest of PlotPy, notably with the gobal colormaps dictionnary
        such as colormaps.ALL_COLORMAPS. Defaults to "None".
    """

    def __init__(self, *args, name: str | None = None) -> None:
        super().__init__(*args)
        # TODO: Add this feature in a release of QwtPython
        self.stops: list[
            ColorStop
        ] = (
            self._QwtLinearColorMap__data.colorStops._ColorStops__stops  # pylint: disable=no-member # type: ignore
        )
        self.name = name or "temporary"

    def is_boundary_stop_index(self, stop_index: int) -> bool:
        """Checks if the given index is a boundary index (first or last).

        Args:
            stop_index: stop color index to check

        Returns:
            True if the index is a boundary index, False otherwise.
        """
        return not (
            self._can_update_next_stop(stop_index)
            and self._can_update_previous_stop(stop_index)
        )

    def _can_update_next_stop(self, stop_index: int) -> bool:
        """Checks if the next color stop can be updated.

        Args:
            stop_index: current color stop index

        Returns:
            True if the next color stop can be updated, False otherwise.
        """
        return stop_index < (len(self.stops) - 1)

    def _can_update_previous_stop(self, stop_index: int) -> bool:
        """Checks if the previous color stop can be updated.

        Args:
            stop_index: current color stop index

        Returns:
            True if the previous color stop can be updated, False otherwise.
        """
        return stop_index > 0

    def update_stops_steps(self, stop_index: int) -> None:
        """Updates the steps of the previous and next color stops of the given index.
        The steps are the distance between the current stop and the next color stop.
        This method can update the given color stop index, the previous one and the next
        stop if necessary.

        Args:
            stop_index: current color stop index to update.
        """
        current_stop = self.stops[stop_index]
        if self._can_update_previous_stop(stop_index):
            prev_stop = self.stops[stop_index - 1]
            prev_stop.updateSteps(current_stop)
        if self._can_update_next_stop(stop_index):
            next_stop = self.stops[stop_index + 1]
            current_stop.updateSteps(next_stop)

    @classmethod
    def from_iterable(
        cls, iterable: Sequence[tuple[float, str]], name=None
    ) -> "CustomQwtLinearColormap":
        """Converts the given iterable of tuples to a colormap (instance of Self).
        The iterable must be at least of length 2. If the iterable is of length 1,
        the colormap will be composed of two identical colors. If the iterable is
        empty, the colormap will be composed of two default colors (blue and yellow).

        Args:
            iterable: Iterable of tuples composed of a float position and a hex color
            string.
            name: Name of the new colormap instance. Defaults to None.

        Returns:
            New CustomQwtLinearColormap instance.
        """
        if len(iterable) == 1:
            iterable = (iterable[0],) * 2
        elif len(iterable) == 0:
            iterable = (
                (0.0, QG.QColor(QC.Qt.GlobalColor.blue)),
                (1.0, QG.QColor(QC.Qt.GlobalColor.yellow)),
            )

        color_min, color_max = iterable[0][1], iterable[-1][1]
        colormap = cls(color_min, color_max, name=name)

        pos_min, pos_max = iterable[0][0], iterable[-1][0]
        for position, color in iterable[1:-1]:
            scaled_position = (position - pos_min) / pos_max
            colormap.addColorStop(scaled_position, color)
        return colormap

    def to_tuples(self) -> tuple[tuple[float, str], ...]:
        """Converts a colormap to a tuple of tuples composed of a float position and a
        hex color string.

        Returns:
            Tuple of tuples composed of a float position and a hex color string.
        """
        return tuple((stop.pos, QG.QColor(stop.rgb).name()) for stop in self.stops)

    def move_color_stop(
        self, stop_index: int, new_pos: float, new_color: QG.QColor | None = None
    ) -> None:
        """Moves a color stop to a new position and updates the steps of the previous
        and next color stops if necessary. Mutates the colormap object!

        Args:
            stop_index: color stop index to move
            new_pos: new color stop position
            new_color: new color stop color. If None, will use the current stop color.
            Defaults to None.
        """
        try:
            stop: ColorStop | None = self.stops[stop_index]
        except IndexError as e:
            print(e)
            return

        if stop is None:
            print("No Colorstops set, aborting edition.")
            return

        new_color = new_color or QG.QColor(stop.rgb)
        new_stop = ColorStop(new_pos, new_color)
        self.stops[stop_index] = new_stop
        self.update_stops_steps(stop_index)

    def delete_stop(self, stop_index: int) -> None:
        """Deletes the color stop at given index and updates the previous color stop
        steps if necessary. Mutates the colormap object!

        Args:
            stop_index: color stop index to delete
        """
        if not self.is_boundary_stop_index(stop_index):
            self.stops.pop(stop_index)
            self.stops[stop_index - 1].updateSteps(self.stops[stop_index])

    def setColorInterval(
        self, color1: QColorInitTypes, color2: QColorInitTypes
    ) -> None:
        """Overload of QwtLinearColorMap.setColorInterval to update the stops list
        attribute.

        Args:
            color1: first color of the interval
            color2: last color of the interval
        """
        super().setColorInterval(color1, color2)
        self.stops: list[
            ColorStop
        ] = self._QwtLinearColorMap__data.colorStops._ColorStops__stops  # type: ignore

    def get_stop_color(self, index: int) -> QG.QColor:
        """Returns the color of the given color stop index.

        Args:
            index: color stop index

        Returns:
            Color of the given color stop index.
        """
        index = min(index, len(self.stops))
        return QG.QColor(self.stops[index].rgb)


class ColorMapWidget(QW.QWidget):
    """Simple colormap widget containing a horizontal slider and a colorbar image.
    The slider is used to edit the colormap that changes in real time. It is
    possible to add/remove handles by right-clicking on the colorbar image. This
    widget does not provide a way to change a handle color. For this, use the
    ColorMapEditor widget or the ColorMapManager widget.

    Args:
        parent: parent widget
        cmap_width: minimum width of the widget. Defaults to 400.
        cmap_height: minimum height of the colorbar. Defaults to 50.
        color1: first color. Ignored if the 'colormap' argument is used. If None,
            default color is blue. Defaults to None.
        color2: second color. Ignored if the 'colormap' argument is used. If None,
            default color is yellow. Defaults to None.
        colormap: colormap instance. If None, color1 and color2 will be used
            to create a new colormap. Defaults to None.
    """

    COLORMAP_CHANGED = QC.Signal()  # type: ignore
    HANDLE_SELECTED = QC.Signal(int)  # type: ignore
    # handleReleased = QC.Signal(int)  # type: ignore
    HANDLE_ADDED = QC.Signal(int, float)  # type: ignore
    HANDLE_DELETED = QC.Signal(int)  # type: ignore

    def __init__(
        self,
        parent: QW.QWidget | None,
        cmap_width: int = 400,
        cmap_height: int = 50,
        color1: QG.QColor | None = None,
        color2: QG.QColor | None = None,
        colormap: CustomQwtLinearColormap | None = None,
    ) -> None:
        super().__init__(parent)

        self.cmap_width = cmap_width
        self.cmap_height = cmap_height
        self.min, self.max = 0.0, 1.0
        self._tolerance = 0.05
        self._px_cursor_offset = 0  # This is a patch because the cursor position is
        # not exactly the handle position...
        self._handle_selected = None

        self.slider_menu = self.setup_menu()

        multi_range_hslider = QColorMapSlider(QC.Qt.Orientation.Horizontal)
        multi_range_hslider.setTickPosition(QW.QSlider.TickPosition.TicksAbove)
        multi_range_hslider.setBarVisible(False)
        multi_range_hslider.setMinimum(self.min)
        multi_range_hslider.setMaximum(self.max)
        multi_range_hslider.setMaximumHeight(20)
        self.multi_range_hslider = multi_range_hslider
        self.set_handles_values((self.min, self.max))
        self.setContextMenuPolicy(QC.Qt.ContextMenuPolicy.CustomContextMenu)

        self._last_selection: tuple[int, int] = 0, 0

        self.qwt_color_interval = QwtInterval(self.min, self.max)

        if colormap is None:
            color1 = QG.QColor(QC.Qt.GlobalColor.blue) if color1 is None else color1
            color2 = QG.QColor(QC.Qt.GlobalColor.yellow) if color2 is None else color2
            self._colormap = CustomQwtLinearColormap(color1, color2)
        else:
            self._colormap = colormap
            self.set_handles_values(colormap.colorStops())

        self.colortable = self._colormap.colorTable(self.qwt_color_interval)

        colormap_label = QW.QLabel("Stylish colormap widget")
        colormap_label.setScaledContents(True)
        self._colormap_label = colormap_label
        self.draw_colormap_image()

        layout = QW.QVBoxLayout(self)
        layout.addWidget(colormap_label)
        layout.addWidget(multi_range_hslider)
        self.range_layout = layout

        self.setLayout(layout)
        self.setToolTip(_("Right click to add/remove a color"))

        self.COLORMAP_CHANGED.connect(self.draw_colormap_image)
        self.multi_range_hslider.valueChanged.connect(
            self._edit_color_map_on_slider_change
        )
        self.multi_range_hslider.sliderPressed.connect(self.emit_handle_selected)
        self.multi_range_hslider.sliderReleased.connect(self.release_handle)
        self.customContextMenuRequested.connect(self.open_slider_menu)

    def set_colormap(self, colormap: CustomQwtLinearColormap) -> None:
        """Replaces the current colormap.

        Args:
            colormap: replacement colormap
        """
        new_values = colormap.colorStops()
        self._colormap = colormap
        self.set_handles_values(new_values)
        self.COLORMAP_CHANGED.emit()

    def get_colormap(self) -> CustomQwtLinearColormap:
        """Get the current colormap being edited.

        Returns:
            current colormap
        """
        return self._colormap

    def update_color_table(self) -> None:
        """Updates and caches the current color table."""
        self.colortable[:] = self._colormap.colorTable(self.qwt_color_interval)

    def emit_handle_selected(self) -> None:
        """When called, computes a slider position from the current position of the
        mouse and maps it to slider range. Then finds which handles was selected and
        emits the custom signal HANDLE_SELECTED(handle_index) and caches the index."""

        self._handle_selected = self.multi_range_hslider.pressed_index
        self.HANDLE_SELECTED.emit(self._handle_selected)

    def release_handle(self) -> None:
        """When called, unset the cached current handle index."""
        self._handle_selected = None

    def draw_colormap_image(self) -> None:
        """Recomputes and redraws the colorbar image."""
        # TODO: check how to update the image without having to recreate one,
        # just by updating the colortable
        self.update_color_table()
        self._colormap_label.setPixmap(self.cmap_to_qimage())

    def get_color_from_value(
        self, value: float, as_type: type[ColorTypeT] = QG.QColor
    ) -> ColorTypeT:
        """Returns the color assigned to a given value using the current colormap.

        Args:
            value: value to assign a color to
            as_type: Color type to be returned (int or QG.QColor). Defaults to
            QG.QColor.

        Returns:
            The assigned color for the input value using the current colormap.
        """
        int_color = self._colormap.rgb(self.qwt_color_interval, value)
        return as_type(int_color)

    def get_handle_color(
        self, handle_index: int, as_type: type[ColorTypeT] = QG.QColor
    ) -> ColorTypeT:
        """Returns the color of a handled using its index. Directly return the color of
        the ColorStop object of the given index.

        Args:
            handle_index: index of the handled to assign a color too.
            as_type: Color type to be returned (int or QG.QColor). Defaults to
            QG.QColor.

        Returns:
            The assigned color for the input handle index using the current colormap.
        """
        int_color = self._colormap.get_stop_color(handle_index)
        return as_type(int_color)

    def get_hex_color(self, handle_index: int) -> str:
        """Same as self.get_handle_color but returns the color as a hex color string.

        Args:
            handle_index: index of the handled to assign a color too.

        Returns:
            Handle's hex color string
        """
        return self.get_handle_color(handle_index, QG.QColor).name()

    def edit_color_stop(
        self,
        index: int,
        new_pos: float | None = None,
        new_color: QG.QColor | int | None = None,
    ) -> None:
        """Edit an existing color stop in the current colormap. Mutates the colormap
        object. Also edits the slider handle position.

        Args:
            index: color stop index to mutate
            new_pos: new color stop position. If not set will remain the same.
            Defaults to None.
            new_color: new color. If not set will remain the same. Defaults to None.
        """
        if new_pos is None:
            new_pos = self.get_handles_tuple()[index]

        if isinstance(new_color, int):
            new_color = QG.QColor(self.colortable[new_color])

        self._colormap.move_color_stop(index, new_pos, new_color)
        self.set_handles_values(self._colormap.colorStops())
        self.COLORMAP_CHANGED.emit()

    def _edit_color_map_on_slider_change(self, raw_values: tuple[float, ...]) -> None:
        """Modifies the colormap depending on the currently selected handle. Tiggered on
        hanle movement.

        Args:
            raw_values: tuple of handles position
        """
        handle_index = self._handle_selected
        values = self.multi_range_hslider.filter_first_last_positions(raw_values)
        if handle_index is not None:
            handle_pos = values[handle_index]
            if handle_index == 0 or handle_index == len(values):
                return

            self._colormap.move_color_stop(handle_index, handle_pos)
            self.COLORMAP_CHANGED.emit()

    def _get_closest_handle_index(self, pos: float) -> tuple[int, float]:
        """Return the index of the closest handle from the given position

        Args:
            pos: position along the slider axis and coordinate space

        Returns:
            index and distance of the closest point (distance can be negative)
        """
        values = self.get_handles_tuple()
        closest_handle = min(range(len(values)), key=lambda i: abs(values[i] - pos))
        return closest_handle, abs(pos - values[closest_handle])

    def _get_neighbour_positions(self, pos: float) -> tuple[float, float]:
        """Return the positions of the previous and next handles from the given
        position. If no handle is found, the method can return self.min and/or self.max

        Args:
            pos: position from which to look for the previous and next handles

        Returns:
            previous and next handle positions
        """
        values = self.get_handles_tuple()
        previous_pos = max(
            filter(lambda val: val <= pos, values[::-1]), default=self.min
        )
        next_pos = min(filter(lambda val: val > pos, values), default=self.max)

        return previous_pos, next_pos

    def _new_available_pos(self, pos: float) -> float:
        """Computes the most position to insert a new handle. This method takes into
        account the input position, the prefered offset if handles are too close,
        previous and next handles from the current position to output the best position
        possible.

        Args:
            pos: requested position

        Returns:
            Best position for insertion according to parameters cited above.
        """
        previous_pos, next_pos = self._get_neighbour_positions(pos)
        if (neighbour_diff := next_pos - previous_pos) < self._tolerance * 2:
            return previous_pos + (neighbour_diff / 2)

        if (pos - previous_pos) < self._tolerance:
            return previous_pos + self._tolerance

        if (next_pos - pos) < self._tolerance:
            return next_pos - self._tolerance

        return pos

    def _add_handle_at_click(self) -> None:
        """Adds a new handle at last right-clicked position thanks to the attribute
        self._last_selection. Mutates the colormap object.
        """
        x, _ = self._last_selection
        new_handle_value = self.multi_range_hslider.widget_pos_to_value(x)
        values = self.get_handles_list()

        new_handle_value = self._new_available_pos(new_handle_value)
        new_color = self.get_color_from_value(new_handle_value)
        self._colormap.addColorStop(new_handle_value, new_color)
        values.append(new_handle_value)
        values.sort()
        self.set_handles_values(values)
        self.HANDLE_ADDED.emit(values.index(new_handle_value), new_handle_value)

    def _delete_handle_at_click(self) -> None:
        """Tries to delete an existing handle at the right-clicked position thanks to
        the attribute self._last_selection. Does nothing if the click is too far from
        a handle. Mutates the colormap object.
        """
        x, _ = self._last_selection
        values: list[float] = self.get_handles_list()
        x_handle_coor_space = self.multi_range_hslider.widget_pos_to_value(x)
        closest_handle_index, click_distance = self._get_closest_handle_index(
            x_handle_coor_space
        )
        if (
            abs(click_distance) > self._tolerance
            or len(values) <= 2
            or closest_handle_index in (0, len(values) - 1)
        ):
            return
        values.pop(closest_handle_index)
        self.set_handles_values(tuple(values))
        self._colormap.delete_stop(closest_handle_index)

        self.HANDLE_DELETED.emit(closest_handle_index)
        self.COLORMAP_CHANGED.emit()

    def setup_menu(self) -> QW.QMenu:
        """Setups the contextual menu used to insert and delete handles.

        Returns:
            Colorbar contextual menu
        """
        new_handle_action = create_action(
            self,
            title=_("Add new color"),
            icon=None,
            triggered=self._add_handle_at_click,
        )
        delete_handle_action = create_action(
            self,
            title=_("Remove color"),
            icon=None,
            triggered=self._delete_handle_at_click,
        )
        actions = (new_handle_action, delete_handle_action)

        menu = QW.QMenu(self)
        add_actions(menu, actions)
        return menu

    def add_handle_at_relative_pos(
        self, relative_pos: float, new_color: QG.QColor | int | None = None
    ) -> None:
        """insert a handle in the widget at the relative position (between 0. and 1.).
        Mutates the colormap object. If the relative position is already occupied by a
        handle, the new handle will be inserted at the closest available position then
        will be moved back to the requested position.

        Args:
            relative_pos: insertion position
        """

        if new_color is None:
            new_color = self._colormap.color(self.qwt_color_interval, relative_pos)

        new_relative_pos = self._new_available_pos(relative_pos)
        self._colormap.addColorStop(new_relative_pos, new_color)

        values = self.get_handles_list()
        values.append(new_relative_pos)
        values.sort()
        new_value_index = values.index(new_relative_pos)

        self.edit_color_stop(new_value_index, relative_pos, None)
        self.HANDLE_ADDED.emit(new_value_index, relative_pos)

    def get_handles_count(self) -> int:
        """Number of slider handles.

        Returns:
            handles count
        """
        return len(self.multi_range_hslider.value())

    def get_handles_list(self) -> list[float]:
        """Return the current handles as a mutable list. If the data doesn't need to be
        mutated, prefer the method self.get_handles_tuple() that directly returns the
        handles tuple without making a conversion to a list.

        Returns:
            Mutable list of handles position
        """
        return list(self.multi_range_hslider.value())

    def get_handles_tuple(self) -> tuple[float, ...]:
        """Passthrough to get the tuple of handles position.

        Returns:
            Immutable tuple of handles position
        """
        return self.multi_range_hslider.value()

    def set_handles_values(self, values: Sequence[float]) -> None:
        """Passthrough to set handles position.

        Args:
            values: sequence of values with a minimum length of 2 (min and max).
        """
        self.multi_range_hslider.setValue(values)

    def cmap_to_qimage(self) -> QG.QPixmap:
        """Build the horizontal colorab pixmap from the current colormap."""
        data = np.zeros((self.cmap_height, self.cmap_width), np.uint8)
        line = np.linspace(0, 255, self.cmap_width)
        data[:, :] = line[np.newaxis, :]
        img = toQImage(data)
        img.setColorTable(self.colortable)
        return QG.QPixmap.fromImage(img)

    def open_slider_menu(self, pos: QC.QPoint) -> None:
        """Opens the contextual menu at input position.

        Args:
            pos: contextual menu position
        """
        slider_pos = self.multi_range_hslider.mapFrom(self, pos)
        self._last_selection = (
            slider_pos.x(),
            slider_pos.y(),
        )
        glob_pos = self.mapToGlobal(pos)

        self.slider_menu.popup(glob_pos)
