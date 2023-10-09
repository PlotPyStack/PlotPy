Overview
--------

The :ref:`items` module provides the classes for the plot items.
Plot items are the graphical objects that are displayed on a 2D plotting widget
like :py:class:`.BasePlot`.
Items may be created either by using the appropriate class constructor or by
using the :obj:`.builder.make` factory object.

.. seealso::

    :ref:`builder`
        Module providing the :obj:`.builder.make` factory object
        which can be used to create plot items

    :ref:`plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

Curves
^^^^^^

The following curve items are available:

* :py:class:`.CurveItem`: a curve plot item
* :py:class:`.ErrorBarCurveItem`: a curve plot item with error bars

Images
^^^^^^

The following image items are available:

* :py:class:`.ImageItem`: simple images
* :py:class:`.TrImageItem`: images supporting arbitrary
  affine transform
* :py:class:`.XYImageItem`: images with non-linear X/Y axes
* :py:class:`.Histogram2DItem`: 2D histogram
* :py:class:`.ImageFilterItem`: rectangular filtering
  area that may be resized and moved onto the processed image
* :py:func:`.assemble_imageitems`
* :py:func:`.get_plot_qrect`
* :py:func:`.get_image_from_plot`

Grid
^^^^

A single grid item is available: :py:class:`.GridItem`.

Shapes
^^^^^^

The following shape items are available:

* :py:class:`.PolygonShape`
* :py:class:`.RectangleShape`
* :py:class:`.ObliqueRectangleShape`
* :py:class:`.PointShape`
* :py:class:`.SegmentShape`
* :py:class:`.EllipseShape`
* :py:class:`.Axes`
* :py:class:`.XRangeSelection`
* :py:class:`.Marker`
* :py:class:`.RectangleSVGShape`
* :py:class:`.SquareSVGShape`
* :py:class:`.CircleSVGShape`

Annotations
^^^^^^^^^^^

The following annotation items are available:

* :py:class:`.annotations.AnnotatedPoint`
* :py:class:`.annotations.AnnotatedSegment`
* :py:class:`.annotations.AnnotatedRectangle`
* :py:class:`.annotations.AnnotatedObliqueRectangle`
* :py:class:`.annotations.AnnotatedEllipse`
* :py:class:`.annotations.AnnotatedCircle`

Labels
^^^^^^

The following label items are available:

* :py:class:`.label.LabelItem`
* :py:class:`.label.LegendBoxItem`
* :py:class:`.label.SelectedLegendBoxItem`
* :py:class:`.label.RangeComputation`
* :py:class:`.label.RangeComputation2d`
* :py:class:`.label.DataInfoLabel`
