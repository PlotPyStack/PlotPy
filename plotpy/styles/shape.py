# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from guidata.dataset.dataitems import (
    BoolItem,
    ColorItem,
    FloatArrayItem,
    FloatItem,
    ImageChoiceItem,
    IntItem,
    StringItem,
)
from guidata.dataset.datatypes import (
    BeginGroup,
    BeginTabGroup,
    DataSet,
    EndGroup,
    EndTabGroup,
    GetAttrProp,
)
from qtpy import QtGui as QG
from qwt import QwtPlotMarker

from plotpy.config import _
from plotpy.styles.base import (
    MARKERSTYLE_CHOICES,
    MARKERSTYLE_NAME,
    MARKERSTYLES,
    BrushStyleItem,
    ItemParameters,
    LineStyleItem,
    SymbolItem,
    TextStyleItem,
)

if TYPE_CHECKING:  # pragma: no cover
    from plotpy.items import AnnotatedShape, Axes, Marker, PolygonShape, XRangeSelection


class MarkerParam(DataSet):
    _styles = BeginTabGroup("Styles")
    # ------------------------------------------------------------------ Line tab
    ___line = BeginGroup(_("Line")).set_prop("display", icon="dashdot.png")
    line = LineStyleItem(_("Line (not selected)"))
    sel_line = LineStyleItem(_("Line (selected)"))
    ___eline = EndGroup(_("Line"))
    # ---------------------------------------------------------------- Symbol tab
    ___sym = BeginGroup(_("Symbol")).set_prop("display", icon="diamond.png")
    symbol = SymbolItem(_("Symbol (not selected)"))
    sel_symbol = SymbolItem(_("Symbol (selected)"))
    ___esym = EndGroup(_("Symbol"))
    # ------------------------------------------------------------------ Text tab
    ___text = BeginGroup(_("Text")).set_prop("display", icon="font.png")
    text = TextStyleItem(_("Text (not selected)"))
    sel_text = TextStyleItem(_("Text (selected)"))
    ___etext = EndGroup(_("Text"))
    # ----------------------------------------------------------------------- End
    _endstyles = EndTabGroup("Styles")
    markerstyle = ImageChoiceItem(
        _("Line style"), MARKERSTYLE_CHOICES, default="NoLine"
    )
    spacing = IntItem(_("Spacing"), default=10, min=0)

    def update_param(self, obj: Marker) -> None:
        """Update parameters from object

        Args:
            obj: Marker object
        """
        self.symbol.update_param(obj.symbol())
        self.text.update_param(obj.label())
        self.line.update_param(obj.linePen())
        self.markerstyle = MARKERSTYLE_NAME[obj.lineStyle()]
        self.spacing = obj.spacing()

    def update_marker(self, obj: Marker) -> None:
        """Update object from parameters

        Args:
            obj: Marker object
        """
        if obj.selected:
            line = self.sel_line
            symb = self.sel_symbol
            text = self.sel_text
        else:
            line = self.line
            symb = self.symbol
            text = self.text
        symb.update_symbol(obj)
        label = obj.label()
        text.update_text(label)
        obj.setLabel(label)
        obj.setLinePen(line.build_pen())
        obj.setLineStyle(getattr(QwtPlotMarker, self.markerstyle))
        obj.setSpacing(self.spacing)
        obj.update_label()

    def set_markerstyle(self, style: None | str | int) -> None:
        """Set marker line style

        Args:
            style: line style. It can be one of the following:
             * convenient values: '+', '-', '|' or None
             * `QwtPlotMarker.NoLine`, `QwtPlotMarker.Vertical`, ...
        """
        self.markerstyle = MARKERSTYLES.get(style, style)


class ShapeParam(DataSet):
    label = StringItem(_("Title"), default="")
    _styles = BeginTabGroup("Styles")
    # ------------------------------------------------------------------ Line tab
    ___line = BeginGroup(_("Line")).set_prop("display", icon="dashdot.png")
    line = LineStyleItem(_("Line (not selected)"))
    sel_line = LineStyleItem(_("Line (selected)"))
    ___eline = EndGroup(_("Line"))
    # ---------------------------------------------------------------- Symbol tab
    ___sym = BeginGroup(_("Symbol")).set_prop("display", icon="diamond.png")
    symbol = SymbolItem(_("Symbol (not selected)"))
    sel_symbol = SymbolItem(_("Symbol (selected)"))
    ___esym = EndGroup(_("Symbol"))
    # ------------------------------------------------------------------ Fill tab
    ___fill = BeginGroup(_("Fill pattern")).set_prop(
        "display", icon="dense6pattern.png"
    )
    fill = BrushStyleItem(_("Fill pattern (not selected)"))
    sel_fill = BrushStyleItem(_("Fill pattern (selected)"))
    ___efill = EndGroup(_("Fill pattern"))
    # ----------------------------------------------------------------------- End
    _endstyles = EndTabGroup("Styles")
    readonly = BoolItem(
        _("Read-only shape"),
        default=False,
        help=_("Read-only shapes can't be removed from " "the item list panel"),
    )
    private = BoolItem(
        _("Private shape"),
        default=False,
        help=_("Private shapes are not shown in " "the item list panel"),
    ).set_pos(col=1)

    def update_param(self, obj: PolygonShape) -> None:
        """Update parameters from object

        Args:
            obj: Shape object
        """
        self.label = str(obj.title().text())
        self.line.update_param(obj.pen)
        self.symbol.update_param(obj.symbol)
        self.fill.update_param(obj.brush)
        self.sel_line.update_param(obj.sel_pen)
        self.sel_symbol.update_param(obj.sel_symbol)
        self.sel_fill.update_param(obj.sel_brush)
        self.readonly = obj.is_readonly()
        self.private = obj.is_private()

    def update_shape(self, obj: PolygonShape) -> None:
        """Update object from parameters

        Args:
            obj: Shape object
        """
        plot = obj.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        obj.setTitle(self.label)
        obj.pen = self.line.build_pen()
        obj.symbol = self.symbol.build_symbol()
        obj.brush = self.fill.build_brush()
        obj.sel_pen = self.sel_line.build_pen()
        obj.sel_symbol = self.sel_symbol.build_symbol()
        obj.sel_brush = self.sel_fill.build_brush()
        obj.set_readonly(self.readonly)
        obj.set_private(self.private)
        if plot is not None:
            plot.blockSignals(False)


class AxesShapeParam(DataSet):
    arrow_angle = FloatItem(_("Arrow angle") + " (°)", min=0, max=90, nonzero=True)
    arrow_size = FloatItem(_("Arrow size") + " (%)", min=0, max=100, nonzero=True)
    _styles = BeginTabGroup("Styles")
    # ------------------------------------------------------------------ Line tab
    ___line = BeginGroup(_("Line")).set_prop("display", icon="dashdot.png")
    xarrow_pen = LineStyleItem(_("Line (X-Axis)"))
    yarrow_pen = LineStyleItem(_("Line (Y-Axis)"))
    ___eline = EndGroup(_("Line"))
    # ------------------------------------------------------------------ Fill tab
    ___fill = BeginGroup(_("Fill pattern")).set_prop(
        "display", icon="dense6pattern.png"
    )
    xarrow_brush = BrushStyleItem(_("Fill pattern (X-Axis)"))
    yarrow_brush = BrushStyleItem(_("Fill pattern (Y-Axis)"))
    ___efill = EndGroup(_("Fill pattern"))
    # ----------------------------------------------------------------------- End
    _endstyles = EndTabGroup("Styles")

    def update_param(self, obj: Axes) -> None:
        """Update parameters from object

        Args:
            obj: Axes object
        """
        self.arrow_angle = obj.arrow_angle
        self.arrow_size = obj.arrow_size
        self.xarrow_pen.update_param(obj.x_pen)
        self.yarrow_pen.update_param(obj.y_pen)
        self.xarrow_brush.update_param(obj.x_brush)
        self.yarrow_brush.update_param(obj.y_brush)

    def update_axes(self, obj: Axes) -> None:
        """Update object from parameters

        Args:
            obj: Axes object
        """
        obj.arrow_angle = self.arrow_angle
        obj.arrow_size = self.arrow_size
        obj.x_pen = self.xarrow_pen.build_pen()
        obj.x_brush = self.xarrow_brush.build_brush()
        obj.y_pen = self.yarrow_pen.build_pen()
        obj.y_brush = self.yarrow_brush.build_brush()


class AnnotationParam(DataSet):
    _multiselection = False
    show_label = BoolItem(_("Show annotation"), default=True)
    show_computations = BoolItem(
        _("Show informations on area " "covered by this shape"), default=True
    )
    show_subtitle = BoolItem(_("Show subtitle"), default=True)
    title = StringItem(_("Title"), default="").set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    subtitle = StringItem(_("Subtitle"), default="").set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    format = StringItem(_("String formatting"), default="%.1f")
    uncertainty = FloatItem(
        _("Uncertainty"),
        default=0.0,
        min=0.0,
        max=1.0,
        help=_("Measurement relative uncertainty"),
    ).set_pos(col=1)
    transform_matrix = FloatArrayItem(
        _("Transform matrix"), default=np.eye(3, dtype=float)
    )
    readonly = BoolItem(
        _("Read-only shape"),
        default=False,
        help=_("Read-only shapes can't be removed from " "the item list panel"),
    )
    private = BoolItem(
        _("Private shape"),
        default=False,
        help=_("Private shapes are not shown in " "the item list panel"),
    ).set_pos(col=1)

    def update_param(self, obj: AnnotatedShape) -> None:
        """Update parameters from object

        Args:
            obj: AnnotatedShape object
        """
        self.show_label = obj.is_label_visible()
        self.show_computations = obj.area_computations_visible
        self.show_subtitle = obj.subtitle_visible
        self.title = str(obj.title().text())
        self.readonly = obj.is_readonly()
        self.private = obj.is_private()

    def update_annotation(self, obj: AnnotatedShape) -> None:
        """Update object from parameters

        Args:
            obj: AnnotatedShape object
        """
        plot = obj.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        obj.setTitle(self.title)
        obj.set_label_visible(self.show_label)
        obj.area_computations_visible = self.show_computations
        obj.subtitle_visible = self.show_subtitle
        obj.update_label()
        obj.set_readonly(self.readonly)
        obj.set_private(self.private)
        if plot is not None:
            plot.blockSignals(False)


class AnnotationParam_MS(AnnotationParam):
    _multiselection = True


ItemParameters.register_multiselection(AnnotationParam, AnnotationParam_MS)


class RangeShapeParam(DataSet):
    _styles = BeginTabGroup("Styles")
    # ------------------------------------------------------------------ Line tab
    ___line = BeginGroup(_("Line")).set_prop("display", icon="dashdot.png")
    line = LineStyleItem(_("Line (not selected)"))
    sel_line = LineStyleItem(_("Line (selected)"))
    ___eline = EndGroup(_("Line"))
    # ---------------------------------------------------------------- Symbol tab
    ___symbol = BeginGroup(_("Symbol")).set_prop("display", icon="diamond.png")
    symbol = SymbolItem(_("Symbol (not selected)"))
    sel_symbol = SymbolItem(_("Symbol (selected)"))
    ___esymbol = EndGroup(_("Symbol"))
    # ------------------------------------------------------------------ Fill tab
    ___fill = BeginGroup(_("Fill")).set_prop("display", icon="dense6pattern.png")
    fill = ColorItem(_("Fill color"))
    shade = FloatItem(_("Shade"), default=0.05, min=0, max=1)
    ___efill = EndGroup(_("Fill"))
    # ----------------------------------------------------------------------- End
    _endstyles = EndTabGroup("Styles")

    def update_param(self, range: XRangeSelection) -> None:
        """Update parameters from object

        Args:
            range: XRangeSelection object
        """
        self.line.update_param(range.pen)
        self.sel_line.update_param(range.sel_pen)
        self.fill = range.brush.color().name()
        self.shade = range.brush.color().alphaF()
        self.symbol.update_param(range.symbol)
        self.sel_symbol.update_param(range.sel_symbol)

    def update_range(self, range: XRangeSelection) -> None:
        """Update object from parameters

        Args:
            range: XRangeSelection object
        """
        range.pen = self.line.build_pen()
        range.sel_pen = self.sel_line.build_pen()
        col = QG.QColor(self.fill)
        col.setAlphaF(self.shade)
        range.brush = QG.QBrush(col)
        range.symbol = self.symbol.build_symbol()
        range.sel_symbol = self.sel_symbol.build_symbol()
