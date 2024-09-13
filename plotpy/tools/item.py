# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Item tools"""

from __future__ import annotations

from typing import Callable

from guidata.qthelpers import get_std_icon
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.constants import ID_ITEMLIST
from plotpy.interfaces import ICurveItemType
from plotpy.items import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPolygon,
    AnnotatedRectangle,
    EllipseShape,
    ObliqueRectangleShape,
    RawImageItem,
    RectangleShape,
)
from plotpy.plot import BasePlot
from plotpy.tools.base import CommandTool, DefaultToolbarID, PanelTool
from plotpy.tools.curve import edit_curve_data, export_curve_data
from plotpy.tools.image import edit_image_data, export_image_data
from plotpy.tools.misc import OpenFileTool


class ItemManipulationBaseTool(CommandTool):
    """Base class for item manipulation tools."""

    TITLE: str | None = None
    ICON: str | None = None
    TIP: str | None = None

    def __init__(
        self,
        manager,
        toolbar_id: str | type[DefaultToolbarID] | None,
        curve_func: Callable,
        image_func: Callable,
    ):
        """
        Initialize the ItemManipulationBaseTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
            curve_func: Callback function for curve items.
            image_func: Callback function for image items.
        """
        super().__init__(
            manager, self.TITLE, icon=self.ICON, tip=self.TIP, toolbar_id=toolbar_id
        )
        self.curve_func = curve_func
        self.image_func = image_func

    def get_supported_items(self, plot: BasePlot) -> list:
        """
        Get supported items from the plot.

        Args:
            plot: Plot instance

        Returns:
            List of supported plot items
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

    def update_status(self, plot: BasePlot) -> None:
        """
        Update the status of the tool.

        Args:
            plot: Plot instance
        """
        self.action.setEnabled(len(self.get_supported_items(plot)) > 0)

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool command.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
        for item in self.get_supported_items(plot):
            if ICurveItemType in item.types():
                self.curve_func(item)
            else:
                self.image_func(item)
        plot.replot()


class EditItemDataTool(ItemManipulationBaseTool):
    """Tool for editing item data."""

    TITLE: str = _("Edit data...")
    ICON: str = "arredit.png"

    def __init__(self, manager, toolbar_id: str | type[DefaultToolbarID] | None = None):
        """
        Initialize the EditItemDataTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
        """
        super().__init__(
            manager, toolbar_id, curve_func=edit_curve_data, image_func=edit_image_data
        )


class ExportItemDataTool(ItemManipulationBaseTool):
    """Tool for exporting item data."""

    TITLE: str = _("Export data...")
    ICON: str = "export.png"

    def __init__(self, manager, toolbar_id: str | type[DefaultToolbarID] | None = None):
        """
        Initialize the ExportItemDataTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
        """
        super().__init__(
            manager,
            toolbar_id,
            curve_func=export_curve_data,
            image_func=export_image_data,
        )


class ItemCenterTool(CommandTool):
    """Tool for centering items."""

    def __init__(self, manager, toolbar_id: str | type[DefaultToolbarID] | None = None):
        """
        Initialize the ItemCenterTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
        """
        super().__init__(
            manager, _("Center items"), "center.png", toolbar_id=toolbar_id
        )

    def get_supported_items(self, plot: BasePlot) -> list:
        """
        Get supported items from the plot.

        Args:
            plot: Plot instance

        Returns:
            List of supported plot items
        """
        item_types = (
            RectangleShape,
            EllipseShape,
            ObliqueRectangleShape,
            AnnotatedRectangle,
            AnnotatedEllipse,
            AnnotatedObliqueRectangle,
            AnnotatedCircle,
            AnnotatedPolygon,
        )
        return [
            item
            for item in plot.get_selected_items(z_sorted=True)
            if isinstance(item, item_types)
        ]

    def update_status(self, plot: BasePlot) -> None:
        """
        Update the status of the tool.

        Args:
            plot: Plot instance
        """
        self.action.setEnabled(len(self.get_supported_items(plot)) > 1)

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool command.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
        items = self.get_supported_items(plot)
        xc0, yc0 = items.pop(-1).get_center()
        for item in items:
            xc, yc = item.get_center()
            item.move_with_selection(xc0 - xc, yc0 - yc)
        plot.replot()


class DeleteItemTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id: str | type[DefaultToolbarID] | None = None):
        """
        Initialize the DeleteItemTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
        """
        super().__init__(manager, _("Remove"), "trash.png", toolbar_id=toolbar_id)

    def get_removable_items(self, plot: BasePlot) -> list:
        """
        Get removable items from the plot.

        Args:
            plot: Plot instance

        Returns:
            List of removable plot items
        """
        return [item for item in plot.get_selected_items() if not item.is_readonly()]

    def update_status(self, plot: BasePlot) -> None:
        """
        Update the status of the tool.

        Args:
            plot: Plot instance
        """
        self.action.setEnabled(len(self.get_removable_items(plot)) > 0)

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool command.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
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

    def __init__(
        self, manager, toolbar_id: str | type[DefaultToolbarID] = DefaultToolbarID
    ):
        """
        Initialize the SaveItemsTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
        """
        super().__init__(
            manager,
            _("Save items"),
            get_std_icon("DialogSaveButton", 16),
            toolbar_id=toolbar_id,
        )

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool command.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
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

    def __init__(
        self, manager, toolbar_id: str | type[DefaultToolbarID] = DefaultToolbarID
    ):
        """
        Initialize the LoadItemsTool.

        Args:
            manager: The plot manager.
            toolbar_id: ID of the toolbar to which this tool belongs.
        """
        super().__init__(
            manager, title=_("Load items"), formats="*.gui", toolbar_id=toolbar_id
        )

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """
        Activate tool command.

        Args:
            plot: Plot instance
            checked: Whether the tool is checked
        """
        filename = self.get_filename(plot)
        if not filename:
            return
        itemfile = open(filename, "rb")
        plot.restore_items(itemfile)
        plot.replot()


class ItemListPanelTool(PanelTool):
    """Tool for managing the item list panel."""

    panel_name: str = _("Item list")
    panel_id: str = ID_ITEMLIST
