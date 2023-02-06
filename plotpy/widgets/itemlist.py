# -*- coding: utf-8 -*-
from guidata.configtools import get_icon, get_image_layout
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.gui import assert_interfaces_valid
from plotpy.utils.misc_from_gui import add_actions, create_action
from plotpy.widgets.interfaces.panel import IPanel
from plotpy.widgets.panels import ID_ITEMLIST, PanelWidget


class ItemListWidget(QW.QListWidget):
    """
    PlotItemList
    List of items attached to plot
    """

    def __init__(self, parent):
        super(ItemListWidget, self).__init__(parent)

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

    def register_panel(self, manager):
        """

        :param manager:
        """
        self.manager = manager

        for plot in self.manager.get_plots():
            plot.SIG_ITEMS_CHANGED.connect(self.items_changed)
            plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)
        self.plot = self.manager.get_plot()

    def contextMenuEvent(self, event):
        """Override Qt method"""
        self.refresh_actions()
        self.menu.popup(event.globalPos())

    def setup_actions(self):
        """

        :return:
        """
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
        settings_ac = create_action(
            self,
            _("Parameters..."),
            icon=get_icon("settings.png"),
            triggered=self.edit_plot_parameters,
        )
        self.remove_ac = create_action(
            self, _("Remove"), icon=get_icon("trash.png"), triggered=self.remove_item
        )
        return [self.moveup_ac, self.movedown_ac, None, settings_ac, self.remove_ac]

    def edit_plot_parameters(self):
        """ """
        self.plot.edit_plot_parameters("item")

    def __is_selection_contiguous(self):
        indexes = sorted([self.row(lw_item) for lw_item in self.selectedItems()])
        return len(indexes) <= 1 or list(range(indexes[0], indexes[-1] + 1)) == indexes

    def get_selected_items(self):
        """Return selected QwtPlot items

        .. warning::

            This is not the same as
            :py:meth:`.baseplot.BasePlot.get_selected_items`.
            Some items could appear in itemlist without being registered in
            plot widget items (in particular, some items could be selected in
            itemlist without being selected in plot widget)
        """
        return [self.items[self.row(lw_item)] for lw_item in self.selectedItems()]

    def refresh_actions(self):
        """ """
        is_selection = len(self.selectedItems()) > 0
        for action in self.menu_actions:
            if action is not None:
                action.setEnabled(is_selection)
        if is_selection:
            remove_state = True
            for item in self.get_selected_items():
                remove_state = remove_state and not item.is_readonly()
            self.remove_ac.setEnabled(remove_state)
            for action in [self.moveup_ac, self.movedown_ac]:
                action.setEnabled(self.__is_selection_contiguous())

    # def __get_item_icon(self, item):
    #     from plotpy.gui.widgets.items.label import LegendBoxItem, LabelItem
    #     from plotpy.gui.widgets.items.annotations import (
    #         AnnotatedShape,
    #         AnnotatedRectangle,
    #         AnnotatedCircle,
    #         AnnotatedEllipse,
    #         AnnotatedPoint,
    #         AnnotatedSegment,
    #     )
    #     from plotpy.gui.widgets.items.shapes import (
    #         SegmentShape,
    #         RectangleShape,
    #         EllipseShape,
    #         PointShape,
    #         PolygonShape,
    #         Axes,
    #         XRangeSelection,
    #     )
    #     from plotpy.gui.widgets.items.image import (
    #         BaseImageItem,
    #         Histogram2DItem,
    #         ImageFilterItem,
    #     )
    #     from plotpy.gui.widgets.histogram import HistogramItem
    #
    #     icon_name = "item.png"
    #     for klass, icon in (
    #         (HistogramItem, "histogram.png"),
    #         (ErrorBarCurveItem, "errorbar.png"),
    #         (CurveItem, "curve.png"),
    #         (GridItem, "grid.png"),
    #         (LegendBoxItem, "legend.png"),
    #         (LabelItem, "label.png"),
    #         (AnnotatedSegment, "segment.png"),
    #         (AnnotatedPoint, "point_shape.png"),
    #         (AnnotatedCircle, "circle.png"),
    #         (AnnotatedEllipse, "ellipse_shape.png"),
    #         (AnnotatedRectangle, "rectangle.png"),
    #         (AnnotatedShape, "annotation.png"),
    #         (SegmentShape, "segment.png"),
    #         (RectangleShape, "rectangle.png"),
    #         (PointShape, "point_shape.png"),
    #         (EllipseShape, "ellipse_shape.png"),
    #         (Axes, "gtaxes.png"),
    #         (Marker, "marker.png"),
    #         (XRangeSelection, "xrange.png"),
    #         (PolygonShape, "freeform.png"),
    #         (Histogram2DItem, "histogram2d.png"),
    #         (ImageFilterItem, "funct.png"),
    #         (BaseImageItem, "image.png"),
    #     ):
    #         if isinstance(item, klass):
    #             icon_name = icon
    #             break
    #     return get_icon(icon_name)

    def __get_item_icon(self, item):
        icon = item.icon()
        if icon is None:
            return get_icon("not_found.png")
        else:
            return icon

    def items_changed(self, plot):
        """Plot items have changed"""
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

    def active_item_changed(self, plot):
        """Plot items have changed"""
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

    def current_row_changed(self, index):
        """QListWidget current row has changed"""
        if index == -1:
            return
        item = self.items[index]
        if not item.can_select():
            item = None
        if item is None:
            self.plot.replot()

    def selection_changed(self):
        """ """
        items = self.get_selected_items()
        self.plot.select_some_items(items)
        self.plot.replot()

    def item_changed(self, listwidgetitem):
        """QListWidget item has changed"""
        item = self.items[self.row(listwidgetitem)]
        visible = listwidgetitem.checkState() == QC.Qt.Checked
        if visible != item.isVisible():
            self.plot.set_item_visible(item, visible)

    def move_item(self, direction):
        """Move item to the background/foreground
        Works only for contiguous selection
        -> 'refresh_actions' method should guarantee that"""
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

    def remove_item(self):
        """ """
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
        super(PlotItemList, self).__init__(parent)
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

    def register_panel(self, manager):
        """Register panel to plot manager"""
        self.manager = manager
        self.listwidget.register_panel(manager)

    def configure_panel(self):
        """Configure panel"""
        pass


assert_interfaces_valid(PlotItemList)
