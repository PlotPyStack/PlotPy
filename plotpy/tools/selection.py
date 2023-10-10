# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103


import numpy as np
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.config import _
from plotpy.events import (
    KeyEventMatch,
    ObjectHandler,
    StandardKeyMatch,
    setup_standard_tool_filter,
)
from plotpy.items import TrImageItem
from plotpy.tools.base import InteractiveTool


class SelectTool(InteractiveTool):
    """
    Graphical Object Selection Tool
    """

    TITLE = _("Selection")
    ICON = "selection.png"
    CURSOR = QC.Qt.CursorShape.ArrowCursor

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        ObjectHandler(filter, QC.Qt.MouseButton.LeftButton, start_state=start_state)
        ObjectHandler(
            filter,
            QC.Qt.MouseButton.LeftButton,
            mods=QC.Qt.KeyboardModifier.ControlModifier,
            start_state=start_state,
            multiselection=True,
        )
        filter.add_event(
            start_state,
            KeyEventMatch(
                (QC.Qt.Key.Key_Enter, QC.Qt.Key.Key_Return, QC.Qt.Key.Key_Space)
            ),
            self.validate,
            start_state,
        )
        filter.add_event(
            start_state,
            StandardKeyMatch(QG.QKeySequence.SelectAll),
            self.select_all_items,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch(
                (
                    QC.Qt.Key.Key_Left,
                    QC.Qt.Key.Key_Right,
                    QC.Qt.Key.Key_Up,
                    QC.Qt.Key.Key_Down,
                )
            ),
            self.move_with_arrow,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch(
                [
                    (QC.Qt.Key.Key_Left, QC.Qt.KeyboardModifier.ControlModifier),
                    (QC.Qt.Key.Key_Right, QC.Qt.KeyboardModifier.ControlModifier),
                    (QC.Qt.Key.Key_Up, QC.Qt.KeyboardModifier.ControlModifier),
                    (QC.Qt.Key.Key_Down, QC.Qt.KeyboardModifier.ControlModifier),
                ]
            ),
            self.move_with_arrow,
            start_state,
        )
        filter.add_event(
            start_state,
            KeyEventMatch(
                [
                    (QC.Qt.Key.Key_Left, QC.Qt.KeyboardModifier.ShiftModifier),
                    (QC.Qt.Key.Key_Right, QC.Qt.KeyboardModifier.ShiftModifier),
                    (
                        QC.Qt.Key.Key_Left,
                        QC.Qt.KeyboardModifier.ControlModifier
                        | QC.Qt.KeyboardModifier.ShiftModifier,
                    ),
                    (
                        QC.Qt.Key.Key_Right,
                        QC.Qt.KeyboardModifier.ControlModifier
                        | QC.Qt.KeyboardModifier.ShiftModifier,
                    ),
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
        if event.modifiers() == QC.Qt.KeyboardModifier.NoModifier:
            if event.key() == QC.Qt.Key.Key_Left:
                dx = -10
            elif event.key() == QC.Qt.Key.Key_Right:
                dx = 10
            elif event.key() == QC.Qt.Key.Key_Up:
                dy = -10
            elif event.key() == QC.Qt.Key.Key_Down:
                dy = 10
        elif event.modifiers() == QC.Qt.KeyboardModifier.ControlModifier:
            if event.key() == QC.Qt.Key.Key_Left:
                dx = -1
            elif event.key() == QC.Qt.Key.Key_Right:
                dx = 1
            elif event.key() == QC.Qt.Key.Key_Up:
                dy = -1
            elif event.key() == QC.Qt.Key.Key_Down:
                dy = 1
        selected_items = filter.plot.get_selected_items()
        for item in selected_items:
            if isinstance(item, TrImageItem):
                item.move_with_arrows(dx, dy)
        filter.plot.replot()

    def rotate_with_arrow(self, filter, event):
        dangle = 0
        if event.modifiers() == QC.Qt.KeyboardModifier.ShiftModifier:
            if event.key() == QC.Qt.Key.Key_Left:
                dangle = -np.deg2rad(0.5)
            elif event.key() == QC.Qt.Key.Key_Right:
                dangle = np.deg2rad(0.5)
        elif (
            event.modifiers() & QC.Qt.KeyboardModifier.ControlModifier
            == QC.Qt.KeyboardModifier.ControlModifier
        ) and (
            event.modifiers() & QC.Qt.KeyboardModifier.ShiftModifier
            == QC.Qt.KeyboardModifier.ShiftModifier
        ):
            if event.key() == QC.Qt.Key.Key_Left:
                dangle = -np.deg2rad(0.05)
            elif event.key() == QC.Qt.Key.Key_Right:
                dangle = np.deg2rad(0.05)
        selected_items = filter.plot.get_selected_items()
        for item in selected_items:
            if isinstance(item, TrImageItem):
                item.rotate_with_arrows(dangle)
        filter.plot.replot()
