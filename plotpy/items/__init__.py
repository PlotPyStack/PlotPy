# -*- coding: utf-8 -*-

# pylint: disable=unused-import
from .annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
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
    RangeComputation2d,
    RangeInfo,
    SelectedLegendBoxItem,
)
from .polygon import PolygonMapItem
from .shapes import (
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
)
