# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
rotatecrop
----------

The `rotatecrop` module provides a dialog box providing essential GUI elements
for rotating (arbitrary angle) and cropping an image:

    * :py:class:`.widgets.rotatecrop.RotateCropDialog`: dialog box
    * :py:class:`.widgets.rotatecrop.RotateCropWidget`: equivalent widget

Reference
~~~~~~~~~

.. autoclass:: RotateCropDialog
   :members:
.. autoclass:: RotateCropWidget
   :members:
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.qthelpers import win32_fix_title_bar_background
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.config import _
from plotpy.items import get_image_in_shape
from plotpy.widgets import basetransform

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np

    from plotpy.items import AnnotatedRectangle, TrImageItem
    from plotpy.plot import PlotOptions
    from plotpy.plot.manager import PlotManager


class RotateCropTransform(basetransform.BaseTransform):
    """Rotate & Crop utils class, to be mixed with a class providing the
    get_plot method, like PlotDialog or RotateCropWidget (see below)

    Args:
        parent (QWidget): Parent widget
        manager (PlotManager): Plot manager
    """

    def __init__(self, parent: RotateCropWidget, manager: PlotManager) -> None:
        super().__init__(parent, manager)
        self.crop_rect: AnnotatedRectangle = None
        self.manager = manager

    # ------BaseTransformUtils API----------------------------------------------

    def set_item(self, item: TrImageItem) -> None:
        """Set associated item

        Args:
            item (TrImageItem): Associated item
        """
        super().set_item(item)
        crect: AnnotatedRectangle = make.annotated_rectangle(
            0, 0, 1, 1, _("Cropping rectangle")
        )
        self.crop_rect = crect
        crect.annotationparam.format = "%.1f cm"
        plot = self.manager.get_plot()
        plot.add_item(crect)
        plot.set_active_item(crect)
        x0, y0, x1, y1 = self.item.get_crop_coordinates()
        crect.set_rect(x0, y0, x1, y1)
        plot.replot()

    def reset_transformation(self) -> None:
        """Reset transformation"""
        x0, y0, x1, y1 = self.item.border_rect.get_rect()
        self.crop_rect.set_rect(x0, y0, x1, y1)

    def apply_transformation(self) -> None:
        """Apply transformation, e.g. crop or rotate"""
        # Let's crop!
        i_points = self.item.border_rect.get_points()
        xmin, ymin = i_points.min(axis=0)
        xmax, ymax = i_points.max(axis=0)
        xc0, yc0, xc1, yc1 = self.crop_rect.shape.get_rect()
        left = max([0, xc0 - xmin])
        right = max([0, xmax - xc1])
        top = max([0, yc0 - ymin])
        bottom = max([0, ymax - yc1])
        self.item.set_crop(left, top, right, bottom)
        #        print "set_crop:", left, top, right, bottom
        self.item.compute_bounds()
        self.manager.get_plot().replot()

    def compute_transformation(self) -> np.ndarray:
        """Compute transformation, return compute output array

        Returns:
            numpy.ndarray: Compute output array
        """
        return get_image_in_shape(self.crop_rect, apply_interpolation=False)

    # ------Private API---------------------------------------------------------
    def show_crop_rect(self, state: bool) -> None:
        """Show/hide cropping rectangle shape

        Args:
            state (bool): Show/hide state
        """
        self.crop_rect.setVisible(state)
        self.crop_rect.label.setVisible(state)
        self.manager.get_plot().replot()


class RotateCropDialog(QW.QDialog):
    """Rotate & Crop Dialog

    Rotate and crop a :py:class:`.image.TrImageItem` plot item

    Args:
        parent (QWidget): Parent widget
        title (str | None): Dialog title
        options (dict | None): Options dict
        resize_to (tuple | None): Resize dialog to (width, height)
        edit (bool | None): Show "Edit" button
        toolbar (bool | None): Show toolbar
    """

    def __init__(
        self,
        parent: QW.QWidget,
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
            title = _("Rotate & Crop")
        self.widget = RotateCropWidget(parent=parent, options=options, toolbar=toolbar)
        self.setWindowFlags(QC.Qt.WindowType.Window)

        buttonhlayout = QW.QHBoxLayout()
        self.add_buttons_to_layout(buttonhlayout, edit)

        dialogvlayout = QW.QVBoxLayout()
        dialogvlayout.addWidget(self.widget)
        dialogvlayout.addLayout(buttonhlayout)
        self.setLayout(dialogvlayout)

        self.transform = self.widget.transform
        self.plot_widget = self.widget.plot_widget
        self.manager = self.widget.plot_widget.manager

        self.accepted.connect(self.transform.accept_changes)
        self.rejected.connect(self.transform.reject_changes)

    def add_buttons_to_layout(self, layout: QW.QBoxLayout, edit: bool) -> None:
        """Add buttons to layout

        Args:
            layout (QBoxLayout): Layout
        """
        if edit:
            self.button_box = bbox = QW.QDialogButtonBox(
                QW.QDialogButtonBox.Ok | QW.QDialogButtonBox.Cancel
            )
            bbox.accepted.connect(self.accept)
            bbox.rejected.connect(self.reject)
            layout.addWidget(bbox)


class RotateCropWidget(basetransform.BaseTransformWidget):
    """Rotate & Crop Widget

    Rotate and crop a :py:class:`.image.TrImageItem` plot item

    Args:
        parent: Parent widget
        toolbar: Show toolbar
        options: Plot options
    """

    def __init__(
        self,
        parent: QW.QWidget,
        toolbar: bool = False,
        options: PlotOptions | None = None,
    ) -> None:
        super().__init__(parent, toolbar=toolbar, options=options)
        self.transform = RotateCropTransform(self, self.plot_widget.manager)
        self.manager = self.plot_widget.manager

    def add_buttons_to_layout(self, layout: QW.QBoxLayout) -> None:
        """Add tool buttons to layout

        Args:
            layout (QBoxLayout): Layout
        """
        # Show crop rectangle checkbox
        show_crop = QW.QCheckBox(_("Show cropping rectangle"), self.plot_widget)
        show_crop.setChecked(True)
        show_crop.toggled.connect(self.show_crop_rect)
        layout.addWidget(show_crop)
        layout.addSpacing(15)
        basetransform.BaseTransformWidget.add_buttons_to_layout(self, layout)

    def apply_transformation(self) -> None:
        """Apply transformation"""
        self.transform.apply_transformation()

    def reset(self) -> None:
        """Reset transformation"""
        self.transform.reset()

    def reject_changes(self) -> None:
        """Reject changes"""
        self.transform.reject_changes()

    def show_crop_rect(self, state: bool) -> None:
        """Show/hide cropping rectangle shape

        Args:
            state (bool): Show/hide state
        """
        self.transform.show_crop_rect(state)


class MultipleRotateCropWidget(basetransform.BaseMultipleTransformWidget):
    """Multiple Rotate & Crop Widget

    Rotate and crop several :py:class:`.image.TrImageItem` plot items"""

    TRANSFORM_WIDGET_CLASS = RotateCropWidget
