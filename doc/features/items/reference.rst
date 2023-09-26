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

Contours
^^^^^^^^

.. autoclass:: plotpy.core.items.ContourItem
   :members:

.. autoclass:: plotpy.core.items.contour.ContourLine
   :members:

.. autofunction:: plotpy.core.items.contour.compute_contours

.. autofunction:: plotpy.core.items.create_contour_items

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

.. autoclass:: plotpy.core.items.PolygonShape
   :members:
.. autoclass:: plotpy.core.items.RectangleShape
   :members:
.. autoclass:: plotpy.core.items.ObliqueRectangleShape
   :members:
.. autoclass:: plotpy.core.items.PointShape
   :members:
.. autoclass:: plotpy.core.items.SegmentShape
   :members:
.. autoclass:: plotpy.core.items.EllipseShape
   :members:
.. autoclass:: plotpy.core.items.Axes
   :members:
.. autoclass:: plotpy.core.items.XRangeSelection
   :members:
.. autoclass:: plotpy.core.items.Marker
   :members:

Annotations
^^^^^^^^^^^

.. autoclass:: plotpy.core.items.AnnotatedPoint
   :members:
.. autoclass:: plotpy.core.items.AnnotatedSegment
   :members:
.. autoclass:: plotpy.core.items.AnnotatedRectangle
   :members:
.. autoclass:: plotpy.core.items.AnnotatedObliqueRectangle
   :members:
.. autoclass:: plotpy.core.items.AnnotatedEllipse
   :members:
.. autoclass:: plotpy.core.items.AnnotatedCircle
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
