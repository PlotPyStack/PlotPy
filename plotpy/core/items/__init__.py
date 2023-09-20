"""
plotpy.core.items
=================

"""

# pylint: disable=unused-import
from plotpy.core.items.annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
    AnnotatedShape,
)
from plotpy.core.items.curve import CurveItem, ErrorBarCurveItem
from plotpy.core.items.grid import GridItem
from plotpy.core.items.histogram import HistogramItem
from plotpy.core.items.image import (
    BaseImageItem,
    Histogram2DItem,
    ImageFilterItem,
    ImageItem,
    MaskedArea,
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
from plotpy.core.items.label import (
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
from plotpy.core.items.polygon import PolygonMapItem
from plotpy.core.items.shapes import (
    AbstractShape,
    Axes,
    ContourShape,
    EllipseShape,
    Marker,
    ObliqueRectangleShape,
    PointShape,
    PolygonShape,
    RectangleShape,
    SegmentShape,
    XRangeSelection,
)
