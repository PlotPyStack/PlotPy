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

Overview
^^^^^^^^

The :mod:`plotpy.events` module provides classes to handle events on a
:class:`plotpy.plot.PlotWidget`.

The following classes are available:

* :class:`.StatefulEventFilter`: stateful event filter
* :class:`.KeyEventMatch`: key event match
* :class:`.StandardKeyMatch`: standard key event match
* :class:`.MouseEventMatch`: mouse event match
* :class:`.GestureEventMatch`: gesture event match
* :class:`.DragHandler`: drag handler
* :class:`.ClickHandler`: click handler
* :class:`.PanHandler`: pan handler
* :class:`.ZoomHandler`: zoom handler
* :class:`.GestureHandler`: gesture handler
* :class:`.PinchPanGestureHandler`: pinch and pan gesture handler
* :class:`.MenuHandler`: menu handler
* :class:`.QtDragHandler`: Qt drag handler
* :class:`.AutoZoomHandler`: auto zoom handler
* :class:`.MoveHandler`: move handler
* :class:`.ObjectHandler`: object handler
* :class:`.RectangularSelectionHandler`: rectangular selection handler
* :class:`.PointSelectionHandler`: point selection handler
* :class:`.ZoomRectHandler`: zoom rectangle handler

Reference
^^^^^^^^^

.. autoclass:: StatefulEventFilter
    :members:
.. autoclass:: KeyEventMatch
    :members:
.. autoclass:: StandardKeyMatch
    :members:
.. autoclass:: MouseEventMatch
    :members:
.. autoclass:: GestureEventMatch
    :members:
.. autoclass:: DragHandler
    :members:
.. autoclass:: ClickHandler
    :members:
.. autoclass:: PanHandler
    :members:
.. autoclass:: ZoomHandler
    :members:
.. autoclass:: GestureHandler
    :members:
.. autoclass:: PinchPanGestureHandler
    :members:
.. autoclass:: MenuHandler
    :members:
.. autoclass:: QtDragHandler
    :members:
.. autoclass:: AutoZoomHandler
    :members:
.. autoclass:: MoveHandler
    :members:
.. autoclass:: ObjectHandler
    :members:
.. autoclass:: RectangularSelectionHandler
    :members:
.. autoclass:: PointSelectionHandler
    :members:
.. autoclass:: ZoomRectHandler
    :members:
"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any, Callable

import numpy as np
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import CONF
from plotpy.coords import axes_to_canvas, canvas_to_axes
from plotpy.items.shape.marker import Marker

if TYPE_CHECKING:
    from qtpy.QtCore import QPoint

    from plotpy.plot.base import BasePlot


def buttons_to_str(buttons: int) -> str:
    """Conversion of Qt flags to string

    Args:
        buttons: Qt flags (e.g. `Qt.LeftButton`, `Qt.RightButton`, etc.)

    Returns:
        Human readable string for the button flags
    """
    string = ""
    if buttons & QC.Qt.LeftButton:
        string += "L"
    if buttons & QC.Qt.MidButton:  # Do not use QC.Qt.MouseButton.MidButton (Qt6!)
        string += "M"
    if buttons & QC.Qt.RightButton:
        string += "R"
    return string


def evt_type_to_str(type: int) -> str:
    """Convert event type to human readable string

    Args:
        type: event type

    Returns:
        Human readable string for the event type
    """
    if type == QC.QEvent.MouseButtonPress:
        return "Mpress"
    elif type == QC.QEvent.MouseButtonRelease:
        return "Mrelease"
    elif type == QC.QEvent.MouseMove:
        return "Mmove"
    elif type == QC.QEvent.ContextMenu:
        return "Context"
    return f"{type:d}"


# MARK: Event handlers -----------------------------------------------------------------
class EventMatch:
    """A callable returning true if it matches an event"""

    def __call__(self, event: QC.QEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
        raise NotImplementedError

    def get_event_types(self) -> frozenset[int]:
        """Returns a set of event types handled by this
        EventMatch.

        This is used to quickly optimize events not handled by any event matchers
        """
        return frozenset()


class KeyEventMatch(EventMatch):
    """
    A callable returning True if it matches a key event

    Args:
        keys: list of keys or couples (key, modifier)
    """

    def __init__(self, keys: list[int | tuple[int, int]]) -> None:
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

    def get_event_types(self) -> frozenset[int]:
        """Return the set of event types handled by this event match"""
        return frozenset((QC.QEvent.KeyPress,))

    def __call__(self, event: QG.QKeyEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
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

    Args:
        keysequence: QKeySequence.StandardKey integer
    """

    def __init__(self, keysequence: int) -> None:
        super().__init__()
        assert isinstance(keysequence, (int, QG.QKeySequence.StandardKey))
        self.keyseq = keysequence

    def get_event_types(self) -> frozenset[int]:
        """Return the set of event types handled by this event match"""
        return frozenset((QC.QEvent.KeyPress,))

    def __call__(self, event: QG.QKeyEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
        return event.type() == QC.QEvent.KeyPress and event.matches(self.keyseq)


class MouseEventMatch(EventMatch):
    """Base class for matching mouse events

    Args:
        evt_type: event type
        btn: button to match
        modifiers: keyboard modifiers to match
    """

    def __init__(
        self, evt_type: int, btn: int, modifiers: int = QC.Qt.NoModifier
    ) -> None:
        super().__init__()
        assert isinstance(modifiers, (int, QC.Qt.KeyboardModifier))
        self.evt_type = evt_type
        self.button = btn
        self.modifiers = modifiers

    def get_event_types(self) -> frozenset[int]:
        """Return the set of event types handled by this event match"""
        return frozenset((self.evt_type,))

    def __call__(self, event: QG.QMouseEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
        if event.type() == self.evt_type:
            if event.button() == self.button:
                if self.modifiers != QC.Qt.NoModifier:
                    if (event.modifiers() & self.modifiers) == self.modifiers:
                        return True
                elif event.modifiers() == QC.Qt.NoModifier:
                    return True
        return False

    def __repr__(self) -> str:
        """Return textual representation"""
        return "<MouseMatch: {}/ {:08x}:{}>".format(
            evt_type_to_str(self.evt_type), self.modifiers, buttons_to_str(self.button)
        )


class MouseMoveMatch(MouseEventMatch):
    def __call__(self, event: QG.QMouseEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
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

    def __init__(self, gesture_type: int, gesture_state: int) -> None:
        super().__init__()
        self.evt_type = QC.QEvent.Gesture
        self.gesture_type = gesture_type
        self.gesture_state = gesture_state

    @staticmethod
    def __get_type_str(gesture_type: int) -> str:
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
    def __get_state_str(gesture_state: int) -> str:
        """Return text representation for gesture state"""
        for attr in (
            "GestureStarted",
            "GestureUpdated",
            "GestureFinished",
            "GestureCanceled",
        ):
            if gesture_state == getattr(QC.Qt, attr):
                return attr

    def get_event_types(self) -> frozenset[int]:
        """Return the set of event types handled by this event match"""
        return frozenset((self.evt_type,))

    def __call__(self, event: QC.QEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
        if event.type() == QC.QEvent.Gesture:
            gesture = event.gesture(self.gesture_type)
            return gesture and gesture.state() == self.gesture_state
        return False

    def __repr__(self) -> str:
        """Return textual representation"""
        type_str = self.__get_type_str(self.gesture_type)
        state_str = self.__get_state_str(self.gesture_state)
        return "<GestureMatch: %s:%s>" % (type_str, state_str)


class WheelEventMatch(EventMatch):
    """A callable returning True if it matches a wheel event

    Args:
        modifiers: keyboard modifiers
    """

    def __init__(self, modifiers: int = QC.Qt.KeyboardModifier.NoModifier) -> None:
        super().__init__()
        self.modifiers = modifiers

    def get_event_types(self) -> frozenset[int]:
        """Return the set of event types handled by this event match"""
        return frozenset((QC.QEvent.Type.Wheel,))

    def __call__(self, event: QG.QWheelEvent) -> bool:
        """Returns True if the event matches the event match

        Args:
            event: event to match
        """
        return isinstance(event, QG.QWheelEvent) and event.modifiers() == self.modifiers


# MARK: Finite state machine -----------------------------------------------------------
class StatefulEventFilter(QC.QObject):
    """State machine for handling events of a plot's canvas

    Args:
        parent: plot on which to install the event filter
    """

    def __init__(self, parent: BasePlot) -> None:
        super().__init__()

        # Machine states: (0: cursor, 1: panning, 2: zooming)
        self.states: dict[int, dict[EventMatch, list[list[callable], int]]] = {0: {}}

        self.cursors: dict[int, QC.Qt.CursorShape] = {}
        self.state = 0
        self.max_state = 0
        self.events: dict[tuple[str, int, int], EventMatch] = {}
        self.plot: BasePlot = parent
        self.all_event_types = frozenset()

    def eventFilter(self, _obj: QC.QObject, event: QC.QEvent) -> bool:
        """The `eventfilter` callback for Qt"""
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

    def set_state(self, state: int, event: QC.QEvent) -> None:
        """Change the current state.
        Can be called by handlers to cancel a state change

        Args:
            state: new state
            event: event that triggered the state change
        """
        assert state in self.states
        if state == self.state:
            return
        self.state = state
        cursor = self.get_cursor(event)
        if cursor is not None:
            self.plot.canvas().setCursor(cursor)

    def new_state(self) -> int:
        """Create (reserve) a new state number

        Returns:
            New state number
        """
        self.max_state += 1
        self.states[self.max_state] = {}
        return self.max_state

    def add_event(
        self, state: int, match: EventMatch, call: callable, next_state: int = None
    ) -> int:
        """Add a transition to the state machine.
        If next_state is provided, it must correspond to an existing state,
        otherwise a new destination state is created

        Args:
            state: current state
            match: event matcher
            call: callable to execute when the event matches
            next_state: next state to go to when the event matches

        Returns:
            Next state number
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

    def nothing(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """A nothing filter, provided to help removing duplicate handlers

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the action
        """
        pass

    # Cursor management ----------------------------------------------------------------
    def set_cursor(self, cursor: QC.Qt.CursorShape, *states: int) -> None:
        """Associate a cursor with one or more states

        Args:
            cursor: cursor shape
            states: state numbers
        """
        assert isinstance(cursor, QC.Qt.CursorShape)
        for s in states:
            self.cursors[s] = cursor

    def get_cursor(self, _event: QC.QEvent) -> QC.Qt.CursorShape | None:
        """Get the cursor associated with a given state/event

        Returns:
            Cursor shape or None if no cursor is associated with the state
        """
        # pass event to potentially choose the cursor based on modifier keys
        cursor = self.cursors.get(self.state, None)
        if cursor is None:
            # no cursor specified : should keep previous one
            return None
        return cursor

    # Mouse management -----------------------------------------------------------------
    def mouse_press(
        self, btn: int, modifiers: int = QC.Qt.NoModifier
    ) -> MouseEventMatch:
        """Create a filter for the MousePress event

        Args:
            btn: button to match
            modifiers: keyboard modifiers to match

        Returns:
            An instance of MouseEventMatch that matches the MousePress event
        """
        return self.events.setdefault(
            ("mousepress", btn, modifiers),
            MouseEventMatch(QC.QEvent.MouseButtonPress, btn, modifiers),
        )

    def mouse_move(
        self, btn: int, modifiers: int = QC.Qt.NoModifier
    ) -> MouseEventMatch:
        """Create a filter for the MouseMove event

        Args:
            btn: button to match
            modifiers: keyboard modifiers to match

        Returns:
            An instance of MouseEventMatch that matches the MouseMove event
        """
        return self.events.setdefault(
            ("mousemove", btn, modifiers),
            MouseMoveMatch(QC.QEvent.MouseMove, btn, modifiers),
        )

    def mouse_release(
        self, btn: int, modifiers: int = QC.Qt.NoModifier
    ) -> MouseEventMatch:
        """Create a filter for the MouseRelease event

        Args:
            btn: The button to match
            modifiers: The keyboard modifiers to match

        Returns:
            An instance of MouseEventMatch that matches the MouseRelease event
        """
        return self.events.setdefault(
            ("mouserelease", btn, modifiers),
            MouseEventMatch(QC.QEvent.MouseButtonRelease, btn, modifiers),
        )

    # Gesture management ---------------------------------------------------------------
    def gesture(self, kind: int, state: int) -> GestureEventMatch:
        """Create a filter for the gesture event

        Args:
            kind: The type of gesture
            state: The state of the gesture

        Returns:
            An instance of GestureEventMatch that matches the gesture event
        """
        return self.events.setdefault(
            ("gesture", kind, state), GestureEventMatch(kind, state)
        )

    # Wheel management -----------------------------------------------------------------
    def wheel(
        self, modifiers: int = QC.Qt.KeyboardModifier.NoModifier
    ) -> WheelEventMatch:
        """Create a filter for wheel events

        Args:
            modifiers: The keyboard modifiers to use with the wheel event

        Returns:
            An instance of WheelEventMatch that matches the wheel event"""
        return self.events.setdefault(("wheel", modifiers), WheelEventMatch(modifiers))


# MARK: Event handlers -----------------------------------------------------------------
class DragHandler(QC.QObject):
    """Base class for click-drag-release event handlers.

    Args:
        filter: The StatefulEventFilter instance.
        btn: The mouse button to match.
        mods: The keyboard modifiers to match. (default: QC.Qt.NoModifier)
        start_state: The starting state. (default: 0)
    """

    cursor = None

    def __init__(
        self,
        filter: StatefulEventFilter,
        btn: int,
        mods: int = QC.Qt.NoModifier,
        start_state: int = 0,
    ) -> None:
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

    def get_move_state(
        self, filter: StatefulEventFilter, pos: QC.QPointF
    ) -> tuple[float, float]:
        """Get the movement state based on the current filter and position

        Args:
            filter: The StatefulEventFilter instance
            pos: The current position

        Returns:
            A tuple containing the movement state in the x and y directions
        """
        rct = filter.plot.contentsRect()
        dx = (pos.x(), self.last.x(), self.start.x(), rct.width())
        dy = (pos.y(), self.last.y(), self.start.y(), rct.height())
        self.last = QC.QPointF(pos)
        return dx, dy

    def start_tracking(self, _filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Start tracking the mouse movement

        Args:
            _filter: The StatefulEventFilter instance
            event: The mouse event
        """
        self.start = self.last = QC.QPointF(event.pos())

    def start_moving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Start moving the mouse

        Args:
            filter: The StatefulEventFilter instance
            event: The mouse event
        """
        return self.move(filter, event)

    def stop_tracking(self, _filter: StatefulEventFilter, _event: QC.QEvent) -> None:
        """Stop tracking the mouse movement

        Args:
            _filter: The StatefulEventFilter instance
            _event: The mouse event
        """
        pass
        # filter.plot.canvas().setMouseTracking(self.parent_tracking)

    def stop_notmoving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop tracking the mouse movement when the mouse is not moving.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.stop_tracking(filter, event)

    def stop_moving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop moving the mouse

        Args:
            filter: The StatefulEventFilter instance
            event: The mouse event
        """
        self.stop_tracking(filter, event)

    def move(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Move the mouse

        Args:
            filter: The StatefulEventFilter instance
            event: The mouse event
        """
        raise NotImplementedError()


class ClickHandler(QC.QObject):
    """Base class for click-release event handlers.

    Args:
        filter: The StatefulEventFilter instance.
        btn: The mouse button to match.
        mods: The keyboard modifiers to match. (default: QC.Qt.NoModifier)
        start_state: The starting state. (default: 0)

    Signals:
        SIG_CLICK_EVENT: Signal emitted by ClickHandler on mouse click
    """

    #: Signal emitted by ClickHandler on mouse click
    SIG_CLICK_EVENT = QC.Signal(object, "QEvent")

    def __init__(
        self,
        filter: StatefulEventFilter,
        btn: int,
        mods: int = QC.Qt.NoModifier,
        start_state: int = 0,
    ) -> None:
        super().__init__()
        self.state0 = filter.add_event(
            start_state, filter.mouse_press(btn, mods), filter.nothing
        )
        filter.add_event(
            self.state0, filter.mouse_release(btn, mods), self.click, start_state
        )

    def click(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Handle the click event.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.SIG_CLICK_EVENT.emit(filter, event)


class PanHandler(DragHandler):
    cursor = QC.Qt.ClosedHandCursor

    def move(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Move the mouse.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        x_state, y_state = self.get_move_state(filter, event.pos())
        filter.plot.do_pan_view(x_state, y_state)


class ZoomHandler(DragHandler):
    cursor = QC.Qt.SizeAllCursor

    def move(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Move the mouse.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
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

    def __init__(self, filter: StatefulEventFilter, start_state: int = 0) -> None:
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
        """Handles the stop of the gesture tracking.

        Args:
            _filter: event filter that contains the BasePlot instance
            _event: event that triggered the stop of the tracking
        """
        pass

    def stop_notmoving(
        self, filter: StatefulEventFilter, event: QW.QGestureEvent
    ) -> None:
        """Handles the stop of the gesture tracking when the gesture is not moving.

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the stop of the tracking
        """
        self.stop_tracking(filter, event)

    def stop_moving(self, filter: StatefulEventFilter, event: QW.QGestureEvent) -> None:
        """Handles the stop of the gesture moving.

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the stop of the moving
        """
        self.stop_tracking(filter, event)

    def move(self, filter: StatefulEventFilter, event: QW.QGestureEvent) -> None:
        """Handles the movement of the gesture.

        Args:
            filter: event filter that contains the BasePlot instance
            event: event that triggered the movement
        """
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
    ) -> None:
        super().__init__(filter, start_state)
        self.last_center_diff = 0
        self.marker: Marker | None = None

    def get_pan_param(
        self, plot: BasePlot, pos: QPoint
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
        self, plot: BasePlot, pos: QPoint, factor: float
    ) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
        """Returns the parameters to use for zooming on the plot.

        Args:
            plot: instance of BasePlot to use as a reference.
            pos: position on the plot canvas of the current hotspot.
            factor: factor by which to zoom (zero-centered).

        Returns:
            Returns two tuples of four floats each, representing the parameters used
            by BasePlot.do_zoom_view.
        """
        rect = plot.contentsRect()
        w, h = rect.width(), rect.height()
        x, y = pos.x(), pos.y()
        dx = (
            x + (w * factor),
            x,
            x,
            w,
        )
        dy = (
            y + (h * factor),
            y,
            y,
            h,
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
        scale_factor = np.clip(gesture.scaleFactor(), 0.95, 1.05) - 1

        pan_dx, pan_dy = self.get_pan_param(plot, center_point)
        zoom_dx, zoom_dy = self.get_zoom_param(plot, center_point, scale_factor)
        plot.do_pan_view(pan_dx, pan_dy, replot=True)
        plot.do_zoom_view(zoom_dx, zoom_dy, lock_aspect_ratio=True)

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
    """Class to handle context menu events."""

    def click(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """
        Handles the click event.

        Args:
            filter: The StatefulEventFilter instance.
            event: The QC.QEvent instance.
        """
        menu = filter.plot.get_context_menu()
        if menu:
            menu.popup(event.globalPos())


class WheelHandler(QC.QObject):
    """Base class for handling mouse wheel events.

    Args:
        filter: event filter into which to add the handler instance.
        mods: Keyboard modifier that can be used at the same time as the wheel to
         trigger the event. Defaults to QC.Qt.KeyboardModifier.NoModifier.
        start_state: start state to use in the event filter state machine.
         Defaults to 0."""

    def __init__(
        self,
        filter: StatefulEventFilter,
        mods=QC.Qt.KeyboardModifier.NoModifier,
        start_state=0,
    ) -> None:
        super().__init__()
        self.state0 = filter.add_event(
            start_state, filter.wheel(mods), self.wheel, start_state
        )

    def wheel(self, filter: StatefulEventFilter, event: QG.QWheelEvent) -> None:
        """Handles the wheel event.

        Args:
            filter: event filter that contains the BasePlot instance
            event: the wheel event that triggered the action."""
        raise NotImplementedError()


class WheelZoomHandler(WheelHandler):
    """Class to handle zooming with the mouse wheel."""

    def get_zoom_param(
        self, plot: BasePlot, pos: QPoint, factor: float
    ) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
        """Returns the parameters to use for zooming on the plot.

        Args:
            plot: instance of BasePlot to use as a reference.
            pos: position on the plot canvas of the current hotspot.
            factor: factor by which to zoom (zero-centered).

        Returns:
            Returns two tuples of four floats each, representing the parameters used
            by BasePlot.do_zoom_view.
        """

        x, y = pos.x(), pos.y()
        rect = plot.contentsRect()
        w, h = rect.width(), rect.height()
        dx = (
            x + (w * factor),
            x,
            x,
            w,
        )
        dy = (
            y + (h * factor),
            y,
            y,
            h,
        )
        return dx, dy

    def wheel(self, filter: StatefulEventFilter, event: QG.QWheelEvent) -> None:
        """Overrides the WheelHandler.wheel method to handle the zooming with the mouse
        wheel.

        Args:
            filter: event filter that contains the BasePlot instance
            event: the wheel event that triggered the zooming. Use to get zoom factor
             and position
        """
        plot = filter.plot
        center_point = event.globalPos()
        center_point = filter.plot.canvas().mapFromGlobal(center_point)  # type: ignore
        zoom_factor = (event.angleDelta().y() / 120) * 0.08
        dx, dy = self.get_zoom_param(plot, center_point, zoom_factor)
        plot.do_zoom_view(dx, dy, lock_aspect_ratio=True)


class QtDragHandler(DragHandler):
    """Class to handle drag events using Qt signals."""

    #: Signal emitted by QtDragHandler when starting tracking
    SIG_START_TRACKING = QC.Signal(object, "QEvent")

    #: Signal emitted by QtDragHandler when stopping tracking and not moving
    SIG_STOP_NOT_MOVING = QC.Signal(object, "QEvent")

    #: Signal emitted by QtDragHandler when stopping tracking and moving
    SIG_STOP_MOVING = QC.Signal(object, "QEvent")

    #: Signal emitted by QtDragHandler when moving
    SIG_MOVE = QC.Signal(object, "QEvent")

    def start_tracking(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Starts tracking the gesture.

        Args:
            filter: The StatefulEventFilter instance.
            event: The QGestureEvent instance.
        """
        DragHandler.start_tracking(self, filter, event)
        self.SIG_START_TRACKING.emit(filter, event)

    def stop_notmoving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stops tracking when the gesture is not moving.

        Args:
            filter: The StatefulEventFilter instance.
            event: The QGestureEvent instance.
        """
        self.SIG_STOP_NOT_MOVING.emit(filter, event)

    def stop_moving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """
        Stops the movement of the gesture.

        Args:
            filter: The StatefulEventFilter instance.
            event: The QGestureEvent instance.
        """
        self.SIG_STOP_MOVING.emit(filter, event)

    def move(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Handles the move event.

        Args:
            filter: The StatefulEventFilter instance.
            event: The QGestureEvent instance.
        """
        self.SIG_MOVE.emit(filter, event)


class AutoZoomHandler(ClickHandler):
    """Class to handle auto-zoom events."""

    def click(self, filter: StatefulEventFilter, _event: QC.QEvent) -> None:
        """Handles the click event.

        Args:
            filter: The StatefulEventFilter instance.
            _event: The QC.QEvent instance.
        """
        filter.plot.do_autoscale()


class MoveHandler:
    """Class to handle moving events.

    Args:
        filter: The StatefulEventFilter instance.
        btn: The mouse button to match.
        mods: The keyboard modifiers to match. (default: QC.Qt.NoModifier)
        start_state: The starting state. (default: 0)
    """

    def __init__(
        self,
        filter: StatefulEventFilter,
        btn: QC.Qt.MouseButton = QC.Qt.NoButton,
        mods: QC.Qt.KeyboardModifiers = QC.Qt.NoModifier,
        start_state: int = 0,
    ):
        filter.add_event(
            start_state, filter.mouse_move(btn, mods), self.move, start_state
        )

    def move(self, filter: StatefulEventFilter, event: QW.QGestureEvent) -> None:
        """
        Handles the move event.

        Args:
            filter: The StatefulEventFilter instance.
            event: The QGestureEvent instance.
        """
        filter.plot.do_move_marker(event)


class UndoMoveObject:
    """Class to handle undo/redo events for moving objects.

    Args:
        obj: The object to move.
        pos1: The initial position.
        pos2: The final position.
    """

    def __init__(
        self, obj: Any, pos1: tuple[float, float], pos2: tuple[float, float]
    ) -> None:
        self.obj = obj
        self.coords1 = canvas_to_axes(obj, pos1)
        self.coords2 = canvas_to_axes(obj, pos2)

    def is_valid(self) -> bool:
        """Check if the object is valid.

        Returns:
            True if the object is valid, False otherwise.
        """
        return self.obj.plot() is not None

    def compute_positions(self) -> tuple[QC.QPointF, QC.QPointF]:
        """Compute the positions of the object.

        Returns:
            A tuple containing the positions of the object.
        """
        pos1 = QC.QPointF(*axes_to_canvas(self.obj, *self.coords1))
        pos2 = QC.QPointF(*axes_to_canvas(self.obj, *self.coords2))
        return pos1, pos2

    def undo(self) -> None:
        """Undo the action."""
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.move_local_shape(pos1, pos2)

    def redo(self) -> None:
        """Redo the action."""
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.move_local_shape(pos2, pos1)


class UndoMovePoint(UndoMoveObject):
    """Class to handle undo/redo events for moving points.

    Args:
        obj: The object to move.
        pos1: The initial position.
        pos2: The final position.
        handle: The handle to move.
        ctrl: The control point.
    """

    def __init__(
        self,
        obj: Any,
        pos1: tuple[float, float],
        pos2: tuple[float, float],
        handle: Any,
        ctrl: Any,
    ) -> None:
        super().__init__(obj, pos1, pos2)
        self.handle = handle
        self.ctrl = ctrl

    def undo(self) -> None:
        """Undo the action."""
        pos1, pos2 = self.compute_positions()
        self.obj.move_local_point_to(self.handle, pos1, self.ctrl)

    def redo(self) -> None:
        """Redo the action."""
        pos1, pos2 = self.compute_positions()
        self.obj.move_local_point_to(self.handle, pos2, self.ctrl)


class UndoRotatePoint(UndoMoveObject):
    """Class to handle undo/redo events for rotating points.

    Args:
        obj: The object to move.
        pos1: The initial position.
        pos2: The final position.
    """

    def __init__(
        self, obj: Any, pos1: tuple[float, float], pos2: tuple[float, float]
    ) -> None:
        super().__init__(obj, pos1, pos2)

    def undo(self) -> None:
        """Undo the action."""
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.rotate_local_shape(pos1, pos2)

    def redo(self) -> None:
        """Redo the action."""
        pos1, pos2 = self.compute_positions()
        self.obj.plot().unselect_all()
        self.obj.rotate_local_shape(pos2, pos1)


class ObjectHandler:
    """Base class for handling objects.

    Args:
        filter: The StatefulEventFilter instance.
        btn: The mouse button to match.
        mods: The keyboard modifiers to match. (default: QC.Qt.NoModifier)
        start_state: The starting state. (default: 0)
        multiselection: Whether to allow multiple selections. (default: False)
    """

    def __init__(
        self,
        filter: StatefulEventFilter,
        btn: int,
        mods: QC.Qt.KeyboardModifiers = QC.Qt.NoModifier,
        start_state: int = 0,
        multiselection: bool = False,
    ) -> None:
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
    def active(self) -> Any:
        """Return active object"""
        if self._active is not None:
            return self._active()

    @active.setter
    def active(self, value: Any) -> None:
        """Set active object"""
        if value is None:
            self._active = None
        else:
            self._active = weakref.ref(value)

    def add_undo_move_action(self, undo_action: Any) -> None:
        """Add undo action to undo stack"""
        self.undo_stack = self.undo_stack[: self.undo_index + 1]
        self.undo_stack.append(undo_action)
        self.undo_index = len(self.undo_stack) - 1

    def undo(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Undo the last action.

        Args:
            filter: The StatefulEventFilter instance.
            event: The event triggering the undo action.
        """
        action = self.undo_stack[self.undo_index]
        if action is not None:
            if action.is_valid():
                action.undo()
                filter.plot.replot()
            else:
                self.undo_stack.remove(action)
            self.undo_index -= 1

    def redo(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Redo the last action.

        Args:
            filter: The StatefulEventFilter instance.
            event: The event triggering the redo action.
        """
        if self.undo_index < len(self.undo_stack) - 1:
            action = self.undo_stack[self.undo_index + 1]
            if action.is_valid():
                action.redo()
                filter.plot.replot()
                self.undo_index += 1
            else:
                self.undo_stack.remove(action)

    def start_tracking(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Starts tracking the mouse movement for selection and interaction.

        Args:
            filter: The filter object.
            event: The mouse event.
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

    def __unselect_objects(self, filter: StatefulEventFilter) -> None:
        """Unselect selected object*s*

        Args:
            filter: The StatefulEventFilter instance.
        """
        plot = filter.plot
        plot.unselect_all()
        plot.replot()

    def __move_or_resize_object(
        self,
        dist: float,
        distance: float,
        event: QC.QEvent,
        filter: StatefulEventFilter,
    ) -> None:
        """Move or resize the object

        Args:
            dist: The distance.
            distance: The distance.
            event: The mouse event.
            filter: The StatefulEventFilter instance.
        """
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

    def move(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Move the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
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

    def stop_tracking(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop tracking the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.add_undo_move_action(self.undo_action)
        if self.unselection_pending:
            self.__unselect_objects(filter)
        self.handle = None
        self.active = None
        self.inside = False
        self.rotate_inside = False


class RectangularSelectionHandler(DragHandler):
    """Base class for handling rectangular selections.

    Args:
        filter: The StatefulEventFilter instance.
        btn: The mouse button to match.
        mods: The keyboard modifiers to match. (default: QC.Qt.NoModifier)
        start_state: The starting state. (default: 0)
    """

    #: Signal emitted by RectangularSelectionHandler when ending selection
    SIG_END_RECT = QC.Signal(object, "QPointF", "QPointF")

    def __init__(
        self,
        filter: StatefulEventFilter,
        btn: int,
        mods: QC.Qt.KeyboardModifiers = QC.Qt.NoModifier,
        start_state: int = 0,
    ) -> None:
        super().__init__(filter, btn, mods, start_state)
        self.avoid_null_shape = False

    def set_shape(
        self,
        shape: Any,
        h0: Any,
        h1: Any,
        setup_shape_cb: Callable | None = None,
        avoid_null_shape: bool = False,
    ) -> None:
        """Set the shape.

        Args:
            shape: The shape.
            h0: The first handle.
            h1: The second handle.
            setup_shape_cb: The setup shape callback.
            avoid_null_shape: Whether to avoid null shape.
        """
        self.shape = shape
        self.shape_h0 = h0
        self.shape_h1 = h1
        self.setup_shape_cb = setup_shape_cb
        self.avoid_null_shape = avoid_null_shape

    def start_tracking(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Start tracking the mouse movement for selection and interaction.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.start = self.last = QC.QPointF(event.pos())

    def start_moving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Start moving the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
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

    def start_moving_action(
        self, filter: StatefulEventFilter, event: QC.QEvent
    ) -> None:
        """Start moving the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        pass

    def move(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Move the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.shape.move_local_point_to(self.shape_h1, event.pos())
        self.move_action(filter, event)
        filter.plot.replot()

    def move_action(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Move the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        pass

    def stop_moving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop moving the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.shape.detach()
        self.stop_moving_action(filter, event)
        filter.plot.replot()

    def stop_moving_action(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop moving the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.SIG_END_RECT.emit(filter, self.start, event.pos())


class PointSelectionHandler(RectangularSelectionHandler):
    """Class to handle point selections."""

    def stop_notmoving(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop the point selection when the point is not moving.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        self.stop_moving(filter, event)


class ZoomRectHandler(RectangularSelectionHandler):
    """Class to handle zoom rectangles."""

    def stop_moving_action(self, filter: StatefulEventFilter, event: QC.QEvent) -> None:
        """Stop moving the object.

        Args:
            filter: The StatefulEventFilter instance.
            event: The mouse event.
        """
        filter.plot.do_zoom_rect_view(self.start, event.pos())


def setup_standard_tool_filter(filter: StatefulEventFilter, start_state: int) -> int:
    """Creation of standard filters (pan/zoom) on middle/right buttons

    Args:
        filter: The StatefulEventFilter instance.
        start_state: The starting state.

    Returns:
        The starting state.
    """
    # Middle button
    # Do not use QC.Qt.MouseButton.MidButton (Qt6!)
    PanHandler(filter, QC.Qt.MidButton, start_state=start_state)
    AutoZoomHandler(filter, QC.Qt.MidButton, start_state=start_state)

    # Right button
    ZoomHandler(filter, QC.Qt.MouseButton.RightButton, start_state=start_state)
    MenuHandler(filter, QC.Qt.MouseButton.RightButton, start_state=start_state)

    # Gestures
    PinchPanGestureHandler(filter, start_state=start_state)

    # Other events
    MoveHandler(filter, start_state=start_state)
    MoveHandler(
        filter, start_state=start_state, mods=QC.Qt.KeyboardModifier.ShiftModifier
    )
    MoveHandler(
        filter, start_state=start_state, mods=QC.Qt.KeyboardModifier.AltModifier
    )
    WheelZoomHandler(
        filter, start_state=start_state, mods=QC.Qt.KeyboardModifier.ControlModifier
    )
    return start_state
