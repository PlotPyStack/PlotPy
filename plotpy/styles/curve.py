# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.dataset import (
    BoolItem,
    DataSet,
    FloatItem,
    GetAttrProp,
    ImageChoiceItem,
    IntItem,
    StringItem,
)
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qwt import QwtPlotCurve

from plotpy.config import _
from plotpy.styles.base import (
    CURVESTYLE_CHOICES,
    CURVESTYLE_NAME,
    ItemParameters,
    LineStyleItem,
    SymbolItem,
)

if TYPE_CHECKING:
    from plotpy.items import CurveItem, PolygonMapItem


class CurveParam(DataSet):
    _multiselection = False
    label = StringItem(_("Title"), default="").set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    line = LineStyleItem(_("Line"))
    symbol = SymbolItem(_("Symbol"))
    shade = FloatItem(_("Shadow"), default=0, min=0, max=1)
    curvestyle = ImageChoiceItem(_("Curve style"), CURVESTYLE_CHOICES, default="Lines")
    baseline = FloatItem(_("Baseline"), default=0.0)
    _downsampling_prop = GetAttrProp("use_downsampling")
    use_downsampling = BoolItem(_("Use downsampling"), default=False).set_prop(
        "display", store=_downsampling_prop
    )
    downsampling_factor = IntItem(_("Downsampling factor"), default=10, min=1).set_prop(
        "display", active=_downsampling_prop
    )

    def update_param(self, curve: CurveItem | PolygonMapItem):
        """Updates the parameters using values from a given CurveItem/PolygonMapItem

        Args:
            curve: reference CurveItem/PolygonMapItem instance
        """
        self.label = str(curve.title().text())
        self.symbol.update_param(curve.symbol())
        self.line.update_param(curve.pen())
        self.curvestyle = CURVESTYLE_NAME[curve.style()]
        self.baseline = curve.baseline()

    def update_item(self, curve: CurveItem | PolygonMapItem):
        """Updates a given CurveItem/PolygonMapItem using the current parameters

        Args:
            curve: instance of CurveItem/PolygonMapItem to update
        """

        plot = curve.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        if not self._multiselection:
            # Non common parameters
            curve.setTitle(self.label)
        curve.setPen(self.line.build_pen())
        # Brush
        linecolor = QG.QColor(self.line.color)
        linecolor.setAlphaF(self.shade)
        brush = QG.QBrush(linecolor)
        if not self.shade:
            brush.setStyle(QC.Qt.NoBrush)
        curve.setBrush(brush)
        # Symbol
        self.symbol.update_symbol(curve)
        # Curve style, type and baseline
        curve.setStyle(getattr(QwtPlotCurve, self.curvestyle))
        curve.setBaseline(self.baseline)
        if plot is not None:
            plot.blockSignals(False)


class CurveParam_MS(CurveParam):
    _multiselection = True


ItemParameters.register_multiselection(CurveParam, CurveParam_MS)
