# -*- coding: utf-8 -*-
from guidata.qthelpers import get_std_icon
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.core.interfaces.common import ICurveItemType
from plotpy.core.items.annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedRectangle,
)
from plotpy.core.items.image.base import RawImageItem
from plotpy.core.items.shapes.ellipse import EllipseShape
from plotpy.core.items.shapes.rectangle import ObliqueRectangleShape, RectangleShape
from plotpy.core.panels import ID_ITEMLIST
from plotpy.core.tools.base import CommandTool, DefaultToolbarID, PanelTool
from plotpy.core.tools.curve import edit_curve_data, export_curve_data
from plotpy.core.tools.image import edit_image_data, export_image_data
from plotpy.core.tools.misc import OpenFileTool


class ItemManipulationBaseTool(CommandTool):
    """ """

    TITLE = None
    ICON = None
    TIP = None

    def __init__(self, manager, toolbar_id, curve_func, image_func):
        super(ItemManipulationBaseTool, self).__init__(
            manager, self.TITLE, icon=self.ICON, tip=self.TIP, toolbar_id=toolbar_id
        )
        self.curve_func = curve_func
        self.image_func = image_func

    def get_supported_items(self, plot):
        """

        :param plot:
        :return:
        """
        all_items = [
            item
            for item in plot.get_items(item_type=ICurveItemType)
            if not item.is_empty()
        ]

        all_items += [
            item
            for item in plot.get_items()
            if isinstance(item, RawImageItem) and not item.is_empty()
        ]
        if len(all_items) == 1:
            return all_items
        else:
            return [item for item in all_items if item in plot.get_selected_items()]

    def update_status(self, plot):
        """

        :param plot:
        """
        self.action.setEnabled(len(self.get_supported_items(plot)) > 0)

    def activate_command(self, plot, checked):
        """Activate tool"""
        for item in self.get_supported_items(plot):
            if ICurveItemType in item.types():
                self.curve_func(item)
            else:
                self.image_func(item)
        plot.replot()


class EditItemDataTool(ItemManipulationBaseTool):
    """Edit item data"""

    TITLE = _("Edit data...")
    ICON = "arredit.png"

    def __init__(self, manager, toolbar_id=None):
        super(EditItemDataTool, self).__init__(
            manager, toolbar_id, curve_func=edit_curve_data, image_func=edit_image_data
        )


class ExportItemDataTool(ItemManipulationBaseTool):
    """ """

    TITLE = _("Export data...")
    ICON = "export.png"

    def __init__(self, manager, toolbar_id=None):
        super(ExportItemDataTool, self).__init__(
            manager,
            toolbar_id,
            curve_func=export_curve_data,
            image_func=export_image_data,
        )


class ItemCenterTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=None):
        super(ItemCenterTool, self).__init__(
            manager, _("Center items"), "center.png", toolbar_id=toolbar_id
        )

    def get_supported_items(self, plot):
        """

        :param plot:
        :return:
        """
        item_types = (
            RectangleShape,
            EllipseShape,
            ObliqueRectangleShape,
            AnnotatedRectangle,
            AnnotatedEllipse,
            AnnotatedObliqueRectangle,
            AnnotatedCircle,
        )
        return [
            item
            for item in plot.get_selected_items(z_sorted=True)
            if isinstance(item, item_types)
        ]

    def update_status(self, plot):
        """

        :param plot:
        """
        self.action.setEnabled(len(self.get_supported_items(plot)) > 1)

    def activate_command(self, plot, checked):
        """Activate tool"""
        items = self.get_supported_items(plot)
        xc0, yc0 = items.pop(-1).get_center()
        for item in items:
            xc, yc = item.get_center()
            item.move_with_selection(xc0 - xc, yc0 - yc)
        plot.replot()


class DeleteItemTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=None):
        super(DeleteItemTool, self).__init__(
            manager, _("Remove"), "trash.png", toolbar_id=toolbar_id
        )

    def get_removable_items(self, plot):
        """

        :param plot:
        :return:
        """
        return [item for item in plot.get_selected_items() if not item.is_readonly()]

    def update_status(self, plot):
        """

        :param plot:
        """
        self.action.setEnabled(len(self.get_removable_items(plot)) > 0)

    def activate_command(self, plot, checked):
        """Activate tool"""
        items = self.get_removable_items(plot)
        if len(items) == 1:
            message = _("Do you really want to remove this item?")
        else:
            message = _("Do you really want to remove selected items?")
        answer = QW.QMessageBox.warning(
            plot, _("Remove"), message, QW.QMessageBox.Yes | QW.QMessageBox.No
        )
        if answer == QW.QMessageBox.Yes:
            plot.del_items(items)
            plot.replot()


class SaveItemsTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(SaveItemsTool, self).__init__(
            manager,
            _("Save items"),
            get_std_icon("DialogSaveButton", 16),
            toolbar_id=toolbar_id,
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        fname, _f = QW.QFileDialog.getSaveFileName(
            plot,
            _("Save items as"),
            _("untitled"),
            "{} (*.gui)".format(_("plotpy items")),
        )
        if not fname:
            return
        itemfile = open(fname, "wb")
        plot.save_items(itemfile, selected=True)


class LoadItemsTool(OpenFileTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(LoadItemsTool, self).__init__(
            manager, title=_("Load items"), formats="*.gui", toolbar_id=toolbar_id
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        filename = self.get_filename(plot)
        if not filename:
            return
        itemfile = open(filename, "rb")
        plot.restore_items(itemfile)
        plot.replot()


class ItemListPanelTool(PanelTool):
    panel_name = _("Item list")
    panel_id = ID_ITEMLIST
