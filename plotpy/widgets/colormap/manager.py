# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Colormap manager
----------------

This module provides a fully featured colormap manager widget and dialog window
that allows to select, edit and save colormaps (existing or new).


Reference
~~~~~~~~~

.. autoclass:: ColorMapNameEdit
    :members:
.. autoclass:: ColorMapManager
    :members:
"""

from __future__ import annotations

from copy import deepcopy

import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW
from guidata.configtools import get_icon
from guidata.qthelpers import exec_dialog

from plotpy.config import _
from plotpy.mathutils.colormap import (
    ALL_COLORMAPS,
    CUSTOM_COLORMAPS,
    DEFAULT_COLORMAPS,
    LARGE_ICON_HEIGHT,
    LARGE_ICON_ORIENTATION,
    LARGE_ICON_WIDTH,
    add_cmap,
    build_icon_from_cmap,
    cmap_exists,
    get_cmap,
)
from plotpy.widgets.colormap.editor import ColorMapEditor
from plotpy.widgets.colormap.widget import EditableColormap


class ColorMapNameEdit(QW.QDialog):
    """Dialog box to enter a colormap name.

    Args:
        parent: parent QWidget. Defaults to None.
        name: default colormap name. Defaults to "".
    """

    def __init__(self, parent: QW.QWidget | None = None, name: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Save"))

        label = QW.QLabel(_("Enter a colormap name:"))
        self._edit = QW.QLineEdit()
        regexp = QC.QRegularExpression("[1-9a-zA-Z_]*")
        self._edit.setValidator(QG.QRegularExpressionValidator(regexp))
        self._edit.setText(name)
        self._edit.setToolTip(
            _(
                "New colormap name cannot contain special characters "
                "except underscores (_)."
            )
        )

        bbox = QW.QDialogButtonBox(QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        hlayout = QW.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addWidget(self._edit)

        dialog_layout = QW.QVBoxLayout()
        dialog_layout.addLayout(hlayout)
        dialog_layout.addWidget(bbox)
        self.setLayout(dialog_layout)

    def get_colormap_name(self) -> str:
        """Return the colormap name entered in the QLineEdit.

        Returns:
            colormap name
        """
        return self._edit.text()

    @classmethod
    def edit(cls, parent: QW.QWidget | None = None, name: str = "") -> str | None:
        """Open the dialog box and return the colormap name entered in the QLineEdit.

        Args:
            parent: parent QWidget. Defaults to None.
            name: default colormap name. Defaults to "".

        Returns:
            colormap name, or None if the dialog box was canceled.
        """
        dialog = cls(parent, name)
        if exec_dialog(dialog):
            return dialog.get_colormap_name()
        return None


class ColorMapManager(QW.QDialog):
    """Colormap manager dialog box. Allows to select, edit and save colormaps.

    Args:
        parent: parent QWidget. Defaults to None.
        active_colormap: name of the default colormap selected. If None or does not
         *exists, will defaults to the first colormap in the list. Defaults to None
    """

    def __init__(
        self,
        parent: QW.QWidget | None = None,
        active_colormap: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowIcon(get_icon("cmap_edit.png"))
        self.setWindowTitle(_("Colormap manager"))

        self.__returned_colormap: EditableColormap | None = None

        if active_colormap is None or not cmap_exists(active_colormap, ALL_COLORMAPS):
            active_colormap = next(iter(ALL_COLORMAPS))

        # Select the active colormap
        self._cmap_choice = QW.QComboBox()
        self._cmap_choice.setMaxVisibleItems(15)
        for cmap in ALL_COLORMAPS.values():
            icon = build_icon_from_cmap(
                cmap, LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, LARGE_ICON_ORIENTATION, 1
            )
            self._cmap_choice.addItem(icon, cmap.name, cmap)

        self._cmap_choice.setIconSize(QC.QSize(LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT))
        self._cmap_choice.setCurrentText(active_colormap)
        select_gbox = QW.QGroupBox(_("Select or create a colormap"))
        select_label = QW.QLabel(_("Colormap presets:"))
        new_btn = QW.QPushButton(_("Create new colormap") + "...")
        new_btn.clicked.connect(self.new_colormap)
        select_gbox_layout = QW.QHBoxLayout()
        select_gbox_layout.addWidget(select_label)
        select_gbox_layout.addWidget(self._cmap_choice)
        select_gbox_layout.addSpacing(10)
        select_gbox_layout.addWidget(new_btn)
        select_gbox_layout.addStretch(1)
        select_gbox.setLayout(select_gbox_layout)

        # Edit the selected colormap
        self.colormap_editor = ColorMapEditor(
            self, colormap=deepcopy(self._cmap_choice.currentData())
        )
        edit_gbox = QW.QGroupBox(_("Edit the selected colormap"))
        edit_gbox_layout = QW.QVBoxLayout()
        edit_gbox_layout.setContentsMargins(0, 0, 0, 0)
        edit_gbox_layout.addWidget(self.colormap_editor)
        edit_gbox.setLayout(edit_gbox_layout)
        edit_gbox.setCheckable(True)
        edit_gbox.setChecked(False)
        new_btn.clicked.connect(lambda: edit_gbox.setChecked(True))
        self.colormap_editor.colormap_widget.COLORMAP_CHANGED.connect(
            self._changes_not_saved
        )

        self._cmap_choice.currentIndexChanged.connect(self.set_colormap)

        self.bbox = QW.QDialogButtonBox(
            QW.QDialogButtonBox.Save
            | QW.QDialogButtonBox.Ok
            | QW.QDialogButtonBox.Cancel
        )
        self._changes_saved = True
        self._save_btn = self.bbox.button(QW.QDialogButtonBox.Save)
        self._save_btn.setEnabled(False)  # type: ignore
        self.bbox.clicked.connect(self.button_clicked)

        dialog_layout = QW.QVBoxLayout()
        dialog_layout.addWidget(select_gbox)
        dialog_layout.addWidget(edit_gbox)
        dialog_layout.addWidget(self.bbox)
        self.setLayout(dialog_layout)

        # The dialog needs to be resizable horizontally but not vertically:
        self.setFixedHeight(self.sizeHint().height())

    def button_clicked(self, button: QW.QAbstractButton) -> None:
        """Callback function to be called when a button is clicked.

        Args:
            button: button clicked
        """
        if button is self._save_btn:
            self.save_colormap()
        elif self.bbox.buttonRole(button) == QW.QDialogButtonBox.AcceptRole:
            self.accept()
        else:
            self.reject()

    def _changes_not_saved(self) -> None:
        """Callback function to be called when the colormap is modified. Enables the
        save button and sets the current_changes_saved attribute to False."""
        self._save_btn.setEnabled(True)  # type: ignore
        self._changes_saved = False

    @property
    def current_changes_saved(self) -> bool:
        """Getter to know if the current colormap has been saved or not.

        Returns:
            True if the current colormap has been saved, False otherwise.
        """
        return self._changes_saved

    def set_colormap(self, index: int) -> None:
        """Set the current colormap to the value present at the given index in the
        QComboBox. Makes a copy of the colormap object so the ColorMapEditor does not
        mutate the original colormap object.

        Args:
            index: index of the colormap in the QComboBox.
        """
        cmap_copy: EditableColormap = deepcopy(self._cmap_choice.itemData(index))
        self.colormap_editor.set_colormap(cmap_copy)
        is_new_colormap = not cmap_exists(cmap_copy.name)
        self._changes_saved = True
        self._save_btn.setEnabled(is_new_colormap)  # type: ignore

    def get_colormap(self) -> EditableColormap | None:
        """Return the selected colormap object.

        Returns:
            selected colormap object
        """
        return self.__returned_colormap

    def __get_new_colormap_name(self, title: str, name: str) -> str | None:
        """Return a new colormap name that does not already exists in the list of
        colormaps.

        Args:
            title: title of the current action
            name: colormap name to check

        Returns:
            new colormap name, or None if the user canceled the action.
        """
        new_name = name
        while True:
            new_name = ColorMapNameEdit.edit(self, new_name)
            if new_name is None:
                return None
            if cmap_exists(new_name, DEFAULT_COLORMAPS):
                QW.QMessageBox.warning(
                    self,
                    title,
                    _(
                        "Name <b>%s</b> is already used by a default colormap, and "
                        "cannot be used for a custom colormap.<br><br>"
                        "Please choose another name."
                    )
                    % new_name,
                )
                continue
            if cmap_exists(new_name, CUSTOM_COLORMAPS) and (
                QW.QMessageBox.question(
                    self,
                    title,
                    _(
                        "Name <b>%s</b> is already used by a custom colormap.<br><br>"
                        "Do you want to overwrite it?"
                    )
                    % new_name,
                    QW.QMessageBox.Yes | QW.QMessageBox.No,
                    QW.QMessageBox.No,
                )
                == QW.QMessageBox.No
            ):
                continue
            break
        return new_name

    def new_colormap(self) -> None:
        """Create a new colormap and set it as the current colormap."""
        cmap = EditableColormap(QG.QColor(0), QG.QColor(4294967295), name=_("New"))
        self.save_colormap(cmap)

    def save_colormap(self, cmap: EditableColormap | None = None) -> bool:
        """Saves the current colormap and handles the validation process. The saved
        colormaps can only be saved in the custom colormaps.

        Args:
            cmap: colormap to save. If None, will use the current colormap.

        Returns:
            True if the colormap has been saved, False otherwise.
        """
        if cmap is None:
            cmap = self.colormap_editor.get_colormap()
            title = _("Save colormap")
        else:
            title = _("New colormap")
        new_name = self.__get_new_colormap_name(title, cmap.name)
        if new_name is None:
            return False

        # Before modifying CUSTOM_COLORMAPS, save this boolean expression:
        is_existing_custom_cmap = cmap_exists(new_name, CUSTOM_COLORMAPS)

        # Take into account the case where the color map exists in custom colormaps
        # but not with the same case (e.g. "viridis" vs "Viridis"). So we need to
        # get the original name of the colormap:
        if is_existing_custom_cmap:
            new_name = get_cmap(new_name).name

        cmap.name = new_name
        add_cmap(cmap)

        icon = build_icon_from_cmap(cmap)
        if is_existing_custom_cmap:
            self._cmap_choice.setCurrentText(new_name)
            current_index = self._cmap_choice.currentIndex()
            self._cmap_choice.setItemData(current_index, cmap)
            self._cmap_choice.setItemIcon(current_index, icon)
        else:
            self._cmap_choice.addItem(icon, new_name, cmap)
            self._cmap_choice.setCurrentText(new_name)

        self._save_btn.setEnabled(False)  # type: ignore
        self._changes_saved = True
        return True

    def accept(self) -> None:
        """Adds logic on top of the normal QDialog.accept method to handle colormap
        save.
        """
        if not self.current_changes_saved and not self.save_colormap():
            return
        self.__returned_colormap = self.colormap_editor.get_colormap()
        super().accept()
