"""
Module plotpy.core.items
===============================

:synopsis:

:moduleauthor: CEA

:platform: All

"""


# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

from plotpy.core.items.annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
    AnnotatedShape,
)

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
from plotpy.core.items.curve import CurveItem, ErrorBarCurveItem
from plotpy.core.items.grid import GridItem
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
    EllipseShape,
    Marker,
    ObliqueRectangleShape,
    PointShape,
    PolygonShape,
    RectangleShape,
    SegmentShape,
    XRangeSelection,
)
