# -*- coding: utf-8 -*-

from __future__ import annotations

from copy import deepcopy
from math import atan2, pi, sqrt
from typing import TYPE_CHECKING

from guidata.dataset.dataitems import (
    BoolItem,
    ButtonItem,
    ColorItem,
    FloatItem,
    ImageChoiceItem,
    IntItem,
    StringItem,
)
from guidata.dataset.datatypes import (
    BeginGroup,
    DataSet,
    DataSetGroup,
    EndGroup,
    ObjectItem,
)
from guidata.dataset.qtitemwidgets import DataSetWidget
from guidata.dataset.qtwidgets import DataSetEditLayout
from guidata.utils import update_dataset
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qwt import QwtPlotCurve, QwtPlotMarker, QwtSymbol

from plotpy.config import _

if TYPE_CHECKING:  # pragma: no cover
    import guidata.dataset.datatypes

    from plotpy.interfaces import IBasePlotItem
    from plotpy.plot import BasePlot

LINESTYLES = {"-": "SolidLine", "--": "DashLine", ":": "DotLine", "-.": "DashDotLine"}
COLORS = {
    "r": "red",
    "g": "green",
    "b": "blue",
    "c": "cyan",
    "m": "magenta",
    "y": "yellow",
    "k": "black",
    "w": "white",
    "G": "gray",
}
MARKERS = {
    "+": QwtSymbol.Cross,
    "o": QwtSymbol.Ellipse,
    "*": QwtSymbol.Star1,
    ".": QwtSymbol(
        QwtSymbol.Ellipse, QG.QBrush(QC.Qt.black), QG.QPen(QC.Qt.black), QC.QSizeF(3, 3)
    ),
    "x": QwtSymbol.XCross,
    "s": QwtSymbol.Rect,
    "d": QwtSymbol.Diamond,
    "^": QwtSymbol.UTriangle,
    "v": QwtSymbol.DTriangle,
    ">": QwtSymbol.RTriangle,
    "<": QwtSymbol.LTriangle,
    "h": QwtSymbol.Star2,
}
MARKERSTYLES = {None: "NoLine", "-": "HLine", "|": "VLine", "+": "Cross"}


LINESTYLE_CHOICES = [
    ("SolidLine", _("Solid line"), "solid.png"),
    ("DashLine", _("Dashed line"), "dash.png"),
    ("DotLine", _("Dotted line"), "dot.png"),
    ("DashDotLine", _("Dash-dot line"), "dashdot.png"),
    ("DashDotDotLine", _("Dash-dot-dot line"), "dashdotdot.png"),
    ("NoPen", _("No line"), "none.png"),
]
MARKER_CHOICES = [
    ("Cross", _("Cross"), "cross.png"),
    ("Ellipse", _("Ellipse"), "ellipse.png"),
    ("Star1", _("Star"), "star.png"),
    ("XCross", _("X-Cross"), "xcross.png"),
    ("Rect", _("Square"), "square.png"),
    ("Diamond", _("Diamond"), "diamond.png"),
    ("UTriangle", _("Triangle"), "triangle_u.png"),
    ("DTriangle", _("Triangle"), "triangle_d.png"),
    ("RTriangle", _("Triangle"), "triangle_r.png"),
    ("LTriangle", _("Triangle"), "triangle_l.png"),
    ("Star2", _("Hexagon"), "hexagon.png"),
    ("NoSymbol", _("No symbol"), "none.png"),
]
CURVESTYLE_CHOICES = [
    ("Lines", _("Lines"), "lines.png"),
    ("Sticks", _("Sticks"), "sticks.png"),
    ("Steps", _("Steps"), "steps.png"),
    ("Dots", _("Dots"), "dots.png"),
    ("NoCurve", _("No curve"), "none.png"),
]

BRUSHSTYLE_CHOICES = [
    ("NoBrush", _("No brush pattern"), "nobrush.png"),
    ("SolidPattern", _("Uniform color"), "solidpattern.png"),
    ("Dense1Pattern", _("Extremely dense brush pattern"), "dense1pattern.png"),
    ("Dense2Pattern", _("Very dense brush pattern"), "dense2pattern.png"),
    ("Dense3Pattern", _("Somewhat dense brush pattern"), "dense3pattern.png"),
    ("Dense4Pattern", _("Half dense brush pattern"), "dense4pattern.png"),
    ("Dense5Pattern", _("Somewhat sparse brush pattern"), "dense5pattern.png"),
    ("Dense6Pattern", _("Very sparse brush pattern"), "dense6pattern.png"),
    ("Dense7Pattern", _("Extremely sparse brush pattern"), "dense7pattern.png"),
    ("HorPattern", _("Horizontal lines"), "horpattern.png"),
    ("VerPattern", _("Vertical lines"), "verpattern.png"),
    ("CrossPattern", _("Crossing horizontal and vertical lines"), "crosspattern.png"),
    ("BDiagPattern", _("Backward diagonal lines"), "bdiagpattern.png"),
    ("FDiagPattern", _("Forward diagonal lines"), "fdiagpattern.png"),
    ("DiagCrossPattern", _("Crossing diagonal lines"), "diagcrosspattern.png"),
    # (
    #     "LinearGradientPattern",
    #     _("Linear gradient (set using a dedicated QBrush constructor)"),
    #     "none.png",
    # ),
    # (
    #     "ConicalGradientPattern",
    #     _("Conical gradient (set using a dedicated QBrush constructor)"),
    #     "none.png",
    # ),
    # (
    #     "RadialGradientPattern",
    #     _("Radial gradient (set using a dedicated QBrush constructor)"),
    #     "none.png",
    # ),
    # ("TexturePattern", _("Custom pattern (see QBrush::setTexture())"), "none.png"),
]

MARKERSTYLE_CHOICES = [
    ("NoLine", _("None"), "none.png"),
    ("HLine", _("Horizontal"), "horiz_marker.png"),
    ("VLine", _("Vertical"), "vert_marker.png"),
    ("Cross", _("Cross"), "cross_marker.png"),
]


def build_reverse_map(lst, obj):
    """

    :param lst:
    :param obj:
    :return:
    """
    dict = {}
    for idx, _name, _icon in lst:
        val = getattr(obj, idx)
        dict[val] = idx
    return dict


MARKER_NAME = build_reverse_map(MARKER_CHOICES, QwtSymbol)
CURVESTYLE_NAME = build_reverse_map(CURVESTYLE_CHOICES, QwtPlotCurve)
LINESTYLE_NAME = build_reverse_map(LINESTYLE_CHOICES, QC.Qt)
BRUSHSTYLE_NAME = build_reverse_map(BRUSHSTYLE_CHOICES, QC.Qt)
MARKERSTYLE_NAME = build_reverse_map(MARKERSTYLE_CHOICES, QwtPlotMarker)


def style_generator(color_keys="bgrcmykG"):
    """Cycling through curve styles"""
    while True:
        for linestyle in sorted(LINESTYLES.keys()):
            for color in color_keys:
                yield color + linestyle


def update_style_attr(style, param):
    """Parse a MATLAB-like style string and
    update the color, linestyle, marker attributes of the param
    object
    """
    for marker in list(MARKERS.keys()):
        if marker in style:
            param.symbol.update_param(MARKERS[marker])
            break
    else:
        param.symbol.update_param(QwtSymbol.NoSymbol)
    for linestyle in list(LINESTYLES.keys()):
        if linestyle in style:
            param.line.style = LINESTYLES[linestyle]
            break
    else:
        param.line.style = "NoPen"
    for color in list(COLORS.keys()):
        if color in style:
            param.line.color = COLORS[color]
            param.symbol.facecolor = COLORS[color]
            param.symbol.edgecolor = COLORS[color]
            break


class ItemParameters:
    """Class handling QwtPlotItem-like parameters

    Args:
        multiselection (bool): if True, the class will handle
    """

    MULTISEL_DATASETS = []
    # Customizing tab display order:
    ENDING_PARAMETERS = (
        "CurveParam",
        "ErrorBarParam",
        "ShapeParam",
        "LabelParam",
        "LegendParam",
        "GridParam",
        "AxesParam",
    )

    def __init__(self, multiselection: bool = False):
        self.multiselection = multiselection
        self.paramdict: dict[str, guidata.dataset.datatypes.DataSet] = {}
        self.items: set[IBasePlotItem] = set()

    @classmethod
    def register_multiselection(cls, klass, klass_ms):
        """Register a DataSet couple: (DataSet, DataSet_for_MultiSelection)"""
        # Inserting element backwards because classes have to be registered
        # from children to parent (see 'add' method to fully understand why)
        cls.MULTISEL_DATASETS.insert(0, (klass, klass_ms))

    def __add(self, key, item, param):
        self.paramdict[key] = param
        self.items.add(item)

    def add(
        self,
        key: str,
        item: IBasePlotItem,
        param: guidata.dataset.datatypes.DataSet,
    ) -> None:
        """
        Add parameters for a given item

        Args:
            key: key to identify the item
            item: item to be customized
            param: parameters to be applied to the item
        """
        if self.multiselection:
            for klass, klass_ms in self.MULTISEL_DATASETS:
                if isinstance(param, klass):
                    title = param.get_title()
                    if key in self.paramdict and not title.endswith("s"):
                        title += "s"
                    param_ms = klass_ms(
                        title=title, comment=param.get_comment(), icon=param.get_icon()
                    )
                    update_dataset(param_ms, param)
                    self.__add(key, item, param_ms)
                    return
        self.__add(key, item, param)

    def get(self, key: str) -> guidata.dataset.datatypes.DataSet:
        """
        Get parameters for a given item

        Args:
            key: key to identify the item
        """
        return deepcopy(self.paramdict.get(key))

    def update(self, plot: BasePlot) -> None:
        """
        Update plot items according to the parameters

        Args:
            plot: plot to be updated
        """
        for item in self.items:
            item.set_item_parameters(self)
        plot.replot()
        plot.SIG_ITEMS_CHANGED.emit(plot)

    def edit(self, plot: BasePlot, title: str, icon: str) -> None:
        """
        Edit parameters

        Args:
            plot: plot to be updated
            title: title of the dialog
            icon: icon of the dialog
        """
        paramdict = self.paramdict.copy()
        ending_parameters = []
        for key in self.ENDING_PARAMETERS:
            if key in paramdict:
                ending_parameters.append(paramdict.pop(key))
        parameters = list(paramdict.values()) + ending_parameters
        dset = DataSetGroup(parameters, title=title.rstrip("."), icon=icon)
        if dset.edit(parent=plot, apply=lambda dset: self.update(plot)):
            self.update(plot)


# ===================================================
# Common font parameters
# ===================================================
def _font_selection(param, item, value, parent):
    font = param.build_font()
    result, valid = QW.QFontDialog.getFont(font, parent)
    if valid:
        param.update_param(result)


class FontParam(DataSet):
    family = StringItem(_("Family"), default="default")
    _choose = ButtonItem(_("Choose font"), _font_selection, default=None).set_pos(col=1)
    size = IntItem(_("Size in point"), default=12)
    bold = BoolItem(_("Bold"), default=False).set_pos(col=1)
    italic = BoolItem(_("Italic"), default=False).set_pos(col=2)

    def update_param(self, font):
        """

        :param font:
        """
        self.family = str(font.family())
        self.size = font.pointSize()
        self.bold = bool(font.bold())
        self.italic = bool(font.italic())

    def build_font(self):
        """

        :return:
        """
        font = QG.QFont(self.family)
        font.setPointSize(self.size)
        font.setBold(self.bold)
        font.setItalic(self.italic)
        return font


class FontItemWidget(DataSetWidget):
    klass = FontParam


class FontItem(ObjectItem):
    """Item holding a LineStyleParam"""

    klass = FontParam


DataSetEditLayout.register(FontItem, FontItemWidget)


# ===================================================
# Common Qwt symbol parameters
# ===================================================
class SymbolParam(DataSet):
    marker = ImageChoiceItem(_("Style"), MARKER_CHOICES, default="NoSymbol")
    size = IntItem(_("Size"), default=9)
    edgecolor = ColorItem(_("Border"), default="gray")
    facecolor = ColorItem(_("Background color"), default="yellow")
    alpha = FloatItem(_("Background alpha"), default=1.0, min=0, max=1)

    def update_param(self, symb):
        """

        :param symb:
        :return:
        """
        if not isinstance(symb, QwtSymbol):
            # check if this is still needed
            # raise RuntimeError
            assert isinstance(symb, QwtSymbol.Style)
            self.marker = MARKER_NAME[symb]
            return
        self.marker = MARKER_NAME[symb.style()]
        self.size = symb.size().width()
        self.edgecolor = str(symb.pen().color().name())
        self.facecolor = str(symb.brush().color().name())

    def build_symbol(self):
        """

        :return:
        """
        marker_type = getattr(QwtSymbol, self.marker)
        color = QG.QColor(self.facecolor)
        color.setAlphaF(self.alpha)
        marker = QwtSymbol(
            marker_type,
            QG.QBrush(color),
            QG.QPen(QG.QColor(self.edgecolor)),
            QC.QSizeF(self.size, self.size),
        )
        return marker

    def update_symbol(self, obj):
        """

        :param obj:
        """
        obj.setSymbol(self.build_symbol())


class SymbolItemWidget(DataSetWidget):
    klass = SymbolParam


class SymbolItem(ObjectItem):
    """Item holding a SymbolParam"""

    klass = SymbolParam


DataSetEditLayout.register(SymbolItem, SymbolItemWidget)


# ===================================================
# Common line style parameters
# ===================================================
class LineStyleParam(DataSet):
    style = ImageChoiceItem(_("Style"), LINESTYLE_CHOICES, default="SolidLine")
    color = ColorItem(_("Color"), default="black")
    width = FloatItem(_("Width"), default=1.0, min=0)

    def update_param(self, pen):
        """

        :param pen:
        """
        self.width = pen.widthF()
        self.color = str(pen.color().name())
        self.style = LINESTYLE_NAME[pen.style()]

    def build_pen(self):
        """

        :return:
        """
        linecolor = QG.QColor(self.color)
        style = getattr(QC.Qt, self.style)
        pen = QG.QPen(linecolor, self.width, style)
        return pen

    def set_style_from_matlab(self, linestyle):
        """Eventually convert MATLAB-like linestyle into Qt linestyle"""
        linestyle = LINESTYLES.get(linestyle, linestyle)  # MATLAB-style
        if linestyle == "":  # MATLAB-style
            linestyle = "NoPen"
        self.style = linestyle


class LineStyleItemWidget(DataSetWidget):
    klass = LineStyleParam


class LineStyleItem(ObjectItem):
    """Item holding a LineStyleParam"""

    klass = LineStyleParam


DataSetEditLayout.register(LineStyleItem, LineStyleItemWidget)


# ===================================================
# Common brush style parameters
# ===================================================
class BrushStyleParam(DataSet):
    style = ImageChoiceItem(_("Style"), BRUSHSTYLE_CHOICES, default="SolidPattern")
    color = ColorItem(_("Color"), default="black")
    alpha = FloatItem(_("Alpha"), default=1.0)
    angle = FloatItem(_("Angle"), default=0.0, min=0)
    sx = FloatItem(_("sx"), default=1.0, min=0)
    sy = FloatItem(_("sy"), default=1.0, min=0)

    def update_param(self, brush):
        """

        :param brush:
        """
        tr = brush.transform()
        pt = tr.map(QC.QPointF(1.0, 0.0))
        self.sx = sqrt(pt.x() ** 2 + pt.y() ** 2)
        self.angle = 180 * atan2(pt.y(), pt.x()) / pi
        pt = tr.map(QC.QPointF(0.0, 1.0))
        self.sy = sqrt(pt.x() ** 2 + pt.y() ** 2)

        col = brush.color()
        self.color = str(col.name())
        self.alpha = col.alphaF()
        self.style = BRUSHSTYLE_NAME[brush.style()]

    def build_brush(self):
        """

        :return:
        """
        color = QG.QColor(self.color)
        color.setAlphaF(self.alpha)
        brush = QG.QBrush(color, getattr(QC.Qt, self.style))
        tr = QG.QTransform()
        tr = tr.scale(self.sx, self.sy)
        tr = tr.rotate(self.angle)
        brush.setTransform(tr)
        return brush


class BrushStyleItemWidget(DataSetWidget):
    klass = BrushStyleParam


class BrushStyleItem(ObjectItem):
    """Item holding a LineStyleParam"""

    klass = BrushStyleParam


DataSetEditLayout.register(BrushStyleItem, BrushStyleItemWidget)


# ===================================================
# QwtText parameters
# ===================================================
class TextStyleParam(DataSet):
    font = FontItem(_("Font"))
    textcolor = ColorItem(_("Text color"), default="blue")
    background_color = ColorItem(_("Background color"), default="white")
    background_alpha = FloatItem(_("Background alpha"), default=0.5, min=0, max=1)

    def update_param(self, obj):
        """obj: QwtText instance"""
        self.font.update_param(obj.font())
        self.textcolor = obj.color().name()
        color = obj.backgroundBrush().color()
        self.background_color = color.name()
        self.background_alpha = color.alphaF()

    def update_text(self, obj):
        """obj: QwtText instance"""
        obj.setColor(QG.QColor(self.textcolor))
        color = QG.QColor(self.background_color)
        color.setAlphaF(self.background_alpha)
        obj.setBackgroundBrush(QG.QBrush(color))
        font = self.font.build_font()
        obj.setFont(font)


class TextStyleItemWidget(DataSetWidget):
    klass = TextStyleParam


class TextStyleItem(ObjectItem):
    """Item holding a TextStyleParam"""

    klass = TextStyleParam


DataSetEditLayout.register(TextStyleItem, TextStyleItemWidget)


# ===================================================
# Grid parameters
# ===================================================
class GridParam(DataSet):
    background = ColorItem(_("Background color"), default="white")
    maj = BeginGroup(_("Major grid"))
    maj_xenabled = BoolItem(_("X Axis"), default=True)
    maj_yenabled = BoolItem(_("Y Axis"), default=True).set_pos(col=1)
    maj_line = LineStyleItem(_("Line"))
    _maj = EndGroup("end group")

    min = BeginGroup(_("Minor grid"))
    min_xenabled = BoolItem(_("X Axis"), default=False)
    min_yenabled = BoolItem(_("Y Axis"), default=False).set_pos(col=1)
    min_line = LineStyleItem(_("Line"))
    _min = EndGroup("fin groupe")

    def update_param(self, grid):
        """

        :param grid:
        """
        plot = grid.plot()
        if plot is not None:
            self.background = str(plot.canvasBackground().color().name())
        self.maj_xenabled = grid.xEnabled()
        self.maj_yenabled = grid.yEnabled()
        self.maj_line.update_param(grid.majorPen())
        self.min_xenabled = grid.xMinEnabled()
        self.min_yenabled = grid.yMinEnabled()
        self.min_line.update_param(grid.minorPen())

    def update_grid(self, grid):
        """

        :param grid:
        """
        plot = grid.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
            plot.setCanvasBackground(QG.QColor(self.background))
        grid.enableX(self.maj_xenabled)
        grid.enableY(self.maj_yenabled)
        grid.setPen(self.maj_line.build_pen())
        grid.enableXMin(self.min_xenabled)
        grid.enableYMin(self.min_yenabled)
        grid.setMinorPen(self.min_line.build_pen())
        grid.setTitle(self.get_title())
        if plot is not None:
            plot.blockSignals(False)
