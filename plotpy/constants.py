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

# ===============================================================================
# Plot types
# ===============================================================================


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


# ===============================================================================
# Plot parameters
# ===============================================================================

PARAMETERS_TITLE_ICON = {
    "grid": (_("Grid..."), "grid.png"),
    "axes": (_("Axes style..."), "axes.png"),
    "item": (_("Parameters..."), "settings.png"),
}


# ===============================================================================
# Panels
# ===============================================================================

#: ID of the `item list` panel
ID_ITEMLIST = "itemlist"
#: ID of the `contrast adjustment` panel
ID_CONTRAST = "contrast"
#: ID of the `X-axis cross section` panel
ID_XCS = "x_cross_section"
#: ID of the `Y-axis cross section` panel
ID_YCS = "y_cross_section"
#: ID of the `oblique averaged cross section` panel
ID_OCS = "oblique_cross_section"
#: ID of the `line cross section` panel
ID_LCS = "line_cross_section"


# ===============================================================================
# Plot items
# ===============================================================================

# Shape Z offset used when adding shapes to the plot
SHAPE_Z_OFFSET = 1000


# Lookup table alpha functions for image items
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

    #: Transparent lowest value and opaque highest value
    STEP = 5

    @classmethod
    def get_member_from_name(cls: type["LUTAlpha"], name: str) -> "LUTAlpha|None":
        """Return the member of the enum from its name"""
        for member in cls:
            if member.name.lower() == name.lower():
                return member
        return None

    @classmethod
    def get_choices(cls: type["LUTAlpha"]) -> list[tuple[int, str]]:
        """Return the list of choices"""
        return [
            (LUTAlpha.NONE.value, _("None")),
            (LUTAlpha.CONSTANT.value, _("Constant")),
            (LUTAlpha.LINEAR.value, _("Linear")),
            (LUTAlpha.SIGMOID.value, _("Sigmoid")),
            (LUTAlpha.TANH.value, _("Hyperbolic tangent")),
            (LUTAlpha.STEP.value, _("Step")),
        ]

    @classmethod
    def get_help(cls: type["LUTAlpha"]) -> str:
        """Return tooltip help for all alpha functions"""
        return _(
            "Alpha function applied to the Look-Up Table (LUT)<br>"
            "to control the transparency of the image:<br>"
            "(maximum opacity is given by the <b>Global alpha</b> parameter)<br><br>"
            "<b>None</b>: No alpha function<br>"
            "<b>Constant</b>: Constant alpha function<br>"
            "<b>Linear</b>: Linear alpha function<br>"
            "<b>Sigmoid</b>: Sigmoid alpha function<br>"
            "<b>Hyperbolic tangent</b>: Hyperbolic tangent alpha function<br>"
            "<b>Step</b>: Lowest value of the LUT is 100% transparent, other "
            "values are opaque"
        )


# Lookup table size
LUT_SIZE = 1024
LUT_MAX = float(LUT_SIZE - 1)
