# -*- coding: utf-8 -*-

"""
Plot Item list
^^^^^^^^^^^^^^

The `plot item list` panel is a widget which displays the list of items attached to
the plot.

.. autoclass:: PlotItemList
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.configtools import get_icon, get_image_layout
from guidata.qthelpers import add_actions, create_action
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.constants import ID_ITEMLIST, PARAMETERS_TITLE_ICON
from plotpy.interfaces import IPanel
from plotpy.interfaces import items as itf
from plotpy.panels.base import PanelWidget
from plotpy.plot import BasePlot, PlotManager
from plotpy.styles.base import ItemParameters

if TYPE_CHECKING:
    from qtpy.QtGui import QContextMenuEvent, QIcon
    from qtpy.QtWidgets import QListWidgetItem, QWidget


class ItemListWidget(QW.QListWidget):
    """
    PlotItemList
    List of items attached to plot
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.manager = None
        self.plot = None  # the default plot...
        self.items = []

        self.currentRowChanged.connect(self.current_row_changed)
        self.itemChanged.connect(self.item_changed)
        self.itemSelectionChanged.connect(self.refresh_actions)
        self.itemSelectionChanged.connect(self.selection_changed)

        self.setWordWrap(True)
        self.setMinimumWidth(140)
        self.setSelectionMode(QW.QListWidget.ExtendedSelection)

        # Setup context menu
        self.menu = QW.QMenu(self)
        self.menu_actions = self.setup_actions()
        self.refresh_actions()
        add_actions(self.menu, self.menu_actions)

    def register_panel(self, manager: PlotManager) -> None:
        """Register panel to plot manager

        Args:
            manager: plot manager to register to
        """
        self.manager = manager

        for plot in self.manager.get_plots():
            plot.SIG_ITEMS_CHANGED.connect(self.items_changed)
            plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)
            plot.SIG_ITEM_PARAMETERS_CHANGED.connect(self.item_parameters_changed)
        self.plot = self.manager.get_plot()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Override Qt method"""
        self.refresh_actions()
        self.menu.popup(event.globalPos())

    def setup_actions(self) -> None:
        """Setup actions"""
        self.rename_ac = create_action(
            self,
            _("Rename"),
            icon=get_icon("rename.png"),
            triggered=self.rename_item,
            shortcut="F2",
        )
        self.movedown_ac = create_action(
            self,
            _("Move to back"),
            icon=get_icon("arrow_down.png"),
            triggered=lambda: self.move_item("down"),
        )
        self.moveup_ac = create_action(
            self,
            _("Move to front"),
            icon=get_icon("arrow_up.png"),
            triggered=lambda: self.move_item("up"),
        )
        self.settings_ac = create_action(
            self,
            _("Parameters..."),
            icon=get_icon("settings.png"),
            triggered=self.edit_plot_parameters,
        )
        self.remove_ac = create_action(
            self, _("Remove"), icon=get_icon("trash.png"), triggered=self.remove_item
        )
        return [
            self.rename_ac,
            self.moveup_ac,
            self.movedown_ac,
            None,
            self.settings_ac,
            self.remove_ac,
        ]

    def edit_plot_parameters(self) -> None:
        """Edit plot parameters"""
        # In order to support non-selectable items, we have to reimplement the
        # `BasePlot.edit_plot_parameters` method. This is because we can select items
        # using the `PlotItemList` widget, but we can't select them using the plot
        # widget. Thus we can't rely on the `BasePlot.get_selected_items` method and
        # other methods that rely on it.
        #
        # This can be tested for example by uncommenting the line containing
        # `item.set_selectable(False)` in the `tests/items/test_transform.py` file.

        # === Reimplementing the `BasePlot.edit_plot_parameters`:
        sel_items = self.get_selected_items()
        multiselection = len(sel_items) > 1
        itemparams = ItemParameters(multiselection=multiselection)
        # === === Reimplementing the `BasePlot.get_plot_parameters`:
        for item in sel_items:
            item.get_item_parameters(itemparams)
        sel_items[0].get_item_parameters(itemparams)
        if self.plot.get_show_axes_tab():
            Param = self.plot.get_axesparam_class(sel_items[0])
            axesparam = Param(
                title=_("Axes"),
                icon="lin_lin.png",
                comment=_("Axes associated to selected item"),
            )
            axesparam.update_param(sel_items[0])
            itemparams.add("AxesParam", self.plot, axesparam)
        # === ===
        title, icon = PARAMETERS_TITLE_ICON["item"]
        itemparams.edit(self.plot, title, icon)
        # ===

    def __is_selection_contiguous(self) -> bool:
        """Check if selected items are contiguous"""
        indexes = sorted([self.row(lw_item) for lw_item in self.selectedItems()])
        return len(indexes) <= 1 or list(range(indexes[0], indexes[-1] + 1)) == indexes

    def get_selected_items(self) -> list[itf.IBasePlotItem]:
        """Return selected QwtPlot items

        .. warning::

            This is not the same as
            :py:meth:`.baseplot.BasePlot.get_selected_items`.
            Some items could appear in itemlist without being registered in
            plot widget items (in particular, some items could be selected in
            itemlist without being selected in plot widget)
        """
        return [self.items[self.row(lw_item)] for lw_item in self.selectedItems()]

    def refresh_actions(self) -> None:
        """Refresh actions"""
        is_selection = len(self.selectedItems()) > 0
        for action in self.menu_actions:
            if action is not None:
                action.setEnabled(is_selection)
        if is_selection:
            editable_state = True
            for item in self.get_selected_items():
                editable_state = editable_state and not item.is_readonly()
            self.remove_ac.setEnabled(editable_state)
            for action in [self.moveup_ac, self.movedown_ac]:
                action.setEnabled(self.__is_selection_contiguous())
            self.rename_ac.setEnabled(editable_state and len(self.selectedItems()) == 1)
            self.settings_ac.setEnabled(editable_state)

    def __get_item_icon(self, item: itf.IBasePlotItem) -> QIcon:
        """Get item icon"""
        return get_icon(item.get_icon_name())

    def items_changed(self, plot: BasePlot) -> None:
        """Plot items have changed

        Args:
            plot: plot
        """
        active_plot = self.manager.get_active_plot()
        if active_plot is not plot:
            return
        self.plot = plot
        _block = self.blockSignals(True)
        active = plot.get_active_item()
        self.items = plot.get_public_items(z_sorted=True)
        self.clear()
        for item in self.items:
            title = item.title().text()
            lw_item = QW.QListWidgetItem(self.__get_item_icon(item), title, self)
            lw_item.setCheckState(
                QC.Qt.Checked if item.isVisible() else QC.Qt.Unchecked
            )
            lw_item.setSelected(item.selected)
            font = lw_item.font()
            if item is active:
                font.setItalic(True)
            else:
                font.setItalic(False)
            lw_item.setFont(font)
            self.addItem(lw_item)
        self.refresh_actions()
        self.blockSignals(_block)

    def active_item_changed(self, plot: BasePlot) -> None:
        """Plot items have changed

        Args:
            plot: plot
        """
        active_plot = self.manager.get_active_plot()
        if active_plot is not plot:
            return
        self.plot = plot
        _block = self.blockSignals(True)
        active = plot.get_active_item()
        for item in self.items:
            title = item.title().text()
            lw_item = self.item(self.items.index(item))
            lw_item.setText(title)
            lw_item.setSelected(item.selected)
            font = lw_item.font()
            if item is active:
                font.setItalic(True)
            else:
                font.setItalic(False)
            lw_item.setFont(font)
        self.refresh_actions()
        self.blockSignals(_block)

    def item_parameters_changed(self, item: itf.IBasePlotItem) -> None:
        """Item parameters have changed

        Args:
            item: item
        """
        if not isinstance(item, BasePlot):
            plot = item.plot()
            if plot is not None:
                self.items_changed(plot)

    def current_row_changed(self, index: int) -> None:
        """QListWidget current row has changed

        Args:
            index: index
        """
        if index == -1:
            return
        item = self.items[index]
        if not item.can_select():
            item = None
        if item is None:
            self.plot.replot()

    def selection_changed(self) -> None:
        """Selection has changed"""
        items = [item for item in self.get_selected_items() if item.can_select()]
        self.plot.select_some_items(items)
        self.plot.replot()

    def item_changed(self, listwidgetitem: QListWidgetItem) -> None:
        """QListWidget item has changed

        Args:
            listwidgetitem: list widget item
        """
        item = self.items[self.row(listwidgetitem)]
        visible = listwidgetitem.checkState() == QC.Qt.Checked
        if visible != item.isVisible():
            self.plot.set_item_visible(item, visible)

    def rename_item(self) -> None:
        """Rename item"""
        item = self.get_selected_items()[0]
        title = item.title().text()
        new_title, ok = QW.QInputDialog.getText(
            self, _("Rename"), _("New title:"), text=title
        )
        if ok and new_title != title:
            item.setTitle(new_title)
            self.plot.replot()
            self.items_changed(self.plot)

    def move_item(self, direction: str) -> None:
        """Move item to the background/foreground
        Works only for contiguous selection
        -> 'refresh_actions' method should guarantee that

        Args:
            direction: direction
        """
        items = self.get_selected_items()
        if direction == "up":
            self.plot.move_up(items)
        else:
            self.plot.move_down(items)
        # Re-select items which can't be selected in plot widget but can be
        # selected in ItemListWidget:
        for item in items:
            lw_item = self.item(self.items.index(item))
            if not lw_item.isSelected():
                lw_item.setSelected(True)
        self.plot.replot()

    def remove_item(self) -> None:
        """Remove item"""
        if len(self.selectedItems()) == 1:
            message = _("Do you really want to remove this item?")
        else:
            message = _("Do you really want to remove selected items?")
        answer = QW.QMessageBox.warning(
            self, _("Remove"), message, QW.QMessageBox.Yes | QW.QMessageBox.No
        )
        if answer == QW.QMessageBox.Yes:
            items = self.get_selected_items()
            self.plot.del_items(items)
            self.plot.replot()


class PlotItemList(PanelWidget):
    """Construct the `plot item list panel`"""

    __implements__ = (IPanel,)
    PANEL_ID = ID_ITEMLIST
    PANEL_TITLE = _("Item list")
    PANEL_ICON = "item_list.png"

    def __init__(self, parent):
        super().__init__(parent)
        self.manager = None

        vlayout = QW.QVBoxLayout()
        self.setLayout(vlayout)

        style = "<span style='color: #444444'><b>%s</b></span>"
        layout, _label = get_image_layout(
            self.PANEL_ICON, style % self.PANEL_TITLE, alignment=QC.Qt.AlignCenter
        )
        vlayout.addLayout(layout)
        self.listwidget = ItemListWidget(self)
        vlayout.addWidget(self.listwidget)

        toolbar = QW.QToolBar(self)
        vlayout.addWidget(toolbar)
        add_actions(toolbar, self.listwidget.menu_actions)

    def register_panel(self, manager: PlotManager) -> None:
        """Register panel to plot manager

        Args:
            manager: plot manager
        """
        self.manager = manager
        self.listwidget.register_panel(manager)

    def configure_panel(self):
        """Configure panel"""
        pass


assert_interfaces_valid(PlotItemList)
