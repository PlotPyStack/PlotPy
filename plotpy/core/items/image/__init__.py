# -*- coding: utf-8 -*-

"""
plotpy.core.items.image
--------------------------

The `image` module provides image-related objects and functions:

    * :py:class:`.image.ImageItem`: simple images
    * :py:class:`.image.TrImageItem`: images supporting arbitrary
      affine transform
    * :py:class:`.image.XYImageItem`: images with non-linear X/Y axes
    * :py:class:`.image.Histogram2DItem`: 2D histogram
    * :py:class:`.image.ImageFilterItem`: rectangular filtering area
      that may be resized and moved onto the processed image
    * :py:func:`.image.assemble_imageitems`
    * :py:func:`.image.get_plot_qrect`
    * :py:func:`.image.get_image_from_plot`

``ImageItem``, ``TrImageItem``, ``XYImageItem``, ``Histogram2DItem`` and
``ImageFilterItem`` objects are plot items (derived from QwtPlotItem) that
may be displayed on a :py:class:`.baseplot.BasePlot` plotting widget.

.. seealso::

    Module :py:mod:`plotpy.core.items.curve`
        Module providing curve-related plot items

    Module :py:mod:`plotpy.core.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Examples
~~~~~~~~

Create a basic image plotting widget:

    * before creating any widget, a `QApplication` must be instantiated (that
      is a `Qt` internal requirement):

>>> import guidata
>>> app = guidata.qapplication()

    * that is mostly equivalent to the following (the only difference is that
      the `plotpy` helper function also installs the `Qt` translation
      corresponding to the system locale):

>>> from PyQt5.QtWidgets import QApplication
>>> app = QApplication([])

    * now that a `QApplication` object exists, we may create the plotting
      widget:

>>> from plotpy.widgets.baseplot import BasePlot, PlotType
>>> plot = BasePlot(title="Example", type=PlotType.IMAGE)

Generate random data for testing purpose:

>>> import numpy as np
>>> data = np.random.rand(100, 100)

Create a simple image item:

    * from the associated plot item class (e.g. `XYImageItem` to create
      an image with non-linear X/Y axes): the item properties are then
      assigned by creating the appropriate style parameters object
      (e.g. :py:class:`.styles.ImageParam`)

>>> from plotpy.core.items.image import ImageItem
>>> from plotpy.core.styles import ImageParam
>>> param = ImageParam()
>>> param.label = 'My image'
>>> image = ImageItem(param)
>>> image.set_data(data)

    * or using the `plot item builder` (see :py:func:`.builder.make`):

>>> from plotpy.core.builder import make
>>> image = make.image(data, title='My image')

Attach the image to the plotting widget:

>>> plot.add_item(image)

Display the plotting widget:

>>> plot.show()
>>> app.exec()

Reference
~~~~~~~~~

.. autoclass:: BaseImageItem
   :members:
.. autoclass:: RawImageItem
   :members:
.. autoclass:: ImageItem
   :members:
.. autoclass: TransformImageMixin
.. autoclass:: TrImageItem
   :members:
.. autoclass:: XYImageItem
   :members:
.. autoclass:: RGBImageItem
   :members:
.. autoclass:: MaskedImageItem
   :members:
.. autoclass:: MaskedXYImageItem
   :members:
.. autoclass:: ImageFilterItem
   :members:
.. autoclass:: XYImageFilterItem
   :members:
.. autoclass:: Histogram2DItem
   :members:
.. autoclass:: QuadGridItem
   :members:

.. autofunction:: assemble_imageitems
.. autofunction:: get_plot_qrect
.. autofunction:: get_image_from_plot
"""

# pylint: disable=unused-import
from plotpy.core.items.image.base import BaseImageItem, RawImageItem
from plotpy.core.items.image.filter import ImageFilterItem, XYImageFilterItem
from plotpy.core.items.image.image_items import ImageItem, RGBImageItem, XYImageItem
from plotpy.core.items.image.masked import MaskedImageItem, MaskedXYImageItem
from plotpy.core.items.image.masked_area import MaskedArea
from plotpy.core.items.image.misc import (
    Histogram2DItem,
    QuadGridItem,
    assemble_imageitems,
    compute_trimageitems_original_size,
    get_image_from_plot,
    get_image_from_qrect,
    get_image_in_shape,
    get_items_in_rectangle,
    get_plot_qrect,
)
from plotpy.core.items.image.transform import TrImageItem
