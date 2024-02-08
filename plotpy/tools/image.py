# -*- coding: utf-8 -*-
"""Image tools"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any, Callable, Literal

from guidata.configtools import get_icon
from guidata.dataset import BoolItem, DataSet, FloatItem
from guidata.qthelpers import add_actions, exec_dialog
from guidata.widgets.arrayeditor import ArrayEditor
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy import io
from plotpy.config import _
from plotpy.constants import ID_CONTRAST, PlotType
from plotpy.events import QtDragHandler, setup_standard_tool_filter
from plotpy.interfaces import (
    IColormapImageItemType,
    IStatsImageItemType,
    IVoiImageItemType,
)
from plotpy.items import (
    AnnotatedRectangle,
    EllipseShape,
    MaskedImageItem,
    MaskedXYImageItem,
    RectangleShape,
    TrImageItem,
    get_items_in_rectangle,
)
from plotpy.mathutils.colormaps import (
    ALL_COLORMAPS,
    build_icon_from_cmap_name,
    get_cmap,
)
from plotpy.tools.base import (
    CommandTool,
    DefaultToolbarID,
    GuiTool,
    InteractiveTool,
    PanelTool,
    ToggleTool,
)
from plotpy.tools.misc import OpenFileTool
from plotpy.tools.shape import CircleTool, RectangleTool, RectangularShapeTool
from plotpy.widgets.colormap.manager import ColorMapManager
from plotpy.widgets.colormap.widget import EditableColormap
from plotpy.widgets.imagefile import exec_image_save_dialog

if TYPE_CHECKING:  # pragma: no cover
    from qtpy.QtCore import QEvent
    from qtpy.QtWidgets import QMenu

    from plotpy.events import StatefulEventFilter
    from plotpy.interfaces.items import IBasePlotItem
    from plotpy.items.image.base import BaseImageItem
    from plotpy.items.shape.base import AbstractShape
    from plotpy.items.shape.polygon import PolygonShape
    from plotpy.plot import BasePlot
    from plotpy.plot.manager import PlotManager
    from plotpy.plot.plotwidget import PlotOptions
    from plotpy.styles.shape import AnnotationParam


class ImageStatsRectangle(AnnotatedRectangle):
    """Rectangle used to display image statistics

    Args:
        x1: X position of the first rectangle corner. Defaults to 0.
        y1: Y position of the first rectangle corner. Defaults to 0.
        x2: X position of the second rectangle corner. Defaults to 0.
        y2: Y position of the second rectangle corner. Defaults to 0.
        annotationparam: _description_. Defaults to None.
        show_surface: _description_. Defaults to False.
        show_integral: _description_. Defaults to False.
    """

    shape: PolygonShape

    def __init__(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 0.0,
        y2: float = 0.0,
        annotationparam: AnnotationParam | None = None,
        show_surface=False,
        show_integral=False,
    ):
        """_summary_"""
        super().__init__(x1, y1, x2, y2, annotationparam)
        self.image_item: BaseImageItem | None = None
        self.setIcon(get_icon("imagestats.png"))
        self.show_surface = show_surface
        self.show_integral = show_integral

    def set_image_item(self, image_item: BaseImageItem) -> None:
        """Set image item to be used for statistics

        Args:
            image_item: image item to be used for statistics
        """
        self.image_item = image_item

    # ----AnnotatedShape API-----------------------------------------------------
    def get_infos(self) -> str | None:
        """Get informations on current shape

        Returns:
            Formatted string with informations on current shape or None.
        """
        if self.image_item is None:
            return None
        plot = self.image_item.plot()
        if plot is None:
            return None
        p0y = plot.transform(0, self.shape.get_points()[0][1])
        p0x = plot.transform(2, self.shape.get_points()[0][0])
        p1y = plot.transform(0, self.shape.get_points()[1][1])
        p1x = plot.transform(2, self.shape.get_points()[1][0])
        p0 = QC.QPointF(p0x, p0y)
        p1 = QC.QPointF(p1x, p1y)
        items = get_items_in_rectangle(plot, p0, p1)
        if len(items) >= 1:
            sorted_items = [
                it for it in sorted(items, key=lambda obj: obj.z()) if it.isVisible()
            ]
            if len(sorted_items) >= 1:
                self.image_item = sorted_items[-1]
            else:
                return _("No available data")
        else:
            return _("No available data")
        return self.image_item.get_stats(
            *self.get_rect(), self.show_surface, self.show_integral
        )


class ImageStatsTool(RectangularShapeTool):
    """Tool to display image statistics in a rectangle

    Args:
        manager: PlotManager instance
        setup_shape_cb: Callback called after shape setup. Defaults to None.
        handle_final_shape_cb: Callback called when handling final shape.
        Defaults to None.
        shape_style: tuple of string to set the shape style. Defaults to None.
        toolbar_id: toolbar id to use. Defaults to DefaultToolbarID. Defaults to
        DefaultToolbarID.
        title: tool title. Defaults to None.
        icon: tool icon filename. Defaults to None.
        tip: user tip to be displayed. Defaults to None.
        show_surface: Flag to show surface. Defaults to False.
        show_integral: Flag to show integral. Defaults to False.

    """

    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Image statistics")
    ICON = "imagestats.png"
    SHAPE_STYLE_KEY = "shape/image_stats"

    def __init__(
        self,
        manager,
        setup_shape_cb: Callable[[AbstractShape], None] | None = None,
        handle_final_shape_cb: Callable[[AbstractShape], None] | None = None,
        shape_style: tuple[str, str] | None = None,
        toolbar_id: Any | type[DefaultToolbarID] = DefaultToolbarID,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
        show_surface: bool = False,
        show_integral: bool = False,
    ) -> None:
        super().__init__(
            manager,
            setup_shape_cb,
            handle_final_shape_cb,
            shape_style,
            toolbar_id,
            title,
            icon,
            tip,
        )
        self._last_item = None
        self.show_surface = show_surface
        self.show_integral = show_integral

    def get_last_item(self) -> BaseImageItem | None:
        """Last image item getter

        Returns:
            Returns last image item or None
        """
        if self._last_item is not None:
            return self._last_item()
        return None

    def create_shape(self) -> tuple[ImageStatsRectangle, Literal[0], Literal[2]]:
        """Returns a new ImageStatsRectangle instance with default x1, y1, x2, y2values
        and current show_surface and show_integral values.

        Returns:
            New ImageStatsRectangle instance
        """
        return (
            ImageStatsRectangle(
                0,
                0,
                1,
                1,
                show_surface=self.show_surface,
                show_integral=self.show_integral,
            ),
            0,
            2,
        )

    def setup_shape(self, shape: ImageStatsRectangle) -> None:
        """Setup and registers given shape.

        Parameters:
            shape: Shape to setup
        """
        super().setup_shape(shape)
        shape.setTitle(_("Image statistics"))
        self.set_shape_style(shape)
        self.register_shape(shape, final=False)

    def register_shape(self, shape: ImageStatsRectangle, final=False) -> None:
        """Register given shape

        Args:
            shape: Shape to register
            final: unused argument. Defaults to False.
        """
        plot = shape.plot()
        image = self.get_last_item()
        if plot is not None and image is not None:
            plot.unselect_all()
            plot.set_active_item(shape)
            shape.set_image_item(image)

    def handle_final_shape(self, shape: ImageStatsRectangle) -> None:
        """Handle final shape

        Args:
            shape: Shape to handled and register
        """
        super().handle_final_shape(shape)
        self.register_shape(shape, final=True)

    def get_associated_item(self, plot: BasePlot) -> BaseImageItem | None:
        """Return a reference to the last image item associated with the tool

        Args:
            plot: Plot instance

        Returns:
            Reference to the last image item associated with the tool
        """
        items = plot.get_selected_items(item_type=IStatsImageItemType)
        if len(items) == 1:
            self._last_item = weakref.ref(items[0])
        return self.get_last_item()

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status if the plot type is not PlotType.CURVE.

        Args:
            plot: Plot instance
        """
        if update_image_tool_status(self, plot):
            item = self.get_associated_item(plot)
            self.action.setEnabled(item is not None)


class ReverseYAxisTool(ToggleTool):
    """Togglable tool to reverse y axis

    Args:
        manager: PlotManager Instance
    """

    def __init__(self, manager: PlotManager) -> None:
        super().__init__(manager, _("Reverse Y axis"))

    def activate_command(self, plot: PlotManager, checked: bool) -> None:
        """Triggers tool action.

        Args:
            plot: Plot instance
            checked: True if tool is checked, False otherwise
        """
        plot.set_axis_direction("left", checked)
        plot.replot()

    def update_status(self, plot: PlotManager) -> None:
        """Update tool status if the plot type is not PlotType.CURVE.

        Args:
            plot: Plot instance
        """
        if update_image_tool_status(self, plot):
            self.action.setChecked(plot.get_axis_direction("left"))


class AspectRatioParam(DataSet):
    """Dataset containing aspect ratio parameters."""

    lock = BoolItem(_("Lock aspect ratio"))
    current = FloatItem(_("Current value")).set_prop("display", active=False)
    ratio = FloatItem(_("Lock value"), min=1e-3)


class AspectRatioTool(CommandTool):
    """Tool to manage the aspect ratio of a plot

    Args:
        manager: PlotManager instance"""

    def __init__(self, manager: PlotManager) -> None:
        super().__init__(manager, _("Aspect ratio"), tip=None, toolbar_id=None)
        self.action.setEnabled(True)

    def create_action_menu(self, manager: PlotManager) -> QMenu:
        """Create and return menu for the tool's action"""
        self.ar_param = AspectRatioParam(_("Aspect ratio"))
        menu = QW.QMenu()
        self.lock_action = manager.create_action(
            _("Lock"), toggled=self.lock_aspect_ratio
        )
        self.ratio1_action = manager.create_action(
            _("1:1"), triggered=self.set_aspect_ratio_1_1
        )
        self.set_action = manager.create_action(
            _("Edit..."), triggered=self.edit_aspect_ratio
        )
        add_actions(menu, (self.lock_action, None, self.ratio1_action, self.set_action))
        return menu

    def set_aspect_ratio_1_1(self) -> None:
        """Reset current aspect ratio to 1:1"""
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_aspect_ratio(ratio=1)
            plot.replot()

    def activate_command(self, plot: PlotManager, checked: bool) -> None:
        """Triggers tool action.

        Args:
            plot: Plot instance
            checked: True if tool is checked, False otherwise
        """

    def __update_actions(self, checked: bool) -> None:
        """Update actions state according to given checked state

        Args:
            checked: True if actions should be enabled, False otherwise
        """
        self.ar_param.lock = checked
        #        self.lock_action.blockSignals(True)
        self.lock_action.setChecked(checked)
        #        self.lock_action.blockSignals(False)
        plot = self.get_active_plot()
        if plot is not None:
            ratio = plot.get_aspect_ratio()
            self.ratio1_action.setEnabled(checked and ratio != 1.0)

    def lock_aspect_ratio(self, checked: bool) -> None:
        """Lock aspect ratio depending on given checked state.

        Args:
            checked: True if aspect ratio should be locked, False otherwise
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_aspect_ratio(lock=checked)
            self.__update_actions(checked)
            plot.replot()

    def edit_aspect_ratio(self) -> None:
        """Edit the aspect ratio with a dataset dialog"""
        plot = self.get_active_plot()
        if plot is not None:
            self.ar_param.lock = plot.lock_aspect_ratio
            self.ar_param.ratio = plot.get_aspect_ratio()
            self.ar_param.current = plot.get_current_aspect_ratio()
            if self.ar_param.edit(parent=plot):
                lock, ratio = self.ar_param.lock, self.ar_param.ratio
                plot.set_aspect_ratio(ratio=ratio, lock=lock)
                self.__update_actions(lock)
                plot.replot()

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status if the plot type is not PlotType.CURVE.

        Args:
            plot: Plot instance
        """
        if update_image_tool_status(self, plot):
            ratio = plot.get_aspect_ratio()
            lock = plot.lock_aspect_ratio
            self.ar_param.ratio, self.ar_param.lock = ratio, lock
            self.__update_actions(lock)


class ContrastPanelTool(PanelTool):
    """Tools to adjust contrast using a dataset dialog"""

    panel_name = _("Contrast adjustment")
    panel_id = ID_CONTRAST

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status.

        Args:
            plot: Plot Instance
        """
        super().update_status(plot)
        update_image_tool_status(self, plot)
        item = plot.get_last_active_item(IVoiImageItemType)
        panel = self.manager.get_panel(self.panel_id)
        for action in panel.toolbar.actions():
            if isinstance(action, QW.QAction):
                action.setEnabled(item is not None)


class ColormapTool(CommandTool):
    """Tool used to select and manage colormaps (inculding visualization, edition
    and saving).

    Args:
        manager: PlotManager Instance
        toolbar_id: Toolbar Id to use. Defaults to DefaultToolbarID.
    """

    def __init__(
        self, manager: PlotManager, toolbar_id=DefaultToolbarID
    ) -> None:  # noqa: F821
        super().__init__(
            manager,
            _("Colormap"),
            tip=_("Select colormap for active image"),
            toolbar_id=toolbar_id,
        )
        self._active_colormap: EditableColormap = ALL_COLORMAPS["jet"]
        self.default_icon = build_icon_from_cmap_name(self._active_colormap.name)
        if self.action is not None:
            self.action.setEnabled(False)
            self.action.setIconText("")
            self.action.setIcon(self.default_icon)

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """Triggers tool action.

        Args:
            plot: Plot instance
            checked: True if tool is checked, False otherwise
        """
        if (
            plot is None
            or not isinstance(self.action, QC.QObject)
            or not isinstance(self.action.text(), str)
        ):
            return
        manager = ColorMapManager(
            plot.parent(), active_colormap=self._active_colormap.name
        )
        if exec_dialog(manager) and (cmap := manager.get_colormap()) is not None:
            self.activate_cmap(cmap)

    def get_selected_images(self, plot: BasePlot) -> list[IBasePlotItem]:
        """Returns the currently selected images in the given plot.

        Args:
            plot: Plot instance

        Returns:
            list of currently selected images in the given plot
        """
        items = plot.get_selected_items(item_type=IColormapImageItemType)
        if not items:
            active_image = plot.get_last_active_item(IColormapImageItemType)
            if active_image:
                items = [active_image]
        return items

    def activate_cmap(self, cmap: str | EditableColormap) -> None:
        """Activate the given colormap. Supports mutliple input types.

        Args:
            cmap: Cmap to apply for currently selected images.
        """
        assert isinstance(cmap, (str, EditableColormap))
        if isinstance(cmap, str):
            self._active_colormap = get_cmap(cmap)
        else:
            self._active_colormap = cmap
        plot = self.get_active_plot()
        if self._active_colormap is not None and plot is not None:
            items = self.get_selected_images(plot)
            for item in items:
                item.param.colormap = self._active_colormap.name
                item.param.update_item(item)
            self.action.setText(_("Colormap: %s") % self._active_colormap.name)
            plot.invalidate()
            self.update_status(plot)

    def update_status(self, plot: BasePlot) -> None:
        """Update tool status if the plot type is not PlotType.CURVE.

        Args:
            plot: Plot Instance
        """
        if update_image_tool_status(self, plot):
            item = plot.get_last_active_item(IColormapImageItemType)
            icon = self.default_icon
            if item:
                self.action.setEnabled(True)
                cmap_name = item.get_color_map_name()
                if cmap_name:
                    icon = build_icon_from_cmap_name(cmap_name)
                    self._active_colormap = get_cmap(cmap_name)
            else:
                self.action.setEnabled(False)
                self._active_colormap = ALL_COLORMAPS["jet"]
            self.action.setIcon(icon)


class ImageMaskTool(CommandTool):
    """Tool to manage image masking

    Args:
        manager: Plot manager instance
        toolbar_id: Toolbar id value
    """

    #: Signal emitted by ImageMaskTool when mask was applied
    SIG_APPLIED_MASK_TOOL = QC.Signal()

    def __init__(self, manager: PlotManager, toolbar_id=DefaultToolbarID) -> None:
        self._mask_shapes = {}
        self._mask_already_restored = {}
        super().__init__(
            manager,
            _("Mask"),
            icon="mask_tool.png",
            tip=_("Manage image masking areas"),
            toolbar_id=toolbar_id,
        )
        self.masked_image = None  # associated masked image item

    def create_action_menu(self, manager: PlotManager) -> QMenu:
        """Create and return the tool's action menu for a given manager.

        Args:
            manager: PlotManager instance
        """
        rect_tool = manager.add_tool(
            RectangleTool,
            toolbar_id=None,
            handle_final_shape_cb=lambda shape: self.handle_shape(shape, inside=True),
            title=_("Mask rectangular area (inside)"),
            icon="mask_rectangle.png",
        )
        rect_out_tool = manager.add_tool(
            RectangleTool,
            toolbar_id=None,
            handle_final_shape_cb=lambda shape: self.handle_shape(shape, inside=False),
            title=_("Mask rectangular area (outside)"),
            icon="mask_rectangle_outside.png",
        )
        ellipse_tool = manager.add_tool(
            CircleTool,
            toolbar_id=None,
            handle_final_shape_cb=lambda shape: self.handle_shape(shape, inside=True),
            title=_("Mask circular area (inside)"),
            icon="mask_circle.png",
        )
        ellipse_out_tool = manager.add_tool(
            CircleTool,
            toolbar_id=None,
            handle_final_shape_cb=lambda shape: self.handle_shape(shape, inside=False),
            title=_("Mask circular area (outside)"),
            icon="mask_circle_outside.png",
        )

        menu = QW.QMenu()
        self.showmask_action = manager.create_action(
            _("Show image mask"), toggled=self.show_mask
        )
        showshapes_action = manager.create_action(
            _("Show masking shapes"), toggled=self.show_shapes
        )
        showshapes_action.setChecked(True)
        applymask_a = manager.create_action(
            _("Apply mask"), icon=get_icon("apply.png"), triggered=self.apply_mask
        )
        clearmask_a = manager.create_action(
            _("Clear mask"), icon=get_icon("delete.png"), triggered=self.clear_mask
        )
        removeshapes_a = manager.create_action(
            _("Remove all masking shapes"),
            icon=get_icon("delete.png"),
            triggered=self.remove_all_shapes,
        )
        add_actions(
            menu,
            (
                self.showmask_action,
                None,
                showshapes_action,
                rect_tool.action,
                ellipse_tool.action,
                rect_out_tool.action,
                ellipse_out_tool.action,
                applymask_a,
                None,
                clearmask_a,
                removeshapes_a,
            ),
        )
        self.action.setMenu(menu)
        return menu

    def update_status(self, plot: BasePlot) -> None:
        """Enables tool if masked_image is set.

        Args:
            plot: Plot instance
        """
        self.action.setEnabled(self.masked_image is not None)

    def register_plot(self, baseplot: BasePlot) -> None:
        """Register plot in the tool instance and connect signals.

        Args:
            baseplot: Plot instance
        """
        super().register_plot(baseplot)
        self._mask_shapes.setdefault(baseplot, [])
        baseplot.SIG_ITEMS_CHANGED.connect(self.items_changed)
        baseplot.SIG_ITEM_SELECTION_CHANGED.connect(self.item_selection_changed)

    def show_mask(self, state: bool):
        """Shows the image mask depending on given state and if masked_image is set

        Args:
            state: True to show mask, False otherwise
        """
        if self.masked_image is not None:
            self.masked_image.set_mask_visible(state)

    def apply_mask(self):
        """Applies the mask to the image"""
        mask = self.masked_image.get_mask()
        plot = self.get_active_plot()
        for shape, inside in self._mask_shapes[plot]:
            if isinstance(shape, RectangleShape):
                self.masked_image.align_rectangular_shape(shape)
                x0, y0, x1, y1 = shape.get_rect()
                self.masked_image.mask_rectangular_area(x0, y0, x1, y1, inside=inside)
            else:
                x0, y0, x1, y1 = shape.get_rect()
                self.masked_image.mask_circular_area(x0, y0, x1, y1, inside=inside)
        self.masked_image.set_mask(mask)
        plot.replot()
        self.SIG_APPLIED_MASK_TOOL.emit()

    def remove_all_shapes(self) -> None:
        """Prompts the user to removes all shapes from the plot"""
        message = _("Do you really want to remove all masking shapes?")
        plot = self.get_active_plot()
        answer = QW.QMessageBox.warning(
            plot,
            _("Remove all masking shapes"),
            message,
            QW.QMessageBox.Yes | QW.QMessageBox.No,
        )
        if answer == QW.QMessageBox.Yes:
            self.remove_shapes()

    def remove_shapes(self) -> None:
        """Removes all shapes from the plot"""
        plot = self.get_active_plot()
        plot.del_items(
            [shape for shape, _inside in self._mask_shapes[plot]]
        )  # remove shapes
        self._mask_shapes[plot] = []
        plot.replot()

    def show_shapes(self, state: bool) -> None:
        """Shows the masking shapes depending on given state

        Args:
            state: True to show shapes, False otherwise
        """
        plot = self.get_active_plot()
        if plot is not None:
            for shape, _inside in self._mask_shapes[plot]:
                shape.setVisible(state)
            plot.replot()

    def handle_shape(self, shape: AbstractShape, inside: bool) -> None:
        """Handles given shape and adds it to the plot and sets it to be the current
        item"""
        shape.set_style("plot", "shape/mask")
        shape.set_private(True)
        plot = self.get_active_plot()
        plot.set_active_item(shape)
        self._mask_shapes[plot] += [(shape, inside)]

    def find_masked_image(
        self, plot: BasePlot
    ) -> MaskedImageItem | MaskedXYImageItem | None:
        """Finds the masked image item in the given plot

        Args:
            plot: Plot instance

        Returns:
            MaskedImageItem or MaskedXYImageItem instance if found, None otherwise
        """
        maskedtypes = (MaskedImageItem, MaskedXYImageItem)
        item = plot.get_active_item()
        if isinstance(item, maskedtypes):
            return item
        items = [item for item in plot.get_items() if isinstance(item, maskedtypes)]
        if items:
            return items[-1]
        return None

    def create_shapes_from_masked_areas(self) -> None:
        """Creates shapes from the masked areas of the masked image (rectangular or
        ellipse).
        """
        plot = self.get_active_plot()
        self._mask_shapes[plot] = []
        for area in self.masked_image.get_masked_areas():
            if area is not None and area.geometry == "rectangular":
                shape = RectangleShape(area.x0, area.y0, area.x1, area.y1)
                self.masked_image.align_rectangular_shape(shape)
            else:
                shape = EllipseShape(
                    area.x0,
                    0.5 * (area.y0 + area.y1),
                    area.x1,
                    0.5 * (area.y0 + area.y1),
                )
            shape.set_style("plot", "shape/mask")
            shape.set_private(True)
            self._mask_shapes[plot] += [(shape, area.inside)]
            plot.blockSignals(True)
            plot.add_item(shape)
            plot.blockSignals(False)

    def set_masked_image(self, plot: BasePlot) -> None:
        """Sets the masked image item from the masked image found in the given plot.

        Args:
            plot: Plot instance
        """
        self.masked_image = item = self.find_masked_image(plot)
        if self.masked_image is not None and not self._mask_already_restored:
            self.create_shapes_from_masked_areas()
            self._mask_already_restored = True
        enable = False if item is None else item.is_mask_visible()
        self.showmask_action.setChecked(enable)

    def items_changed(self, plot: BasePlot) -> None:
        """Updates the masked image and the tool status for a given plot.

        Args:
            plot: Plot instance
        """
        self.set_masked_image(plot)
        self._mask_shapes[plot] = [
            (shape, inside)
            for shape, inside in self._mask_shapes[plot]
            if shape.plot() is plot
        ]
        self.update_status(plot)

    def item_selection_changed(self, plot: BasePlot) -> None:
        """Updates the masked image and the tool status for a given plot.
        Args:
            plot: Plot instance
        """
        self.set_masked_image(plot)
        self.update_status(plot)

    def clear_mask(self) -> None:
        """Prompts the user to clear the image mask (removes all masks)"""
        message = _("Do you really want to clear the mask?")
        plot = self.get_active_plot()
        answer = QW.QMessageBox.warning(
            plot, _("Clear mask"), message, QW.QMessageBox.Yes | QW.QMessageBox.No
        )
        if answer == QW.QMessageBox.Yes:
            self.masked_image.unmask_all()
            plot.replot()

    def activate_command(self, plot: BasePlot, checked=True):
        """Triggers tool action.

        Args:
            plot: Plot instance
            checked: True if tool is checked, False otherwise
        """
        pass


class LockTrImageTool(ToggleTool):
    """Lock (rotation, translation, resize)
    Args:
        manager: PlotManager instance
        toolbar_id: Toolbar id value. Not used."""

    def __init__(self, manager: PlotManager, toolbar_id=None) -> None:
        super().__init__(
            manager, title=_("Lock"), icon=get_icon("lock.png"), toolbar_id=None
        )

    def activate_command(self, plot: PlotManager, checked: bool) -> None:
        """Trigger tool action.

        Args:
            plot: Plot instance
            checked: True if tool is checked, False otherwise
        """
        itemlist = self.get_supported_items(plot)
        if self.action is not None and self.action.isEnabled():
            for item in itemlist:
                item.set_locked(checked)
                if item.is_locked():
                    item.setIcon(get_icon("trimage_lock.png"))
                else:
                    item.setIcon(get_icon("image.png"))
            plot.SIG_ITEMS_CHANGED.emit(plot)

    def get_supported_items(self, plot: BasePlot) -> list[IBasePlotItem | TrImageItem]:
        """Returns a list of supported items from the given plot selected items.

        Args:
            plot: Plot instance

        Returns:
            List of supported items from the given plot selected items
        """
        return [
            _it for _it in plot.get_selected_items() if isinstance(_it, TrImageItem)
        ]

    def update_status(self, plot: BasePlot) -> None:
        """Updates the tool status depending on the selected items in the given plot.

        Args:
            plot: Plot instance
        """
        itemlist = self.get_supported_items(plot)
        if len(itemlist) > 0:  # at least one TrImage in selection
            self.action.setEnabled(True)
            locklist = [_it.is_locked() for _it in itemlist]
            if locklist.count(False) > 0:  # at least one image is not locked
                self.action.setChecked(False)
                self.title = _("Lock")
                self.action.setText(self.title)
                self.icon = get_icon("trimage_lock.png")
                self.action.setIcon(self.icon)
            else:  # all images are locked
                self.action.setChecked(True)
                self.title = _("Unlock")
                self.action.setText(self.title)
                self.icon = get_icon("trimage_unlock.png")
                self.action.setIcon(self.icon)
        else:
            self.action.setEnabled(False)

    def setup_context_menu(self, menu: QW.QMenu, plot: BasePlot) -> None:
        """Command Tool re-implement"""
        if self.action is not None and self.action.isEnabled():
            menu.addAction(self.action)


class OpenImageTool(OpenFileTool):
    """Tool to open an image file

    Args:
        manager: PlotManager instance
        toolbar_id: Toolbar id value. Defaults to DefaultToolbarID.
    """

    def __init__(self, manager: PlotManager, toolbar_id=DefaultToolbarID) -> None:
        super().__init__(
            manager,
            title=_("Open image"),
            formats=io.iohandler.get_filters("load"),
            toolbar_id=toolbar_id,
        )


class RotationCenterTool(InteractiveTool):
    """Tool to set the rotation center of an image

    Args:
       manager: PlotManager instance
       toolbar_id: toolbar id to use. Defaults to DefaultToolbarID.. Defaults to
        DefaultToolbarID.
       title: tool title. Defaults to None.
       icon: tool icon filename. Defaults to None.
       tip: user tip to be displayed. Defaults to None.
       switch_to_default_tool: Flag to switch to default tool. Defaults to True.
       rotation_point_move_with_shape: Flag to move rotation point with shape when it
        is moved. Defaults to True.
       rotation_center: True if image already has a rotation center, False otherwise.
       on_all_items: True if rotation center should be set on all items or False if only
        on selected ones. Defaults to True.

    """

    TITLE = _("Rotation Center")
    ICON = "rotationcenter.jpg"
    CURSOR = QC.Qt.CursorShape.CrossCursor

    SIG_TOOL_ENABLED = QC.Signal(bool)

    def __init__(
        self,
        manager: BasePlot,
        toolbar_id: Any | type[DefaultToolbarID] = DefaultToolbarID,
        title: str | None = None,
        icon: str | None = None,
        tip: str | None = None,
        switch_to_default_tool=True,
        rotation_point_move_with_shape=True,
        rotation_center=True,
        on_all_items=True,
    ) -> None:
        super().__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )

        self.rotation_point_move_with_shape = rotation_point_move_with_shape
        self.rotation_center = rotation_center
        self.on_all_items = on_all_items
        self.action.triggered.connect(self.action_triggered)
        self.filter: StatefulEventFilter | None = None
        self.pos: QC.QPointF | None = None

    def setup_filter(self, baseplot: BasePlot) -> int:
        """Setup event filter and connect signals.

        Args:
            baseplot: Plot instance

        Returns:
            plot's filter new start state
        """
        self.filter = baseplot.filter
        # Initialisation du filtre
        start_state = self.filter.new_state()
        # Bouton gauche :
        if not self.rotation_center:
            handler = QtDragHandler(
                self.filter, QC.Qt.MouseButton.LeftButton, start_state=start_state
            )
            handler.SIG_START_TRACKING.connect(self.mouse_press)
        #        else:
        #            self.mouse_press(filter, QEvent(QEvent.MouseButtonPress))
        return setup_standard_tool_filter(self.filter, start_state)

    def update_status(self, plot: BasePlot) -> None:
        """Updates the tool status depending on the selected items in the given plot.

        Args:
            plot: Plot instance
        """
        enabled = False
        self.action.setEnabled(enabled)
        selected_items = plot.get_selected_items()
        for item in selected_items:
            if isinstance(item, TrImageItem):
                enabled = True
                break
        self.action.setEnabled(enabled)
        self.SIG_TOOL_ENABLED.emit(enabled)

    def action_triggered(self, checked: bool) -> None:
        """Action triggered slot

        Args:
            checked: unused argument
        """
        if self.rotation_center and self.filter is not None:
            self.mouse_press(self.filter, QC.QEvent(QC.QEvent.Type.MouseButtonPress))

    def mouse_press(self, filter: StatefulEventFilter, event: QEvent) -> None:
        """We create a new shape if it's the first point
        otherwise we add a new point.

        Args:
            filter: StatefulEventFilter instance
            event: QEvent instance
        """
        plot = filter.plot
        selected_items = plot.get_selected_items()
        all_items = plot.get_items()
        if self.rotation_center:
            if not self.on_all_items:
                for item in selected_items:
                    if isinstance(item, TrImageItem):
                        item.set_rotation_point_to_center()
            else:
                for item in all_items:
                    if isinstance(item, TrImageItem):
                        item.set_rotation_point_to_center()
        else:  # graphical user_defined rotation point
            pos = event.pos()
            plot = filter.plot
            self.pos = QC.QPointF(
                plot.invTransform(2, pos.x()), plot.invTransform(0, pos.y())
            )
            if not self.on_all_items:
                for item in selected_items:
                    if isinstance(item, TrImageItem):
                        item.set_rotation_point(
                            self.pos.x(),
                            self.pos.y(),
                            self.rotation_point_move_with_shape,
                        )
            else:
                for item in all_items:
                    if isinstance(item, TrImageItem):
                        item.set_rotation_point(
                            self.pos.x(),
                            self.pos.y(),
                            self.rotation_point_move_with_shape,
                        )
            filter.plot.replot()
        self.validate(filter, event)  # switch to default tool


class RotateCropTool(CommandTool):
    """Rotate & Crop tool

    See :py:class:`.rotatecrop.RotateCropDialog` dialog.

    Args:
        manager: PlotManager instance
        toolbar_id: toolbar id to use. Defaults to DefaultToolbarID.
        options: PlotOptions for the tool. Defaults to None.
    """

    def __init__(
        self,
        manager: PlotManager,
        toolbar_id=DefaultToolbarID,
        options: PlotOptions | None = None,
    ) -> None:
        super().__init__(
            manager,
            title=_("Rotate and crop"),
            icon=get_icon("rotate.png"),
            toolbar_id=toolbar_id,
        )
        self.options = options

    def activate_command(self, plot: BasePlot, checked: bool) -> None:
        """Activate tool

        Args:
            plot: Plot instance
            checked: True if tool is checked, False otherwise
        """
        # This import can't be done at the module level because it creates a
        # circular import: we create a dialog that itself instantiates a
        # PlotWidget, so it needs to import plotpy.widgets.plotwidget at some
        # point.
        # pylint: disable=import-outside-toplevel
        from plotpy.widgets.rotatecrop import RotateCropDialog

        for item in plot.get_selected_items():
            if isinstance(item, TrImageItem):
                z = int(item.z())
                plot.del_item(item)
                dlg = RotateCropDialog(plot.parent(), options=self.options)
                dlg.set_item(item)
                ok = dlg.exec()
                plot.add_item(item, z=z)
                if not ok:
                    break

    def update_status(self, plot: BasePlot) -> None:
        """Updates the tool status depending on the selected items in the given plot.

        Args:
            plot: Plot instance
        """
        status = any(
            isinstance(item, TrImageItem) for item in plot.get_selected_items()
        )
        self.action.setEnabled(status)


def update_image_tool_status(tool: GuiTool, plot: BasePlot) -> bool:
    """Update tool status if the plot type is not PlotType.CURVE.

    Args:
        tool: Tool instance
        plot: Plot instance
    """
    enabled = plot.options.type != PlotType.CURVE
    tool.action.setEnabled(enabled)
    return enabled


def export_image_data(item) -> None:
    """Export image item data to file"""
    exec_image_save_dialog(item.plot(), item.data)


def edit_image_data(item) -> None:
    """Edit image item data in array editor"""
    dialog = ArrayEditor(item.plot())
    dialog.setup_and_check(item.data)
    dialog.exec_()
