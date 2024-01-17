# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""This module provides a more complete colormap editor widget than the one provided
by ColorMapWidget (plotpy/widgets/colormap_widget.py). It allows to edit a colormap
by changing its color stops (add/delete/move/change color).
"""

import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW
from guidata.dataset import ColorItem, DataSet, FloatItem
from guidata.dataset.datatypes import GetAttrProp, NotProp
from guidata.dataset.qtwidgets import DataSetEditGroupBox

from plotpy.config import _
from plotpy.widgets.colormap_widget import ColorMapWidget, CustomQwtLinearColormap


class ColorMapEditor(QW.QWidget):
    """Widget that allows a user to edit a colormap by changing its color stops (
    add/delete/move/change color). Right click on the colorbar or slider to add or
    remove colors stops. A existing colormap instance can be used. However, the
    modifications are inplace so you should copy the object if you do not want to
    mutate it.

    Args:
        parent: Parent widget.
        cmap_width: Cmap size in pixels. Defaults to 400.
        cmap_height: Cmap height in pixels. Defaults to 50.
        color1: First color of the colormap. If None, color blue is used. Ignored if
        argument 'colormap' is used. Defaults to None.
        color2: Last color of the colormap. If None, color yellow is used.Ignored if
        argument 'colormap' is used. Defaults to None
        colormap: An already initialized colormap to use in the widget.
        Defaults to None.
    """

    class ColorPickDataSet(DataSet):
        """Dataset with the field used to edit a color stop."""

        _position_locked = False

        position = (
            FloatItem(
                _("Relative position"),
                min=0.0,
                max=1.0,
                help=_("Must be a value between 0.0 and 1.0."),
            )
            .set_prop("display", format="%.2f")
            .set_prop("display", active=NotProp(GetAttrProp("_position_locked")))
        )
        hex_color = ColorItem(
            "Pick color", help="Pick a color to use for the selected cursor."
        )

        def lock_position(self, lock=True):
            """Used to lock the position of the cursor value.

            Args:
                lock: True if value must be locked. Defaults to True.
            """
            self._position_locked = lock

        def is_position_locked(self):
            """Returns True if the position is locked.

            Returns:
                True if position is locked, False otherwise.
            """
            return self._position_locked

        def set_position(self, position: float):
            """Set a new position for the cursor. Value is rounded to 2 decimals.

            Args:
                position: new position to set
            """
            self.position = round(position, 2)

        def get_position(self) -> float:
            """Return the current position of the cursor.

            Returns:
                float value of the cursor position
            """
            return self.position  # type: ignore

        def set_color(self, hex_color: str):
            """Set a new hex color for the cursor.

            Args:
                hex_color: str hex color to set (e.g. "#FF0000" for red)
            """
            self.hex_color = hex_color

        def get_hex_color(self) -> str:
            """Return the current str hex color of the cursor.

            Returns:
                str hex color of the cursor (e.g. "#FF0000" for red)
            """
            return self.hex_color  # type: ignore

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

        color1 = QG.QColor(QC.Qt.GlobalColor.blue) if color1 is None else color1
        color2 = QG.QColor(QC.Qt.GlobalColor.yellow) if color2 is None else color2
        self.colormap_widget = ColorMapWidget(
            self, cmap_width, cmap_height, color1, color2, colormap
        )

        self.tabs = QW.QTabWidget()

        self.datasets: list[DataSetEditGroupBox[ColorMapEditor.ColorPickDataSet]] = []

        self.setup_tabs()
        self.tabs.setCurrentIndex(0)
        self.update_tabs_names_from_current()

        self.editor_layout = QW.QVBoxLayout(self)

        self.editor_layout.addWidget(self.colormap_widget)
        self.editor_layout.addWidget(self.tabs)

        self.setLayout(self.editor_layout)

        self.colormap_widget.HANDLE_SELECTED.connect(self.change_current_dataset)
        self.colormap_widget.HANDLE_ADDED.connect(self.new_tab)
        self.colormap_widget.HANDLE_DELETED.connect(self.delete_tab)
        self.colormap_widget.multi_range_hslider.sliderMoved.connect(
            self.update_current_dataset
        )

    def set_colormap(self, colormap: CustomQwtLinearColormap):
        """Replaces the current colormap.

        Args:
            colormap: replacement colormap
        """
        self.colormap_widget.blockSignals(True)
        self.colormap_widget.set_colormap(colormap)
        self.colormap_widget.blockSignals(False)
        self.setup_tabs()

    def get_colormap(self) -> CustomQwtLinearColormap:
        """Get the current colormap being edited.

        Returns:
            current colormap
        """
        return self.colormap_widget.get_colormap()

    def change_current_dataset(self, dataset_index: int):
        """Wrapper functio to change the current dataset (=current tab)

        Args:
            dataset_index: dataset index (=tab) to set current
        """
        self.tabs.setCurrentIndex(dataset_index)

    def update_tab_color(self, tab_index: int):
        """Update the tab icon color for the given tab index.

        Args:
            tab_index: index of the tab to update
        """
        handle_color = self.colormap_widget.get_handle_color(tab_index)

        pixmap = QG.QPixmap(10, 10)  # Size of the square
        pixmap.fill(handle_color)  # Color of the square
        new_icon = QG.QIcon(pixmap)
        self.tabs.setTabIcon(tab_index, new_icon)

        hex_color = handle_color.name()
        dataset_grp = self.datasets[tab_index]
        dataset_grp.dataset.set_color(hex_color)
        dataset_grp.get()

    def update_tabs_names_from_current(self):
        """Update all the tab names from the current active tab (useful when a new one
        is added).
        """
        start_index = self.tabs.currentIndex()
        for i in range(start_index, self.tabs.count()):
            self.tabs.setTabText(i, str(i + 1))

    def new_tab(self, index: int, handle_pos: float):
        """Add/insert a new tab at the given index and set its relative position and
        color.

        Args:
            index: index of the insertion/appending.
            handle_pos: relative value to set in the tab (new handle current position)
        """
        title = ""
        # title.setPixmap(pixmap)

        dw = DataSetEditGroupBox(
            QW.QLabel(title, self),
            self.ColorPickDataSet,
            # comment=_("Edit color point."),
        )
        dw.dataset.set_position(handle_pos)

        hex_color = self.colormap_widget.get_hex_color(index)
        dw.dataset.set_color(hex_color)

        dw.SIG_APPLY_BUTTON_CLICKED.connect(self.update_colormap_widget)

        if index == self.tabs.count():
            self.datasets.append(dw)
            self.tabs.addTab(dw, title)
        else:
            self.datasets.insert(index, dw)
            self.tabs.insertTab(index, dw, title)
            dw.updateGeometry()

        self.tabs.setCurrentIndex(index)
        dw.set()

        self.update_tab_color(index)
        self.update_tabs_names_from_current()

    def setup_tabs(self):
        """Clear and setup all the tabs from the current colormap. Can be used to reset
        all tabs after initialization.
        """
        self.datasets.clear()
        self.tabs.clear()
        for i, handle_pos in enumerate(self.colormap_widget.get_handles_tuple()):
            self.new_tab(i, handle_pos)
        self.datasets[0].dataset.lock_position()
        self.datasets[0].get()
        self.datasets[-1].dataset.lock_position()
        self.datasets[-1].get()

    def reset_colors(self):
        """Updates all the tab icons color."""
        for i in range(len(self.colormap_widget)):
            self.update_tab_color(i)

    def delete_tab(self, tab_index: int):
        """Removes the tab/dataset at given index.

        Args:
            tab_index: index to remove
        """
        self.tabs.removeTab(tab_index)
        self.datasets.pop(tab_index)
        self.tabs.setCurrentIndex(tab_index)
        self.update_tabs_names_from_current()

    def update_colormap_widget(self):
        """Update the colormap widget (colorbar and handles) with the values from the
        current tab.
        """
        current_index = self.tabs.currentIndex()
        current_dataset = self.datasets[current_index].dataset

        new_slider_values = self.colormap_widget.get_handles_list()

        if 0 < current_index < self.tabs.count() - 1:
            relative_pos = current_dataset.get_position()
        else:
            relative_pos = new_slider_values[current_index]
            current_dataset.set_position(relative_pos)
            self.datasets[current_index].get()

        new_color = QG.QColor(current_dataset.get_hex_color())
        self.colormap_widget.edit_color_stop(current_index, relative_pos, new_color)
        self.update_tab_color(current_index)

    def update_current_dataset(self):
        """Update values in the current dataset/tab with the values from the colormap
        widget.
        """
        current_index = self.tabs.currentIndex()
        current_dataset_grp = self.datasets[current_index]
        relative_pos = self.colormap_widget.get_handles_tuple()[current_index]
        current_dataset_grp.dataset.set_position(relative_pos)
        current_dataset_grp.get()


if __name__ == "__main__":
    app = QW.QApplication([])
    demo = ColorMapEditor(None)
    demo.show()
    app.exec_()
