# -*- coding: utf-8 -*-

"""
plotpy.core.styles
------------------

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
    COLORS,
    MARKERS,
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
    LUTAlpha,
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
