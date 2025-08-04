# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Annotation Item builder
-----------------------

This module provides a set of factory functions to simplify the creation
of annotation items.
"""

# Note: when adding method to builder classes, please do not forget to update the
# documentation (see builder.rst file). Because of class inheritance, the methods
# are not automatically documented (otherwise, they would be sorted alphabetically,
# due to a limitation of sphinx auto-doc).

from __future__ import annotations

import numpy as np

from plotpy.config import _
from plotpy.items import (
    AnnotatedCircle,
    AnnotatedEllipse,
    AnnotatedPoint,
    AnnotatedPolygon,
    AnnotatedRectangle,
    AnnotatedSegment,
    AnnotatedXRange,
    AnnotatedYRangeSelection,
)
from plotpy.styles import AnnotationParam


class AnnotationBuilder:
    """Class regrouping a set of factory functions to simplify the creation
    of annotation items."""

    def __get_annotationparam(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotationParam:
        param = AnnotationParam(_("Annotation"), icon="annotation.png")
        if title is not None:
            param.title = title
        if subtitle is not None:
            param.subtitle = subtitle
        if show_label is not None:
            param.show_label = show_label
        if show_computations is not None:
            param.show_computations = show_computations
        if show_subtitle is not None:
            param.show_subtitle = show_subtitle
        if format is not None:
            param.format = format
        if uncertainty is not None:
            param.uncertainty = uncertainty
        if transform_matrix is not None:
            param.transform_matrix = transform_matrix
        if readonly is not None:
            param.readonly = readonly
        if private is not None:
            param.private = private
        return param

    def annotated_point(
        self,
        x: float,
        y: float,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedPoint:
        """Make an annotated point `plot item`

        Args:
            x: point x coordinate
            y: point y coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedPoint` object
        """
        param = self.__get_annotationparam(
            title=title,
            subtitle=subtitle,
            show_label=show_label,
            show_computations=show_computations,
            show_subtitle=show_subtitle,
            format=format,
            uncertainty=uncertainty,
            transform_matrix=transform_matrix,
            readonly=readonly,
            private=private,
        )
        shape = AnnotatedPoint(x, y, param)
        shape.set_style("plot", "shape/drag")
        return shape

    def __annotated_shape(
        self,
        shapeclass,
        points,
        title,
        subtitle,
        show_label,
        show_computations,
        show_subtitle,
        format,
        uncertainty,
        transform_matrix,
        readonly,
        private,
        section: str = "plot",
        option: str = "shape/drag",
    ):
        param = self.__get_annotationparam(
            title=title,
            subtitle=subtitle,
            show_label=show_label,
            show_computations=show_computations,
            show_subtitle=show_subtitle,
            format=format,
            uncertainty=uncertainty,
            transform_matrix=transform_matrix,
            readonly=readonly,
            private=private,
        )
        if isinstance(points, np.ndarray):
            shape = shapeclass(points, annotationparam=param)
        else:
            shape = shapeclass(*points, annotationparam=param)
        shape.set_style(section, option)
        return shape

    def annotated_rectangle(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedRectangle:
        """Make an annotated rectangle `plot item`

        Args:
            x0: rectangle x0 coordinate
            y0: rectangle y0 coordinate
            x1: rectangle x1 coordinate
            y1: rectangle y1 coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedRectangle` object
        """
        points = x0, y0, x1, y1
        return self.__annotated_shape(
            AnnotatedRectangle,
            points,
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
        )

    def annotated_ellipse(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        x2: float | None = None,
        y2: float | None = None,
        x3: float | None = None,
        y3: float | None = None,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedEllipse:
        """Make an annotated ellipse `plot item`

        Args:
            x0: ellipse x0 coordinate
            y0: ellipse y0 coordinate
            x1: ellipse x1 coordinate
            y1: ellipse y1 coordinate
            x2: ellipse x2 coordinate. Default is None
            y2: ellipse y2 coordinate. Default is None
            x3: ellipse x3 coordinate. Default is None
            y3: ellipse y3 coordinate. Default is None
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedEllipse` object
        """
        points = x0, y0, x1, y1
        item = self.__annotated_shape(
            AnnotatedEllipse,
            points,
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
        )
        if x2 is not None and y2 is not None and x3 is not None and y3 is not None:
            item.set_ydiameter(x2, y2, x3, y3)
        return item

    def annotated_circle(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedCircle:
        """Make an annotated circle `plot item`

        Args:
            x0: circle x0 coordinate
            y0: circle y0 coordinate
            x1: circle x1 coordinate
            y1: circle y1 coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedCircle` object
        """
        points = x0, y0, x1, y1
        return self.__annotated_shape(
            AnnotatedCircle,
            points,
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
        )

    def annotated_segment(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedSegment:
        """Make an annotated segment `plot item`

        Args:
            x0: segment x0 coordinate
            y0: segment y0 coordinate
            x1: segment x1 coordinate
            y1: segment y1 coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedSegment` object
        """
        points = x0, y0, x1, y1
        return self.__annotated_shape(
            AnnotatedSegment,
            points,
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
        )

    def annotated_xrange(
        self,
        x0: float,
        x1: float,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedXRange:
        """Make an annotated x-range selection `plot item`

        Args:
            x0: lower x coordinate
            x1: upper x coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedXRange` object
        """
        return self.__annotated_shape(
            AnnotatedXRange,
            (x0, x1),
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
            section="plot",
            option="range",
        )

    def annotated_yrange(
        self,
        y0: float,
        y1: float,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedYRangeSelection:
        """Make an annotated y-range selection `plot item`

        Args:
            y0: lower y coordinate
            y1: upper y coordinate
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedYRangeSelection` object
        """
        return self.__annotated_shape(
            AnnotatedYRangeSelection,
            (y0, y1),
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
            section="plot",
            option="range",
        )

    def annotated_polygon(
        self,
        points: np.ndarray,
        title: str | None = None,
        subtitle: str | None = None,
        show_label: bool | None = None,
        show_computations: bool | None = None,
        show_subtitle: bool | None = None,
        format: str | None = None,
        uncertainty: float | None = None,
        transform_matrix: np.ndarray | None = None,
        readonly: bool | None = None,
        private: bool | None = None,
    ) -> AnnotatedPolygon:
        """Make an annotated polygon `plot item`

        Args:
            points: polygon points
            title: label name. Default is None
            subtitle: label subtitle. Default is None
            show_label: show label. Default is None
            show_computations: show computations. Default is None
            show_subtitle: show subtitle. Default is None
            format: string formatting. Default is None
            uncertainty: measurement relative uncertainty. Default is None
            transform_matrix: transform matrix. Default is None
            readonly: readonly. Default is None
            private: private. Default is None

        Returns:
            :py:class:`.AnnotatedPolygon` object
        """
        return self.__annotated_shape(
            AnnotatedPolygon,
            points,
            title,
            subtitle,
            show_label,
            show_computations,
            show_subtitle,
            format,
            uncertainty,
            transform_matrix,
            readonly,
            private,
        )
