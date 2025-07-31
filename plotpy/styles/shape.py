# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import numpy as np
from guidata.dataset import (
    BeginGroup,
    BeginTabGroup,
    BoolItem,
    ColorItem,
    DataSet,
    EndGroup,
    EndTabGroup,
    FloatArrayItem,
    FloatItem,
    GetAttrProp,
    ImageChoiceItem,
    IntItem,
    StringItem,
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

if TYPE_CHECKING:
    from plotpy.items import AnnotatedShape, Axes, Marker, PolygonShape, XRangeSelection
    from plotpy.plot import BasePlot
    from plotpy.styles import (
        BrushStyleParam,
        LineStyleParam,
        SymbolParam,
        TextStyleParam,
    )


class MarkerParam(DataSet):
    """Parameters for a marker item"""

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
        self.symbol: SymbolParam
        self.text: TextStyleParam
        self.line: LineStyleParam
        self.symbol.update_param(obj.symbol())
        self.text.update_param(obj.label())
        self.line.update_param(obj.linePen())
        self.markerstyle = MARKERSTYLE_NAME[obj.lineStyle()]
        self.spacing = obj.spacing()

    def update_item(self, item: Marker) -> None:
        """Update object from parameters

        Args:
            item: Marker object
        """
        if item.selected:
            line = self.sel_line
            symb = self.sel_symbol
            text = self.sel_text
        else:
            line = self.line
            symb = self.symbol
            text = self.text
        symb.update_symbol(item)
        label = item.label()
        text.update_text(label)
        item.setLabel(label)
        item.setLinePen(line.build_pen())
        item.setLineStyle(getattr(QwtPlotMarker, self.markerstyle))
        item.setSpacing(self.spacing)
        item.update_label()

    # TODO: remove this method in a future release
    def update_marker(self, obj: Marker) -> None:
        """Update object from parameters. Deprecated, use update_item instead.

        Args:
            obj: Marker object
        """
        warnings.warn(
            "`MarkerParam.update_marker` method is deprecated and will be removed "
            "in a future release. Please use `update_item` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.update_item(obj)

    def set_markerstyle(self, style: None | str | int) -> None:
        """Set marker line style

        Args:
            style: line style. It can be one of the following:
             * convenient values: '+', '-', '|' or None
             * `QwtPlotMarker.NoLine`, `QwtPlotMarker.Vertical`, ...
        """
        self.markerstyle = MARKERSTYLES.get(style, style)


class ShapeParam(DataSet):
    """Parameters for a shape item"""

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
        help=_("Read-only shapes can't be removed from the item list panel"),
    )
    private = BoolItem(
        _("Private shape"),
        default=False,
        help=_("Private shapes are not shown in the item list panel"),
    ).set_pos(col=1)

    def update_param(self, obj: PolygonShape) -> None:
        """Update parameters from object

        Args:
            obj: Shape object
        """
        self.line: LineStyleParam
        self.symbol: SymbolParam
        self.fill: BrushStyleParam
        self.sel_line: LineStyleParam
        self.sel_symbol: SymbolParam
        self.sel_fill: BrushStyleParam
        self.label = str(obj.title().text())
        self.line.update_param(obj.pen)
        self.symbol.update_param(obj.symbol)
        self.fill.update_param(obj.brush)
        self.sel_line.update_param(obj.sel_pen)
        self.sel_symbol.update_param(obj.sel_symbol)
        self.sel_fill.update_param(obj.sel_brush)
        self.readonly = obj.is_readonly()
        self.private = obj.is_private()

    def update_item(self, item: PolygonShape) -> None:
        """Update object from parameters

        Args:
            item: Shape object
        """
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.setTitle(self.label)
        item.pen = self.line.build_pen()
        item.symbol = self.symbol.build_symbol()
        item.brush = self.fill.build_brush()
        item.sel_pen = self.sel_line.build_pen()
        item.sel_symbol = self.sel_symbol.build_symbol()
        item.sel_brush = self.sel_fill.build_brush()
        item.set_readonly(self.readonly)
        item.set_private(self.private)
        if plot is not None:
            plot.blockSignals(False)

    # TODO: remove this method in a future release
    def update_shape(self, obj: PolygonShape) -> None:
        """Update object from parameters. Deprecated, use update_item instead.

        Args:
            obj: Shape object
        """
        warnings.warn(
            "`ShapeParam.update_shape` method is deprecated and will be removed "
            "in a future release. Please use `update_item` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.update_item(obj)


class AxesShapeParam(DataSet):
    """Parameters for an axes item"""

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

    def update_param(self, item: Axes) -> None:
        """Update parameters from object

        Args:
            obj: Axes object
        """
        self.xarrow_pen: LineStyleParam
        self.yarrow_pen: LineStyleParam
        self.xarrow_brush: BrushStyleParam
        self.yarrow_brush: BrushStyleParam
        self.arrow_angle = item.arrow_angle
        self.arrow_size = item.arrow_size
        self.xarrow_pen.update_param(item.x_pen)
        self.yarrow_pen.update_param(item.y_pen)
        self.xarrow_brush.update_param(item.x_brush)
        self.yarrow_brush.update_param(item.y_brush)

    def update_item(self, item: Axes) -> None:
        """Update object from parameters

        Args:
            obj: Axes object
        """
        item.arrow_angle = self.arrow_angle
        item.arrow_size = self.arrow_size
        item.x_pen = self.xarrow_pen.build_pen()
        item.x_brush = self.xarrow_brush.build_brush()
        item.y_pen = self.yarrow_pen.build_pen()
        item.y_brush = self.yarrow_brush.build_brush()

    # TODO: remove this method in a future release
    def update_axes(self, obj: Axes) -> None:
        """Update object from parameters. Deprecated, use update_item instead.

        Args:
            obj: Axes object
        """
        warnings.warn(
            "`AxesShapeParam.update_axes` method is deprecated and will be removed "
            "in a future release. Please use `update_item` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.update_item(obj)


class AnnotationParam(DataSet):
    """Parameters for annotations"""

    _multiselection = False
    show_label = BoolItem(_("Show annotation"), default=True)
    show_computations = BoolItem(
        _("Show informations on area covered by this shape"), default=True
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
        help=_("Read-only shapes can't be removed from the item list panel"),
    )
    private = BoolItem(
        _("Private shape"),
        default=False,
        help=_("Private shapes are not shown in the item list panel"),
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

    def update_item(self, item: AnnotatedShape) -> None:
        """Update object from parameters

        Args:
            obj: AnnotatedShape object
        """
        plot: BasePlot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        item.setTitle(self.title)
        item.set_label_visible(self.show_label)
        item.area_computations_visible = self.show_computations
        item.subtitle_visible = self.show_subtitle
        item.update_label()
        item.set_readonly(self.readonly)
        item.set_private(self.private)
        if plot is not None:
            plot.blockSignals(False)

    # TODO: remove this method in a future release
    def update_annotation(self, obj: AnnotatedShape) -> None:
        """Update object from parameters. Deprecated, use update_item instead.

        Args:
            obj: AnnotatedShape object
        """
        warnings.warn(
            "`AnnotationParam.update_annotation` method is deprecated and "
            "will be removed in a future release. Please use `update_item` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.update_item(obj)


class AnnotationParam_MS(AnnotationParam):
    """Parameters for annotations with multi-selection enabled"""

    _multiselection = True


ItemParameters.register_multiselection(AnnotationParam, AnnotationParam_MS)


class RangeShapeParam(DataSet):
    """Parameters for a range selection item"""

    label = StringItem(_("Title"), default="")
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

    def update_param(self, obj: XRangeSelection) -> None:
        """Update parameters from object

        Args:
            obj: XRangeSelection object
        """
        self.label = str(obj.title().text())
        self.line: LineStyleParam
        self.sel_line: LineStyleParam
        self.symbol: SymbolParam
        self.sel_symbol: SymbolParam
        self.line.update_param(obj.pen)
        self.sel_line.update_param(obj.sel_pen)
        self.fill = obj.brush.color().name()
        self.shade = obj.brush.color().alphaF()
        self.symbol.update_param(obj.symbol)
        self.sel_symbol.update_param(obj.sel_symbol)

    def update_item(self, item: XRangeSelection) -> None:
        """Update object from parameters

        Args:
            range: XRangeSelection object
        """
        item.setTitle(self.label)
        item.pen = self.line.build_pen()
        item.sel_pen = self.sel_line.build_pen()
        col = QG.QColor(self.fill)
        col.setAlphaF(self.shade)
        item.brush = QG.QBrush(col)
        item.symbol = self.symbol.build_symbol()
        item.sel_symbol = self.sel_symbol.build_symbol()

    # TODO: remove this method in a future release
    def update_range(self, obj: XRangeSelection) -> None:
        """Update object from parameters. Deprecated, use update_item instead.

        Args:
            obj: XRangeSelection object
        """
        warnings.warn(
            "`RangeShapeParam.update_range` method is deprecated and "
            "will be removed in a future release. Please use `update_item` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.update_item(obj)
