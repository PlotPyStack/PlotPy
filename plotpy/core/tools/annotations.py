# -*- coding: utf-8 -*-
from plotpy.core.items.annotations import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedObliqueRectangle,
    AnnotatedPoint,
    AnnotatedRectangle,
    AnnotatedSegment,
)
from plotpy.core.tools.shapes import (
    CircleTool,
    EllipseTool,
    ObliqueRectangleTool,
    PointTool,
    RectangleTool,
    SegmentTool,
)


class AnnotatedRectangleTool(RectangleTool):
    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedRectangle(0, 0, 1, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 2


class AnnotatedObliqueRectangleTool(ObliqueRectangleTool):
    AVOID_NULL_SHAPE = True

    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedObliqueRectangle(0, 0, 1, 0, 1, 1, 0, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 2


class AnnotatedCircleTool(CircleTool):
    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedCircle(0, 0, 1, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 1


class AnnotatedEllipseTool(EllipseTool):
    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedEllipse(0, 0, 1, 1)
        annotation.shape.switch_to_circle()
        self.set_shape_style(annotation)
        return annotation, 0, 1

    def handle_final_shape(self, shape):
        """

        :param shape:
        """
        shape.shape.switch_to_ellipse()
        super(EllipseTool, self).handle_final_shape(shape)


class AnnotatedPointTool(PointTool):
    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedPoint(0, 0)
        self.set_shape_style(annotation)
        return annotation, 0, 0


class AnnotatedSegmentTool(SegmentTool):
    def create_shape(self):
        """

        :return:
        """
        annotation = AnnotatedSegment(0, 0, 1, 1)
        self.set_shape_style(annotation)
        return annotation, 0, 1
