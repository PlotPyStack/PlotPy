# -*- coding: utf-8 -*-
from guidata.dataset.dataitems import (
    BoolItem,
    ChoiceItem,
    ColorItem,
    FloatItem,
    IntItem,
)
from guidata.dataset.datatypes import DataSet
from qtpy import QtGui as QG

from plotpy.config import _


class ErrorBarParam(DataSet):
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

    def update_param(self, curve):
        """

        :param curve:
        """
        color = curve.errorPen.color()
        self.color = str(color.name())
        self.alpha = color.alphaF()
        self.width = curve.errorPen.widthF()
        self.cap = curve.errorCap
        self.ontop = curve.errorOnTop

    def update_item(self, curve):
        """

        :param curve:
        """
        color = QG.QColor(self.color)
        color.setAlphaF(self.alpha)
        curve.errorPen = QG.QPen(color, self.width)
        curve.errorBrush = QG.QBrush(color)
        curve.errorCap = self.cap
        curve.errorOnTop = self.ontop
