# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
fliprotate
----------

The `FlipRotate` module provides a dialog box providing essential GUI elements
for rotating (arbitrary angle) and cropping an image:

    * :py:class:`.widgets.fliprotate.FlipRotateDialog`: dialog box
    * :py:class:`.widgets.fliprotate.FlipRotateWidget`: equivalent widget

Reference
~~~~~~~~~

.. autoclass:: FlipRotateDialog
   :members:
.. autoclass:: FlipRotateWidget
   :members:
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from guidata.configtools import get_icon
from guidata.qthelpers import create_toolbutton, win32_fix_title_bar_background
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QWidget  # Helping out python_qt_documentation

from plotpy.config import _
from plotpy.widgets import basetransform

if TYPE_CHECKING:  # pragma: no cover
    from plotpy.plot import PlotOptions
    from plotpy.plot.manager import PlotManager


class FlipRotateTransform(basetransform.BaseTransform):
    """Rotate & Crop mixin class, to be mixed with a class providing the
    get_plot method, like PlotDialog or FlipRotateWidget (see below)

    Args:
        parent (QWidget): Parent widget
        manager (PlotManager): Plot manager
    """

    def __init__(self, parent: FlipRotateWidget, manager: PlotManager) -> None:
        super().__init__(parent, manager)
        self.parent = parent
        self.manager = manager

    # ------BaseTransformMixin API----------------------------------------------
    def apply_transformation(self) -> None:
        """Apply transformation, e.g. crop or rotate"""
        angle, hflip, vflip = self.parent.get_parameters()
        x, y, _a, px, py, _hf, _vf = self.item.get_transform()
        self.item.set_transform(x, y, angle * np.pi / 180, px, py, hflip, vflip)
        self.manager.get_plot().replot()

    def compute_transformation(self) -> np.ndarray:
        """Compute transformation, return compute output array

        Returns:
            Output array
        """
        angle, hflip, vflip = self.parent.get_parameters()
        data = self.item.data.copy()
        if hflip:
            data = np.fliplr(data)
        if vflip:
            data = np.flipud(data)
        if angle:
            k = int((-angle % 360) / 90)
            data = np.rot90(data, k)
        return data


class FlipRotateDialog(QW.QDialog):
    """Flip & Rotate Dialog

    Flip and rotate a :py:class:`.TrImageItem` plot item

    Args:
        parent: Parent widget
        title: Window title
        options: Options
        resize_to: Resize to (width, height)
        edit: Edit mode
        toolbar: Show toolbar
    """

    def __init__(
        self,
        parent: QWidget,
        title: str | None = None,
        options: dict | None = None,
        resize_to: tuple[int, int] | None = None,
        edit: bool = True,
        toolbar: bool = False,
    ) -> None:
        super().__init__(parent)
        win32_fix_title_bar_background(self)

        if resize_to is not None:
            width, height = resize_to
            self.resize(width, height)

        self.button_box = None

        if title is None:
            title = _("Flip & Rotate")
        self.setWindowTitle(title)
        self.widget = FlipRotateWidget(parent=parent, options=options, toolbar=toolbar)
        self.setWindowFlags(QC.Qt.WindowType.Window)

        buttonhlayout = QW.QHBoxLayout()
        self.add_buttons_to_layout(buttonhlayout, edit)

        dialogvlayout = QW.QVBoxLayout()
        dialogvlayout.addWidget(self.widget)
        dialogvlayout.addLayout(buttonhlayout)
        self.setLayout(dialogvlayout)

        self.transform = self.widget.transform
        self.plot_widget = plot_widget = self.widget.plot_widget
        self.manager = plot_widget.manager
        self.toolbar = plot_widget.toolbar

        self.accepted.connect(self.transform.accept_changes)
        self.rejected.connect(self.transform.reject_changes)

    def add_buttons_to_layout(self, layout: QW.QBoxLayout, edit: bool) -> None:
        """Add buttons to layout

        Args:
            layout: Layout
            edit: Edit mode
        """
        if edit:
            self.button_box = bbox = QW.QDialogButtonBox(
                QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel
            )
            bbox.accepted.connect(self.accept)
            bbox.rejected.connect(self.reject)
            layout.addWidget(bbox)


class FlipRotateWidget(basetransform.BaseTransformWidget):
    """Flip & Rotate Widget

    Flip and rotate a :py:class:`.TrImageItem` plot item

    Args:
        parent: Parent widget
        toolbar: Show toolbar
        options: Plot options
    """

    ROTATION_ANGLES = [str((i - 1) * 90) for i in range(4)]

    def __init__(
        self,
        parent: QWidget,
        toolbar: bool = False,
        options: PlotOptions | None = None,
    ):
        self.angle_combo = None
        self.hflip_btn = None
        self.vflip_btn = None
        super().__init__(parent, toolbar=toolbar, options=options)
        self.transform = FlipRotateTransform(self, self.plot_widget.manager)
        self.manager = self.plot_widget.manager

    def add_buttons_to_layout(self, layout: QW.QBoxLayout) -> None:
        """Add tool buttons to layout

        Args:
            layout: Layout
        """
        # Image orientation
        angle_label = QW.QLabel(_("Angle %s:") % "(°)")
        layout.addWidget(angle_label)
        self.angle_combo = QW.QComboBox(self)
        self.angle_combo.addItems(self.ROTATION_ANGLES)
        self.angle_combo.setCurrentIndex(1)
        self.angle_combo.currentIndexChanged.connect(
            lambda index: self.transform.apply_transformation()
        )
        layout.addWidget(self.angle_combo)
        layout.addSpacing(10)

        # Image flipping
        flip_label = QW.QLabel(_("Flip:"))
        layout.addWidget(flip_label)
        hflip = create_toolbutton(
            self,
            text="",
            icon=get_icon("hflip.png"),
            toggled=lambda state: self.transform.apply_transformation(),
            autoraise=False,
        )
        self.hflip_btn = hflip
        layout.addWidget(hflip)
        vflip = create_toolbutton(
            self,
            text="",
            icon=get_icon("vflip.png"),
            toggled=lambda state: self.transform.apply_transformation(),
            autoraise=False,
        )
        self.vflip_btn = vflip
        layout.addWidget(vflip)
        layout.addSpacing(15)

        # self.add_reset_button(layout)
        basetransform.BaseTransformWidget.add_buttons_to_layout(
            self, layout, apply=False
        )

    def apply_transformation(self) -> None:
        """Apply transformation"""
        self.transform.apply_transformation()

    def reset(self) -> None:
        """Reset transformation"""
        self.angle_combo.setCurrentIndex(1)
        self.hflip_btn.setChecked(False)
        self.vflip_btn.setChecked(False)

    def set_parameters(self, angle: float, hflip: bool, vflip: bool) -> None:
        """Set transform parameters

        Args:
            angle: Angle
            hflip: Horizontal flip
            vflip: Vertical flip
        """
        angle_index = self.ROTATION_ANGLES.index(str(angle))
        self.angle_combo.setCurrentIndex(angle_index)
        self.hflip_btn.setChecked(hflip)
        self.vflip_btn.setChecked(vflip)

    def get_parameters(self) -> tuple[float, bool, bool]:
        """Return transform parameters

        Returns:
            Tuple of angle, horizontal flip, vertical flip
        """
        angle = int(str(self.angle_combo.currentText()))
        hflip = self.hflip_btn.isChecked()
        vflip = self.vflip_btn.isChecked()
        return angle, hflip, vflip


class MultipleFlipRotateWidget(basetransform.BaseMultipleTransformWidget):
    """Multiple Flip & Rotate Widget

    Flip and rotate several :py:class:`.image.TrImageItem` plot items"""

    TRANSFORM_WIDGET_CLASS = FlipRotateWidget
