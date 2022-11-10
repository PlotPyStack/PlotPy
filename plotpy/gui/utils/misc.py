# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
plotpy.gui.utils.misc
---------------------

The ``plotpy.gui.utils.misc`` module provides helper functions for developing
easily Qt-based graphical user interfaces.
"""


from collections import namedtuple

from plotpy.core.config.config import CONF
from plotpy.gui.config.misc import get_icon
from plotpy.gui.widgets.ext_gui_lib import (
    QAction,
    QColor,
    QGroupBox,
    QIcon,
    QKeyEvent,
    QKeySequence,
    QMenu,
    QPushButton,
    QShortcut,
    Qt,
    QToolButton,
)


def text_to_qcolor(text):
    """Create a QColor from specified string"""
    color = QColor()
    if not isinstance(text, str):  # testing for QString (PyQt API#1)
        text = str(text)
    if text.startswith("#") and len(text) == 7:
        correct = "#0123456789abcdef"
        for char in text:
            if char.lower() not in correct:
                return color
    elif text not in list(QColor.colorNames()):
        return color
    color.setNamedColor(text)
    return color


def create_action(
    parent,
    title,
    triggered=None,
    toggled=None,
    shortcut=None,
    icon=None,
    tip=None,
    checkable=None,
    context=Qt.WindowShortcut,
    enabled=None,
):
    """
    Create a new QAction
    """

    if isinstance(title, bytes):
        title = str(title, "utf8")

    action = QAction(title, parent)
    if triggered:
        if checkable:
            action.triggered.connect(triggered)
        else:
            action.triggered.connect(lambda checked=False: triggered())
    if checkable is not None:
        # Action may be checkable even if the toggled signal is not connected
        action.setCheckable(checkable)
    if toggled:
        action.toggled.connect(toggled)
        action.setCheckable(True)
    if icon is not None:
        assert isinstance(icon, QIcon)
        action.setIcon(icon)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if enabled is not None:
        action.setEnabled(enabled)
    action.setShortcutContext(context)
    return action


def create_toolbutton(
    parent,
    icon=None,
    text=None,
    triggered=None,
    tip=None,
    toggled=None,
    shortcut=None,
    autoraise=True,
    enabled=None,
):
    """Create a QToolButton"""
    if autoraise:
        button = QToolButton(parent)
    else:
        button = QPushButton(parent)
    if text is not None:
        button.setText(text)
    if icon is not None:
        if isinstance(icon, str):
            icon = get_icon(icon)
        button.setIcon(icon)
    if text is not None or tip is not None:
        button.setToolTip(text if tip is None else tip)
    if autoraise:
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setAutoRaise(True)
    if triggered is not None:
        button.clicked.connect(lambda checked=False: triggered())
    if toggled is not None:
        button.toggled.connect(toggled)
        button.setCheckable(True)
    if shortcut is not None:
        button.setShortcut(shortcut)
    if enabled is not None:
        button.setEnabled(enabled)
    return button


def create_groupbox(
    parent, title=None, toggled=None, checked=None, flat=False, layout=None
):
    """Create a QGroupBox"""
    if title is None:
        group = QGroupBox(parent)
    else:
        group = QGroupBox(title, parent)
    group.setFlat(flat)
    if toggled is not None:
        group.setCheckable(True)
        if checked is not None:
            group.setChecked(checked)
        group.toggled.connect(toggled)
    if layout is not None:
        group.setLayout(layout)
    return group


def keybinding(attr):
    """Return keybinding"""
    ks = getattr(QKeySequence, attr)
    return QKeySequence.keyBindings(ks)[0].toString()


def add_separator(target):
    """Add separator to target only if last action is not a separator"""
    target_actions = list(target.actions())
    if target_actions:
        if not target_actions[-1].isSeparator():
            target.addSeparator()


def add_actions(target, actions):
    """
    Add actions (list of QAction instances) to target (menu, toolbar)
    """
    for action in actions:
        if isinstance(action, QAction):
            target.addAction(action)
        elif isinstance(action, QMenu):
            target.addMenu(action)
        elif isinstance(action, QToolButton) or \
             isinstance(action,  QPushButton):
            target.addWidget(action)
        elif action is None:
            add_separator(target)


Shortcut = namedtuple("Shortcut", "data")


def config_shortcut(action, context, name, parent):
    """
    Create a Shortcut namedtuple for a widget

    The data contained in this tuple will be registered in
    our shortcuts preferences page
    """
    keystr = get_shortcut(context, name)
    qsc = QShortcut(QKeySequence(keystr), parent, action)
    qsc.setContext(Qt.WidgetWithChildrenShortcut)
    sc = Shortcut(data=(qsc, context, name))
    return sc


def get_shortcut(context, name):
    """Get keyboard shortcut (key sequence string)"""
    return CONF.get("shortcuts", "%s/%s" % (context, name))


def tuple2keyevent(past_event):
    """Convert tuple into a QKeyEvent instance"""
    return QKeyEvent(*past_event)


def restore_keyevent(event):
    """

    :param event:
    :return:
    """
    if isinstance(event, tuple):
        _, key, modifiers, text, _, _ = event
        event = tuple2keyevent(event)
    else:
        text = event.text()
        modifiers = event.modifiers()
        key = event.key()
    ctrl = modifiers & Qt.ControlModifier
    shift = modifiers & Qt.ShiftModifier
    return event, text, key, ctrl, shift
