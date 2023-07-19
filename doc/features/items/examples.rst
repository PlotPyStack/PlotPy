Examples
--------

Curve example
^^^^^^^^^^^^^

Create a basic curve plotting widget:

* before creating any widget, a `QApplication` must be instantiated (that
  is a `Qt` internal requirement)::

    >>> import guidata
    >>> app = guidata.qapplication()

* that is mostly equivalent to the following (the only difference is that
  the :mod:`plotpy` helper function also installs the `Qt` translation
  corresponding to the system locale)::

    >>> from qtpy.QtWidgets import QApplication
    >>> app = QApplication([])

* now that a `QApplication` object exists, we may create the plotting
  widget::

    >>> from plotpy.core.plot.base import BasePlot, PlotType
    >>> plot = BasePlot(title="Example", xlabel="X", ylabel="Y", type=PlotType.CURVE)

Create a curve item:

* from the associated plot item class (e.g. `ErrorBarCurveItem` to create
  a curve with error bars): the item properties are then assigned by creating
  the appropriate style parameters object (e.g. :py:class:`.styles.ErrorBarParam`)::

    >>> from plotpy.core.items.curve import CurveItem
    >>> from plotpy.core.styles import CurveParam
    >>> param = CurveParam()
    >>> param.label = 'My curve'
    >>> curve = CurveItem(param)
    >>> curve.set_data(x, y)

* or using the `plot item builder` (see :py:attr:`plotpy.core.builder.make`)::

    >>> from plotpy.core.builder import make
    >>> curve = make.curve(x, y, title='My curve')

Attach the curve to the plotting widget::

    >>> plot.add_item(curve)

Display the plotting widget::

    >>> plot.show()
    >>> app.exec()

Image example
^^^^^^^^^^^^^

Create a basic image plotting widget (see also `Curve example`_)::

    >>> import guidata
    >>> app = guidata.qapplication()
    >>> from plotpy.widgets.baseplot import BasePlot, PlotType
    >>> plot = BasePlot(title="Example", type=PlotType.IMAGE)

Generate random data for testing purpose::

    >>> import numpy as np
    >>> data = np.random.rand(100, 100)

Create a simple image item:

* from the associated plot item class (e.g. `XYImageItem` to create
  an image with non-linear X/Y axes): the item properties are then
  assigned by creating the appropriate style parameters object
  (e.g. :py:class:`.styles.ImageParam`)::

    >>> from plotpy.core.items.image import ImageItem
    >>> from plotpy.core.styles import ImageParam
    >>> param = ImageParam()
    >>> param.label = 'My image'
    >>> image = ImageItem(param)
    >>> image.set_data(data)

* or using the `plot item builder` (see :py:attr:`plotpy.core.builder.make`)::

    >>> from plotpy.core.builder import make
    >>> image = make.image(data, title='My image')

Final steps (see also `Curve example`_)::

    >>> plot.add_item(image)
    >>> plot.show()
    >>> app.exec()

Shape example
^^^^^^^^^^^^^

A shape may be created:

* from the associated plot item class (e.g. `RectangleShape` to create a
  rectangle): the item properties are then assigned by creating the
  appropriate style parameters object (:py:class:`.styles.ShapeParam`)::

    >>> from plotpy.core.items.shapes import RectangleShape
    >>> from plotpy.core.styles import ShapeParam
    >>> param = ShapeParam()
    >>> param.title = 'My rectangle'
    >>> rect_item = RectangleShape(0., 2., 4., 0., param)

* or using the `plot item builder` (see :py:attr:`plotpy.core.builder.make`)::

    >>> from plotpy.core.builder import make
    >>> rect_item = make.rectangle(0., 2., 4., 0., title='My rectangle')

Annotation example
^^^^^^^^^^^^^^^^^^

An annotated shape may be created:

* from the associated plot item class (e.g. `AnnotatedCircle` to
  create an annotated circle): the item properties are then assigned
  by creating the appropriate style parameters object
  (:py:class:`.styles.AnnotationParam`)::

    >>> from plotpy.core.items.annotations import AnnotatedCircle
    >>> from plotpy.core.styles import AnnotationParam
    >>> param = AnnotationParam()
    >>> param.title = 'My circle'
    >>> circle_item = AnnotatedCircle(0., 2., 4., 0., param)

* or using the `plot item builder` (see :py:attr:`plotpy.core.builder.make`)::

    >>> from plotpy.core.builder import make
    >>> circle_item = make.annotated_circle(0., 2., 4., 0., title='My circle')
