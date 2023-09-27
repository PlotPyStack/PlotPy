# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Constants
=========

This module provides constants used in plotpy.
"""

from __future__ import annotations

from enum import Enum

from plotpy.config import _

# TODO: Move here other constants from around the codebase


class PlotType(Enum):
    """
    This is the enum used for the plot type. Defines how the plot should deal with the
    different PlotItems types (curves and images)
    """

    #: Automatic plot type. The first PlotItem attached to the plot sets the type.
    #: All tools (curve and image related) are registered and accessible depending
    #: on the last selected PlotItem.
    AUTO = 1

    #: Curve specialized plot. The y axis is not reversed and the aspect ratio is not
    #: locked by default. Only CURVE typed tools are automatically registered.
    CURVE = 2

    #: Image specialized plot. The y axis is reversed and the aspect ratio is locked
    #: by default. Only IMAGE typed tools are automatically registered.
    IMAGE = 3

    #: No assumption is made on the type of items to be displayed on the plot. Acts
    #: like the CURVE value of the enum for y axis and aspect ratio. No tool are
    #: automatically registered.
    MANUAL = 4


PARAMETERS_TITLE_ICON = {
    "grid": (_("Grid..."), "grid.png"),
    "axes": (_("Axes style..."), "axes.png"),
    "item": (_("Parameters..."), "settings.png"),
}
