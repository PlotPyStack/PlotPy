# -*- coding: utf-8 -*-

"""
plotpy.widgets.cross_section
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

.. literalinclude:: ../../plotpy/tests/gui/cross_section.py

Reference
~~~~~~~~~

.. autoclass:: XCrossSection
   :members:
.. autoclass:: YCrossSection
   :members:
.. autoclass:: XCrossSectionPlot
   :members:
.. autoclass:: YCrossSectionPlot
   :members:
"""

from .csplot import XCrossSectionPlot, YCrossSectionPlot  # pylint: disable=W0611
from .cswidget import XCrossSection, YCrossSection  # pylint: disable=W0611
