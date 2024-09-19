# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

from __future__ import annotations

from plotpy.items import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedPolygon,
    AnnotatedRectangle,
    AnnotatedSegment,
)
from plotpy.tools.shape import (
    CircleTool,
    EllipseTool,
    ObliqueRectangleTool,
    PointTool,
    PolygonTool,
    RectangleTool,
    SegmentTool,
)


class AnnotatedPolygonTool(PolygonTool):
    """
    Tool for creating annotated polygon shapes.

    This tool extends the PolygonTool to create AnnotatedPolygon objects.
    """

    def create_shape(self) -> AnnotatedPolygon:
        """
        Create an annotated polygon shape.

        Returns:
            A tuple containing the AnnotatedPolygon object and its handle indices.
        """
        annotation = AnnotatedPolygon()
        self.set_shape_style(annotation)
        return annotation


class AnnotatedRectangleTool(RectangleTool):
    """
    Tool for creating annotated rectangle shapes.

    This tool extends the RectangleTool to create AnnotatedRectangle objects.
    """

    def create_shape(self) -> tuple[AnnotatedRectangle, int, int]:
        """
        Create an annotated rectangle shape.

        Returns:
            A tuple containing the AnnotatedRectangle object and its handle indices.
        """
        annotation = AnnotatedRectangle(0, 0, 1, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 2


class AnnotatedObliqueRectangleTool(ObliqueRectangleTool):
    """
    Tool for creating annotated oblique rectangle shapes.

    This tool extends the ObliqueRectangleTool to create
    AnnotatedObliqueRectangle objects.
    """

    AVOID_NULL_SHAPE: bool = True

    def create_shape(self) -> tuple[AnnotatedObliqueRectangle, int, int]:
        """
        Create an annotated oblique rectangle shape.

        Returns:
            A tuple containing the AnnotatedObliqueRectangle object
            and its handle indices.
        """
        annotation = AnnotatedObliqueRectangle(0, 0, 1, 0, 1, 1, 0, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 2


class AnnotatedCircleTool(CircleTool):
    """
    Tool for creating annotated circle shapes.

    This tool extends the CircleTool to create AnnotatedCircle objects.
    """

    def create_shape(self) -> tuple[AnnotatedCircle, int, int]:
        """
        Create an annotated circle shape.

        Returns:
            A tuple containing the AnnotatedCircle object and its handle indices.
        """
        annotation = AnnotatedCircle(0, 0, 1, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 1


class AnnotatedEllipseTool(EllipseTool):
    """
    Tool for creating annotated ellipse shapes.

    This tool extends the EllipseTool to create AnnotatedEllipse objects.
    """

    def create_shape(self) -> tuple[AnnotatedEllipse, int, int]:
        """
        Create an annotated ellipse shape.

        Returns:
            A tuple containing the AnnotatedEllipse object and its handle indices.
        """
        annotation = AnnotatedEllipse(0, 0, 1, 1)
        annotation.shape.switch_to_circle()
        self.set_shape_style(annotation)
        return annotation, 0, 1


class AnnotatedPointTool(PointTool):
    """
    Tool for creating annotated point shapes.

    This tool extends the PointTool to create AnnotatedPoint objects.
    """

    def create_shape(self) -> tuple[AnnotatedPoint, int, int]:
        """
        Create an annotated point shape.

        Returns:
            A tuple containing the AnnotatedPoint object and its handle indices.
        """
        annotation = AnnotatedPoint(0, 0)
        self.set_shape_style(annotation)
        return annotation, 0, 0


class AnnotatedSegmentTool(SegmentTool):
    """
    Tool for creating annotated segment shapes.

    This tool extends the SegmentTool to create AnnotatedSegment objects.
    """

    def create_shape(self) -> tuple[AnnotatedSegment, int, int]:
        """
        Create an annotated segment shape.

        Returns:
            A tuple containing the AnnotatedSegment object and its handle indices.
        """
        annotation = AnnotatedSegment(0, 0, 1, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 1
