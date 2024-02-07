# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable-msg=W0622,R0903
# W0622: complains about filter being a builtin
# R0903: complains about too few public methods which is the purpose here

"""
Event handling
--------------

The :mod:`plotpy.events` module provides classes to handle events on a
:class:`plotpy.plot.PlotWidget`.
"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

import numpy as np
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import CONF
from plotpy.coords import axes_to_canvas, canvas_to_axes
from plotpy.items.shape.marker import Marker

if TYPE_CHECKING:
    from plotpy.plot.base import BasePlot

CursorShape = type(QC.Qt.CursorShape.ArrowCursor)


def buttons_to_str(buttons: int) -> str:
    """Conversion des flags Qt en chaine"""
    string = ""
    if buttons & QC.Qt.LeftButton:
        string += "L"
    if buttons & QC.Qt.MidButton:
        string += "M"
    if buttons & QC.Qt.RightButton:
        string += "R"
    return string


def evt_type_to_str(type: int) -> str:
    """Représentation textuelle d'un type d'événement (debug)"""
    if type == QC.QEvent.MouseButtonPress:
        return "Mpress"
    elif type == QC.QEvent.MouseButtonRelease:
        return "Mrelease"
    elif type == QC.QEvent.MouseMove:
        return "Mmove"
    elif type == QC.QEvent.ContextMenu:
        return "Context"
    else:
        return f"{type:d}"


# Event matching classes  ----------
class EventMatch:
    """A callable returning true if it matches an event"""

    def __call__(self, event):
        raise NotImplementedError

    def get_event_types(self) -> frozenset[int]:
        """Returns a set of event types handled by this
        EventMatch.
        This is used to quickly optimize events not handled
        by any event matchers
        """
        return frozenset()


class KeyEventMatch(EventMatch):
    """
    A callable returning True if it matches a key event
    keys: list of keys or couples (key, modifier)
    """

    def __init__(self, keys):
        super().__init__()
        key_list, mod_list = [], []
        for item in keys:
            if isinstance(item, (tuple, list)):
                k, m = item
            else:
                k = item
                # Avoid bad arguments: modifier instead of key
                assert k not in (
                    QC.Qt.ControlModifier,
                    QC.Qt.ShiftModifier,
                    QC.Qt.AltModifier,
                    QC.Qt.NoModifier,
                )
                m = QC.Qt.NoModifier
            key_list.append(k)
            mod_list.append(m)
        self.keys = key_list
        self.mods = mod_list

    def get_event_types(self):
        """

        :return:
        """
        return frozenset((QC.QEvent.KeyPress,))

    def __call__(self, event: QG.QKeyEvent) -> bool:
        if event.type() == QC.QEvent.KeyPress:
            my_key = event.key()
            my_mod = event.modifiers()
            if my_key in self.keys:
                mod = self.mods[self.keys.index(my_key)]
                if mod == QC.Qt.NoModifier or my_mod & mod:
                    return True
        return False


class StandardKeyMatch(EventMatch):
    """
    A callable returning True if it matches a key event
    keysequence: QKeySequence.StandardKey integer
    """

    def __init__(self, keysequence):
        super().__init__()
        assert isinstance(keysequence, (int, QG.QKeySequence.StandardKey))
        self.keyseq = keysequence

    def get_event_types(self):
        """

        :return:
        """
        return frozenset((QC.QEvent.KeyPress,))

    def __call__(self, event):
        return event.type() == QC.QEvent.KeyPress and event.matches(self.keyseq)


class MouseEventMatch(EventMatch):
    """Base class for matching mouse events"""

    def __init__(self, evt_type, btn, modifiers=QC.Qt.NoModifier):
        super().__init__()
        assert isinstance(modifiers, (int, QC.Qt.KeyboardModifier))
        self.evt_type = evt_type
        self.button = btn
        self.modifiers = modifiers

    def get_event_types(self):
        """

        :return:
        """
        return frozenset((self.evt_type,))

    def __call__(self, event):
        if event.type() == self.evt_type:
            if event.button() == self.button:
                if self.modifiers != QC.Qt.NoModifier:
                    if (event.modifiers() & self.modifiers) == self.modifiers:
                        return True
                elif event.modifiers() == QC.Qt.NoModifier:
                    return True
        return False

    def __repr__(self):
        return "<MouseMatch: {}/ {:08x}:{}>".format(
            evt_type_to_str(self.evt_type), self.modifiers, buttons_to_str(self.button)
        )


class MouseMoveMatch(MouseEventMatch):
    def __call__(self, event):
        if event.type() == self.evt_type:
            if (
                self.button != QC.Qt.NoButton
                and (event.buttons() & self.button == self.button)
            ) or event.buttons() == QC.Qt.NoButton:
                if self.modifiers != QC.Qt.NoModifier:
                    if (event.modifiers() & self.modifiers) == self.modifiers:
                        return True
                elif event.modifiers() == QC.Qt.NoModifier:
                    return True
        return False


class GestureEventMatch(EventMatch):
    """Base class for matching gesture events"""

    def __init__(self, gesture_type, gesture_state):
        super().__init__()
        self.evt_type = QC.QEvent.Gesture
        self.gesture_type = gesture_type
        self.gesture_state = gesture_state

    @staticmethod
    def __get_type_str(gesture_type):
        """Return text representation for gesture type"""
        for attr in (
            "TapGesture",
            "TapAndHoldGesture",
            "PanGesture",
            "PinchGesture",
            "SwipeGesture",
            "CustomGesture",
        ):
            if gesture_type == getattr(QC.Qt, attr):
                return attr

    @staticmethod
    def __get_state_str(gesture_state):
        """Return text representation for gesture state"""
        for attr in (
            "GestureStarted",
            "GestureUpdated",
            "GestureFinished",
            "GestureCanceled",
        ):
            if gesture_state == getattr(QC.Qt, attr):
                return attr

    def get_event_types(self):
        return frozenset((self.evt_type,))

    def __call__(self, event):
        # print(event)
        if event.type() == QC.QEvent.Gesture:
            # print(event.gestures()[0].gestureType())
            gesture = event.gesture(self.gesture_type)
            # print(gesture)
            if gesture:
                print(gesture.hotSpot(), self.__get_state_str(gesture.state()))
            return gesture and gesture.state() == self.gesture_state
        return False

    def __repr__(self):
        type_str = self.__get_type_str(self.gesture_type)
        state_str = self.__get_state_str(self.gesture_state)
        return "<GestureMatch: %s:%s>" % (type_str, state_str)


# Finite state machine for event handling ----------
class StatefulEventFilter(QC.QObject):
    """Gestion d'une machine d'état pour les événements
    d'un canvas
    """

    def __init__(self, parent: BasePlot):
        super().__init__()
        self.states = {0: {}}  # 0 : cursor 1: panning, 2: zooming
        self.cursors = {}
        self.state = 0
        self.max_state = 0
        self.events = {}
        self.plot: BasePlot = parent
        self.all_event_types = frozenset()

    def eventFilter(self, _obj, event):
        """Le callback 'eventfilter' pour Qt"""
        if not hasattr(self, "all_event_types"):
            print(repr(self), self)
        if event.type() not in self.all_event_types:
            return False
        state = self.states[self.state]
        for match, (call_list, next_state) in list(state.items()):
            if match(event):
                self.set_state(next_state, event)
                for call in call_list:
                    call(self, event)  # might change state
        return False

    def set_state(self, state, event):
        """Change l'état courant.

        Peut être appelé par les handlers pour annuler un
        changement d'état"""
        assert state in self.states
        if state == self.state:
            return
        self.state = state
        cursor = self.get_cursor(event)
        if cursor is not None:
            self.plot.canvas().setCursor(cursor)

    def new_state(self):
        """Création (réservation) d'un nouveau numéro d'état"""
        self.max_state += 1
        self.states[self.max_state] = {}
        return self.max_state

    def add_event(self, state, match, call, next_state=None):
        """Ajoute une transition sur la machine d'état
        si next_state est fourni, il doit correspondre à un état existant
        sinon un nouvel état d'arrivée est créé
        """
        assert isinstance(state, int)
        assert isinstance(match, EventMatch)
        self.all_event_types = self.all_event_types.union(match.get_event_types())
        entry = self.states[state].setdefault(match, [[], None])
        entry[0].append(call)
        if entry[1] is None:
            if next_state is None:
                next_state = self.new_state()
            else:
                pass
        else:
            if next_state is not None:
                assert next_state == entry[1]
            else:
                next_state = entry[1]

        entry[1] = next_state
        return next_state

    # gestion du curseur
    def set_cursor(self, cursor, *states):
        """Associe un curseur à un ou plusieurs états"""
        assert isinstance(cursor, CursorShape)
        for s in states:
            self.cursors[s] = cursor

    def get_cursor(self, _event):
        """Récupère le curseur associé à un état / événement donné"""
        # on passe event pour eventuellement pouvoir choisir
        # le curseur en fonction des touches de modification
        cursor = self.cursors.get(self.state, None)
        if cursor is None:
            # no cursor specified : should keep previous one
            return None
        return cursor

    # Fonction utilitaires
    def mouse_press(self, btn, modifiers=QC.Qt.NoModifier):
        """Création d'un filtre pour l'événement MousePress"""
        return self.events.setdefault(
            ("mousepress", btn, modifiers),
            MouseEventMatch(QC.QEvent.MouseButtonPress, btn, modifiers),
        )

    def mouse_move(self, btn, modifiers=QC.Qt.NoModifier):
        """Création d'un filtre pour l'événement MouseMove"""
        return self.events.setdefault(
            ("mousemove", btn, modifiers),
            MouseMoveMatch(QC.QEvent.MouseMove, btn, modifiers),
        )

    def mouse_release(self, btn, modifiers=QC.Qt.NoModifier):
        """Création d'un filtre pour l'événement MouseRelease"""
        return self.events.setdefault(
            ("mouserelease", btn, modifiers),
            MouseEventMatch(QC.QEvent.MouseButtonRelease, btn, modifiers),
        )

    def gesture(self, kind, state):
        """Création d'un filtre pour l'événement pincement"""
        return self.events.setdefault(
            ("gesture", kind, state), GestureEventMatch(kind, state)
        )

    def nothing(self, filter, event):
        """A nothing filter, provided to help removing duplicate handlers"""
        pass


class DragHandler(QC.QObject):
    """Classe de base pour les gestionnaires d'événements du type
    click - drag - release
    """

    cursor = None

    def __init__(self, filter, btn, mods=QC.Qt.NoModifier, start_state=0):
        super().__init__()
        self.state0 = filter.add_event(
            start_state, filter.mouse_press(btn, mods), self.start_tracking
        )
        self.state1 = filter.add_event(
            self.state0, filter.mouse_move(btn, mods), self.start_moving
        )
        filter.add_event(
            self.state1, filter.mouse_move(btn, mods), self.move, self.state1
        )
        filter.add_event(
            self.state0,
            filter.mouse_release(btn, mods),
            self.stop_notmoving,
            start_state,
        )
        filter.add_event(
            self.state1, filter.mouse_release(btn, mods), self.stop_moving, start_state
        )
        if self.cursor is not None:
            filter.set_cursor(self.cursor, self.state0, self.state1)
        self.start = None  # first mouse position
        self.last = None  # mouse position seen during last event
        self.parent_tracking = None

    def get_move_state(self, filter, pos):
        """

        :param filter:
        :param pos:
        :return:
        """
        rct = filter.plot.contentsRect()
        dx = (pos.x(), self.last.x(), self.start.x(), rct.width())
        dy = (pos.y(), self.last.y(), self.start.y(), rct.height())
        self.last = QC.QPointF(pos)
        return dx, dy

    def start_tracking(self, _filter, event):
        """

        :param _filter:
        :param event:
        """
        self.start = self.last = QC.QPointF(event.pos())

    def start_moving(self, filter, event):
        """

        :param filter:
        :param event:
        :return:
        """
        return self.move(filter, event)

    def stop_tracking(self, _filter, _event):
        """

        :param _filter:
        :param _event:
        """
        pass
        # filter.plot.canvas().setMouseTracking(self.parent_tracking)

    def stop_notmoving(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.stop_tracking(filter, event)

    def stop_moving(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.stop_tracking(filter, event)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        raise NotImplementedError()


class ClickHandler(QC.QObject):
    """Classe de base pour les gestionnaires d'événements du type
    click - release
    """

    #: Signal emitted by ClickHandler on mouse click
    SIG_CLICK_EVENT = QC.Signal(object, "QEvent")

    def __init__(self, filter, btn, mods=QC.Qt.NoModifier, start_state=0):
        super().__init__()
        self.state0 = filter.add_event(
            start_state, filter.mouse_press(btn, mods), filter.nothing
        )
        filter.add_event(
            self.state0, filter.mouse_release(btn, mods), self.click, start_state
        )

    def click(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.SIG_CLICK_EVENT.emit(filter, event)


class PanHandler(DragHandler):
    cursor = QC.Qt.ClosedHandCursor

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        x_state, y_state = self.get_move_state(filter, event.pos())
        filter.plot.do_pan_view(x_state, y_state)


class ZoomHandler(DragHandler):
    cursor = QC.Qt.SizeAllCursor

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        x_state, y_state = self.get_move_state(filter, event.pos())
        filter.plot.do_zoom_view(x_state, y_state)


class GestureHandler(QC.QObject):
    """Base class used to handle gestures.

    Args:
        filter: event filter into which to add the handler instance.
        start_state: start state to use in the event filter state machine.
         Defaults to 0.

    """

    kind: QC.Qt.GestureType | None = None

    def __init__(self, filter: StatefulEventFilter, start_state=0) -> None:
        super().__init__()
        filter.plot.canvas().grabGesture(self.kind)
        self.state0 = filter.add_event(
            start_state,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureStarted),
            self.start_tracking,
        )
        self.state1 = filter.add_event(
            self.state0,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureUpdated),
            self.start_moving,
        )
        filter.add_event(
            self.state1,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureUpdated),
            self.move,
            self.state1,
        )
        filter.add_event(
            self.state0,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureFinished),
            self.stop_notmoving,
            start_state,
        )
        filter.add_event(
            self.state1,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureFinished),
            self.stop_moving,
            start_state,
        )
        filter.add_event(
            self.state0,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureCanceled),
            self.stop_notmoving,
            start_state,
        )
        filter.add_event(
            self.state1,
            filter.gesture(self.kind, QC.Qt.GestureState.GestureCanceled),
            self.stop_notmoving,
            start_state,
        )
        self.start = QC.QPoint()  # first gesture position
        self.last = QC.QPoint()  # gesture position seen during last event
        self.parent_tracking = None

    def get_glob_position(self, event: QW.QGestureEvent) -> QC.QPointF:
        """Returns the hotspot global position of the gesture event.

        Args:
            event: event from which to get the position

        Returns:
            event hotspot poisition in global coordinates.
        """
        return self.get_gesture(event).hotSpot()

    def get_gesture(self, event: QW.QGestureEvent) -> QW.QGesture:
        """Returns the gesture from the event.

        Args:
            event: event from which to get the gesture.

        Returns:
            gesture from the event.
        """
        return event.gesture(self.kind)

    def start_tracking(
        self, filter: StatefulEventFilter, event: QW.QGestureEvent
    ) -> None:
        """Handles the start of the gesture tracking.

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the start of the tracking, used to get
             a position.
        """
        origin = self.get_glob_position(event)
        self.start = self.last = filter.plot.canvas().mapFromGlobal(origin.toPoint())

    def start_moving(
        self, filter: StatefulEventFilter, event: QW.QGestureEvent
    ) -> None:
        """Handles the start of the gesture moving.

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the start of the moving
        """
        return self.move(filter, event)

    def stop_tracking(
        self, _filter: StatefulEventFilter, _event: QW.QGestureEvent
    ) -> None:
        pass

    def stop_notmoving(
        self, filter: StatefulEventFilter, event: QW.QGestureEvent
    ) -> None:
        self.stop_tracking(filter, event)

    def stop_moving(self, filter: StatefulEventFilter, event: QW.QGestureEvent) -> None:
        self.stop_tracking(filter, event)

    def move(self, filter: StatefulEventFilter, event: QW.QGestureEvent) -> None:
        raise NotImplementedError


class PinchPanGestureHandler(GestureHandler):
    """Class used to handle pinch and pan gestures.

    Args:
        filter: event filter into which to add the handler instance.
        start_state: start state to use in the event filter state machine.
         Defaults to 0.

    """

    kind = QC.Qt.GestureType.PinchGesture

    def __init__(
        self,
        filter: StatefulEventFilter,
        start_state=0,
    ):
        super().__init__(filter, start_state)
        self.last_center_diff = 0
        self.marker: Marker | None = None

    def get_pan_param(
        self, plot: BasePlot, pos: QC.QPoint
    ) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
        """Returns the parameters to use for panning the plot.

        Args:
            plot: instance of BasePlot to use as a reference.
            pos: position on the plot canvas of the current hotspot.

        Returns:
            Returns two tuples of four floats each, representing the parameters used
            by BasePlot.do_pan_view.
        """
        rct = plot.contentsRect()
        dx = (pos.x(), self.last.x(), self.start.x(), rct.width())
        dy = (pos.y(), self.last.y(), self.start.y(), rct.height())
        self.last = pos
        return dx, dy

    def get_zoom_param(
        self, plot: BasePlot, pos: QC.QPoint, factor: float
    ) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
        """Returns the parameters to use for zooming on the plot.

        Args:
            plot: instance of BasePlot to use as a reference.
            pos: position on the plot canvas of the current hotspot.
            factor: factor by which to zoom.

        Returns:
            Returns two tuples of four floats each, representing the parameters used
            by BasePlot.do_zoom_view.
        """
        rect_width = plot.contentsRect().width()
        dx = (
            pos.x() * factor,
            pos.x(),
            pos.x(),
            rect_width,
        )
        dy = (
            pos.y() * factor,
            pos.y(),
            pos.y(),
            rect_width,
        )
        return dx, dy

    def start_tracking(
        self, filter: StatefulEventFilter, event: QW.QGestureEvent
    ) -> None:
        """Overrides the GestureHandler.start_tracking method to add a marker at the
        hostpot of the pinch gesture.

        Args:
            filter: event filter that contains the BasePlot instance
            event: Gesture event that triggered the start of the tracking, used to get
             a position.
        """
        plot = filter.plot
        if self.marker is None:
            self.marker = Marker()
            self.marker.attach(plot)
            self.marker.setZ(plot.get_max_z() + 1)
            self.marker.setVisible(True)
        pos = plot.canvas().mapFromGlobal(self.get_glob_position(event).toPoint())
        self.marker.move_local_point_to(0, pos)

        return super().start_tracking(filter, event)

    def move(self, filter: StatefulEventFilter, event: QW.QGestureEvent) -> None:
        """Overrides the GestureHandler.move method to handle the pinch and pan gesture.

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the move, used to get the hotspot position.
        """
        gesture: QW.QPinchGesture = self.get_gesture(event)
        plot = filter.plot

        center_point = self.get_glob_position(event)
        center_point = filter.plot.canvas().mapFromGlobal(center_point.toPoint())
        scale_factor = np.clip(gesture.scaleFactor(), 0.90, 1.1)

        pan_dx, pan_dy = self.get_pan_param(plot, center_point)
        zoom_dx, zoom_dy = self.get_zoom_param(plot, center_point, scale_factor)
        plot.do_zoom_view(zoom_dx, zoom_dy, replot=False)
        plot.do_pan_view(pan_dx, pan_dy)

    def stop_tracking(
        self, _filter: StatefulEventFilter, _event: QW.QGestureEvent
    ) -> None:
        """Overrides the GestureHandler.stop_tracking method to remove the marker when
        the gesture tracking stops.

        Args:
            _filter: event filter that contains the BasePlot instance
            _event: event that triggered the stop, not used.
        """
        if self.marker is not None:
            self.marker.detach()
            self.marker = None


class MenuHandler(ClickHandler):
    def click(self, filter, event):
        """

        :param filter:
        :param event:
        """
        menu = filter.plot.get_context_menu()
        if menu:
            menu.popup(event.globalPos())


class QtDragHandler(DragHandler):
    #: Signal emitted by QtDragHandler when starting tracking
    SIG_START_TRACKING = QC.Signal(object, "QEvent")

    #: Signal emitted by QtDragHandler when stopping tracking and not moving
    SIG_STOP_NOT_MOVING = QC.Signal(object, "QEvent")

    #: Signal emitted by QtDragHandler when stopping tracking and moving
    SIG_STOP_MOVING = QC.Signal(object, "QEvent")

    #: Signal emitted by QtDragHandler when moving
    SIG_MOVE = QC.Signal(object, "QEvent")

    def start_tracking(self, filter, event):
        """

        :param filter:
        :param event:
        """
        DragHandler.start_tracking(self, filter, event)
        self.SIG_START_TRACKING.emit(filter, event)

    def stop_notmoving(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.SIG_STOP_NOT_MOVING.emit(filter, event)

    def stop_moving(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.SIG_STOP_MOVING.emit(filter, event)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.SIG_MOVE.emit(filter, event)


class AutoZoomHandler(ClickHandler):
    def click(self, filter, _event):
        """

        :param filter:
        :param _event:
        """
        filter.plot.do_autoscale()


class MoveHandler:
    """ """

    def __init__(
        self, filter, btn=QC.Qt.NoButton, mods=QC.Qt.NoModifier, start_state=0
    ):
        filter.add_event(
            start_state, filter.mouse_move(btn, mods), self.move, start_state
        )

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        filter.plot.do_move_marker(event)


class UndoMoveObject:
    """ """

    def __init__(self, obj, pos1, pos2):
        self.obj = obj
        self.coords1 = canvas_to_axes(obj, pos1)
        self.coords2 = canvas_to_axes(obj, pos2)

    def is_valid(self):
        """

        :return:
        """
        return self.obj.plot() is not None

    def compute_positions(self):
        """

        :return:
        """
        pos1 = QC.QPointF(*axes_to_canvas(self.obj, *self.coords1))
        pos2 = QC.QPointF(*axes_to_canvas(self.obj, *self.coords2))
        return pos1, pos2

    def undo(self):
        """ """
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.move_local_shape(pos1, pos2)

    def redo(self):
        """ """
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.move_local_shape(pos2, pos1)


class UndoMovePoint(UndoMoveObject):
    """ """

    def __init__(self, obj, pos1, pos2, handle, ctrl):
        super().__init__(obj, pos1, pos2)
        self.handle = handle
        self.ctrl = ctrl

    def undo(self):
        """ """
        pos1, pos2 = self.compute_positions()
        self.obj.move_local_point_to(self.handle, pos1, self.ctrl)

    def redo(self):
        """ """
        pos1, pos2 = self.compute_positions()
        self.obj.move_local_point_to(self.handle, pos2, self.ctrl)


class UndoRotatePoint(UndoMoveObject):
    def __init__(self, obj, pos1, pos2):
        super().__init__(obj, pos1, pos2)

    def undo(self):
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.rotate_local_shape(pos1, pos2)

    def redo(self):
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.rotate_local_shape(pos2, pos1)


class ObjectHandler:
    """ """

    def __init__(
        self,
        filter: StatefulEventFilter,
        btn,
        mods=QC.Qt.NoModifier,
        start_state=0,
        multiselection=False,
    ):
        self.multiselection = multiselection
        self.start_state = start_state
        self.state0 = filter.add_event(
            start_state, filter.mouse_press(btn, mods), self.start_tracking
        )
        filter.add_event(
            self.state0, filter.mouse_move(btn, mods), self.move, self.state0
        )
        filter.add_event(
            self.state0,
            filter.mouse_release(btn, mods),
            self.stop_tracking,
            start_state,
        )
        filter.add_event(
            start_state, StandardKeyMatch(QG.QKeySequence.Undo), self.undo, start_state
        )
        filter.add_event(
            start_state, StandardKeyMatch(QG.QKeySequence.Redo), self.redo, start_state
        )
        self.handle = None  # first mouse position
        self.inside = False
        self.rotate_inside = False  # cas de la rotation avec un point à l'intérieur
        self._active = None  # mouse position seen during last event
        self.last_pos = None
        self.unselection_pending = None

        self.undo_stack = [None]
        self.undo_index = 0
        self.first_pos = None
        self.undo_action = None

    @property
    def active(self):
        """

        :return:
        """
        if self._active is not None:
            return self._active()

    @active.setter
    def active(self, value):
        if value is None:
            self._active = None
        else:
            self._active = weakref.ref(value)

    def add_undo_move_action(self, undo_action):
        """

        :param undo_action:
        """
        self.undo_stack = self.undo_stack[: self.undo_index + 1]
        self.undo_stack.append(undo_action)
        self.undo_index = len(self.undo_stack) - 1

    def undo(self, filter, event):
        """

        :param filter:
        :param event:
        """
        action = self.undo_stack[self.undo_index]
        if action is not None:
            if action.is_valid():
                action.undo()
                filter.plot.replot()
            else:
                self.undo_stack.remove(action)
            self.undo_index -= 1

    def redo(self, filter, event):
        """

        :param filter:
        :param event:
        """
        if self.undo_index < len(self.undo_stack) - 1:
            action = self.undo_stack[self.undo_index + 1]
            if action.is_valid():
                action.redo()
                filter.plot.replot()
                self.undo_index += 1
            else:
                self.undo_stack.remove(action)

    def start_tracking(self, filter, event):
        """

        :param filter:
        :param event:
        :return:
        """
        plot = filter.plot
        self.inside = False
        self.rotate_inside = False
        self.active = None
        self.handle = None
        self.first_pos = pos = event.pos()
        self.last_pos = QC.QPointF(pos)
        selected = plot.get_active_item()
        distance = CONF.get("plot", "selection/distance", 6)

        (
            nearest,
            nearest_dist,
            nearest_handle,
            nearest_inside,
        ) = plot.get_nearest_object(pos, distance)
        if nearest is not None:
            # Is the nearest object the real deal?
            if not nearest.can_select() or nearest_dist >= distance:
                # Looking for the nearest object in z containing cursor position
                (
                    nearest,
                    nearest_dist,
                    nearest_handle,
                    nearest_inside,
                ) = plot.get_nearest_object_in_z(pos)

        # This will unselect active item only if it's not moved afterwards:
        self.unselection_pending = selected is nearest
        if selected and not self.multiselection:
            # An item is selected
            self.active = selected
            (dist, self.handle, self.inside, other_object) = self.active.hit_test(pos)
            if other_object is not None:
                # e.g. LegendBoxItem: 'other_object' is the selected curve
                plot.set_active_item(other_object)
                return
            if dist >= distance and not self.inside:
                # The following allows to move together selected items by
                # clicking inside any of them (instead of active item only)
                other_selitems = [
                    _it
                    for _it in plot.get_selected_items()
                    if _it is not self.active and _it.can_move()
                ]
                for selitem in other_selitems:
                    dist, handle, inside, _other = selitem.hit_test(pos)
                    if dist < distance or inside:
                        self.inside = inside
                        break
                else:
                    self.__unselect_objects(filter)
                    filter.set_state(self.start_state, event)
                    return
        else:
            # No item is selected
            self.active = nearest
            self.handle = nearest_handle
            self.inside = nearest_inside
            dist = nearest_dist
            if nearest is not None:
                plot.set_active_item(nearest)
                if not nearest.selected:
                    if not self.multiselection:
                        plot.unselect_all()
                    plot.select_item(nearest)

        # Eventually move or resize selected object:
        self.__move_or_resize_object(dist, distance, event, filter)
        plot.replot()

    def __unselect_objects(self, filter):
        """Unselect selected object*s*"""
        plot = filter.plot
        plot.unselect_all()
        plot.replot()

    def __move_or_resize_object(self, dist, distance, event, filter):
        if (
            self.active is not None
            and self.active.can_move() is False
            and self.inside
            and self.active.can_rotate()
        ):
            # Rotate inside
            self.inside = False
            self.rotate_inside = True
            return
        if (
            dist < distance
            and self.handle is not None
            and (self.active.can_resize() or self.active.can_rotate())
        ):
            # Resize / move handle
            self.inside = False
            return
        if self.inside and self.active.can_move():
            # Move object
            return
        # can't move, can't resize
        filter.set_state(self.start_state, event)
        if self.unselection_pending:
            self.__unselect_objects(filter)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        :return:
        """
        if self.active is None:
            return
        self.unselection_pending = False
        if self.rotate_inside:
            self.active.rotate_local_shape(self.last_pos, event.pos())
            self.undo_action = UndoRotatePoint(self.active, event.pos(), self.first_pos)
        elif self.inside:
            self.active.move_local_shape(self.last_pos, event.pos())
            self.undo_action = UndoMoveObject(self.active, event.pos(), self.first_pos)
        else:
            ctrl = event.modifiers() & QC.Qt.ControlModifier == QC.Qt.ControlModifier
            self.active.move_local_point_to(self.handle, event.pos(), ctrl)
            self.undo_action = UndoMovePoint(
                self.active, self.first_pos, event.pos(), self.handle, ctrl
            )
        self.last_pos = QC.QPointF(event.pos())
        filter.plot.replot()

    def stop_tracking(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.add_undo_move_action(self.undo_action)
        if self.unselection_pending:
            self.__unselect_objects(filter)
        self.handle = None
        self.active = None
        self.inside = False
        self.rotate_inside = False


class RectangularSelectionHandler(DragHandler):
    """ """

    #: Signal emitted by RectangularSelectionHandler when ending selection
    SIG_END_RECT = QC.Signal(object, "QPointF", "QPointF")

    def __init__(self, filter, btn, mods=QC.Qt.NoModifier, start_state=0):
        super().__init__(filter, btn, mods, start_state)
        self.avoid_null_shape = False

    def set_shape(self, shape, h0, h1, setup_shape_cb=None, avoid_null_shape=False):
        """

        :param shape:
        :param h0:
        :param h1:
        :param setup_shape_cb:
        :param avoid_null_shape:
        """
        self.shape = shape
        self.shape_h0 = h0
        self.shape_h1 = h1
        self.setup_shape_cb = setup_shape_cb
        self.avoid_null_shape = avoid_null_shape

    def start_tracking(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.start = self.last = QC.QPointF(event.pos())

    def start_moving(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.shape.attach(filter.plot)
        self.shape.setZ(filter.plot.get_max_z() + 1)
        if self.avoid_null_shape:
            self.start -= QC.QPointF(1, 1)
        self.shape.move_local_point_to(self.shape_h0, self.start)
        self.shape.move_local_point_to(self.shape_h1, event.pos())
        self.start_moving_action(filter, event)
        if self.setup_shape_cb is not None:
            self.setup_shape_cb(self.shape)
        self.shape.show()
        filter.plot.replot()

    def start_moving_action(self, filter, event):
        """Les classes derivees peuvent surcharger cette methode"""
        pass

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.shape.move_local_point_to(self.shape_h1, event.pos())
        self.move_action(filter, event)
        filter.plot.replot()

    def move_action(self, filter, event):
        """Les classes derivees peuvent surcharger cette methode"""
        pass

    def stop_moving(self, filter, event):
        """

        :param filter:
        :param event:
        """
        self.shape.detach()
        self.stop_moving_action(filter, event)
        filter.plot.replot()

    def stop_moving_action(self, filter, event):
        """Les classes derivees peuvent surcharger cette methode"""
        self.SIG_END_RECT.emit(filter, self.start, event.pos())


class PointSelectionHandler(RectangularSelectionHandler):
    def stop_notmoving(self, filter, event):
        self.stop_moving(filter, event)


class ZoomRectHandler(RectangularSelectionHandler):
    def stop_moving_action(self, filter, event):
        """

        :param filter:
        :param event:
        """
        filter.plot.do_zoom_rect_view(self.start, event.pos())


def setup_standard_tool_filter(filter: StatefulEventFilter, start_state):
    """Création des filtres standard (pan/zoom) sur boutons milieu/droit"""
    # Bouton du milieu
    PanHandler(filter, QC.Qt.MidButton, start_state=start_state)
    AutoZoomHandler(filter, QC.Qt.MidButton, start_state=start_state)

    # Bouton droit
    ZoomHandler(filter, QC.Qt.RightButton, start_state=start_state)
    MenuHandler(filter, QC.Qt.RightButton, start_state=start_state)

    # Gestes
    PinchPanGestureHandler(filter, start_state=start_state)

    # Autres (touches, move)
    MoveHandler(filter, start_state=start_state)
    MoveHandler(filter, start_state=start_state, mods=QC.Qt.ShiftModifier)
    MoveHandler(filter, start_state=start_state, mods=QC.Qt.AltModifier)
    return start_state
