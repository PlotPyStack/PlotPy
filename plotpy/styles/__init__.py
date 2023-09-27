# -*- coding: utf-8 -*-

"""
plotpy.styles
------------------

"""

# pylint: disable=W0611

from plotpy.styles.axes import (
    AxesParam,
    AxeStyleParam,
    AxisItem,
    AxisItemWidget,
    AxisParam,
    ImageAxesParam,
)
from plotpy.styles.base import (
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
from plotpy.styles.curve import CurveParam, CurveParam_MS
from plotpy.styles.errorbar import ErrorBarParam
from plotpy.styles.histogram import (
    Histogram2DParam,
    Histogram2DParam_MS,
    HistogramParam,
)
from plotpy.styles.image import (
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
from plotpy.styles.label import (
    LabelParam,
    LabelParam_MS,
    LabelParamWithContents,
    LabelParamWithContents_MS,
    LegendParam,
    LegendParam_MS,
)
from plotpy.styles.shape import (
    AnnotationParam,
    AnnotationParam_MS,
    AxesShapeParam,
    MarkerParam,
    RangeShapeParam,
    ShapeParam,
)
