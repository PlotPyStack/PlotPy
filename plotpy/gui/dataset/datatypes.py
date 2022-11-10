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
plotpy.gui.dataset.datatypes
============================

The ``plotpy.gui.dataset.datatypes`` module contains implementation for
DataSets (DataSet, DataSetGroup, ...) and related objects (ItemProperty,
ValueProp, ...).
"""

# pylint: disable-msg=W0622
# pylint: disable-msg=W0212

import collections
import re
import sys
import traceback

from plotpy.core.dataset.datatypes import DataSet, DataSetGroup, GetAttrProp
from plotpy.gui.dataset.qtwidgets import (
    DataSetEditDialog,
    DataSetGroupEditDialog,
    DataSetShowDialog,
)

DEBUG_DESERIALIZE = False
FMT_GROUPS = re.compile(r"(?<!%)%\((\w+)\)")


class DataSetGui(DataSet):
    """
    Construct a DataSet object is a set of DataItem objects
        * title [string]
        * comment [string]: text shown on the top of the first data item
        * icon [QIcon or string]: icon show on the button (optional)
          (string: icon filename as in plotpy image search paths)
    """

    def __init__(self, title=None, comment=None, icon=""):
        super().__init__(title, comment, icon)

    def edit(self, parent=None, apply=None, size=None, additionnal_widget=None):
        """
        Open a dialog box to edit data set
            * parent: parent widget (default is None, meaning no parent)
            * apply: apply callback (default is None)
            * size: dialog size (QSize object or integer tuple (width, height))
            * additionnal_widget: widget affiché en premier dans la boite de dialogue
        """
        win = DataSetEditDialog(
            self, icon=self.get_icon(), parent=parent, apply=apply, size=size
        )
        if additionnal_widget:
            win.layout.insertWidget(0,additionnal_widget)
        return win.exec_()

    def view(self, parent=None, size=None):
        """
        Open a dialog box to view data set
            * parent: parent widget (default is None, meaning no parent)
            * size: dialog size (QSize object or integer tuple (width, height))
        """
        win = DataSetShowDialog(self, icon=self.get_icon(), parent=parent, size=size)
        return win.exec_()


class DataSetGroupGui(DataSetGroup):
    """
    Construct a DataSetGroup object, used to group several datasets together
        * datasets [list of DataSet objects]
        * title [string]
        * icon [QIcon or string]: icon show on the button (optional)
          (string: icon filename as in plotpy image search paths)

    This class tries to mimics the DataSet interface.

    The GUI should represent it as a notebook with one page for each
    contained dataset.
    """

    def __init__(self, datasets, title=None, icon=""):
        super().__init__(datasets, title, icon)

    def edit(self, parent=None, apply=None):
        """
        Open a dialog box to edit data set
        """
        win = DataSetGroupEditDialog(
            self, icon=self.get_icon(), parent=parent, apply=apply
        )
        return win.exec_()

class ActivableDataSetGui(DataSetGui):
    """
    An ActivableDataSetGui instance must have an "enable" class attribute which
    will set the active state of the dataset instance
    (see example in: tests/activable_dataset.py)
    """

    _ro = True  # default *instance* attribute value
    _active = True
    _ro_prop = GetAttrProp("_ro")
    _active_prop = GetAttrProp("_active")

    def __init__(self, title=None, comment=None, icon=""):
        DataSetGui.__init__(self, title, comment, icon)

    #        self.set_readonly()

    @classmethod
    def active_setup(klass):
        """
        This class method must be called after the child class definition
        in order to setup the dataset active state
        """
        klass.set_global_prop("display", active=klass._active_prop)
        klass.enable.set_prop(
            "display", active=True, hide=klass._ro_prop, store=klass._active_prop
        )

    def set_readonly(self):
        """
        The dataset is now in read-only mode, i.e. all data items are disabled
        """
        self._ro = True
        self._active = self.enable

    def set_writeable(self):
        """
        The dataset is now in read/write mode, i.e. all data items are enabled
        """
        self._ro = False
        self._active = self.enable

