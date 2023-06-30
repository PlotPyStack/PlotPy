# -*- coding: utf-8 -*-
import math

from guidata.configtools import get_icon
from guidata.utils import update_dataset
from guidata.utils.misc import assert_interfaces_valid
from qtpy import QtCore as QC
from qwt import QwtPlotMarker

from plotpy.config import CONF, _
from plotpy.core.interfaces.common import IBasePlotItem, IShapeItemType
from plotpy.core.items.utils import canvas_to_axes
from plotpy.core.styles.base import MARKERSTYLES
from plotpy.core.styles.shape import MarkerParam


class Marker(QwtPlotMarker):
    """
    A marker that has two callbacks
    for restraining it's coordinates and
    displaying it's label
    we want to derive from QwtPlotMarker so
    we have to reimplement some of AbstractShape's methods
    (and PyQt doesn't really like multiple inheritance...)
    """

    __implements__ = (IBasePlotItem,)
    _readonly = True
    _private = False
    _can_select = True
    _can_resize = True
    _can_rotate = False
    _can_move = True

    def __init__(self, label_cb=None, constraint_cb=None, markerparam=None):
        super(Marker, self).__init__()
        self._pending_center_handle = None
        self.selected = False
        self.label_cb = label_cb
        if constraint_cb is None:
            constraint_cb = self.center_handle
        self.constraint_cb = constraint_cb
        if markerparam is None:
            self.markerparam = MarkerParam(_("Marker"))
            self.markerparam.read_config(CONF, "plot", "marker/cursor")
        else:
            self.markerparam = markerparam
        self.markerparam.update_marker(self)
        self.setIcon(get_icon("marker.png"))

    # ------QwtPlotItem API------------------------------------------------------
    def draw(self, painter, xmap, ymap, canvasrect):
        """Reimplemented to update label and (eventually) center handle"""
        if self._pending_center_handle:
            x, y = self.center_handle(self.xValue(), self.yValue())
            self.setValue(x, y)
        self.update_label()
        QwtPlotMarker.draw(self, painter, xmap, ymap, canvasrect)

    # ------IBasePlotItem API----------------------------------------------------
    def set_selectable(self, state):
        """Set item selectable state"""
        self._can_select = state

    def set_resizable(self, state):
        """Set item resizable state
        (or any action triggered when moving an handle, e.g. rotation)"""
        self._can_resize = state

    def set_movable(self, state):
        """Set item movable state"""
        self._can_move = state

    def set_rotatable(self, state):
        """Set item rotatable state"""
        self._can_rotate = state

    def can_select(self):
        """

        :return:
        """
        return self._can_select

    def can_resize(self):
        """

        :return:
        """
        return self._can_resize

    def can_rotate(self):
        """

        :return:
        """
        return self._can_rotate

    def can_move(self):
        """

        :return:
        """
        return self._can_move

    def types(self):
        """Returns a group or category for this item
        this should be a class object inheriting from
        IItemType
        """
        return (IShapeItemType,)

    def set_readonly(self, state):
        """Set object readonly state"""
        self._readonly = state

    def is_readonly(self):
        """Return object readonly state"""
        return self._readonly

    def set_private(self, state):
        """Set object as private"""
        self._private = state

    def is_private(self):
        """Return True if object is private"""
        return self._private

    def select(self):
        """
        Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        if self.selected:
            # Already selected
            return
        self.selected = True
        self.markerparam.update_marker(self)
        self.invalidate_plot()

    def unselect(self):
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        self.selected = False
        self.markerparam.update_marker(self)
        self.invalidate_plot()

    def hit_test(self, pos):
        """
        Return a tuple with four elements:
        (distance, attach point, inside, other_object)

        distance:
            distance in pixels (canvas coordinates)
            to the closest attach point
        attach point:
            handle of the attach point
        inside:
            True if the mouse button has been clicked inside the object
        other_object:
            if not None, reference of the object which
            will be considered as hit instead of self
        """
        plot = self.plot()
        xc, yc = pos.x(), pos.y()
        x = plot.transform(self.xAxis(), self.xValue())
        y = plot.transform(self.yAxis(), self.yValue())
        ms = self.markerparam.markerstyle
        # The following assert has no purpose except reminding that the
        # markerstyle is one of the MARKERSTYLES dictionary values, in case
        # this dictionary evolves in the future (this should not fail):
        assert ms in list(MARKERSTYLES.values())
        if ms == "NoLine":
            return math.sqrt((x - xc) ** 2 + (y - yc) ** 2), 0, False, None
        elif ms == "HLine":
            return math.sqrt((y - yc) ** 2), 0, False, None
        elif ms == "VLine":
            return math.sqrt((x - xc) ** 2), 0, False, None
        elif ms == "Cross":
            return math.sqrt(min((x - xc) ** 2, (y - yc) ** 2)), 0, False, None

    def update_item_parameters(self):
        """ """
        self.markerparam.update_param(self)

    def get_item_parameters(self, itemparams):
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item
        """
        self.update_item_parameters()
        itemparams.add("MarkerParam", self, self.markerparam)

    def set_item_parameters(self, itemparams):
        """
        Change the appearance of this item according
        to the parameter set provided

        params is a list of Datasets of the same types as those returned
        by get_item_parameters
        """
        update_dataset(
            self.markerparam, itemparams.get("MarkerParam"), visible_only=True
        )
        self.markerparam.update_marker(self)
        if self.selected:
            self.select()

    def move_local_point_to(self, handle, pos, ctrl=None):
        """Move a handle as returned by hit_test to the new position pos
        ctrl: True if <Ctrl> button is being pressed, False otherwise"""
        x, y = canvas_to_axes(self, pos)
        self.set_pos(x, y)

    def move_local_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in canvas coordinates"""
        old_pt = canvas_to_axes(self, old_pos)
        new_pt = canvas_to_axes(self, new_pos)
        self.move_shape(old_pt, new_pt)

    def move_with_selection(self, delta_x, delta_y):
        """
        Translate the shape together with other selected items
        delta_x, delta_y: translation in plot coordinates
        """
        self.move_shape([0, 0], [delta_x, delta_y])

    # ------Public API-----------------------------------------------------------
    def set_style(self, section, option):
        """

        :param section:
        :param option:
        """
        self.markerparam.read_config(CONF, section, option)
        self.markerparam.update_marker(self)

    def set_pos(self, x=None, y=None):
        """

        :param x:
        :param y:
        """
        if x is None:
            x = self.xValue()
        if y is None:
            y = self.yValue()
        if self.constraint_cb:
            x, y = self.constraint_cb(x, y)
        self.setValue(x, y)
        if self.plot():
            self.plot().SIG_MARKER_CHANGED.emit(self)

    def get_pos(self):
        """

        :return:
        """
        return self.xValue(), self.yValue()

    def set_markerstyle(self, style):
        """

        :param style:
        """
        param = self.markerparam
        param.set_markerstyle(style)
        param.update_marker(self)

    def is_vertical(self):
        """Return True if this is a vertical cursor"""
        return self.lineStyle() == QwtPlotMarker.VLine

    def is_horizontal(self):
        """Return True if this is an horizontal cursor"""
        return self.lineStyle() == QwtPlotMarker.HLine

    def center_handle(self, x, y):
        r"""Center cursor handle depending on marker style (\|, -)"""
        plot = self.plot()
        if plot is None:
            self._pending_center_handle = True
        else:
            self._pending_center_handle = False
            if self.is_vertical():
                ymap = plot.canvasMap(self.yAxis())
                y_top, y_bottom = ymap.s1(), ymap.s2()
                y = 0.5 * (y_top + y_bottom)
            elif self.is_horizontal():
                xmap = plot.canvasMap(self.xAxis())
                x_left, x_right = xmap.s1(), xmap.s2()
                x = 0.5 * (x_left + x_right)
        return x, y

    def move_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in canvas coordinates"""
        dx = new_pos[0] - old_pos[0]
        dy = new_pos[1] - old_pos[1]
        x, y = self.xValue(), self.yValue()
        return self.move_point_to(0, (x + dx, y + dy))

    def invalidate_plot(self):
        """ """
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def update_label(self):
        """

        :return:
        """
        x, y = self.xValue(), self.yValue()
        if self.label_cb:
            label = self.label_cb(x, y)
            if label is None:
                return
        elif self.is_vertical():
            label = f"x = {x:g}"
        elif self.is_horizontal():
            label = f"y = {y:g}"
        else:
            label = f"x = {x:g}<br>y = {y:g}"
        text = self.label()
        text.setText(label)
        self.setLabel(text)
        plot = self.plot()
        if plot is not None:
            xaxis = plot.axisScaleDiv(self.xAxis())
            if x < (xaxis.upperBound() + xaxis.lowerBound()) / 2:
                hor_alignment = QC.Qt.AlignRight
            else:
                hor_alignment = QC.Qt.AlignLeft
            yaxis = plot.axisScaleDiv(self.yAxis())
            ymap = plot.canvasMap(self.yAxis())
            y_top, y_bottom = ymap.s1(), ymap.s2()
            if y < 0.5 * (yaxis.upperBound() + yaxis.lowerBound()):
                if y_top > y_bottom:
                    ver_alignment = QC.Qt.AlignBottom
                else:
                    ver_alignment = QC.Qt.AlignTop
            else:
                if y_top > y_bottom:
                    ver_alignment = QC.Qt.AlignTop
                else:
                    ver_alignment = QC.Qt.AlignBottom
            self.setLabelAlignment(hor_alignment | ver_alignment)


assert_interfaces_valid(Marker)
