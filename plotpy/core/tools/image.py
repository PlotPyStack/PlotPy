# -*- coding: utf-8 -*-
import weakref

from guidata.configtools import get_icon
from guidata.dataset.dataitems import BoolItem, FloatItem
from guidata.dataset.datatypes import DataSet
from guidata.qthelpers import add_actions
from guidata.widgets.objecteditor import oedit
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.core import io
from plotpy.core.constants import PlotType
from plotpy.core.events import QtDragHandler, setup_standard_tool_filter
from plotpy.core.interfaces.common import (
    IColormapImageItemType,
    IStatsImageItemType,
    IVoiImageItemType,
)
from plotpy.core.items import (
    AnnotatedRectangle,
    EllipseShape,
    RectangleShape,
    TrImageItem,
    get_items_in_rectangle,
)
from plotpy.core.items.image.masked import MaskedImageMixin
from plotpy.core.panels.base import ID_CONTRAST
from plotpy.core.tools.base import (
    CommandTool,
    DefaultToolbarID,
    InteractiveTool,
    PanelTool,
    ToggleTool,
)
from plotpy.core.tools.misc import OpenFileTool
from plotpy.core.tools.shapes import CircleTool, RectangleTool, RectangularShapeTool
from plotpy.mathutils.colormap import build_icon_from_cmap, get_cmap, get_colormap_list
from plotpy.widgets.imagefile import exec_image_save_dialog


class ImageStatsRectangle(AnnotatedRectangle):
    """ """

    def __init__(
        self,
        x1=0,
        y1=0,
        x2=0,
        y2=0,
        annotationparam=None,
        show_surface=False,
        show_integral=False,
    ):
        super(ImageStatsRectangle, self).__init__(x1, y1, x2, y2, annotationparam)
        self.image_item = None
        self.setIcon(get_icon("imagestats.png"))
        self.show_surface = show_surface
        self.show_integral = show_integral

    def set_image_item(self, image_item):
        """

        :param image_item:
        """
        self.image_item = image_item

    # ----AnnotatedShape API-----------------------------------------------------
    def get_infos(self) -> str:
        """Get informations on current shape

        Returns:
            str: Formatted string with informations on current shape
        """
        if self.image_item is None:
            return
        plot = self.image_item.plot()
        if plot is None:
            return
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
    """ """

    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Image statistics")
    ICON = "imagestats.png"
    SHAPE_STYLE_KEY = "shape/image_stats"

    def __init__(
        self,
        manager,
        setup_shape_cb=None,
        handle_final_shape_cb=None,
        shape_style=None,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        show_surface=False,
        show_integral=False,
    ):
        super(ImageStatsTool, self).__init__(
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

    def get_last_item(self):
        """

        :return:
        """
        if self._last_item is not None:
            return self._last_item()

    def create_shape(self):
        """

        :return:
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

    def setup_shape(self, shape):
        """

        :param shape:
        """
        super(ImageStatsTool, self).setup_shape(shape)
        shape.setTitle(_("Image statistics"))
        self.set_shape_style(shape)
        self.register_shape(shape, final=False)

    def register_shape(self, shape, final=False):
        """

        :param shape:
        :param final:
        """
        plot = shape.plot()
        if plot is not None:
            plot.unselect_all()
            plot.set_active_item(shape)
            shape.set_image_item(self.get_last_item())

    def handle_final_shape(self, shape):
        """

        :param shape:
        """
        super(ImageStatsTool, self).handle_final_shape(shape)
        self.register_shape(shape, final=True)

    def get_associated_item(self, plot):
        """

        :param plot:
        :return:
        """
        items = plot.get_selected_items(item_type=IStatsImageItemType)
        if len(items) == 1:
            self._last_item = weakref.ref(items[0])
        return self.get_last_item()

    def update_status(self, plot):
        """

        :param plot:
        """
        if update_image_tool_status(self, plot):
            item = self.get_associated_item(plot)
            self.action.setEnabled(item is not None)


class ReverseYAxisTool(ToggleTool):
    """ """

    def __init__(self, manager):
        super(ReverseYAxisTool, self).__init__(manager, _("Reverse Y axis"))

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.set_axis_direction("left", checked)
        plot.replot()

    def update_status(self, plot):
        """

        :param plot:
        """
        if update_image_tool_status(self, plot):
            self.action.setChecked(plot.get_axis_direction("left"))


class AspectRatioParam(DataSet):
    lock = BoolItem(_("Lock aspect ratio"))
    current = FloatItem(_("Current value")).set_prop("display", active=False)
    ratio = FloatItem(_("Lock value"), min=1e-3)


class AspectRatioTool(CommandTool):
    """ """

    def __init__(self, manager):
        super(AspectRatioTool, self).__init__(
            manager, _("Aspect ratio"), tip=None, toolbar_id=None
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
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

    def set_aspect_ratio_1_1(self):
        """ """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_aspect_ratio(ratio=1)
            plot.replot()

    def activate_command(self, plot, checked):
        """Activate tool"""
        pass

    def __update_actions(self, checked):
        self.ar_param.lock = checked
        #        self.lock_action.blockSignals(True)
        self.lock_action.setChecked(checked)
        #        self.lock_action.blockSignals(False)
        plot = self.get_active_plot()
        if plot is not None:
            ratio = plot.get_aspect_ratio()
            self.ratio1_action.setEnabled(checked and ratio != 1.0)

    def lock_aspect_ratio(self, checked):
        """Lock aspect ratio"""
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_aspect_ratio(lock=checked)
            self.__update_actions(checked)
            plot.replot()

    def edit_aspect_ratio(self):
        """ """
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

    def update_status(self, plot):
        """

        :param plot:
        """
        if update_image_tool_status(self, plot):
            ratio = plot.get_aspect_ratio()
            lock = plot.lock_aspect_ratio
            self.ar_param.ratio, self.ar_param.lock = ratio, lock
            self.__update_actions(lock)


class ContrastPanelTool(PanelTool):
    panel_name = _("Contrast adjustment")
    panel_id = ID_CONTRAST

    def update_status(self, plot):
        """

        :param plot:
        """
        super(ContrastPanelTool, self).update_status(plot)
        update_image_tool_status(self, plot)
        item = plot.get_last_active_item(IVoiImageItemType)
        panel = self.manager.get_panel(self.panel_id)
        for action in panel.toolbar.actions():
            if isinstance(action, QW.QAction):
                action.setEnabled(item is not None)


class ColormapTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(ColormapTool, self).__init__(
            manager,
            _("Colormap"),
            tip=_("Select colormap for active " "image"),
            toolbar_id=toolbar_id,
        )
        self.action.setEnabled(False)
        self.action.setIconText("")
        self.default_icon = build_icon_from_cmap(get_cmap("jet"), width=16, height=16)
        self.action.setIcon(self.default_icon)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
        menu = QW.QMenu()
        for cmap_name in get_colormap_list():
            cmap = get_cmap(cmap_name)
            icon = build_icon_from_cmap(cmap)
            action = menu.addAction(icon, cmap_name)
            action.setEnabled(True)
        menu.triggered.connect(self.activate_cmap)
        return menu

    def activate_command(self, plot, checked):
        """Activate tool"""
        pass

    def get_selected_images(self, plot):
        """

        :param plot:
        :return:
        """
        items = [it for it in plot.get_selected_items(item_type=IColormapImageItemType)]
        if not items:
            active_image = plot.get_last_active_item(IColormapImageItemType)
            if active_image:
                items = [active_image]
        return items

    def activate_cmap(self, action):
        """

        :param action:
        """
        plot = self.get_active_plot()
        if plot is not None:
            items = self.get_selected_images(plot)
            cmap_name = str(action.text())
            for item in items:
                item.param.colormap = cmap_name
                item.param.update_item(item)
            self.action.setText(cmap_name)
            plot.invalidate()
            self.update_status(plot)

    def update_status(self, plot):
        """

        :param plot:
        """
        if update_image_tool_status(self, plot):
            item = plot.get_last_active_item(IColormapImageItemType)
            icon = self.default_icon
            if item:
                self.action.setEnabled(True)
                if item.get_color_map_name():
                    icon = build_icon_from_cmap(
                        item.get_color_map(), width=16, height=16
                    )
            else:
                self.action.setEnabled(False)
            self.action.setIcon(icon)


class ImageMaskTool(CommandTool):
    """ """

    #: Signal emitted by ImageMaskTool when mask was applied
    SIG_APPLIED_MASK_TOOL = QC.Signal()

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        self._mask_shapes = {}
        self._mask_already_restored = {}
        super(ImageMaskTool, self).__init__(
            manager,
            _("Mask"),
            icon="mask_tool.png",
            tip=_("Manage image masking areas"),
            toolbar_id=toolbar_id,
        )
        self.masked_image = None  # associated masked image item

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
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

    def update_status(self, plot):
        """

        :param plot:
        """
        self.action.setEnabled(self.masked_image is not None)

    def register_plot(self, baseplot):
        """

        :param baseplot:
        """
        super(ImageMaskTool, self).register_plot(baseplot)
        self._mask_shapes.setdefault(baseplot, [])
        baseplot.SIG_ITEMS_CHANGED.connect(self.items_changed)
        baseplot.SIG_ITEM_SELECTION_CHANGED.connect(self.item_selection_changed)

    def show_mask(self, state):
        """

        :param state:
        """
        if self.masked_image is not None:
            self.masked_image.set_mask_visible(state)

    def apply_mask(self):
        """ """
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

    def remove_all_shapes(self):
        """ """
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

    def remove_shapes(self):
        """ """
        plot = self.get_active_plot()
        plot.del_items(
            [shape for shape, _inside in self._mask_shapes[plot]]
        )  # remove shapes
        self._mask_shapes[plot] = []
        plot.replot()

    def show_shapes(self, state):
        """

        :param state:
        """
        plot = self.get_active_plot()
        if plot is not None:
            for shape, _inside in self._mask_shapes[plot]:
                shape.setVisible(state)
            plot.replot()

    def handle_shape(self, shape, inside):
        """

        :param shape:
        :param inside:
        """
        shape.set_style("plot", "shape/mask")
        shape.set_private(True)
        plot = self.get_active_plot()
        plot.set_active_item(shape)
        self._mask_shapes[plot] += [(shape, inside)]

    def find_masked_image(self, plot):
        """

        :param plot:
        :return:
        """
        item = plot.get_active_item()
        if isinstance(item, MaskedImageMixin):
            return item
        else:
            items = [
                item for item in plot.get_items() if isinstance(item, MaskedImageMixin)
            ]
            if items:
                return items[-1]

    def create_shapes_from_masked_areas(self):
        """ """
        plot = self.get_active_plot()
        self._mask_shapes[plot] = []
        for area in self.masked_image.get_masked_areas():
            if area.geometry == "rectangular":
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

    def set_masked_image(self, plot):
        """

        :param plot:
        """
        self.masked_image = item = self.find_masked_image(plot)
        if self.masked_image is not None and not self._mask_already_restored:
            self.create_shapes_from_masked_areas()
            self._mask_already_restored = True
        enable = False if item is None else item.is_mask_visible()
        self.showmask_action.setChecked(enable)

    def items_changed(self, plot):
        """

        :param plot:
        """
        self.set_masked_image(plot)
        self._mask_shapes[plot] = [
            (shape, inside)
            for shape, inside in self._mask_shapes[plot]
            if shape.plot() is plot
        ]
        self.update_status(plot)

    def item_selection_changed(self, plot):
        """

        :param plot:
        """
        self.set_masked_image(plot)
        self.update_status(plot)

    def clear_mask(self):
        """ """
        message = _("Do you really want to clear the mask?")
        plot = self.get_active_plot()
        answer = QW.QMessageBox.warning(
            plot, _("Clear mask"), message, QW.QMessageBox.Yes | QW.QMessageBox.No
        )
        if answer == QW.QMessageBox.Yes:
            self.masked_image.unmask_all()
            plot.replot()

    def activate_command(self, plot, checked):
        """Activate tool"""
        pass


class LockTrImageTool(ToggleTool):
    """Lock (rotation, translation, resize)"""

    def __init__(self, manager, toolbar_id=None):
        super(LockTrImageTool, self).__init__(
            manager, title=_("Lock"), icon=get_icon("lock.png"), toolbar_id=None
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        itemlist = self.get_supported_items(plot)
        if self.action.isEnabled():
            for item in itemlist:
                item.set_locked(checked)
                if item.is_locked():
                    item.setIcon(get_icon("trimage_lock.png"))
                else:
                    item.setIcon(get_icon("image.png"))
            plot.SIG_ITEMS_CHANGED.emit(plot)

    def get_supported_items(self, plot):
        return [
            _it for _it in plot.get_selected_items() if isinstance(_it, TrImageItem)
        ]

    def update_status(self, plot):
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

    def setup_context_menu(self, menu, plot):
        """Command Tool re-implement"""
        if self.action.isEnabled():
            menu.addAction(self.action)


class OpenImageTool(OpenFileTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(OpenImageTool, self).__init__(
            manager,
            title=_("Open image"),
            formats=io.iohandler.get_filters("load"),
            toolbar_id=toolbar_id,
        )


class RotationCenterTool(InteractiveTool):
    TITLE = _("Rotation Center")
    ICON = "rotationcenter.jpg"
    CURSOR = QC.Qt.CursorShape.CrossCursor

    SIG_TOOL_ENABLED = QC.Signal(bool)

    def __init__(
        self,
        manager,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=True,
        rotation_point_move_with_shape=True,
        rotation_center=True,
        on_all_items=True,
    ):
        super(RotationCenterTool, self).__init__(
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

    def setup_filter(self, baseplot):
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

    def update_status(self, plot):
        """API"""
        enabled = False
        self.action.setEnabled(enabled)
        selected_items = plot.get_selected_items()
        for item in selected_items:
            if isinstance(item, TrImageItem):
                enabled = True
                break
        self.action.setEnabled(enabled)
        self.SIG_TOOL_ENABLED.emit(enabled)

    def action_triggered(self, checked):
        if self.rotation_center:
            self.mouse_press(self.filter, QC.QEvent(QC.QEvent.MouseButtonPress))

    def mouse_press(self, filter, event):
        """We create a new shape if it's the first point
        otherwise we add a new point
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
        # This import can't be done at the module level because it creates a
        # circular import: we create a dialog that itself instantiates a
        # PlotWidget, so it needs to import plotpy.widgets.plotwidget at some
        # point.
        # pylint: disable=import-outside-toplevel
        from plotpy.widgets.rotatecrop import RotateCropDialog

        for item in plot.get_selected_items():
            if isinstance(item, TrImageItem):
                z = item.z()
                plot.del_item(item)
                dlg = RotateCropDialog(plot.parent(), options=self.options)
                dlg.set_item(item)
                ok = dlg.exec()
                plot.add_item(item, z=z)
                if not ok:
                    break

    def update_status(self, plot):
        """

        :param plot:
        """
        status = any(
            [isinstance(item, TrImageItem) for item in plot.get_selected_items()]
        )
        self.action.setEnabled(status)


def update_image_tool_status(tool, plot):
    """

    :param tool:
    :param plot:
    :return:
    """
    enabled = plot.type != PlotType.CURVE
    tool.action.setEnabled(enabled)
    return enabled


def export_image_data(item):
    """Export image item data to file"""

    exec_image_save_dialog(item.plot(), item.data)


def edit_image_data(item):
    """Edit image item data to file"""

    oedit(item.data)
