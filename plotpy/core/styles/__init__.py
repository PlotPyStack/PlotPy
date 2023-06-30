# -*- coding: utf-8 -*-

"""
plotpy.core.styles
---------------------

The `styles` module provides set of parameters (DataSet classes) to
configure `plot items` and `plot tools`.

.. seealso::

    Module :py:mod:`.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

    Module :py:mod:`.tools`
        Module providing the `plot tools`

Reference
~~~~~~~~~

.. autoclass:: CurveParam
   :members:
.. autoclass:: ErrorBarParam
   :members:
.. autoclass:: GridParam
   :members:
.. autoclass:: ImageParam
   :members:
.. autoclass:: TrImageParam
   :members:
.. autoclass:: ImageFilterParam
   :members:
.. autoclass:: HistogramParam
   :members:
.. autoclass:: Histogram2DParam
   :members:
.. autoclass:: AxesParam
   :members:
.. autoclass:: ImageAxesParam
   :members:
.. autoclass:: LabelParam
   :members:
.. autoclass:: LegendParam
   :members:
.. autoclass:: ShapeParam
   :members:
.. autoclass:: AnnotationParam
   :members:
.. autoclass:: AxesShapeParam
   :members:
.. autoclass:: RangeShapeParam
   :members:
.. autoclass:: MarkerParam
   :members:
.. autoclass:: FontParam
   :members:
.. autoclass:: SymbolParam
   :members:
.. autoclass:: LineStyleParam
   :members:
.. autoclass:: BrushStyleParam
   :members:
.. autoclass:: TextStyleParam
   :members:
.. autoclass:: RawImageParam
   :members:
.. autoclass:: XYImageParam
   :members:
.. autoclass:: RGBImageParam
   :members:
.. autoclass:: MaskedImageParam
   :members:
.. autoclass:: MaskedXYImageParam
   :members:

"""

# pylint: disable=W0611

from plotpy.core.styles.axes import (
    AxesParam,
    AxeStyleParam,
    AxisItem,
    AxisItemWidget,
    AxisParam,
    ImageAxesParam,
)
from plotpy.core.styles.base import (
    BrushStyleItem,
    BrushStyleItemWidget,
    BrushStyleParam,
    FontItem,
    FontItemWidget,
    FontParam,
    GridParam,
    ItemParameters,
    LineStyleItem,
    LineStyleItemWidget,
    LineStyleParam,
    SymbolItem,
    SymbolItemWidget,
    SymbolParam,
    TextStyleItem,
    TextStyleItemWidget,
    TextStyleParam,
    style_generator,
    update_style_attr,
)
from plotpy.core.styles.curve import CurveParam, CurveParam_MS
from plotpy.core.styles.errorbar import ErrorBarParam
from plotpy.core.styles.histogram import (
    Histogram2DParam,
    Histogram2DParam_MS,
    HistogramParam,
)
from plotpy.core.styles.image import (
    BaseImageParam,
    ImageFilterParam,
    ImageParam,
    ImageParam_MS,
    ImageParamMixin,
    MaskedImageParam,
    MaskedImageParam_MS,
    MaskedImageParamMixin,
    MaskedXYImageParam,
    MaskedXYImageParam_MS,
    QuadGridParam,
    RawImageParam,
    RawImageParam_MS,
    RGBImageParam,
    TransformParamMixin,
    TrImageParam,
    TrImageParam_MS,
    XYImageParam,
    XYImageParam_MS,
)
from plotpy.core.styles.label import (
    LabelParam,
    LabelParam_MS,
    LabelParamWithContents,
    LabelParamWithContents_MS,
    LegendParam,
    LegendParam_MS,
)
from plotpy.core.styles.shape import (
    AnnotationParam,
    AnnotationParam_MS,
    AxesShapeParam,
    MarkerParam,
    RangeShapeParam,
    ShapeParam,
)
