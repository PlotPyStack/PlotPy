# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.dataset import BoolItem, ChoiceItem, ColorItem, DataSet, FloatItem, IntItem
from qtpy import QtGui as QG

from plotpy.config import _

if TYPE_CHECKING:
    from plotpy.items import ErrorBarCurveItem


class ErrorBarParam(DataSet):
    """Error bar style parameters for a curve."""

    mode = ChoiceItem(
        _("Display"),
        default=0,
        choices=[_("error bars with caps (x, y)"), _("error area (y)")],
        help=_(
            "Note: only y-axis error bars are shown in "
            "error area mode\n(width and cap parameters "
            "will also be ignored)"
        ),
    )
    color = ColorItem(_("Color"), default="darkred")
    alpha = FloatItem(
        _("Alpha"), default=0.9, min=0, max=1, help=_("Error bar transparency")
    )
    width = FloatItem(_("Width"), default=1.0, min=1)
    cap = IntItem(_("Cap"), default=4, min=0)
    ontop = BoolItem(_("set to foreground"), _("Visibility"), default=False)

    def update_param(self, item: ErrorBarCurveItem) -> None:
        """
        Update the parameters associated with the error bar item.

        Args:
            item: The error bar item from which to update the parameters.
        """
        color = item.errorPen.color()
        self.color = str(color.name())
        self.alpha = color.alphaF()
        self.width = item.errorPen.widthF()
        self.cap = item.errorCap
        self.ontop = item.errorOnTop

    def update_item(self, item: ErrorBarCurveItem) -> None:
        """
        Update the error bar item with the parameters.

        Args:
            item: The error bar item to update.
        """
        color = QG.QColor(self.color)
        color.setAlphaF(self.alpha)
        item.errorPen = QG.QPen(color, self.width)
        item.errorBrush = QG.QBrush(color)
        item.errorCap = self.cap
        item.errorOnTop = self.ontop
