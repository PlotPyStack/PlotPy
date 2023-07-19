Reference
---------

Base classes
^^^^^^^^^^^^

.. autoclass:: plotpy.core.interfaces.common.IItemType
.. autoclass:: plotpy.core.interfaces.common.IBasePlotItem
.. autoclass:: plotpy.core.interfaces.common.IColormapImageItemType

Curves
^^^^^^

.. autoclass:: plotpy.core.items.CurveItem
   :members:
.. autoclass:: plotpy.core.items.ErrorBarCurveItem
   :members:

Images
^^^^^^

.. autoclass:: plotpy.core.items.BaseImageItem
   :members:
.. autoclass:: plotpy.core.items.RawImageItem
   :members:
.. autoclass:: plotpy.core.items.ImageItem
   :members:
.. autoclass:: plotpy.core.items.TrImageItem
   :members:
.. autoclass:: plotpy.core.items.XYImageItem
   :members:
.. autoclass:: plotpy.core.items.RGBImageItem
   :members:
.. autoclass:: plotpy.core.items.MaskedImageItem
   :members:
.. autoclass:: plotpy.core.items.MaskedXYImageItem
   :members:
.. autoclass:: plotpy.core.items.ImageFilterItem
   :members:
.. autoclass:: plotpy.core.items.XYImageFilterItem
   :members:
.. autoclass:: plotpy.core.items.QuadGridItem
   :members:

.. autofunction:: plotpy.core.items.assemble_imageitems
.. autofunction:: plotpy.core.items.get_plot_qrect
.. autofunction:: plotpy.core.items.get_image_from_plot

Histograms
^^^^^^^^^^

.. autoclass:: plotpy.core.items.HistogramItem
   :members:
.. autoclass:: plotpy.core.items.Histogram2DItem
    :members:

Grid
^^^^

.. autoclass:: plotpy.core.items.GridItem
   :members:

Shapes
^^^^^^

.. autoclass:: plotpy.core.items.shapes.PolygonShape
   :members:
.. autoclass:: plotpy.core.items.shapes.RectangleShape
   :members:
.. autoclass:: plotpy.core.items.shapes.ObliqueRectangleShape
   :members:
.. autoclass:: plotpy.core.items.shapes.PointShape
   :members:
.. autoclass:: plotpy.core.items.shapes.SegmentShape
   :members:
.. autoclass:: plotpy.core.items.shapes.EllipseShape
   :members:
.. autoclass:: plotpy.core.items.shapes.Axes
   :members:
.. autoclass:: plotpy.core.items.shapes.XRangeSelection
   :members:
.. autoclass:: plotpy.core.items.shapes.Marker
   :members:

Annotations
^^^^^^^^^^^

.. autoclass:: plotpy.core.items.annotations.AnnotatedPoint
   :members:
.. autoclass:: plotpy.core.items.annotations.AnnotatedSegment
   :members:
.. autoclass:: plotpy.core.items.annotations.AnnotatedRectangle
   :members:
.. autoclass:: plotpy.core.items.annotations.AnnotatedObliqueRectangle
   :members:
.. autoclass:: plotpy.core.items.annotations.AnnotatedEllipse
   :members:
.. autoclass:: plotpy.core.items.annotations.AnnotatedCircle
   :members:

Labels
^^^^^^

.. autoclass:: plotpy.core.items.LabelItem
   :members:
.. autoclass:: plotpy.core.items.LegendBoxItem
   :members:
.. autoclass:: plotpy.core.items.SelectedLegendBoxItem
   :members:
.. autoclass:: plotpy.core.items.RangeComputation
   :members:
.. autoclass:: plotpy.core.items.RangeComputation2d
   :members:
.. autoclass:: plotpy.core.items.DataInfoLabel
   :members:
.. autoclass:: plotpy.core.items.ObjectInfo
   :members:
