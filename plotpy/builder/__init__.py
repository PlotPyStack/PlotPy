# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Item builder
------------

The `builder` module provides a builder singleton class that can be
used to simplify the creation of plot items.
"""

from __future__ import annotations

from .annotation import AnnotationBuilder
from .curvemarker import CurveMarkerCursorBuilder
from .image import ImageBuilder
from .label import LabelBuilder
from .plot import WidgetBuilder
from .shape import ShapeBuilder


class PlotBuilder(
    WidgetBuilder,
    CurveMarkerCursorBuilder,
    ImageBuilder,
    LabelBuilder,
    ShapeBuilder,
    AnnotationBuilder,
):
    """Class regrouping a set of factory functions to simplify the creation
    of plot widgets and plot items.

    It is a singleton class, so you should not create instances of this class
    but use the :py:data:`plotpy.builder.make` instance instead.
    """

    def __init__(self):
        super().__init__()


#: Instance of :py:class:`.PlotBuilder`
make = PlotBuilder()
