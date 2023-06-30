# -*- coding: utf-8 -*-

"""
plotpy.core.items.curve
--------------------------

The `curve` module provides curve-related objects:
    * :py:class:`.curve.CurveItem`: a curve plot item
    * :py:class:`.curve.ErrorBarCurveItem`: a curve plot item with
      error bars

``CurveItem`` object is a plot items (derived from QwtPlotItem) that may be displayed
on a 2D plotting widget like :py:class:`.baseplot.BasePlot`.

.. seealso::

    Module :py:mod:`plotpy.core.items.image`
        Module providing image-related plot items

    Module :py:mod:`plotpy.core.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Examples
~~~~~~~~

Create a basic curve plotting widget:
    * before creating any widget, a `QApplication` must be instantiated (that
      is a `Qt` internal requirement):

>>> import guidata
>>> app = guidata.qapplication()

    * that is mostly equivalent to the following (the only difference is that
      the `plotpy` helper function also installs the `Qt` translation
      corresponding to the system locale):

>>> from qtpy.QtWidgets import QApplication
>>> app = QApplication([])

    * now that a `QApplication` object exists, we may create the plotting
      widget:

>>> from plotpy.core.plot.base import BasePlot, PlotType
>>> plot = BasePlot(title="Example", xlabel="X", ylabel="Y", type=PlotType.CURVE)

Create a curve item:
    * from the associated plot item class (e.g. `ErrorBarCurveItem` to
      create a curve with error bars): the item properties are then assigned
      by creating the appropriate style parameters object
      (e.g. :py:class:`.styles.ErrorBarParam`)

>>> from plotpy.core.items.curve import CurveItem
>>> from plotpy.core.styles import CurveParam
>>> param = CurveParam()
>>> param.label = 'My curve'
>>> curve = CurveItem(param)
>>> curve.set_data(x, y)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.core.builder import make
>>> curve = make.curve(x, y, title='My curve')

Attach the curve to the plotting widget:

>>> plot.add_item(curve)

Display the plotting widget:

>>> plot.show()
>>> app.exec()

Reference
~~~~~~~~~

.. autoclass:: CurveItem
   :members:
.. autoclass:: ErrorBarCurveItem
   :members:
"""

from plotpy.core.items.curve.base import CurveItem  # pylint: disable=W0611
from plotpy.core.items.curve.errorbar import ErrorBarCurveItem  # pylint: disable=W0611
