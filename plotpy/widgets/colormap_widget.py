# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

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

ColorType = TypeVar("ColorType", bound=Union[QG.QColor, int])


class CustomQwtLinearColormap(QwtLinearColorMap):
    def __init__(self, *args, name: str | None = "None"):
        super().__init__(*args)
        # TODO: Add this feature in a release of QwtPython
        self.stops: list[ColorStop] = self._QwtLinearColorMap__data.colorStops._ColorStops__stops  # type: ignore
        self.name = name or "tmp"

    def is_boundary_stop_index(self, stop_index: int):
        return not (
            self._can_update_next_stop(stop_index)
            and self._can_update_previous_stop(stop_index)
        )

    def _can_update_next_stop(self, stop_index: int) -> bool:
        return stop_index < (len(self.stops) - 1)

    def _can_update_previous_stop(self, stop_index: int) -> bool:
        return stop_index > 0

    def update_stops_steps(self, stop_index: int):
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
        return tuple((stop.pos, QG.QColor(stop.rgb).name()) for stop in self.stops)

    def move_color_stop(
        self, stop_index: int, new_pos: float, new_color: QG.QColor | None = None
    ):
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

    def delete_stop(self, stop_index: int):
        if not self.is_boundary_stop_index(stop_index):
            self.stops.pop(stop_index)
            self.stops[stop_index - 1].updateSteps(self.stops[stop_index])

    def setColorInterval(self, color1, color2) -> None:
        res = super().setColorInterval(color1, color2)
        self.stops: list[
            ColorStop
        ] = self._QwtLinearColorMap__data.colorStops._ColorStops__stops  # type: ignore
        return res


class ColorMapWidget(QW.QWidget):
    colormapChanged = QC.Signal()  # type: ignore
    handleSelected = QC.Signal(int)  # type: ignore
    # handleReleased = QC.Signal(int)  # type: ignore
    handleAdded = QC.Signal(int, float)  # type: ignore
    handleDeleted = QC.Signal(int)  # type: ignore

    def __init__(
        self,
        parent: QW.QWidget | None,
        cmap_width: int = 400,
        cmap_height: int = 50,
        color1: QG.QColor = QG.QColor(QC.Qt.GlobalColor.blue),
        color2: QG.QColor = QG.QColor(QC.Qt.GlobalColor.yellow),
        colormap: CustomQwtLinearColormap | None = None,
    ) -> None:
        super().__init__(parent)

        self.cmap_width = cmap_width
        self.cmap_height = cmap_height
        self.min, self.max = 0.0, 1.0
        self._tolerance = 0.05
        self._px_cursor_offset = 0  # This is a patch because the cursor position is not exactly the handle position...
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
            self.color1, self.color2 = color1, color2
            self._colormap = CustomQwtLinearColormap(self.color1, self.color2)
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

        self.colormapChanged.connect(self.draw_colormap_image)
        self.multi_range_hslider.valueChanged.connect(
            self._edit_color_map_on_slider_change
        )
        self.multi_range_hslider.sliderPressed.connect(self.emit_handle_selected)
        self.multi_range_hslider.sliderReleased.connect(self.release_handle)
        self.customContextMenuRequested.connect(self.open_slider_menu)

        # self.setGeometry(600, 300, 580, 300)
        # self.activateWindow()
        # self.show()

    def setColormap(self, colormap: CustomQwtLinearColormap):
        """Replaces the current colormap.

        Args:
            colormap: replacement colormap
        """
        new_values = colormap.colorStops()
        self._colormap = colormap
        self.set_handles_values(new_values)
        self.colormapChanged.emit()

    def getColormap(self) -> CustomQwtLinearColormap:
        """Get the current colormap being edited.

        Returns:
            current colormap
        """
        return self._colormap

    def update_color_table(self):
        """Updates and caches the current color table."""
        self.colortable[:] = self._colormap.colorTable(self.qwt_color_interval)

    def emit_handle_selected(self):
        """When called, computes a slider position from the current position of the mouse
        and maps it to slider range. Then finds which handles was selected and emits the
        custom signal handleSelected(handle_index) and caches the index."""
        # pos = (
        #     self.multi_range_hslider.mapFromGlobal(QG.QCursor.pos()).x()
        #     - self._px_cursor_offset
        # )
        # handle_pos = self.multi_range_hslider.widget_pos_to_value(pos)
        # handle_index, _ = self._get_closest_handle_index(handle_pos)
        # print(
        #     f"Handle {handle_index} vs {self.multi_range_hslider._pressedIndex} at {handle_pos} selected"
        # )
        # self._handle_selected = handle_index
        self._handle_selected = self.multi_range_hslider.pressed_index
        self.handleSelected.emit(self._handle_selected)

    def release_handle(self):
        """When called, unset the cached current handle index."""
        self._handle_selected = None

    def draw_colormap_image(self):
        """Recomputes and redraws the colorbar image."""
        # TODO: check how to update the image without having to recreate one, just by updating the colortable
        self.update_color_table()
        # if (pixmap := self._colormap_label.pixmap()) is not None:
        #     image = pixmap.toImage()
        #     image.setColorTable(self.colortable)
        #     self._colormap_label.setPixmap(QG.QPixmap.fromImage(image))
        # else:
        self._colormap_label.setPixmap(self.cmap_to_qimage())

    def get_color_from_value(
        self, value: float, as_type: type[ColorType] = QG.QColor
    ) -> ColorType:
        """Returns the color assigned to a given value using the current colormap.

        Args:
            value: value to assign a color to
            as_type: Color type to be returned (int or QG.QColor). Defaults to QG.QColor.

        Returns:
            The assigned color for the input value using the current colormap.
        """
        int_color = self._colormap.rgb(self.qwt_color_interval, value)
        return as_type(int_color)

    def get_handle_color(
        self, handle_index: int, as_type: type[ColorType] = QG.QColor
    ) -> ColorType:
        """Returns the color of a handled using its index. Calls self.get_color_from_value
        behinds the scene.

        Args:
            handle_index: index of the handled to assign a color too.
            as_type: Color type to be returned (int or QG.QColor). Defaults to QG.QColor.

        Returns:
            The assigned color for the input handle index using the current colormap.
        """
        handle_value = self.get_handles_tuple()[handle_index]
        return self.get_color_from_value(handle_value, as_type)

    def get_hex_color(self, handle_index: int) -> str:
        """Same as self.get_handle_color but returns the color as a hex color string.

        Args:
            handle_index: index of the handled to assign a color too.

        Returns:
            Handle's hex color string
        """
        handle_value = self.get_handles_tuple()[handle_index]
        return self.get_color_from_value(handle_value, QG.QColor).name()

    def edit_color_stop(
        self,
        index: int,
        new_pos: float | None = None,
        new_color: QG.QColor | int | None = None,
    ):
        """Edit an existing color stop in the current colormap. Mutates the colormap
        object.

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
        self.colormapChanged.emit()

    def _edit_color_map_on_slider_change(self, raw_values: tuple[float, ...]):
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
            self.colormapChanged.emit()

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
        """Return the positions of the previous and next handles from the given position.
        If no handle is found, the method can return self.min and/or self.max

        Args:
            pos: position from which to look for the previous and next handles

        Returns:
            previous and next handle positions
        """
        values = self.get_handles_tuple()
        previous_pos = max(
            filter(lambda val: val < pos, values[::-1]), default=self.min
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
        if (neighbour_diff := (next_pos - previous_pos)) < self._tolerance * 2:
            return previous_pos + (neighbour_diff / 2)

        elif (pos - previous_pos) < self._tolerance:
            return previous_pos + self._tolerance

        elif (next_pos - pos) < self._tolerance:
            return next_pos - self._tolerance

        return pos

    def _add_handle_at_click(self):
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
        self.handleAdded.emit(values.index(new_handle_value), new_handle_value)

    def _delete_handle_at_click(self):
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

        self.handleDeleted.emit(closest_handle_index)
        self.colormapChanged.emit()

    def setup_menu(self):
        """Setups the contextual menu used to insert and delete handles.

        Returns:
            _description_
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
    ):
        """insert a handle in the widget at the relative position (between 0. and 1.).
        Mutates the colormap object.

        Args:
            relative_pos: insertion position
        """

        if new_color is None:
            new_color = self._colormap.color(self.qwt_color_interval, relative_pos)

        self._colormap.addColorStop(relative_pos, new_color)

        values = self.get_handles_list()
        values.append(relative_pos)
        values.sort()
        self.set_handles_values(values)

        self.colormapChanged.emit()
        self.handleAdded.emit(values.index(relative_pos), relative_pos)

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

    def set_handles_values(self, values: Sequence[float]):
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

    def open_slider_menu(self, pos: QC.QPoint):
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


if __name__ == "__main__":
    app = QW.QApplication([])
    demo = ColorMapWidget(None)
    demo.add_handle_at_relative_pos(0.5, QG.QColor(QC.Qt.GlobalColor.red))
    # demo.add_handle_at_relative_pos(0.7, QG.QColor(QC.Qt.GlobalColor.red))
    demo.show()
    app.exec_()
