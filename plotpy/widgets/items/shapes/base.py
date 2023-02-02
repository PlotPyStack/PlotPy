# -*- coding: utf-8 -*-
from qwt import QwtPlotItem

from plotpy.utils.gui import assert_interfaces_valid
from plotpy.widgets.interfaces.common import IBasePlotItem, IShapeItemType
from plotpy.widgets.items.utils import canvas_to_axes


class AbstractShape(QwtPlotItem):
    """Interface pour les objets manipulables
    il n'est pas nécessaire de dériver de QwtShape si on
    réutilise une autre classe dérivée de QwtPlotItem

    La classe de base
    """

    __implements__ = (IBasePlotItem,)

    _readonly = False
    _private = False
    _can_select = True
    _can_resize = True
    _can_rotate = False  # TODO: implement shape rotation?
    _can_move = True

    def __init__(self):
        super(AbstractShape, self).__init__()
        self.selected = False

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
        """Select item"""
        self.selected = True
        self.invalidate_plot()

    def unselect(self):
        """Unselect item"""
        self.selected = False
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
        pass

    def update_item_parameters(self):
        """
        Update item parameters (dataset) from object properties
        """
        pass

    def get_item_parameters(self, itemparams):
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item
        """
        pass

    def set_item_parameters(self, itemparams):
        """
        Change the appearance of this item according
        to the parameter set provided

        params is a list of Datasets of the same types as those returned
        by get_item_parameters
        """
        pass

    def move_local_point_to(self, handle, pos, ctrl=None):
        """Move a handle as returned by hit_test to the new position pos
        ctrl: True if <Ctrl> button is being pressed, False otherwise"""
        pt = canvas_to_axes(self, pos)
        self.move_point_to(handle, pt, ctrl)
        if self.plot():
            self.plot().SIG_ITEM_RESIZED.emit(self, 0, 0)

    def move_local_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in canvas coordinates"""
        old_pt = canvas_to_axes(self, old_pos)
        new_pt = canvas_to_axes(self, new_pos)
        self.move_shape(old_pt, new_pt)
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, *(old_pt + new_pt))

    def move_with_selection(self, delta_x, delta_y):
        """
        Translate the shape together with other selected items
        delta_x, delta_y: translation in plot coordinates
        """
        self.move_shape([0, 0], [delta_x, delta_y])

    # ------Public API-----------------------------------------------------------
    def move_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        pass

    def move_shape(self, old_pos, new_pos):
        """Translate the shape such that old_pos becomes new_pos
        in axis coordinates"""
        pass

    def invalidate_plot(self):
        """ """
        plot = self.plot()
        if plot is not None:
            plot.invalidate()

    def is_empty(self):
        return False


assert_interfaces_valid(AbstractShape)
