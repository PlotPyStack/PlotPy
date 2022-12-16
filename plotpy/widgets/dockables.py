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
plotpy.gui.widgets.dockables
----------------------------

The ``plotpy.gui.widgets.dockables`` module provides ready-to-use or generic widgets
for developing easily Qt-based graphical user interfaces.
"""

from qtpy import QtCore as QC
from qtpy import QtWidgets as QW


class DockableWidgetMixin(object):
    """ """

    ALLOWED_AREAS = QC.Qt.AllDockWidgetAreas
    LOCATION = QC.Qt.TopDockWidgetArea
    FEATURES = (
        QW.QDockWidget.DockWidgetClosable
        | QW.QDockWidget.DockWidgetFloatable
        | QW.QDockWidget.DockWidgetMovable
    )

    def __init__(self, parent):
        self.parent_widget = parent
        self._isvisible = False
        self.dockwidget = None
        self._allowed_areas = self.ALLOWED_AREAS
        self._location = self.LOCATION
        self._features = self.FEATURES

    def setup_dockwidget(self, location=None, features=None, allowed_areas=None):
        """

        :param location:
        :param features:
        :param allowed_areas:
        """
        assert (
            self.dockwidget is None
        ), "Dockwidget must be setup before calling 'create_dockwidget'"
        if location is not None:
            self._location = location
        if features is not None:
            self._features = features
        if allowed_areas is not None:
            self._allowed_areas = allowed_areas

    def get_focus_widget(self):
        """ """
        pass

    def create_dockwidget(self, title):
        """Add to parent QMainWindow as a dock widget"""
        dock = QW.QDockWidget(title, self.parent_widget)
        dock.setObjectName(self.__class__.__name__ + "_dw")
        dock.setAllowedAreas(self._allowed_areas)
        dock.setFeatures(self._features)
        dock.setWidget(self)
        dock.visibilityChanged.connect(self.visibility_changed)
        self.dockwidget = dock
        return (dock, self._location)

    def is_visible(self):
        """

        :return:
        """
        return self._isvisible

    def visibility_changed(self, enable):
        """DockWidget visibility has changed"""
        if enable:
            self.dockwidget.raise_()
            widget = self.get_focus_widget()
            if widget is not None:
                widget.setFocus()
        self._isvisible = enable and self.dockwidget.isVisible()


class DockableWidget(QW.QWidget, DockableWidgetMixin):
    """ """

    def __init__(self, parent):
        super(DockableWidget, self).__init__(parent, parent=parent)
