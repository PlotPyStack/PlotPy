Reference
---------

Base classes
^^^^^^^^^^^^

.. autoclass:: plotpy.interfaces.IItemType
.. autoclass:: plotpy.interfaces.IBasePlotItem
.. autoclass:: plotpy.interfaces.IColormapImageItemType

Curves
^^^^^^

.. autoclass:: plotpy.items.CurveItem
   :members:
.. autoclass:: plotpy.items.ErrorBarCurveItem
   :members:

Images
^^^^^^

.. autoclass:: plotpy.items.BaseImageItem
   :members:
.. autoclass:: plotpy.items.RawImageItem
   :members:
.. autoclass:: plotpy.items.ImageItem
   :members:
.. autoclass:: plotpy.items.TrImageItem
   :members:
.. autoclass:: plotpy.items.XYImageItem
   :members:
.. autoclass:: plotpy.items.RGBImageItem
   :members:
.. autoclass:: plotpy.items.MaskedArea
   :members:
.. autoclass:: plotpy.items.MaskedImageItem
   :members:
.. autoclass:: plotpy.items.MaskedXYImageItem
   :members:
.. autoclass:: plotpy.items.ImageFilterItem
   :members:
.. autoclass:: plotpy.items.XYImageFilterItem
   :members:
.. autoclass:: plotpy.items.QuadGridItem
   :members:

.. autofunction:: plotpy.items.assemble_imageitems
.. autofunction:: plotpy.items.get_plot_qrect
.. autofunction:: plotpy.items.get_image_from_plot

Contours
^^^^^^^^

.. autoclass:: plotpy.items.ContourItem
   :members:

.. autoclass:: plotpy.items.contour.ContourLine
   :members:

.. autofunction:: plotpy.items.contour.compute_contours

.. autofunction:: plotpy.items.create_contour_items

Histograms
^^^^^^^^^^

.. autoclass:: plotpy.items.HistogramItem
   :members:
.. autoclass:: plotpy.items.Histogram2DItem
    :members:

Grid
^^^^

.. autoclass:: plotpy.items.GridItem
   :members:

Shapes
^^^^^^

.. autoclass:: plotpy.items.PolygonShape
   :members:
.. autoclass:: plotpy.items.RectangleShape
   :members:
.. autoclass:: plotpy.items.ObliqueRectangleShape
   :members:
.. autoclass:: plotpy.items.PointShape
   :members:
.. autoclass:: plotpy.items.SegmentShape
   :members:
.. autoclass:: plotpy.items.EllipseShape
   :members:
.. autoclass:: plotpy.items.Axes
   :members:
.. autoclass:: plotpy.items.XRangeSelection
   :members:
.. autoclass:: plotpy.items.Marker
   :members:

Annotations
^^^^^^^^^^^

.. autoclass:: plotpy.items.AnnotatedShape
   :members:
.. autoclass:: plotpy.items.AnnotatedPoint
   :members:
.. autoclass:: plotpy.items.AnnotatedSegment
   :members:
.. autoclass:: plotpy.items.AnnotatedRectangle
   :members:
.. autoclass:: plotpy.items.AnnotatedObliqueRectangle
   :members:
.. autoclass:: plotpy.items.AnnotatedEllipse
   :members:
.. autoclass:: plotpy.items.AnnotatedCircle
   :members:

Labels
^^^^^^

.. autoclass:: plotpy.items.LabelItem
   :members:
.. autoclass:: plotpy.items.LegendBoxItem
   :members:
.. autoclass:: plotpy.items.SelectedLegendBoxItem
   :members:
.. autoclass:: plotpy.items.RangeComputation
   :members:
.. autoclass:: plotpy.items.RangeComputation2d
   :members:
.. autoclass:: plotpy.items.DataInfoLabel
   :members:
.. autoclass:: plotpy.items.ObjectInfo
   :members:
