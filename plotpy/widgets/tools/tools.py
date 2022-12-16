# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103

"""
plotpy.gui.widgets.tools
------------------------

The `tools` module provides a collection of `plot tools` :
    * :py:class:`.tools.RectZoomTool`
    * :py:class:`.tools.SelectTool`
    * :py:class:`.tools.SelectPointTool`
    * :py:class:`.tools.RotationCenterTool`
    * :py:class:`.tools.MultiLineTool`
    * :py:class:`.tools.FreeFormTool`
    * :py:class:`.tools.LabelTool`
    * :py:class:`.tools.RectangleTool`
    * :py:class:`.tools.PointTool`
    * :py:class:`.tools.SegmentTool`
    * :py:class:`.tools.CircleTool`
    * :py:class:`.tools.EllipseTool`
    * :py:class:`.tools.PlaceAxesTool`
    * :py:class:`.tools.AnnotatedRectangleTool`
    * :py:class:`.tools.AnnotatedCircleTool`
    * :py:class:`.tools.AnnotatedEllipseTool`
    * :py:class:`.tools.AnnotatedPointTool`
    * :py:class:`.tools.AnnotatedSegmentTool`
    * :py:class:`.tools.HRangeTool`
    * :py:class:`.tools.DummySeparatorTool`
    * :py:class:`.tools.AntiAliasingTool`
    * :py:class:`.tools.DisplayCoordsTool`
    * :py:class:`.tools.ReverseYAxisTool`
    * :py:class:`.tools.AspectRatioTool`
    * :py:class:`.tools.PanelTool`
    * :py:class:`.tools.ItemListPanelTool`
    * :py:class:`.tools.ContrastPanelTool`
    * :py:class:`.tools.ColormapTool`
    * :py:class:`.tools.XCSPanelTool`
    * :py:class:`.tools.YCSPanelTool`
    * :py:class:`.tools.CrossSectionTool`
    * :py:class:`.tools.AverageCrossSectionTool`
    * :py:class:`.tools.SaveAsTool`
    * :py:class:`.tools.CopyToClipboardTool`
    * :py:class:`.tools.OpenFileTool`
    * :py:class:`.tools.OpenImageTool`
    * :py:class:`.tools.SnapshotTool`
    * :py:class:`.tools.PrintTool`
    * :py:class:`.tools.SaveItemsTool`
    * :py:class:`.tools.LoadItemsTool`
    * :py:class:`.tools.AxisScaleTool`
    * :py:class:`.tools.HelpTool`
    * :py:class:`.tools.ExportItemDataTool`
    * :py:class:`.tools.EditItemDataTool`
    * :py:class:`.tools.ItemCenterTool`
    * :py:class:`.tools.DeleteItemTool`

A `plot tool` is an object providing various features to a plotting widget
(:py:class:`.baseplot.BasePlot`):
buttons, menus, selection tools, image I/O tools, etc.
To make it work, a tool has to be registered to the plotting widget's manager,
i.e. an instance of the :py:class:`.plot.PlotManager` class (see
the :py:mod:`.plot` module for more details on the procedure).

The `BasePlot` widget do not provide any `PlotManager`: the
manager has to be created separately. On the contrary, the ready-to-use widget
:py:class:`.plot.PlotWidget` are higher-level plotting widgets with integrated manager, tools and
panels.

.. seealso::

    Module :py:mod:`.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

Example
~~~~~~~

The following example add all the existing image tools to an `PlotWidget` object
for testing purpose:

.. literalinclude:: ../../../tests/gui/image_plot_tools.py
   :start-after: SHOW


.. image:: /images/screenshots/image_plot_tools.png


Reference
~~~~~~~~~
.. autoclass:: InteractiveTool
   :members:
.. autoclass:: RectZoomTool
   :members:
   :inherited-members:
.. autoclass:: SelectTool
   :members:
   :inherited-members:
.. autoclass:: SelectPointTool
   :members:
   :inherited-members:
.. autoclass:: RotationCenterTool
   :members:
   :inherited-members:
.. autoclass:: MultiLineTool
   :members:
   :inherited-members:
.. autoclass:: FreeFormTool
   :members:
   :inherited-members:
.. autoclass:: LabelTool
   :members:
   :inherited-members:
.. autoclass:: RectangleTool
   :members:
   :inherited-members:
.. autoclass:: PointTool
   :members:
   :inherited-members:
.. autoclass:: SegmentTool
   :members:
   :inherited-members:
.. autoclass:: CircleTool
   :members:
   :inherited-members:
.. autoclass:: EllipseTool
   :members:
   :inherited-members:
.. autoclass:: PlaceAxesTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedRectangleTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedCircleTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedEllipseTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedPointTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedSegmentTool
   :members:
   :inherited-members:
.. autoclass:: HRangeTool
   :members:
   :inherited-members:
.. autoclass:: DummySeparatorTool
   :members:
   :inherited-members:
.. autoclass:: AntiAliasingTool
   :members:
   :inherited-members:
.. autoclass:: DisplayCoordsTool
   :members:
   :inherited-members:
.. autoclass:: ReverseYAxisTool
   :members:
   :inherited-members:
.. autoclass:: AspectRatioTool
   :members:
   :inherited-members:
.. autoclass:: PanelTool
   :members:
   :inherited-members:
.. autoclass:: ItemListPanelTool
   :members:
   :inherited-members:
.. autoclass:: ContrastPanelTool
   :members:
   :inherited-members:
.. autoclass:: ColormapTool
   :members:
   :inherited-members:
.. autoclass:: XCSPanelTool
   :members:
   :inherited-members:
.. autoclass:: YCSPanelTool
   :members:
   :inherited-members:
.. autoclass:: CrossSectionTool
   :members:
   :inherited-members:
.. autoclass:: AverageCrossSectionTool
   :members:
   :inherited-members:
.. autoclass:: SaveAsTool
   :members:
   :inherited-members:
.. autoclass:: CopyToClipboardTool
   :members:
   :inherited-members:
.. autoclass:: OpenFileTool
   :members:
   :inherited-members:
.. autoclass:: OpenImageTool
   :members:
   :inherited-members:
.. autoclass:: SnapshotTool
   :members:
   :inherited-members:
.. autoclass:: PrintTool
   :members:
   :inherited-members:
.. autoclass:: SaveItemsTool
   :members:
   :inherited-members:
.. autoclass:: LoadItemsTool
   :members:
   :inherited-members:
.. autoclass:: AxisScaleTool
   :members:
   :inherited-members:
.. autoclass:: HelpTool
   :members:
   :inherited-members:
.. autoclass:: ExportItemDataTool
   :members:
   :inherited-members:
.. autoclass:: EditItemDataTool
   :members:
   :inherited-members:
.. autoclass:: ItemCenterTool
   :members:
   :inherited-members:
.. autoclass:: DeleteItemTool
   :members:
   :inherited-members:
.. autoclass:: ImageMaskTool
   :members:
   :inherited-members:
"""

# TODO: z(long-terme) à partir d'une sélection rectangulaire sur une image
#      afficher un ArrayEditor montrant les valeurs de la zone sélectionnée

from __future__ import unicode_literals

import os.path as osp
import sys
import weakref

import numpy as np

from plotpy.core.dataset.dataitems import BoolItem, ChoiceItem, FloatItem, TextItem
from plotpy.core.dataset.datatypes import BeginGroup, EndGroup
from plotpy.gui.config.misc import get_icon
from plotpy.gui.dataset.datatypes import DataSetGui
from plotpy.gui.utils.icons import get_std_icon
from plotpy.gui.utils.misc import add_actions, add_separator
from plotpy.gui.widgets.colormap import (
    build_icon_from_cmap,
    get_cmap,
    get_colormap_list,
)
from plotpy.gui.widgets.config import _
from plotpy.gui.widgets.dialog import get_open_filename, get_save_filename
from plotpy.gui.widgets.events import (
    ClickHandler,
    KeyEventMatch,
    ObjectHandler,
    QtDragHandler,
    RectangularSelectionHandler,
    StandardKeyMatch,
    ZoomRectHandler,
    setup_standard_tool_filter,
)
from plotpy.gui.widgets.ext_gui_lib import (
    QAction,
    QActionGroup,
    QEvent,
    QKeySequence,
    QMenu,
    QMessageBox,
    QObject,
    QPointF,
    QPrintDialog,
    QPrinter,
    Qt,
    QToolButton,
    Signal,
)
from plotpy.gui.widgets.interfaces import (
    IColormapImageItemType,
    ICurveItemType,
    IImageItemType,
    IPlotManager,
    IShapeItemType,
    IStatsImageItemType,
    IVoiImageItemType,
)
from plotpy.gui.widgets.items.annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
)
from plotpy.gui.widgets.items.image import TrImageItem, get_items_in_rectangle
from plotpy.gui.widgets.items.shapes import (
    Axes,
    EllipseShape,
    Marker,
    ObliqueRectangleShape,
    PointShape,
    PolygonShape,
    RectangleShape,
    SegmentShape,
)
from plotpy.gui.widgets.panels import ID_CONTRAST, ID_ITEMLIST, ID_OCS, ID_XCS, ID_YCS

try:
    # PyQt4 4.3.3 on Windows (static DLLs) with py2exe installed:
    # -> pythoncom must be imported first, otherwise py2exe's boot_com_servers
    #    will raise an exception ("Unable to load DLL [...]") when calling any
    #    of the QFileDialog static methods (getOpenFileName, ...)
    import pythoncom
except ImportError:
    pass


class SelectTool(InteractiveTool):
    """
    Graphical Object Selection Tool
    """

    TITLE = _("Selection")
    ICON = "selection.png"
    CURSOR = Qt.ArrowCursor

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        ObjectHandler(filter, Qt.LeftButton, start_state=start_state)
        ObjectHandler(
            filter,
            Qt.LeftButton,
            mods=Qt.ControlModifier,
            start_state=start_state,
            multiselection=True,
        )
        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space)),
            self.validate,
            start_state,
        )
        filter.add_event(
            start_state,
            StandardKeyMatch(QKeySequence.SelectAll),
            self.select_all_items,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch((Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down)),
            self.move_with_arrow,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch(
                [
                    (Qt.Key_Left, Qt.ControlModifier),
                    (Qt.Key_Right, Qt.ControlModifier),
                    (Qt.Key_Up, Qt.ControlModifier),
                    (Qt.Key_Down, Qt.ControlModifier),
                ]
            ),
            self.move_with_arrow,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch(
                [
                    (Qt.Key_Left, Qt.ShiftModifier),
                    (Qt.Key_Right, Qt.ShiftModifier),
                    (Qt.Key_Left, Qt.ControlModifier + Qt.ShiftModifier),
                    (Qt.Key_Right, Qt.ControlModifier + Qt.ShiftModifier),
                ]
            ),
            self.rotate_with_arrow,
            start_state,
        )
        return setup_standard_tool_filter(filter, start_state)

    def select_all_items(self, filter, event):
        """

        :param filter:
        :param event:
        """
        filter.plot.select_all()
        filter.plot.replot()

    def move_with_arrow(self, filter, event):
        dx, dy = 0, 0
        if event.modifiers() == Qt.NoModifier:
            if event.key() == Qt.Key_Left:
                dx = -10
            elif event.key() == Qt.Key_Right:
                dx = 10
            elif event.key() == Qt.Key_Up:
                dy = -10
            elif event.key() == Qt.Key_Down:
                dy = 10
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Left:
                dx = -1
            elif event.key() == Qt.Key_Right:
                dx = 1
            elif event.key() == Qt.Key_Up:
                dy = -1
            elif event.key() == Qt.Key_Down:
                dy = 1
        selected_items = filter.plot.get_selected_items()
        for item in selected_items:
            if isinstance(item, TrImageItem):
                item.move_with_arrows(dx, dy)
        filter.plot.replot()

    def rotate_with_arrow(self, filter, event):
        dangle = 0
        if event.modifiers() == Qt.ShiftModifier:
            if event.key() == Qt.Key_Left:
                dangle = -np.deg2rad(0.5)
            elif event.key() == Qt.Key_Right:
                dangle = np.deg2rad(0.5)
        elif (event.modifiers() & Qt.ControlModifier == Qt.ControlModifier) and (
            event.modifiers() & Qt.ShiftModifier == Qt.ShiftModifier
        ):
            if event.key() == Qt.Key_Left:
                dangle = -np.deg2rad(0.05)
            elif event.key() == Qt.Key_Right:
                dangle = np.deg2rad(0.05)
        selected_items = filter.plot.get_selected_items()
        for item in selected_items:
            if isinstance(item, TrImageItem):
                item.rotate_with_arrows(dangle)
        filter.plot.replot()


class SelectPointTool(InteractiveTool):
    """ """

    TITLE = _("Point selection")
    ICON = "point_selection.png"
    MARKER_STYLE_SECT = "plot"
    MARKER_STYLE_KEY = "marker/curve"
    CURSOR = Qt.PointingHandCursor

    def __init__(
        self,
        manager,
        mode="reuse",
        on_active_item=False,
        title=None,
        icon=None,
        tip=None,
        end_callback=None,
        toolbar_id=DefaultToolbarID,
        marker_style=None,
        switch_to_default_tool=None,
    ):
        super(SelectPointTool, self).__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        assert mode in ("reuse", "create")
        self.mode = mode
        self.end_callback = end_callback
        self.marker = None
        self.last_pos = None
        self.on_active_item = on_active_item
        if marker_style is not None:
            self.marker_style_sect = marker_style[0]
            self.marker_style_key = marker_style[1]
        else:
            self.marker_style_sect = self.MARKER_STYLE_SECT
            self.marker_style_key = self.MARKER_STYLE_KEY

    def set_marker_style(self, marker):
        """

        :param marker:
        """
        marker.set_style(self.marker_style_sect, self.marker_style_key)

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        handler = QtDragHandler(filter, Qt.LeftButton, start_state=start_state)
        handler.SIG_START_TRACKING.connect(self.start)
        handler.SIG_MOVE.connect(self.move)
        handler.SIG_STOP_NOT_MOVING.connect(self.stop)
        handler.SIG_STOP_MOVING.connect(self.stop)
        return setup_standard_tool_filter(filter, start_state)

    def start(self, filter, event):
        """

        :param filter:
        :param event:
        """
        if self.marker is None:
            title = ""
            if self.TITLE:
                title = f"<b>{self.TITLE}</b><br>"
            if self.on_active_item:
                constraint_cb = filter.plot.on_active_curve
                label_cb = lambda x, y: title + filter.plot.get_coordinates_str(x, y)
            else:
                constraint_cb = None
                label_cb = lambda x, y: f"{title}x = {x:g}<br>y = {y:g}"
            self.marker = Marker(label_cb=label_cb, constraint_cb=constraint_cb)
            self.set_marker_style(self.marker)
        self.marker.attach(filter.plot)
        self.marker.setZ(filter.plot.get_max_z() + 1)
        self.marker.setVisible(True)

    def stop(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.move(filter, event)
        if self.mode != "reuse":
            self.marker.detach()
            self.marker = None
        if self.end_callback:
            self.end_callback(self)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        :return:
        """
        if self.marker is None:
            return  # something is wrong ...
        self.marker.move_local_point_to(0, event.pos())
        filter.plot.replot()
        self.last_pos = self.marker.xValue(), self.marker.yValue()

    def get_coordinates(self):
        """

        :return:
        """
        return self.last_pos


class RotationCenterTool(InteractiveTool):
    TITLE = _("Rotation Center")
    ICON = "rotationcenter.jpg"
    CURSOR = Qt.CrossCursor

    SIG_TOOL_ENABLED = Signal(bool)

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
            handler = QtDragHandler(self.filter, Qt.LeftButton, start_state=start_state)
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
            self.mouse_press(self.filter, QEvent(QEvent.MouseButtonPress))

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
            self.pos = QPointF(
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


class LabelTool(InteractiveTool):
    """ """

    TITLE = _("Label")
    ICON = "label.png"
    LABEL_STYLE_SECT = "plot"
    LABEL_STYLE_KEY = "label"
    SWITCH_TO_DEFAULT_TOOL = True

    def __init__(
        self,
        manager,
        handle_label_cb=None,
        label_style=None,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=None,
    ):
        self.handle_label_cb = handle_label_cb
        super(LabelTool, self).__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        if label_style is not None:
            self.label_style_sect = label_style[0]
            self.label_style_key = label_style[1]
        else:
            self.label_style_sect = self.LABEL_STYLE_SECT
            self.label_style_key = self.LABEL_STYLE_KEY

    def set_label_style(self, label):
        """

        :param label:
        """
        label.set_style(self.label_style_sect, self.label_style_key)

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        handler = ClickHandler(filter, Qt.LeftButton, start_state=start_state)
        handler.SIG_CLICK_EVENT.connect(self.add_label_to_plot)
        return setup_standard_tool_filter(filter, start_state)

    def add_label_to_plot(self, filter, event):
        """

        :param filter:
        :param event:
        """
        plot = filter.plot

        class TextParam(DataSetGui):
            text = TextItem("", _("Label"))

        textparam = TextParam(_("Label text"), icon=self.ICON)
        if textparam.edit(plot):
            text = textparam.text.replace("\n", "<br>")
            from plotpy.gui.widgets.builder import make

            label = make.label(text, (0, 0), (10, 10), "TL")
            title = label.labelparam.label
            self.set_label_style(label)
            label.setTitle(self.TITLE)
            x = plot.invTransform(label.xAxis(), event.pos().x())
            y = plot.invTransform(label.yAxis(), event.pos().y())
            label.set_pos(x, y)
            label.setTitle(title)
            label.labelparam.update_param(label)
            plot.add_item(label)
            if self.handle_label_cb is not None:
                self.handle_label_cb(label)
            plot.replot()
            self.SIG_TOOL_JOB_FINISHED.emit()


class RectangularActionTool(InteractiveTool):
    """ """

    SHAPE_STYLE_SECT = "plot"
    SHAPE_STYLE_KEY = "shape/drag"
    AVOID_NULL_SHAPE = False

    def __init__(
        self,
        manager,
        func,
        shape_style=None,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        fix_orientation=False,
        switch_to_default_tool=None,
    ):
        self.action_func = func
        self.fix_orientation = fix_orientation
        super(RectangularActionTool, self).__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        if shape_style is not None:
            self.shape_style_sect = shape_style[0]
            self.shape_style_key = shape_style[1]
        else:
            self.shape_style_sect = self.SHAPE_STYLE_SECT
            self.shape_style_key = self.SHAPE_STYLE_KEY
        self.last_final_shape = None
        self.switch_to_default_tool = switch_to_default_tool

    def get_last_final_shape(self):
        """

        :return:
        """
        if self.last_final_shape is not None:
            return self.last_final_shape()

    def set_shape_style(self, shape):
        """

        :param shape:
        """
        shape.set_style(self.shape_style_sect, self.shape_style_key)

    def create_shape(self):
        """

        :return:
        """
        shape = RectangleShape(0, 0, 1, 1)
        self.set_shape_style(shape)
        return shape, 0, 2

    def setup_shape(self, shape):
        """

        :param shape:
        """
        pass

    def get_shape(self):
        """Reimplemented RectangularActionTool method"""
        shape, h0, h1 = self.create_shape()
        self.setup_shape(shape)
        return shape, h0, h1

    def get_final_shape(self, plot, p0, p1):
        """

        :param plot:
        :param p0:
        :param p1:
        :return:
        """
        shape, h0, h1 = self.create_shape()
        self.setup_shape(shape)
        plot.add_item_with_z_offset(shape, SHAPE_Z_OFFSET)
        shape.move_local_point_to(h0, p0)
        shape.move_local_point_to(h1, p1)
        self.last_final_shape = weakref.ref(shape)
        return shape

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        handler = RectangularSelectionHandler(
            filter, Qt.LeftButton, start_state=start_state
        )
        shape, h0, h1 = self.get_shape()
        handler.set_shape(
            shape, h0, h1, self.setup_shape, avoid_null_shape=self.AVOID_NULL_SHAPE
        )
        handler.SIG_END_RECT.connect(self.end_rect)
        return setup_standard_tool_filter(filter, start_state)

    def end_rect(self, filter, p0, p1):
        """

        :param filter:
        :param p0:
        :param p1:
        """
        plot = filter.plot
        if self.fix_orientation:
            left, right = min(p0.x(), p1.x()), max(p0.x(), p1.x())
            top, bottom = min(p0.y(), p1.y()), max(p0.y(), p1.y())
            self.action_func(plot, QPointF(left, top), QPointF(right, bottom))
        else:
            self.action_func(plot, p0, p1)
        self.SIG_TOOL_JOB_FINISHED.emit()
        if self.switch_to_default_tool:
            shape = self.get_last_final_shape()
            plot.set_active_item(shape)


class PlaceAxesTool(RectangularShapeTool):
    TITLE = _("Axes")
    ICON = "gtaxes.png"
    SHAPE_STYLE_KEY = "shape/axes"

    def create_shape(self):
        """

        :return:
        """
        shape = Axes((0, 1), (1, 1), (0, 0))
        self.set_shape_style(shape)
        return shape, 0, 2


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
    def get_infos(self):
        """Return formatted string with informations on current shape"""
        from plotpy.gui.widgets.items.image import get_items_in_rectangle

        if self.image_item is None:
            return
        plot = self.image_item.plot()
        if plot is None:
            return
        p0y = plot.transform(0, self.shape.get_points()[0][1])
        p0x = plot.transform(2, self.shape.get_points()[0][0])
        p1y = plot.transform(0, self.shape.get_points()[1][1])
        p1x = plot.transform(2, self.shape.get_points()[1][0])
        p0 = QPointF(p0x, p0y)
        p1 = QPointF(p1x, p1y)
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


def update_image_tool_status(tool, plot):
    """

    :param tool:
    :param plot:
    :return:
    """
    from plotpy.gui.widgets.baseplot import PlotType

    enabled = plot.type != PlotType.CURVE
    tool.action.setEnabled(enabled)
    return enabled


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


class CrossSectionTool(RectangularShapeTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Cross section")
    ICON = "csection.png"
    SHAPE_STYLE_KEY = "shape/cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_XCS, ID_YCS)

    def create_shape(self):
        """

        :return:
        """
        return AnnotatedPoint(0, 0), 0, 0

    def setup_shape(self, shape):
        """

        :param shape:
        """
        self.setup_shape_appearance(shape)
        super(CrossSectionTool, self).setup_shape(shape)
        self.register_shape(shape, final=False)

    def setup_shape_appearance(self, shape):
        """

        :param shape:
        """
        self.set_shape_style(shape)
        param = shape.annotationparam
        param.title = self.SHAPE_TITLE
        #        param.show_computations = False
        param.update_annotation(shape)

    def register_shape(self, shape, final=False):
        """

        :param shape:
        :param final:
        """
        plot = shape.plot()
        if plot is not None:
            plot.unselect_all()
            plot.set_active_item(shape)
        for panel_id in self.PANEL_IDS:
            panel = self.manager.get_panel(panel_id)
            if panel is not None:
                panel.register_shape(shape, final=final)

    def activate(self):
        """Activate tool"""
        super(CrossSectionTool, self).activate()
        for panel_id in self.PANEL_IDS:
            panel = self.manager.get_panel(panel_id)
            panel.setVisible(True)
            shape = self.get_last_final_shape()
            if shape is not None:
                panel.update_plot(shape)

    def handle_final_shape(self, shape):
        """

        :param shape:
        """
        super(CrossSectionTool, self).handle_final_shape(shape)
        self.register_shape(shape, final=True)


class AverageCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Average cross section")
    ICON = "csection_a.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE

    def create_shape(self):
        """

        :return:
        """
        return AnnotatedRectangle(0, 0, 1, 1), 0, 2


class ObliqueCrossSectionTool(CrossSectionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Oblique averaged cross section")
    ICON = "csection_oblique.png"
    SHAPE_STYLE_KEY = "shape/average_cross_section"
    SHAPE_TITLE = TITLE
    PANEL_IDS = (ID_OCS,)

    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedObliqueRectangle(0, 0, 1, 0, 1, 1, 0, 1)
        self.set_shape_style(annotation)
        annotation.setIcon(get_icon(self.ICON))
        return annotation, 0, 2


class RectZoomTool(InteractiveTool):
    TITLE = _("Rectangle zoom")
    ICON = "magnifier.png"

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        handler = ZoomRectHandler(filter, Qt.LeftButton, start_state=start_state)
        shape, h0, h1 = self.get_shape()
        handler.set_shape(shape, h0, h1)
        return setup_standard_tool_filter(filter, start_state)

    def get_shape(self):
        """

        :return:
        """
        shape = RectangleShape(0, 0, 1, 1)
        shape.set_style("plot", "shape/rectzoom")
        return shape, 0, 2


class BaseCursorTool(InteractiveTool):
    """ """

    TITLE = None
    ICON = None

    def __init__(
        self,
        manager,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=None,
    ):
        super(BaseCursorTool, self).__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        self.shape = None

    def create_shape(self):
        """Create and return the cursor/range shape"""
        raise NotImplementedError

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        self.handler = QtDragHandler(filter, Qt.LeftButton, start_state=start_state)
        self.handler.SIG_MOVE.connect(self.move)
        self.handler.SIG_STOP_NOT_MOVING.connect(self.end_move)
        self.handler.SIG_STOP_MOVING.connect(self.end_move)
        return setup_standard_tool_filter(filter, start_state)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        plot = filter.plot
        if not self.shape:
            self.shape = self.create_shape()
            self.shape.attach(plot)
            self.shape.setZ(plot.get_max_z() + 1)
            self.shape.move_local_point_to(0, event.pos())
            self.shape.setVisible(True)
        self.shape.move_local_point_to(1, event.pos())
        plot.replot()

    def end_move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        if self.shape is not None:
            assert self.shape.plot() == filter.plot
            filter.plot.add_item_with_z_offset(self.shape, SHAPE_Z_OFFSET)
            self.shape = None
            self.SIG_TOOL_JOB_FINISHED.emit()


class HRangeTool(BaseCursorTool):
    TITLE = _("Horizontal selection")
    ICON = "xrange.png"

    def create_shape(self):
        """

        :return:
        """
        from plotpy.gui.widgets.items.shapes import XRangeSelection

        return XRangeSelection(0, 0)


class VCursorTool(BaseCursorTool):
    TITLE = _("Vertical cursor")
    ICON = "vcursor.png"

    def create_shape(self):
        """

        :return:
        """
        marker = Marker()
        marker.set_markerstyle("|")
        return marker


class HCursorTool(BaseCursorTool):
    TITLE = _("Horizontal cursor")
    ICON = "hcursor.png"

    def create_shape(self):
        """

        :return:
        """
        marker = Marker()
        marker.set_markerstyle("-")
        return marker


class XCursorTool(BaseCursorTool):
    TITLE = _("Cross cursor")
    ICON = "xcursor.png"

    def create_shape(self):
        """

        :return:
        """
        marker = Marker()
        marker.set_markerstyle("+")
        return marker


class CurveStatsTool(BaseCursorTool):
    """ """

    TITLE = _("Signal statistics")
    ICON = "xrange.png"
    SWITCH_TO_DEFAULT_TOOL = True

    def __init__(
        self, manager, toolbar_id=DefaultToolbarID, title=None, icon=None, tip=None
    ):
        super(CurveStatsTool, self).__init__(
            manager, toolbar_id, title=title, icon=icon, tip=tip
        )
        self._last_item = None
        self.label = None

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
        from plotpy.gui.widgets.items.shapes import XRangeSelection

        return XRangeSelection(0, 0)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        super(CurveStatsTool, self).move(filter, event)
        if self.label is None:
            plot = filter.plot
            curve = self.get_associated_item(plot)
            from plotpy.gui.widgets.builder import make

            self.label = make.computations(
                self.shape,
                "TL",
                [
                    (
                        curve,
                        "%g &lt; x &lt; %g",
                        lambda *args: (args[0].min(), args[0].max()),
                    ),
                    (
                        curve,
                        "%g &lt; y &lt; %g",
                        lambda *args: (args[1].min(), args[1].max()),
                    ),
                    (curve, "&lt;y&gt;=%g", lambda *args: args[1].mean()),
                    (curve, "σ(y)=%g", lambda *args: args[1].std()),
                    (curve, "∑(y)=%g", lambda *args: np.trapz(args[1])),
                    (curve, "∫ydx=%g", lambda *args: np.trapz(args[1], args[0])),
                ],
            )
            self.label.attach(plot)
            self.label.setZ(plot.get_max_z() + 1)
            self.label.setVisible(True)

    def end_move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        super(CurveStatsTool, self).end_move(filter, event)
        if self.label is not None:
            filter.plot.add_item_with_z_offset(self.label, SHAPE_Z_OFFSET)
            self.label = None

    def get_associated_item(self, plot):
        """

        :param plot:
        :return:
        """
        items = plot.get_selected_items(item_type=ICurveItemType)
        if len(items) == 1:
            self._last_item = weakref.ref(items[0])
        return self.get_last_item()

    def update_status(self, plot):
        """

        :param plot:
        """
        item = self.get_associated_item(plot)
        self.action.setEnabled(item is not None)


class DummySeparatorTool(GuiTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(DummySeparatorTool, self).__init__(manager, toolbar_id)

    def setup_toolbar(self, toolbar):
        """Setup tool's toolbar"""
        add_separator(toolbar)

    def setup_context_menu(self, menu, plot):
        """

        :param menu:
        :param plot:
        """
        add_separator(menu)


class CommandTool(GuiTool):
    """Base class for command tools: action, context menu entry"""

    CHECKABLE = False

    def __init__(
        self, manager, title, icon=None, tip=None, toolbar_id=DefaultToolbarID
    ):
        self.title = title
        if icon and isinstance(icon, str):
            self.icon = get_icon(icon)
        else:
            self.icon = icon
        self.tip = tip
        super(CommandTool, self).__init__(manager, toolbar_id)

    def create_action(self, manager):
        """Create and return tool's action"""
        return manager.create_action(
            self.title,
            icon=self.icon,
            tip=self.tip,
            triggered=self.activate,
            checkable=self.CHECKABLE,
        )

    def setup_context_menu(self, menu, plot):
        """

        :param menu:
        :param plot:
        """
        menu.addAction(self.action)

    def activate(self, checked=True):
        """

        :param checked:
        """
        plot = self.get_active_plot()
        if plot is not None:
            self.activate_command(plot, checked)

    def set_status_active_item(self, plot):
        """

        :param plot:
        """
        item = plot.get_active_item()
        if item:
            self.action.setEnabled(True)
        else:
            self.action.setEnabled(False)


class DoAutoscaleTool(CommandTool):
    """
    A tool to perfrom autoscale for associated plot
    """

    def __init__(
        self,
        manager,
        title=_("AutoScale"),
        icon="autoscale.png",
        tip=None,
        toolbar_id=DefaultToolbarID,
    ):

        super(DoAutoscaleTool, self).__init__(
            manager, title=title, icon=icon, tip=tip, toolbar_id=toolbar_id
        )

    def setup_context_menu(self, menu, plot):
        """re-implement"""
        pass

    def activate_command(self, plot, checked):
        """Activate tool"""
        if checked:
            plot.do_autoscale()


class ToggleTool(CommandTool):
    """ """

    CHECKABLE = True

    def __init__(self, manager, title, icon=None, tip=None, toolbar_id=None):
        super(ToggleTool, self).__init__(manager, title, icon, tip, toolbar_id)


class BasePlotMenuTool(CommandTool):
    """
    A tool that gather parameter panels from the BasePlot
    and proposes to edit them and set them back
    """

    def __init__(
        self, manager, key, title=None, icon=None, tip=None, toolbar_id=DefaultToolbarID
    ):
        from plotpy.gui.widgets.baseplot import PARAMETERS_TITLE_ICON

        default_title, default_icon = PARAMETERS_TITLE_ICON[key]
        if title is None:
            title = default_title
        if icon is None:
            icon = default_icon
        super(BasePlotMenuTool, self).__init__(manager, title, icon, tip, toolbar_id)
        # Warning: icon (str) --(Base class constructor)--> self.icon (QIcon)
        self.key = key

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.edit_plot_parameters(self.key)

    def update_status(self, plot):
        """

        :param plot:
        """
        status = plot.get_plot_parameters_status(self.key)
        self.action.setEnabled(status)


class AntiAliasingTool(ToggleTool):
    """ """

    def __init__(self, manager):
        super(AntiAliasingTool, self).__init__(manager, _("Antialiasing (curves)"))

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.set_antialiasing(checked)
        plot.replot()

    def update_status(self, plot):
        """

        :param plot:
        """
        self.action.setChecked(plot.antialiased)


class DisplayCoordsTool(CommandTool):
    """ """

    def __init__(self, manager):
        super(DisplayCoordsTool, self).__init__(
            manager,
            _("Markers"),
            icon=get_icon("on_curve.png"),
            tip=None,
            toolbar_id=None,
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
        menu = QMenu()
        self.canvas_act = manager.create_action(
            _("Free"), toggled=self.activate_canvas_pointer
        )
        self.curve_act = manager.create_action(
            _("Bound to active item"), toggled=self.activate_curve_pointer
        )
        add_actions(menu, (self.canvas_act, self.curve_act))
        return menu

    def activate_canvas_pointer(self, enable):
        """

        :param enable:
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_pointer("canvas" if enable else None)

    def activate_curve_pointer(self, enable):
        """

        :param enable:
        """
        plot = self.get_active_plot()
        if plot is not None:
            plot.set_pointer("curve" if enable else None)

    def update_status(self, plot):
        """

        :param plot:
        """
        self.canvas_act.setChecked(plot.canvas_pointer)
        self.curve_act.setChecked(plot.curve_pointer)


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


class AspectRatioParam(DataSetGui):
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
        menu = QMenu()
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


class PanelTool(ToggleTool):
    """ """

    panel_id = None
    panel_name = None

    def __init__(self, manager):
        super(PanelTool, self).__init__(manager, self.panel_name)
        manager.get_panel(self.panel_id).SIG_VISIBILITY_CHANGED.connect(
            self.action.setChecked
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        panel = self.manager.get_panel(self.panel_id)
        panel.setVisible(checked)

    def update_status(self, plot):
        """

        :param plot:
        """
        panel = self.manager.get_panel(self.panel_id)
        self.action.setChecked(panel.isVisible())


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
            if isinstance(action, QAction):
                action.setEnabled(item is not None)


class XCSPanelTool(PanelTool):
    panel_name = _("X-axis cross section")
    panel_id = ID_XCS


class YCSPanelTool(PanelTool):
    panel_name = _("Y-axis cross section")
    panel_id = ID_YCS


class OCSPanelTool(PanelTool):
    panel_name = _("Oblique averaged cross section")
    panel_id = ID_OCS


class ItemListPanelTool(PanelTool):
    panel_name = _("Item list")
    panel_id = ID_ITEMLIST


class SaveAsTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(SaveAsTool, self).__init__(
            manager,
            _("Save as..."),
            get_std_icon("DialogSaveButton", 16),
            toolbar_id=toolbar_id,
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        # FIXME: Qt's PDF printer is unable to print plots including images
        # --> until this bug is fixed internally, disabling PDF output format
        #     when plot has image items.
        formats = "%s (*.png)" % _("PNG image")
        from plotpy.gui.widgets.interfaces import IImageItemType

        for item in plot.get_items():
            if IImageItemType in item.types():
                break
        else:
            formats += "\n%s (*.pdf)" % _("PDF document")
        fname, _f = get_save_filename(plot, _("Save as"), _("untitled"), formats)
        if fname:
            plot.save_widget(fname)


class CopyToClipboardTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(CopyToClipboardTool, self).__init__(
            manager,
            _("Copy to clipboard"),
            get_icon("copytoclipboard.png"),
            toolbar_id=toolbar_id,
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.copy_to_clipboard()


def save_snapshot(plot, p0, p1, new_size=None):
    """
    Save rectangular plot area
    p0, p1: resp. top left and bottom right points (`QPointF` objects)
    new_size: destination image size (tuple: (width, height))
    """
    from plotpy.gui.widgets import io
    from plotpy.gui.widgets.items.image import (
        compute_trimageitems_original_size,
        get_image_from_plot,
        get_items_in_rectangle,
        get_plot_qrect,
    )

    items = get_items_in_rectangle(plot, p0, p1)
    if not items:
        QMessageBox.critical(
            plot,
            _("Rectangle snapshot"),
            _("There is no supported image item in current selection."),
        )
        return
    src_x, src_y, src_w, src_h = get_plot_qrect(plot, p0, p1).getRect()
    original_size = compute_trimageitems_original_size(items, src_w, src_h)

    if new_size is None:
        new_size = (p1.x() - p0.x() + 1, p1.y() - p0.y() + 1)  # Screen size

    from plotpy.gui.widgets.resizedialog import ResizeDialog

    dlg = ResizeDialog(
        plot, new_size=new_size, old_size=original_size, text=_("Destination size:")
    )
    if not dlg.exec_():
        return

    class SnapshotParam(DataSetGui):
        _levels = BeginGroup(_("Image levels adjustments"))
        apply_contrast = BoolItem(_("Apply contrast settings"), default=False)
        apply_interpolation = BoolItem(_("Apply interpolation algorithm"), default=True)
        norm_range = BoolItem(_("Scale levels to maximum range"), default=False)
        _end_levels = EndGroup(_("Image levels adjustments"))
        _multiple = BeginGroup(_("Superimposed images"))
        add_images = ChoiceItem(
            _("If image B is behind image A, " "replace intersection by"),
            [(False, "A"), (True, "A+B")],
            default=None,
        )
        _end_multiple = EndGroup(_("Superimposed images"))

    param = SnapshotParam(_("Rectangle snapshot"))
    if not param.edit(parent=plot):
        return

    if dlg.keep_original_size:
        destw, desth = original_size
    else:
        destw, desth = dlg.width, dlg.height

    try:
        data = get_image_from_plot(
            plot,
            p0,
            p1,
            destw=destw,
            desth=desth,
            add_images=param.add_images,
            apply_lut=param.apply_contrast,
            apply_interpolation=param.apply_interpolation,
            original_resolution=dlg.keep_original_size,
        )

        dtype = None
        for item in items:
            if dtype is None or item.data.dtype.itemsize > dtype.itemsize:
                dtype = item.data.dtype
        if param.norm_range:
            data = io.scale_data_to_dtype(data, dtype=dtype)
        else:
            data = np.array(data, dtype=dtype)
    except MemoryError:
        mbytes = int(destw * desth * 32.0 / (8 * 1024**2))
        text = _(
            "There is not enough memory left to process "
            "this {destw:d} x {desth:d} image ({mbytes:d} "
            "MB would be required)."
        )
        text = text.format(destw=destw, desth=desth, mbytes=mbytes)
        QMessageBox.critical(plot, _("Memory error"), text)
        return
    for model_item in items:
        model_fname = model_item.get_filename()
        if model_fname is not None and model_fname.lower().endswith(".dcm"):
            break
    else:
        model_fname = None
    fname, _f = get_save_filename(
        plot,
        _("Save as"),
        _("untitled"),
        io.iohandler.get_filters("save", data.dtype, template=True),
    )
    _base, ext = osp.splitext(fname)
    options = {}
    if not fname:
        return
    elif ext.lower() == ".png":
        options.update(dict(dtype=np.uint8, max_range=True))
    elif ext.lower() == ".dcm":
        try:
            # pydicom 1.0
            from pydicom import dicomio
        except ImportError:
            # pydicom 0.9
            import dicom as dicomio
        model_dcm = dicomio.read_file(model_fname)
        try:
            ps_attr = "ImagerPixelSpacing"
            ps_x, ps_y = getattr(model_dcm, ps_attr)
        except AttributeError:
            ps_attr = "PixelSpacing"
            ps_x, ps_y = getattr(model_dcm, ps_attr)
        model_dcm.Rows, model_dcm.Columns = data.shape

        dest_height, dest_width = data.shape
        (
            _x,
            _y,
            _angle,
            model_dx,
            model_dy,
            _hflip,
            _vflip,
        ) = model_item.get_transform()
        new_ps_x = ps_x * src_w / (model_dx * dest_width)
        new_ps_y = ps_y * src_h / (model_dy * dest_height)
        setattr(model_dcm, ps_attr, [new_ps_x, new_ps_y])
        options.update(dict(template=model_dcm))
    io.imwrite(fname, data, **options)


class SnapshotTool(RectangularActionTool):
    """ """

    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Rectangle snapshot")
    ICON = "snapshot.png"

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(SnapshotTool, self).__init__(
            manager, save_snapshot, toolbar_id=toolbar_id, fix_orientation=True
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
        from plotpy.gui.widgets.items.image import TrImageItem
        from plotpy.gui.widgets.rotatecrop import RotateCropDialog

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
        from plotpy.gui.widgets.items.image import TrImageItem

        status = any(
            [isinstance(item, TrImageItem) for item in plot.get_selected_items()]
        )
        self.action.setEnabled(status)


class PrintTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(PrintTool, self).__init__(
            manager, _("Print..."), get_icon("print.png"), toolbar_id=toolbar_id
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        printer = QPrinter()
        dialog = QPrintDialog(printer, plot)
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        ok = dialog.exec_()
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        if ok:
            plot.print_(printer)


class OpenFileTool(CommandTool):
    """ """

    #: Signal emitted by OpenFileTool when a file was opened (arg: filename)
    SIG_OPEN_FILE = Signal(str)

    def __init__(
        self, manager, title=_("Open..."), formats="*.*", toolbar_id=DefaultToolbarID
    ):
        super(OpenFileTool, self).__init__(
            manager, title, get_std_icon("DialogOpenButton", 16), toolbar_id=toolbar_id
        )
        self.formats = formats
        self.directory = ""

    def get_filename(self, plot):
        """

        :param plot:
        :return:
        """
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        filename, _f = get_open_filename(plot, _("Open"), self.directory, self.formats)
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        filename = str(filename)
        if filename:
            self.directory = osp.dirname(filename)
        return filename

    def activate_command(self, plot, checked):
        """Activate tool"""
        filename = self.get_filename(plot)
        if filename:
            self.SIG_OPEN_FILE.emit(filename)


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
        fname, _f = get_save_filename(
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


class OpenImageTool(OpenFileTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        from plotpy.gui.widgets import io

        super(OpenImageTool, self).__init__(
            manager,
            title=_("Open image"),
            formats=io.iohandler.get_filters("load"),
            toolbar_id=toolbar_id,
        )


class AxisScaleTool(CommandTool):
    """ """

    def __init__(self, manager):
        super(AxisScaleTool, self).__init__(
            manager, _("Scale"), icon=get_icon("log_log.png"), tip=None, toolbar_id=None
        )
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
        menu = QMenu()
        group = QActionGroup(manager.get_main())
        lin_lin = manager.create_action(
            "Lin Lin",
            icon=get_icon("lin_lin.png"),
            toggled=lambda state, x="lin", y="lin": self.set_scale(state, x, y),
        )
        lin_log = manager.create_action(
            "Lin Log",
            icon=get_icon("lin_log.png"),
            toggled=lambda state, x="lin", y="log": self.set_scale(state, x, y),
        )
        log_lin = manager.create_action(
            "Log Lin",
            icon=get_icon("log_lin.png"),
            toggled=lambda state, x="log", y="lin": self.set_scale(state, x, y),
        )
        log_log = manager.create_action(
            "Log Log",
            icon=get_icon("log_log.png"),
            toggled=lambda state, x="log", y="log": self.set_scale(state, x, y),
        )
        self.scale_menu = {
            ("lin", "lin"): lin_lin,
            ("lin", "log"): lin_log,
            ("log", "lin"): log_lin,
            ("log", "log"): log_log,
        }
        for obj in (group, menu):
            add_actions(obj, (lin_lin, lin_log, log_lin, log_log))
        return menu

    def update_status(self, plot):
        """

        :param plot:
        """
        item = plot.get_active_item()
        active_scale = ("lin", "lin")
        if item is not None:
            xscale = plot.get_axis_scale(item.xAxis())
            yscale = plot.get_axis_scale(item.yAxis())
            active_scale = xscale, yscale
        for scale_type, scale_action in list(self.scale_menu.items()):
            if item is None:
                scale_action.setEnabled(False)
            else:
                scale_action.setEnabled(True)
                if active_scale == scale_type:
                    scale_action.setChecked(True)
                else:
                    scale_action.setChecked(False)

    def set_scale(self, checked, xscale, yscale):
        """

        :param checked:
        :param xscale:
        :param yscale:
        :return:
        """
        if not checked:
            return
        plot = self.get_active_plot()
        if plot is not None:
            cur_xscale, cur_yscale = plot.get_scales()
            if cur_xscale != xscale or cur_yscale != yscale:
                plot.set_scales(xscale, yscale)


class HelpTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(HelpTool, self).__init__(
            manager,
            _("Help"),
            get_std_icon("DialogHelpButton", 16),
            toolbar_id=toolbar_id,
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        QMessageBox.information(
            plot,
            _("Help"),
            _(
                """Keyboard/mouse shortcuts:
  - single left-click: item (curve, image, ...) selection
  - single right-click: context-menu relative to selected item
  - shift: on-active-curve (or image) cursor
  - alt: free cursor
  - left-click + mouse move: move item (when available)
  - middle-click + mouse move: pan
  - right-click + mouse move: zoom"""
            ),
        )


class AboutTool(CommandTool):
    """ """

    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(AboutTool, self).__init__(
            manager, _("About") + " plotpy", get_icon("plotpy.svg"), toolbar_id=None
        )

    def activate_command(self, plot, checked):
        """Activate tool"""
        from plotpy.gui.widgets.about import about

        QMessageBox.about(plot, _("About") + " plotpy", about(html=True))


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
        from plotpy.gui.widgets.items.image import RawImageItem

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


def export_curve_data(item):
    """Export curve item data to text file"""
    item_data = item.get_data()
    if len(item_data) > 2:
        x, y, dx, dy = item_data
        array_list = [x, y]
        if dx is not None:
            array_list.append(dx)
        if dy is not None:
            array_list.append(dy)
        data = np.array(array_list).T
    else:
        x, y = item_data
        data = np.array([x, y]).T
    plot = item.plot()
    title = _("Export")
    if item.param.label:
        title += f" ({item.param.label})"
    fname, _f = get_save_filename(plot, title, "", _("Text file") + " (*.txt)")
    if fname:
        try:
            np.savetxt(str(fname), data, delimiter=",")
        except RuntimeError as error:
            QMessageBox.critical(
                plot,
                _("Export"),
                _("Unable to export item data.")
                + "<br><br>"
                + _("Error message:")
                + "<br>"
                + str(error),
            )


def export_image_data(item):
    """Export image item data to file"""
    from plotpy.gui.widgets.qthelpers import exec_image_save_dialog

    exec_image_save_dialog(item.plot(), item.data)


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


def edit_curve_data(item):
    """Edit curve item data to text file"""
    item_data = item.get_data()
    if len(item_data) > 2:
        x, y, dx, dy = item_data
        array_list = [x, y]
        if dx is not None:
            array_list.append(dx)
        if dy is not None:
            array_list.append(dy)
        data = np.array(array_list).T
    else:
        x, y = item_data
        data = np.array([x, y]).T
    from plotpy.gui.widgets.variableexplorer.objecteditor import oedit

    if oedit(data) is not None:
        if data.shape[1] > 2:
            if data.shape[1] == 3:
                x, y, tmp = data.T
                if dx is not None:
                    dx = tmp
                else:
                    dy = tmp
            else:
                x, y, dx, dy = data.T
            item.set_data(x, y, dx, dy)
        else:
            x, y = data.T
            item.set_data(x, y)


def edit_image_data(item):
    """Edit image item data to file"""
    from plotpy.gui.widgets.variableexplorer.objecteditor import oedit

    oedit(item.data)


class EditItemDataTool(ItemManipulationBaseTool):
    """Edit item data"""

    TITLE = _("Edit data...")
    ICON = "arredit.png"

    def __init__(self, manager, toolbar_id=None):
        super(EditItemDataTool, self).__init__(
            manager, toolbar_id, curve_func=edit_curve_data, image_func=edit_image_data
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
        from plotpy.gui.widgets.items.annotations import (
            AnnotatedCircle,
            AnnotatedEllipse,
            AnnotatedObliqueRectangle,
            AnnotatedRectangle,
        )
        from plotpy.gui.widgets.items.shapes import (
            EllipseShape,
            ObliqueRectangleShape,
            RectangleShape,
        )

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
        answer = QMessageBox.warning(
            plot, _("Remove"), message, QMessageBox.Yes | QMessageBox.No
        )
        if answer == QMessageBox.Yes:
            plot.del_items(items)
            plot.replot()


class FilterTool(CommandTool):
    """ """

    def __init__(self, manager, filter, toolbar_id=None):
        super(FilterTool, self).__init__(
            manager, str(filter.name), toolbar_id=toolbar_id
        )
        self.filter = filter

    def update_status(self, plot):
        """

        :param plot:
        """
        self.set_status_active_item(plot)

    def activate_command(self, plot, checked):
        """Activate tool"""
        plot.apply_filter(self.filter)


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
        menu = QMenu()
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
    SIG_APPLIED_MASK_TOOL = Signal()

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

        menu = QMenu()
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
        answer = QMessageBox.warning(
            plot,
            _("Remove all masking shapes"),
            message,
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
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
        from plotpy.gui.widgets.items.image import MaskedImageMixin

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
        answer = QMessageBox.warning(
            plot, _("Clear mask"), message, QMessageBox.Yes | QMessageBox.No
        )
        if answer == QMessageBox.Yes:
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


class RectangularSelectionTool(RectangularActionTool):
    SWITCH_TO_DEFAULT_TOOL = True
    TITLE = _("Rectangular selection tool")
    ICON = "rectangular_select.png"

    def __init__(self, manager, intersect=True, toolbar_id=DefaultToolbarID):
        super(RectangularSelectionTool, self).__init__(
            manager, self.select_items, toolbar_id=toolbar_id, fix_orientation=True
        )
        self.intersect = intersect

    def select_items(self, plot, p0, p1):
        items_to_select = []
        # select items that implement IShapeItemType (annotation shapes, ...)
        items = get_items_in_rectangle(
            plot,
            p0,
            p1,
            item_type=IShapeItemType,
            intersect=self.intersect,
        )
        for item in items:
            if item.isVisible():
                items_to_select.append(item)
        # select items that implement IExportROIImageItemType (TrImageItem, ...)
        items = get_items_in_rectangle(
            plot,
            p0,
            p1,
            item_type=IImageItemType,
            intersect=self.intersect,
        )
        for item in items:
            if item.isVisible():
                items_to_select.append(item)
        plot.select_some_items(items_to_select)
