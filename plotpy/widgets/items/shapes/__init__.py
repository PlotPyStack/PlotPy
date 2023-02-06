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
plotpy.widgets.items.shapes
---------------------------

The `shapes` module provides geometrical shapes:
    * :py:class:`.shapes.PolygonShape`
    * :py:class:`.shapes.RectangleShape`
    * :py:class:`.shapes.ObliqueRectangleShape`
    * :py:class:`.shapes.PointShape`
    * :py:class:`.shapes.SegmentShape`
    * :py:class:`.shapes.EllipseShape`
    * :py:class:`.shapes.Axes`
    * :py:class:`.shapes.XRangeSelection`

A shape is a plot item (derived from QwtPlotItem) that may be displayed
on a 2D plotting widget like :py:class:`.baseplot.BasePlot`.

.. seealso:: module :py:mod:`.annotations`

Examples
~~~~~~~~

A shape may be created:
    * from the associated plot item class (e.g. `RectangleShape` to create a
      rectangle): the item properties are then assigned by creating the
      appropriate style parameters object
      (:py:class:`.styles.ShapeParam`)

>>> from plotpy.gui.widgets.items.shapes import RectangleShape
>>> from plotpy.gui.widgets.styles import ShapeParam
>>> param = ShapeParam()
>>> param.title = 'My rectangle'
>>> rect_item = RectangleShape(0., 2., 4., 0., param)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.gui.widgets.builder import make
>>> rect_item = make.rectangle(0., 2., 4., 0., title='My rectangle')

Reference
~~~~~~~~~

.. autoclass:: PolygonShape
   :members:
   :inherited-members:
.. autoclass:: RectangleShape
   :members:
   :inherited-members:
.. autoclass:: ObliqueRectangleShape
   :members:
   :inherited-members:
.. autoclass:: PointShape
   :members:
   :inherited-members:
.. autoclass:: SegmentShape
   :members:
   :inherited-members:
.. autoclass:: EllipseShape
   :members:
   :inherited-members:
.. autoclass:: Axes
   :members:
   :inherited-members:
.. autoclass:: XRangeSelection
   :members:
   :inherited-members:
.. autoclass:: Marker
   :members:
   :inherited-members:
"""
from plotpy.widgets.items.shapes.axis import Axes
from plotpy.widgets.items.shapes.base import AbstractShape
from plotpy.widgets.items.shapes.ellipse import EllipseShape
from plotpy.widgets.items.shapes.marker import Marker
from plotpy.widgets.items.shapes.point import PointShape
from plotpy.widgets.items.shapes.polygon import PolygonShape
from plotpy.widgets.items.shapes.range import XRangeSelection
from plotpy.widgets.items.shapes.rectangle import ObliqueRectangleShape, RectangleShape
from plotpy.widgets.items.shapes.segment import SegmentShape
