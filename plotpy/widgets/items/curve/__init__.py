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

"""
plotpy.widgets.items.curve
--------------------------

The `curve` module provides curve-related objects:
    * :py:class:`.curve.CurveItem`: a curve plot item
    * :py:class:`.curve.ErrorBarCurveItem`: a curve plot item with
      error bars

``CurveItem`` object is a plot items (derived from QwtPlotItem) that may be displayed
on a 2D plotting widget like :py:class:`.baseplot.BasePlot`.

.. seealso::

    Module :py:mod:`plotpy.gui.widgets.items.image`
        Module providing image-related plot items

    Module :py:mod:`plotpy.gui.widgets.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Examples
~~~~~~~~

Create a basic curve plotting widget:
    * before creating any widget, a `QApplication` must be instantiated (that
      is a `Qt` internal requirement):

>>> import plotpy.widgets
>>> app = plotpy.widgets.qapplication()

    * that is mostly equivalent to the following (the only difference is that
      the `plotpy` helper function also installs the `Qt` translation
      corresponding to the system locale):

>>> from qtpy.QtWidgets import QApplication
>>> app = QApplication([])

    * now that a `QApplication` object exists, we may create the plotting
      widget:

>>> from plotpy.widgets.plot.base import BasePlot, PlotType
>>> plot = BasePlot(title="Example", xlabel="X", ylabel="Y", type=PlotType.CURVE)

Create a curve item:
    * from the associated plot item class (e.g. `ErrorBarCurveItem` to
      create a curve with error bars): the item properties are then assigned
      by creating the appropriate style parameters object
      (e.g. :py:class:`.styles.ErrorBarParam`)

>>> from plotpy.gui.widgets.items.curve import CurveItem
>>> from plotpy.gui.widgets.styles import CurveParam
>>> param = CurveParam()
>>> param.label = 'My curve'
>>> curve = CurveItem(param)
>>> curve.set_data(x, y)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.gui.widgets.builder import make
>>> curve = make.curve(x, y, title='My curve')

Attach the curve to the plotting widget:

>>> plot.add_item(curve)

Display the plotting widget:

>>> plot.show()
>>> app.exec_()

Reference
~~~~~~~~~

.. autoclass:: CurveItem
   :members:
   :inherited-members:
.. autoclass:: ErrorBarCurveItem
   :members:
   :inherited-members:
"""
from plotpy.widgets.items.curve.base import CurveItem
from plotpy.widgets.items.curve.errorbar import ErrorBarCurveItem
