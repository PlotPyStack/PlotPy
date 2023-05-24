# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.core.panels
-------------------------

The `panels` module provides :py:class:`.panels.PanelWidget` (the
`panel` widget class from which all panels must derived from) and identifiers
for each kind of panel:

    * :py:data:`.panels.ID_ITEMLIST`: ID of the `item list` panel
    * :py:data:`.panels.ID_CONTRAST`: ID of the `contrast
      adjustment` panel
    * :py:data:`.panels.ID_XCS`: ID of the `X-axis cross section`
      panel
    * :py:data:`.panels.ID_YCS`: ID of the `Y-axis cross section`
      panel

.. seealso::

    Module :py:mod:`.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

    Module :py:mod:`.tools`
        Module providing the `plot tools`
"""

from guidata.qtwidgets import DockableWidget
from qtpy import QtCore as QC

# ===============================================================================
# Panel IDs
# ===============================================================================

#: Item list panel
ID_ITEMLIST = "itemlist"

#: Contrast adjustment panel
ID_CONTRAST = "contrast"

#: X-cross section panel
ID_XCS = "x_cross_section"

#: Y-cross section panel
ID_YCS = "y_cross_section"

#: Oblique averaged cross section panel
ID_OCS = "oblique_cross_section"


# ===============================================================================
# Base Panel Widget class
# ===============================================================================
class PanelWidget(DockableWidget):
    """Panel Widget base class"""

    PANEL_ID = None  # string
    PANEL_TITLE = None  # string
    PANEL_ICON = None  # string

    #: Signal emitted by PanelWidget when its visibility has changed (arg: bool)
    SIG_VISIBILITY_CHANGED = QC.Signal(bool)

    def __init__(self, parent=None):
        super(PanelWidget, self).__init__(parent)
        assert self.PANEL_ID is not None
        if self.PANEL_TITLE is not None:
            self.setWindowTitle(self.PANEL_TITLE)
        if self.PANEL_ICON is not None:
            from guidata.configtools import get_icon

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
        # For compatibility with the plotpy.core.panels.PanelWidget interface:
        self.SIG_VISIBILITY_CHANGED.emit(self._isvisible)
