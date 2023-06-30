# -*- coding: utf-8 -*-

"""
plotpy.core.plot
-----------------------

The `plot` module provides the following features:
    * :py:class:`.plot.PlotManager`: the `plot manager` is an object to
      link `plots`, `panels` and `tools` together for designing highly
      versatile graphical user interfaces
    * :py:class:`.plot.PlotWidget`: a ready-to-use widget for curve/image
      displaying with an integrated and preconfigured `plot manager` providing
      the `item list panel` and curve/image-related `tools`
    * :py:class:`.plot.PlotDialog`: a ready-to-use dialog box for
      curve/image displaying with an integrated and preconfigured `plot manager`
      providing the `item list panel` and curve/image-related `tools`

.. seealso::

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

    Module :py:mod:`.tools`
        Module providing the `plot tools`

    Module :py:mod:`.panels`
        Module providing the `plot panels` IDs

    Module :py:mod:`.baseplot`
        Module providing the `plotpy` plotting widget base class


Class diagrams
~~~~~~~~~~~~~~

Curve-related widgets with integrated plot manager:

.. image:: /images/curve_widgets.png

Image-related widgets with integrated plot manager:

.. image:: /images/image_widgets.png

Building your own plot manager:

.. image:: /images/my_plot_manager.png


Examples
~~~~~~~~

Simple example *without* the `plot manager`:

.. literalinclude:: ../../plotpy/tests/gui/test_filtertest1.py
   :start-after: guitest:

Simple example *with* the `plot manager`:
even if this simple example does not justify the use of the `plot manager`
(this is an unnecessary complication here), it shows how to use it. In more
complex applications, using the `plot manager` allows to design highly versatile
graphical user interfaces.

.. literalinclude:: ../../plotpy/tests/gui/test_filtertest2.py
   :start-after: guitest:

Reference
~~~~~~~~~

.. autoclass:: PlotManager
   :members:
.. autoclass:: PlotWidget
   :members:
.. autoclass:: PlotDialog
   :members:
.. autoclass:: PlotWindow
   :members:

"""

from .manager import PlotManager  # pylint: disable=W0611
from .plotwidget import PlotDialog, PlotWidget, PlotWindow  # pylint: disable=W0611
