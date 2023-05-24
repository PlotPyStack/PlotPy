# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

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
   :inherited-members:
.. autoclass:: FlipRotateWidget
   :members:
   :inherited-members:
"""
import numpy as np
from guidata.configtools import get_icon
from guidata.qthelpers import create_toolbutton, win32_fix_title_bar_background
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.widgets import basetransform


class FlipRotateTransform(basetransform.BaseTransform):
    """Rotate & Crop mixin class, to be mixed with a class providing the
    get_plot method, like PlotDialog or FlipRotateWidget (see below)"""

    def __init__(self, parent, manager):
        super().__init__(parent, manager)
        self.parent = parent
        self.manager = manager

    # ------BaseTransformMixin API----------------------------------------------
    def apply_transformation(self):
        """Apply transformation, e.g. crop or rotate"""
        angle, hflip, vflip = self.parent.get_parameters()
        x, y, _a, px, py, _hf, _vf = self.item.get_transform()
        self.item.set_transform(x, y, angle * np.pi / 180, px, py, hflip, vflip)
        self.manager.get_plot().replot()

    def compute_transformation(self):
        """Compute transformation, return compute output array"""
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

    Flip and rotate a :py:class:`.image.TrImageItem` plot item"""

    def __init__(
        self,
        parent,
        wintitle=None,
        options=None,
        resize_to=None,
        edit=True,
        toolbar=False,
    ):
        super(FlipRotateDialog, self).__init__(parent)
        win32_fix_title_bar_background(self)

        if resize_to is not None:
            width, height = resize_to
            self.resize(width, height)

        self.button_box = None

        if wintitle is None:
            wintitle = _("Flip & Rotate")
        self.widget = FlipRotateWidget(
            parent=parent,
            options=options,
            # resize_to=resize_to,
            # edit=edit,
            toolbar=toolbar,
        )
        self.setWindowFlags(QC.Qt.WindowType.Window)

        buttonhlayout = QW.QHBoxLayout()
        self.add_buttons_to_layout(buttonhlayout, edit)

        dialogvlayout = QW.QVBoxLayout()
        dialogvlayout.addWidget(self.widget)
        dialogvlayout.addLayout(buttonhlayout)
        self.setLayout(dialogvlayout)

        self.transf = self.widget.transf
        self.manager = self.widget.manager
        self.imagewidget = self.widget.imagewidget
        self.toolbar = self.manager.toolbar

        self.accepted.connect(self.transf.accept_changes)
        self.rejected.connect(self.transf.reject_changes)

    def add_buttons_to_layout(self, layout, edit):
        """Add buttons to layout"""
        if edit:
            self.button_box = bbox = QW.QDialogButtonBox(
                QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel
            )
            bbox.accepted.connect(self.accept)
            bbox.rejected.connect(self.reject)
            layout.addWidget(bbox)


class FlipRotateWidget(basetransform.BaseTransformWidget):
    """Flip & Rotate Widget

    Flip and rotate a :py:class:`.image.TrImageItem` plot item"""

    ROTATION_ANGLES = [str((i - 1) * 90) for i in range(4)]

    def __init__(self, parent, toolbar=False, options=None):
        self.angle_combo = None
        self.hflip_btn = None
        self.vflip_btn = None
        basetransform.BaseTransformWidget.__init__(self, parent, toolbar, options=options)
        self.transf = FlipRotateTransform(self, self.imagewidget.manager)
        self.manager = self.imagewidget.manager

    def add_buttons_to_layout(self, layout):
        """Add tool buttons to layout"""
        # Image orientation
        angle_label = QW.QLabel(_("Angle (°):"))
        layout.addWidget(angle_label)
        self.angle_combo = QW.QComboBox(self)
        self.angle_combo.addItems(self.ROTATION_ANGLES)
        self.angle_combo.setCurrentIndex(1)
        self.angle_combo.currentIndexChanged.connect(
            lambda index: self.transf.apply_transformation()
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
            toggled=lambda state: self.transf.apply_transformation(),
            autoraise=False,
        )
        self.hflip_btn = hflip
        layout.addWidget(hflip)
        vflip = create_toolbutton(
            self,
            text="",
            icon=get_icon("vflip.png"),
            toggled=lambda state: self.transf.apply_transformation(),
            autoraise=False,
        )
        self.vflip_btn = vflip
        layout.addWidget(vflip)
        layout.addSpacing(15)

        # self.add_reset_button(layout)
        basetransform.BaseTransformWidget.add_buttons_to_layout(self, layout, apply=False)

    def apply_transformation(self):
        angle, hflip, vflip = self.get_parameters()
        self.transf.apply_transformation(angle, hflip, vflip)

    def reset(self):
        """Reset transformation"""
        self.angle_combo.setCurrentIndex(1)
        self.hflip_btn.setChecked(False)
        self.vflip_btn.setChecked(False)

    def set_parameters(self, angle, hflip, vflip):
        """Set transform parameters"""
        angle_index = self.ROTATION_ANGLES.index(str(angle))
        self.angle_combo.setCurrentIndex(angle_index)
        self.hflip_btn.setChecked(hflip)
        self.vflip_btn.setChecked(vflip)

    def get_parameters(self):
        """Return transform parameters"""
        angle = int(str(self.angle_combo.currentText()))
        hflip = self.hflip_btn.isChecked()
        vflip = self.vflip_btn.isChecked()
        return angle, hflip, vflip


class MultipleFlipRotateWidget(basetransform.BaseMultipleTransformWidget):
    """Multiple Flip & Rotate Widget

    Flip and rotate several :py:class:`.image.TrImageItem` plot items"""

    TRANSFORM_WIDGET_CLASS = FlipRotateWidget
