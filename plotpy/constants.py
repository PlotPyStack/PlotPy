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

import enum

from plotpy.config import _

# TODO: Move here other constants from around the codebase


class PlotType(enum.Enum):
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


class LUTAlpha(enum.Enum):
    """LUT Alpha functions"""

    #: No alpha function
    NONE = 0

    #: Constant alpha function
    CONSTANT = 1

    #: Linear alpha function
    LINEAR = 2

    #: Sigmoid alpha function
    SIGMOID = 3

    #: Hyperbolic tangent alpha function
    TANH = 4

    @classmethod
    def get_member_from_name(cls: type["LUTAlpha"], name: str) -> "LUTAlpha|None":
        """Return the member of the enum from its name"""
        for member in cls:
            if member.name.lower() == name.lower():
                return member
        return None

    def get_choices(self):
        """Return the list of choices"""
        return [
            (LUTAlpha.NONE.value, _("None")),
            (LUTAlpha.CONSTANT.value, _("Constant")),
            (LUTAlpha.LINEAR.value, _("Linear")),
            (LUTAlpha.SIGMOID.value, _("Sigmoid")),
            (LUTAlpha.TANH.value, _("Hyperbolic tangent")),
        ]
