# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Shape Item builder
------------------

This module provides a set of factory functions to simplify the creation
of shape items.
"""

# Note: when adding method to builder classes, please do not forget to update the
# documentation (see builder.rst file). Because of class inheritance, the methods
# are not automatically documented (otherwise, they would be sorted alphabetically,
# due to a limitation of sphinx auto-doc).

from __future__ import annotations

import numpy as np

from plotpy.items import (
    CircleSVGShape,
    EllipseShape,
    PolygonShape,
    RectangleShape,
    RectangleSVGShape,
    SegmentShape,
    SquareSVGShape,
)


class ShapeBuilder:
    """Class regrouping a set of factory functions to simplify the creation
    of shape items."""

    def __shape(self, shapeclass, x0, y0, x1, y1, title=None):
        shape = shapeclass(x0, y0, x1, y1)
        shape.set_style("plot", "shape/drag")
        if title is not None:
            shape.setTitle(title)
        return shape

    def rectangle(
        self, x0: float, y0: float, x1: float, y1: float, title: str | None = None
    ) -> RectangleShape:
        """Make a rectangle shape `plot item`

        Args:
            x0: rectangle x0 coordinate
            y0: rectangle y0 coordinate
            x1: rectangle x1 coordinate
            y1: rectangle y1 coordinate
            title: label name. Default is None

        Returns:
            :py:class:`.RectangleShape` object
        """
        return self.__shape(RectangleShape, x0, y0, x1, y1, title)

    def ellipse(
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
    ) -> EllipseShape:
        """Make an ellipse shape `plot item`

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

        Returns:
            :py:class:`.EllipseShape` object
        """
        item = self.__shape(EllipseShape, x0, y0, x1, y1, title)
        item.switch_to_ellipse()
        if x2 is not None and y2 is not None and x3 is not None and y3 is not None:
            item.set_ydiameter(x2, y2, x3, y3)
        return item

    def polygon(
        self, x: np.ndarray, y: np.ndarray, closed: bool, title: str | None = None
    ) -> PolygonShape:
        """Make a polygon shape `plot item`

        Args:
            x: polygon x coordinates
            y: polygon y coordinates
            closed: closed polygon
            title: label name. Default is None

        Returns:
            :py:class:`.PolygonShape` object
        """
        points = np.array([x, y]).T
        item = PolygonShape(points, closed=closed)
        item.set_style("plot", "shape/drag")
        if title is not None:
            item.setTitle(title)
        return item

    def circle(
        self, x0: float, y0: float, x1: float, y1: float, title: str | None = None
    ) -> EllipseShape:
        """Make a circle shape `plot item`

        Args:
            x0: circle x0 coordinate
            y0: circle y0 coordinate
            x1: circle x1 coordinate
            y1: circle y1 coordinate
            title: label name. Default is None

        Returns:
            :py:class:`.EllipseShape` object
        """
        item = self.__shape(EllipseShape, x0, y0, x1, y1, title)
        item.switch_to_circle()
        return item

    def segment(
        self, x0: float, y0: float, x1: float, y1: float, title: str | None = None
    ) -> SegmentShape:
        """Make a segment shape `plot item`

        Args:
            x0: segment x0 coordinate
            y0: segment y0 coordinate
            x1: segment x1 coordinate
            y1: segment y1 coordinate
            title: label name. Default is None

        Returns:
            :py:class:`.SegmentShape` object
        """
        return self.__shape(SegmentShape, x0, y0, x1, y1, title)

    def svg(
        self,
        shape: str,
        fname_or_data: str | bytes,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        title: str | None = None,
    ) -> (CircleSVGShape, RectangleSVGShape, SquareSVGShape):
        """Make a SVG shape `plot item`

        Args:
            shape: shape type ("circle", "rectangle", "square")
            fname_or_data: filename or data
            x0: shape x0 coordinate
            y0: shape y0 coordinate
            x1: shape x1 coordinate
            y1: shape y1 coordinate
            title: label name. Default is None

        Returns:
            SVG shape
        """
        assert shape in ("circle", "rectangle", "square")
        assert isinstance(fname_or_data, (str, bytes))
        if isinstance(fname_or_data, str):
            with open(fname_or_data, "rb") as file:
                data = file.read()
        else:
            data = fname_or_data
        shapeklass = {
            "circle": CircleSVGShape,
            "rectangle": RectangleSVGShape,
            "square": SquareSVGShape,
        }[shape]
        shape = self.__shape(shapeklass, x0, y0, x1, y1, title)
        shape.set_data(data)
        return shape
