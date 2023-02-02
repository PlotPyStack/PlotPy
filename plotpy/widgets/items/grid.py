# -*- coding: utf-8 -*-
"""
* :py:class:`.curve.GridItem`
.. autoclass:: GridItem
   :members:
"""
import sys

from guidata.configtools import get_icon
from qwt import QwtPlotGrid

from plotpy.config import _
from plotpy.utils.gui import assert_interfaces_valid
from plotpy.widgets.interfaces.common import IBasePlotItem, IDecoratorItemType
from plotpy.widgets.styles.base import GridParam


class GridItem(QwtPlotGrid):
    """
    Construct a grid `plot item` with the parameters *gridparam*
    (see :py:class:`.styles.GridParam`)
    """

    __implements__ = (IBasePlotItem,)

    _readonly = True
    _private = False

    def __init__(self, gridparam=None):
        super(GridItem, self).__init__()
        if gridparam is None:
            self.gridparam = GridParam(title=_("Grid"), icon="grid.png")
        else:
            self.gridparam = gridparam
        self.selected = False
        self.immutable = True  # set to false to allow moving points around
        self.update_params()  # won't work completely because it's not yet
        # attached to plot (actually, only canvas background won't be updated)
        self.setIcon(get_icon("grid.png"))

    def types(self):
        """

        :return:
        """
        return (IDecoratorItemType,)

    def attach(self, plot):
        """Reimplemented to update plot canvas background"""
        QwtPlotGrid.attach(self, plot)
        self.update_params()

    def set_readonly(self, state):
        """Set object read-only state"""
        self._readonly = state

    def is_readonly(self):
        """Return object read-only state"""
        return self._readonly

    def set_private(self, state):
        """Set object as private"""
        self._private = state

    def is_private(self):
        """Return True if object is private"""
        return self._private

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
        return False

    def can_resize(self):
        """

        :return:
        """
        return False

    def can_rotate(self):
        """

        :return:
        """
        return False

    def can_move(self):
        """

        :return:
        """
        return False

    def select(self):
        """Select item"""
        pass

    def unselect(self):
        """Unselect item"""
        pass

    def hit_test(self, pos):
        """

        :param pos:
        :return:
        """
        return sys.maxsize, 0, False, None

    def move_local_point_to(self, handle, pos, ctrl=None):
        """

        :param handle:
        :param pos:
        :param ctrl:
        """
        pass

    def move_local_shape(self, old_pos, new_pos):
        """

        :param old_pos:
        :param new_pos:
        """
        pass

    def move_with_selection(self, delta_x, delta_y):
        """

        :param delta_x:
        :param delta_y:
        """
        pass

    def update_params(self):
        """ """
        self.gridparam.update_grid(self)

    def update_item_parameters(self):
        """ """
        self.gridparam.update_param(self)

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        itemparams.add("GridParam", self, self.gridparam)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        self.gridparam = itemparams.get("GridParam")
        self.gridparam.update_grid(self)


assert_interfaces_valid(GridItem)
