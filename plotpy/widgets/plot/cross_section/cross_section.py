# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

# pylint: disable=C0103

"""
plotpy.gui.widgets.cross_section
--------------------------------

The `cross_section` module provides cross section related objects:
    * :py:class:`.cross_section.XCrossSection`: the X-axis
      `cross-section panel`
    * :py:class:`.cross_section.YCrossSection`: the Y-axis
      `cross-section panel`
    * and other related objects which are exclusively used by the cross-section
      panels

Example
~~~~~~~

Simple cross-section demo:

.. literalinclude:: ../../../tests/gui/cross_section.py

Reference
~~~~~~~~~

.. autoclass:: XCrossSection
   :members:
   :inherited-members:
.. autoclass:: YCrossSection
   :members:
   :inherited-members:
.. autoclass:: XCrossSectionPlot
   :members:
.. autoclass:: YCrossSectionPlot
   :members:
"""

from __future__ import print_function

import warnings
import weakref

import numpy as np

from plotpy.gui.config.misc import get_icon
from plotpy.gui.utils.gui import assert_interfaces_valid
from plotpy.gui.utils.misc import add_actions, create_action
from plotpy.gui.widgets.baseplot import BasePlot, PlotType
from plotpy.gui.widgets.builder import make
from plotpy.gui.widgets.config import CONF, _
from plotpy.gui.widgets.ext_gui_lib import (
    QHBoxLayout,
    QPointF,
    QSize,
    QSizePolicy,
    QSpacerItem,
    Qt,
    QToolBar,
    QVBoxLayout,
)
from plotpy.gui.widgets.geometry import rotate, translate, vector_angle, vector_norm
from plotpy.gui.widgets.interfaces import IBasePlotItem, ICSImageItemType, IPanel
from plotpy.gui.widgets.items.curve import ErrorBarCurveItem
from plotpy.gui.widgets.items.image import (
    INTERP_LINEAR,
    LUT_MAX,
    _scale_tr,
    get_image_from_qrect,
)
from plotpy.gui.widgets.items.utils import axes_to_canvas, canvas_to_axes
from plotpy.gui.widgets.panels import ID_OCS, ID_XCS, ID_YCS, PanelWidget
from plotpy.gui.widgets.plot import PlotManager
from plotpy.gui.widgets.styles import CurveParam
from plotpy.gui.widgets.tools import ExportItemDataTool

LUT_AXIS_TITLE = _("LUT scale") + (" (0-%d)" % LUT_MAX)


assert_interfaces_valid(CrossSectionWidget)


# ===============================================================================
# Oblique cross sections
# ===============================================================================
DEBUG = False
TEMP_ITEM = None
