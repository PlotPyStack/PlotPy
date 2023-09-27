# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Base features
^^^^^^^^^^^^^

The panels base module provides :py:class:`.PanelWidget` (the `panel` widget
class from which all panels must derived from) and identifiers for each kind
of panel.

.. autodata:: ID_ITEMLIST
.. autodata:: ID_CONTRAST
.. autodata:: ID_XCS
.. autodata:: ID_YCS
.. autodata:: ID_OCS

.. autoclass:: PanelWidget
    :members:
"""

from guidata.configtools import get_icon
from guidata.widgets.dockable import DockableWidget
from qtpy import QtCore as QC

# ===============================================================================
# Panel IDs
# ===============================================================================

#: ID of the `item list` panel
ID_ITEMLIST = "itemlist"

#: ID of the `contrast adjustment` panel
ID_CONTRAST = "contrast"

#: ID of the `X-axis cross section` panel
ID_XCS = "x_cross_section"

#: ID of the `Y-axis cross section` panel
ID_YCS = "y_cross_section"

#: ID of the `oblique averaged cross section` panel
ID_OCS = "oblique_cross_section"


# ===============================================================================
# Base Panel Widget class
# ===============================================================================
class PanelWidget(DockableWidget):
    """Panel Widget base class"""

    PANEL_ID = None  # string
    PANEL_TITLE = None  # string
    PANEL_ICON = None  # string

    #: Signal emitted by PanelWidget when its visibility has changed
    #:
    #: Args:
    #:     enable (bool): True if the panel is visible
    SIG_VISIBILITY_CHANGED = QC.Signal(bool)

    def __init__(self, parent=None):
        super(PanelWidget, self).__init__(parent)
        assert self.PANEL_ID is not None
        if self.PANEL_TITLE is not None:
            self.setWindowTitle(self.PANEL_TITLE)
        if self.PANEL_ICON is not None:
            self.setWindowIcon(get_icon(self.PANEL_ICON))

    def showEvent(self, event):
        """

        :param event:
        """
        DockableWidget.showEvent(self, event)
        if self.dockwidget is None:
            self.SIG_VISIBILITY_CHANGED.emit(True)

    def hideEvent(self, event):
        """

        :param event:
        """
        DockableWidget.hideEvent(self, event)
        if self.dockwidget is None:
            self.SIG_VISIBILITY_CHANGED.emit(False)

    def visibility_changed(self, enable):
        """DockWidget visibility has changed"""
        DockableWidget.visibility_changed(self, enable)
        # For compatibility with the plotpy.panels.PanelWidget interface:
        self.SIG_VISIBILITY_CHANGED.emit(self._isvisible)
