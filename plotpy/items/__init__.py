# -*- coding: utf-8 -*-

# pylint: disable=unused-import
# flake8: noqa

from .annotation import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedPolygon,
    AnnotatedSegment,
    AnnotatedXRange,
    AnnotatedYRange,
    AnnotatedShape,
)
from .contour import ContourItem, create_contour_items
from .curve import CurveItem, ErrorBarCurveItem
from .grid import GridItem
from .histogram import HistogramItem
from .image import (
    BaseImageItem,
    Histogram2DItem,
    ImageFilterItem,
    ImageItem,
    MaskedImageItem,
    MaskedXYImageItem,
    QuadGridItem,
    RawImageItem,
    RGBImageItem,
    TrImageItem,
    XYImageFilterItem,
    XYImageItem,
    assemble_imageitems,
    compute_trimageitems_original_size,
    get_image_from_plot,
    get_image_from_qrect,
    get_image_in_shape,
    get_items_in_rectangle,
    get_plot_qrect,
)
from .image.masked import MaskedArea, MaskedImageItem, MaskedXYImageItem
from .label import (
    AbstractLabelItem,
    DataInfoLabel,
    LabelItem,
    LegendBoxItem,
    ObjectInfo,
    RangeComputation,
    XRangeComputation,
    YRangeComputation,
    RangeComputation2d,
    RangeInfo,
    SelectedLegendBoxItem,
)
from .polygonmap import PolygonMapItem
from .shape import (
    AbstractShape,
    Axes,
    CircleSVGShape,
    EllipseShape,
    Marker,
    ObliqueRectangleShape,
    PointShape,
    PolygonShape,
    RectangleShape,
    RectangleSVGShape,
    SegmentShape,
    SquareSVGShape,
    XRangeSelection,
    YRangeSelection,
)
