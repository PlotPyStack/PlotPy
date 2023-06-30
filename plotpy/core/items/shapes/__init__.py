# -*- coding: utf-8 -*-

"""
plotpy.core.items.shapes
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

>>> from plotpy.core.items.shapes import RectangleShape
>>> from plotpy.core.styles import ShapeParam
>>> param = ShapeParam()
>>> param.title = 'My rectangle'
>>> rect_item = RectangleShape(0., 2., 4., 0., param)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.core.builder import make
>>> rect_item = make.rectangle(0., 2., 4., 0., title='My rectangle')

Reference
~~~~~~~~~

.. autoclass:: PolygonShape
   :members:
.. autoclass:: RectangleShape
   :members:
.. autoclass:: ObliqueRectangleShape
   :members:
.. autoclass:: PointShape
   :members:
.. autoclass:: SegmentShape
   :members:
.. autoclass:: EllipseShape
   :members:
.. autoclass:: Axes
   :members:
.. autoclass:: XRangeSelection
   :members:
.. autoclass:: Marker
   :members:
"""

# pylint: disable=W0611
from plotpy.core.items.shapes.axis import Axes
from plotpy.core.items.shapes.base import AbstractShape
from plotpy.core.items.shapes.ellipse import EllipseShape
from plotpy.core.items.shapes.marker import Marker
from plotpy.core.items.shapes.point import PointShape
from plotpy.core.items.shapes.polygon import PolygonShape
from plotpy.core.items.shapes.range import XRangeSelection
from plotpy.core.items.shapes.rectangle import ObliqueRectangleShape, RectangleShape
from plotpy.core.items.shapes.segment import SegmentShape
