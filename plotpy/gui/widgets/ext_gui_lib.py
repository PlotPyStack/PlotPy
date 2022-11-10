# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.gui.widgets.ext_gui_lib
------------------------------

The purpose of this transitional package is to regroup all the references to
the ``PythonQwt`` library (`qwt` package).

No other ``plotpy`` module should import ``qwt`` or use any of its
interfaces directly.
"""

# pylint: disable=unused-import

from PyQt5 import uic
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty as Property
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtDesigner import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qwt import *
from qwt import __version__ as QWT_VERSION
