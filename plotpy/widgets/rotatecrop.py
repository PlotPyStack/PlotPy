# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

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
   :inherited-members:
.. autoclass:: RotateCropWidget
   :members:
   :inherited-members:
"""

from guidata.configtools import get_icon
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.widgets import base
from plotpy.widgets.builder import make
from plotpy.widgets.items.image.misc import get_image_in_shape
from plotpy.widgets.items.image.transform import TrImageItem
from plotpy.widgets.tools.base import CommandTool, DefaultToolbarID


class RotateCropMixin(base.BaseTransformMixin):
    """Rotate & Crop mixin class, to be mixed with a class providing the
    get_plot method, like PlotDialog or RotateCropWidget (see below)"""

    def __init__(self):
        base.BaseTransformMixin.__init__(self)
        self.crop_rect = None

    # ------BaseTransformMixin API----------------------------------------------
    def add_buttons_to_layout(self, layout):
        """Add tool buttons to layout"""
        # Show crop rectangle checkbox
        show_crop = QW.QCheckBox(_("Show cropping rectangle"), self)
        show_crop.setChecked(True)
        show_crop.toggled.connect(self.show_crop_rect)
        layout.addWidget(show_crop)
        layout.addSpacing(15)
        base.BaseTransformMixin.add_buttons_to_layout(self, layout)

    def set_item(self, item):
        """Set associated item -- must be a TrImageItem object"""
        base.BaseTransformMixin.set_item(self, item)
        crect = make.annotated_rectangle(0, 0, 1, 1, _("Cropping rectangle"))
        self.crop_rect = crect
        crect.annotationparam.format = "%.1f cm"
        plot = self.get_plot()
        plot.add_item(crect)
        plot.set_active_item(crect)
        x0, y0, x1, y1 = self.item.get_crop_coordinates()
        crect.set_rect(x0, y0, x1, y1)
        plot.replot()

    def reset_transformation(self):
        """Reset transformation"""
        x0, y0, x1, y1 = self.item.border_rect.get_rect()
        self.crop_rect.set_rect(x0, y0, x1, y1)

    def apply_transformation(self):
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
        self.get_plot().replot()

    def compute_transformation(self):
        """Compute transformation, return compute output array"""
        return get_image_in_shape(self.crop_rect, apply_interpolation=False)

    # ------Private API---------------------------------------------------------
    def show_crop_rect(self, state):
        """Show/hide cropping rectangle shape"""
        self.crop_rect.setVisible(state)
        self.crop_rect.label.setVisible(state)
        self.get_plot().replot()


class RotateCropDialog(base.BaseTransformDialog, RotateCropMixin):
    """Rotate & Crop Dialog

    Rotate and crop a :py:class:`.image.TrImageItem` plot item"""

    def __init__(
        self,
        parent,
        wintitle=None,
        options=None,
        resize_to=None,
        edit=True,
        toolbar=False,
    ):
        RotateCropMixin.__init__(self)
        base.BaseTransformDialog.__init__(
            self,
            parent,
            wintitle=wintitle,
            options=options,
            resize_to=resize_to,
            edit=edit,
            toolbar=toolbar,
        )


class RotateCropTool(CommandTool):
    """Rotate & Crop tool

    See :py:class:`.rotatecrop.RotateCropDialog` dialog."""

    def __init__(self, manager, toolbar_id=DefaultToolbarID, options=None):
        super(RotateCropTool, self).__init__(
            manager,
            title=_("Rotate and crop"),
            icon=get_icon("rotate.png"),
            toolbar_id=toolbar_id,
        )
        self.options = options

    def activate_command(self, plot, checked):
        """Activate tool"""

        for item in plot.get_selected_items():
            if isinstance(item, TrImageItem):
                z = item.z()
                plot.del_item(item)
                dlg = RotateCropDialog(plot.parent(), options=self.options)
                dlg.set_item(item)
                ok = dlg.exec_()
                plot.add_item(item, z=z)
                if not ok:
                    break

    def update_status(self, plot):
        """

        :param plot:
        """
        from plotpy.widgets.items.image.transform import TrImageItem

        status = any(
            [isinstance(item, TrImageItem) for item in plot.get_selected_items()]
        )
        self.action.setEnabled(status)


class RotateCropWidget(base.BaseTransformWidget, RotateCropMixin):
    """Rotate & Crop Widget

    Rotate and crop a :py:class:`.image.TrImageItem` plot item"""

    def __init__(self, parent, options=None):
        base.BaseTransformWidget.__init__(self, parent, options=options)
        RotateCropMixin.__init__(self)


class MultipleRotateCropWidget(base.BaseMultipleTransformWidget):
    """Multiple Rotate & Crop Widget

    Rotate and crop several :py:class:`.image.TrImageItem` plot items"""

    TRANSFORM_WIDGET_CLASS = RotateCropWidget
