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
from guidata.env import execenv
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
    delete_cmap,
    get_cmap,
)
from plotpy.widgets.colormap.editor import ColorMapEditor
from plotpy.widgets.colormap.widget import EditableColormap


class ColorMapNameEdit(QW.QDialog):
    """Dialog box to enter a colormap name.

    Args:
        parent: parent QWidget. Defaults to None.
        title: dialog box title. Defaults to "".
        name: default colormap name. Defaults to "".
    """

    def __init__(
        self, parent: QW.QWidget | None = None, title: str = "", name: str = ""
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

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
    def edit(
        cls, parent: QW.QWidget | None = None, title: str = "", name: str = ""
    ) -> str | None:
        """Open the dialog box and return the colormap name entered in the QLineEdit.

        Args:
            parent: parent QWidget. Defaults to None.
            title: dialog box title. Defaults to "".
            name: default colormap name. Defaults to "".

        Returns:
            colormap name, or None if the dialog box was canceled.
        """
        dialog = cls(parent, title, name)
        if exec_dialog(dialog):
            return dialog.get_colormap_name()
        return None


class ColorMapManager(QW.QDialog):
    """Colormap manager dialog box. Allows to select, edit and save colormaps.

    Args:
        parent: parent QWidget. Defaults to None.
        active_colormap: name of the active colormap.

    .. note::

        The active colormap is the colormap that will be selected by default when the
        dialog box is opened. If the colormap does not exist (or if None is provided),
        the first colormap in the list will be selected by default.

        The active colormap cannot be removed. If the active colormap is a custom
        colormap, the remove button will be enabled but a dialog box will warn the user
        that the colormap cannot be removed.
    """

    SIG_APPLY_COLORMAP = QC.Signal(str)

    def __init__(
        self,
        parent: QW.QWidget | None = None,
        active_colormap: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowIcon(get_icon("cmap_edit.png"))
        self.setWindowTitle(_("Colormap manager"))

        self.active_cmap_name = default_colormap = active_colormap

        self.__returned_colormap: EditableColormap | None = None

        if default_colormap is None or not cmap_exists(default_colormap, ALL_COLORMAPS):
            default_colormap = next(iter(ALL_COLORMAPS))

        # Select the active colormap
        self._cmap_choice = QW.QComboBox()
        self._cmap_choice.setMaxVisibleItems(15)
        for cmap in ALL_COLORMAPS.values():
            icon = build_icon_from_cmap(
                cmap, LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, LARGE_ICON_ORIENTATION, 1
            )
            self._cmap_choice.addItem(icon, cmap.name, cmap)

        self._cmap_choice.setIconSize(QC.QSize(LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT))
        self._cmap_choice.setCurrentText(default_colormap)

        add_btn = QW.QPushButton(get_icon("edit_add.png"), _("Add") + "...")
        add_btn.clicked.connect(self.add_colormap)
        self._remove_btn = QW.QPushButton(get_icon("delete.png"), _("Remove") + "...")
        is_custom_cmap = cmap_exists(default_colormap, CUSTOM_COLORMAPS)
        self._remove_btn.setEnabled(is_custom_cmap)
        self._remove_btn.clicked.connect(self.remove_colormap)

        select_gbox = QW.QGroupBox(_("Select or create a colormap"))
        select_label = QW.QLabel(_("Colormap presets:"))
        select_gbox_layout = QW.QHBoxLayout()
        select_gbox_layout.addWidget(select_label)
        select_gbox_layout.addWidget(self._cmap_choice)
        select_gbox_layout.addSpacing(10)
        select_gbox_layout.addWidget(add_btn)
        select_gbox_layout.addWidget(self._remove_btn)
        select_gbox.setLayout(select_gbox_layout)

        # Edit the selected colormap
        current_cmap = self._cmap_choice.currentData()
        # This test is necessary because the currentData method returns a QVariant
        # object, which may be handled differently by PyQt5, PySide2 and PySide6.
        # This is an attempt to fix an issue with PySide6 (segfault).
        if isinstance(current_cmap, EditableColormap):
            current_cmap = deepcopy(current_cmap)
        else:
            current_cmap = None
        self.colormap_editor = ColorMapEditor(self, colormap=current_cmap)

        self._edit_gbox = QW.QGroupBox(_("Edit the selected colormap"))
        edit_gbox_layout = QW.QVBoxLayout()
        edit_gbox_layout.setContentsMargins(0, 0, 0, 0)
        edit_gbox_layout.addWidget(self.colormap_editor)
        self._edit_gbox.setLayout(edit_gbox_layout)
        self._edit_gbox.setCheckable(True)
        self._edit_gbox.setChecked(False)
        self.colormap_editor.colormap_widget.COLORMAP_CHANGED.connect(
            self._changes_not_saved
        )

        self._cmap_choice.currentIndexChanged.connect(self.set_colormap)

        self.bbox = QW.QDialogButtonBox(
            QW.QDialogButtonBox.Apply
            | QW.QDialogButtonBox.Save
            | QW.QDialogButtonBox.Ok
            | QW.QDialogButtonBox.Cancel
        )
        self._changes_saved = True
        self._save_btn = self.bbox.button(QW.QDialogButtonBox.Save)
        self._save_btn.setEnabled(False)  # type: ignore
        self._apply_btn = self.bbox.button(QW.QDialogButtonBox.Apply)
        self._apply_btn.setEnabled(False)  # type: ignore
        self.bbox.clicked.connect(self.button_clicked)

        dialog_layout = QW.QVBoxLayout()
        dialog_layout.addWidget(select_gbox)
        dialog_layout.addWidget(self._edit_gbox)
        dialog_layout.addWidget(self.bbox)
        self.setLayout(dialog_layout)

        # The dialog needs to be resizable horizontally but not vertically:
        self.setFixedHeight(self.sizeHint().height())

    def button_clicked(self, button: QW.QAbstractButton) -> None:
        """Callback function to be called when a button is clicked.

        Args:
            button: button clicked
        """
        if button is self._apply_btn:
            if not self.current_changes_saved and not self.save_colormap():
                return
            self._apply_btn.setEnabled(False)
            self.SIG_APPLY_COLORMAP.emit(self.colormap_editor.get_colormap().name)
        elif button is self._save_btn:
            self.save_colormap()
        elif self.bbox.buttonRole(button) == QW.QDialogButtonBox.AcceptRole:
            self.accept()
        else:
            self.reject()

    def _changes_not_saved(self) -> None:
        """Callback function to be called when the colormap is modified. Enables the
        save button and sets the current_changes_saved attribute to False."""
        self._save_btn.setEnabled(True)  # type: ignore
        self._apply_btn.setEnabled(True)  # type: ignore
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

        is_custom_cmap = cmap_exists(cmap_copy.name, CUSTOM_COLORMAPS)
        self._remove_btn.setEnabled(is_custom_cmap)

        self._changes_saved = True
        is_new_colormap = not cmap_exists(cmap_copy.name)
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
            new_name = ColorMapNameEdit.edit(self, title, new_name)
            if new_name is None:
                return None
            if cmap_exists(new_name, DEFAULT_COLORMAPS):
                QW.QMessageBox.warning(
                    self,
                    title,
                    _(
                        "Name <b>%s</b> is already used by a predefined colormap, and "
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

    def add_colormap(self) -> None:
        """Create a new colormap and set it as the current colormap."""
        cmap = EditableColormap(QG.QColor(0), QG.QColor(4294967295), name=_("New"))
        if self.save_colormap(cmap):
            # If the colormap save dialog was accepted, then we enable the colormap
            # editor group box.
            # Otherwise, we leave the colormap editor group box at its current state.
            self._edit_gbox.setChecked(True)

    def remove_colormap(self) -> None:
        """Remove the current colormap."""
        cmap = self.colormap_editor.get_colormap()
        if cmap is None:
            return
        name = cmap.name
        if name == self.active_cmap_name or cmap_exists(name, DEFAULT_COLORMAPS):
            if execenv.unattended:  # For testing purposes only
                return
            if name == self.active_cmap_name:
                msg = _("Colormap <b>%s</b> is the active colormap.")
            else:
                msg = _("Colormap <b>%s</b> is a predefined colormap.")
            QW.QMessageBox.warning(
                self,
                _("Remove"),
                msg % name + "<br>" + _("Thus, this colormap cannot be removed."),
                QW.QMessageBox.Ok,
            )
            return
        if execenv.unattended:  # For testing purposes only
            if not execenv.accept_dialogs:
                return
        elif (
            QW.QMessageBox.question(
                self,
                _("Remove"),
                _("Do you want to delete colormap <b>%s</b>?") % name,
                QW.QMessageBox.Yes | QW.QMessageBox.No,
                QW.QMessageBox.No,
            )
            == QW.QMessageBox.No
        ):
            return
        delete_cmap(cmap)
        current_index = self._cmap_choice.currentIndex()
        self._cmap_choice.removeItem(current_index)
        self._changes_saved = True
        self._save_btn.setEnabled(False)
        self._cmap_choice.setCurrentIndex(max(current_index - 1, 0))

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
            title = _("Add colormap")
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

        icon = build_icon_from_cmap(
            cmap, LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, LARGE_ICON_ORIENTATION, 1
        )
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
