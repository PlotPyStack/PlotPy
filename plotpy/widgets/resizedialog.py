# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Resize dialog
-------------

The `resizedialog` module provides a dialog box providing essential GUI
for entering parameters needed to resize an image:
:py:class:`.widgets.resizedialog.ResizeDialog`.

Reference
~~~~~~~~~

.. autoclass:: ResizeDialog
   :members:
"""

from guidata.qthelpers import win32_fix_title_bar_background
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtCore import Qt

from plotpy.config import _


def is_edit_valid(edit):
    """

    :param edit:
    :return:
    """
    text = edit.text()
    state = edit.validator().validate(text, 0)
    if isinstance(state, (tuple, list)):
        state = state[0]
    return state == QG.QIntValidator.Acceptable


class ResizeDialog(QW.QDialog):
    """Resize dialog box"""

    def __init__(self, parent, new_size, old_size, text="", keep_original_size=False):
        QW.QDialog.__init__(self, parent)
        win32_fix_title_bar_background(self)

        def intfunc(tup):
            return [int(val) for val in tup]

        if intfunc(new_size) == intfunc(old_size):
            self.keep_original_size = True
        else:
            self.keep_original_size = keep_original_size
        self.width, self.height = new_size
        self.old_width, self.old_height = old_size
        self.ratio = self.width / self.height

        layout = QW.QVBoxLayout()
        self.setLayout(layout)

        formlayout = QW.QFormLayout()
        layout.addLayout(formlayout)

        if text:
            label = QW.QLabel(text)
            label.setAlignment(Qt.AlignHCenter)
            formlayout.addRow(label)

        self.w_edit = w_edit = QW.QLineEdit(self)
        w_valid = QG.QIntValidator(w_edit)
        w_valid.setBottom(1)
        w_edit.setValidator(w_valid)

        self.h_edit = h_edit = QW.QLineEdit(self)
        h_valid = QG.QIntValidator(h_edit)
        h_valid.setBottom(1)
        h_edit.setValidator(h_valid)

        zbox = QW.QCheckBox(_("Original size"), self)

        formlayout.addRow(_("Width (pixels)"), w_edit)
        formlayout.addRow(_("Height (pixels)"), h_edit)
        formlayout.addRow("", zbox)

        formlayout.addRow(_("Original size:"), QW.QLabel("%d x %d" % old_size))
        self.z_label = QW.QLabel()
        formlayout.addRow(_("Zoom factor:"), self.z_label)

        # Button box
        self.bbox = bbox = QW.QDialogButtonBox(
            QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel
        )
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        layout.addWidget(bbox)

        self.w_edit.setText(str(int(self.width)))
        self.h_edit.setText(str(int(self.height)))
        self.update_widgets()

        self.setWindowTitle(_("Resize"))

        w_edit.textChanged.connect(self.width_changed)
        h_edit.textChanged.connect(self.height_changed)
        zbox.toggled.connect(self.toggled_no_zoom)
        zbox.setChecked(self.keep_original_size)

    def update_widgets(self):
        """ """
        valid = True
        for edit in (self.w_edit, self.h_edit):
            if not is_edit_valid(edit):
                valid = False
        self.bbox.button(QW.QDialogButtonBox.Ok).setEnabled(valid)
        self.z_label.setText("%d %s" % (100 * self.width / self.old_width, "%"))

    def width_changed(self, text):
        """

        :param text:
        """
        if is_edit_valid(self.sender()):
            self.width = int(text)
            self.height = int(self.width / self.ratio)
            self.h_edit.blockSignals(True)
            self.h_edit.setText(str(self.height))
            self.h_edit.blockSignals(False)
        self.update_widgets()

    def height_changed(self, text):
        """

        :param text:
        """
        if is_edit_valid(self.sender()):
            self.height = int(text)
            self.width = int(self.ratio * self.height)
            self.w_edit.blockSignals(True)
            self.w_edit.setText(str(self.width))
            self.w_edit.blockSignals(False)
        self.update_widgets()

    def toggled_no_zoom(self, state):
        """

        :param state:
        """
        self.keep_original_size = state
        if state:
            self.z_label.setText("100 %")
            self.bbox.button(QW.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.update_widgets()
        for widget in (self.w_edit, self.h_edit):
            widget.setDisabled(state)

    def get_zoom(self):
        """

        :return:
        """
        if self.keep_original_size:
            return 1
        elif self.width > self.height:
            return self.width / self.old_width
        else:
            return self.height / self.old_height
