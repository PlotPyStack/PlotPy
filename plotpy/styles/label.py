# -*- coding: utf-8 -*-
from guidata.dataset.dataitems import (
    BoolItem,
    ChoiceItem,
    ColorItem,
    FloatItem,
    IntItem,
    StringItem,
    TextItem,
)
from guidata.dataset.datatypes import (
    BeginGroup,
    BeginTabGroup,
    DataSet,
    EndGroup,
    EndTabGroup,
    GetAttrProp,
    NotProp,
    Obj,
)
from guidata.utils import update_dataset
from qtpy import QtGui as QG

from plotpy.config import _
from plotpy.styles.base import FontItem, ItemParameters, LineStyleItem, SymbolItem


class LabelParam(DataSet):
    _multiselection = False
    _legend = False
    _no_contents = True
    label = StringItem(_("Title"), default="").set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )

    _styles = BeginTabGroup("Styles")
    # -------------------------------------------------------------- Contents tab
    ___cont = BeginGroup(_("Contents")).set_prop(
        "display", icon="label.png", hide=GetAttrProp("_no_contents")
    )
    contents = TextItem("").set_prop("display", hide=GetAttrProp("_no_contents"))
    ___econt = EndGroup(_("Contents")).set_prop(
        "display", hide=GetAttrProp("_no_contents")
    )
    # ---------------------------------------------------------------- Symbol tab
    symbol = SymbolItem(_("Symbol")).set_prop(
        "display", icon="diamond.png", hide=GetAttrProp("_legend")
    )
    # ---------------------------------------------------------------- Border tab
    border = LineStyleItem(
        _("Border"), default=Obj(color="#cbcbcb"), help=_("set width to 0 to disable")
    ).set_prop("display", icon="dashdot.png")
    # ------------------------------------------------------------------ Text tab
    ___text = BeginGroup(_("Text")).set_prop("display", icon="font.png")
    font = FontItem(_("Text font"))
    color = ColorItem(_("Text color"), default="#000000")
    bgcolor = ColorItem(_("Background color"), default="#ffffff")
    bgalpha = FloatItem(_("Background transparency"), min=0.0, max=1.0, default=0.8)
    ___etext = EndGroup(_("Text"))
    # -------------------------------------------------------------- Position tab
    ___position = BeginGroup(_("Position")).set_prop("display", icon="move.png")
    _begin_anchor = BeginGroup(_("Position relative to anchor")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    anchor = ChoiceItem(
        _("Corner"),
        [
            ("TL", _("Top left")),
            ("TR", _("Top right")),
            ("BL", _("Bottom left")),
            ("BR", _("Bottom right")),
            ("L", _("Left")),
            ("R", _("Right")),
            ("T", _("Top")),
            ("B", _("Bottom")),
            ("C", _("Center")),
        ],
        default="TL",
        help=_("Label position relative to anchor point"),
    ).set_prop("display", hide=GetAttrProp("_multiselection"))
    xc = IntItem(
        _("ΔX"),
        default=5,
        help=_("Horizontal offset (pixels) relative to anchor point"),
    ).set_prop("display", hide=GetAttrProp("_multiselection"))
    yc = (
        IntItem(
            _("ΔY"),
            default=5,
            help=_("Vertical offset (pixels) relative to anchor point"),
        )
        .set_pos(col=1)
        .set_prop("display", hide=GetAttrProp("_multiselection"))
    )
    _end_anchor = EndGroup(_("Anchor")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    _begin_anchorpos = BeginGroup(_("Anchor position")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    _abspos_prop = GetAttrProp("abspos")
    abspos = (
        BoolItem(text=_("Attach to canvas"), label=_("Anchor"), default=True)
        .set_prop("display", store=_abspos_prop)
        .set_prop("display", hide=GetAttrProp("_multiselection"))
    )
    xg = (
        FloatItem(_("X"), default=0.0, help=_("X-axis position in canvas coordinates"))
        .set_prop("display", active=NotProp(_abspos_prop))
        .set_prop("display", hide=GetAttrProp("_multiselection"))
    )
    yg = (
        FloatItem(_("Y"), default=0.0, help=_("Y-axis position in canvas coordinates"))
        .set_pos(col=1)
        .set_prop("display", active=NotProp(_abspos_prop))
        .set_prop("display", hide=GetAttrProp("_multiselection"))
    )
    move_anchor = (
        ChoiceItem(
            _("Interact"),
            (
                (True, _("moving object changes anchor position")),
                (False, _("moving object changes label position")),
            ),
            default=True,
        )
        .set_prop("display", active=NotProp(_abspos_prop))
        .set_prop("display", hide=GetAttrProp("_multiselection"))
    )
    absg = (
        ChoiceItem(
            _("Position"),
            [
                ("TL", _("Top left")),
                ("TR", _("Top right")),
                ("BL", _("Bottom left")),
                ("BR", _("Bottom right")),
                ("L", _("Left")),
                ("R", _("Right")),
                ("T", _("Top")),
                ("B", _("Bottom")),
                ("C", _("Center")),
            ],
            default="TL",
            help=_("Absolute position on canvas"),
        )
        .set_prop("display", active=_abspos_prop)
        .set_prop("display", hide=GetAttrProp("_multiselection"))
    )
    _end_anchorpos = EndGroup(_("Anchor position")).set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )
    ___eposition = EndGroup(_("Position"))
    # ----------------------------------------------------------------------- End
    _endstyles = EndTabGroup("Styles")

    def update_param(self, obj):
        """

        :param obj:
        """
        # The following is necessary only for shape labels:
        # when shape is just created (and not yet moved), we need to update
        # these attributes
        update_dataset(self, obj.labelparam)
        if self.abspos:
            self.absg = obj.G
        else:
            self.xg, self.yg = obj.G
        self.xc, self.yc = obj.C
        self.label = obj.title().text()

    def update_label(self, obj):
        """

        :param obj:
        """
        if not self._multiselection:
            if self.abspos:
                obj.G = self.absg
            else:
                obj.G = (self.xg, self.yg)
            obj.C = self.xc, self.yc
            obj.anchor = self.anchor
            obj.move_anchor = self.move_anchor
            obj.setTitle(self.label)
        obj.marker = self.symbol.build_symbol()
        obj.border_pen = self.border.build_pen()
        obj.set_text_style(self.font.build_font(), self.color)
        color = QG.QColor(self.bgcolor)
        color.setAlphaF(self.bgalpha)
        obj.bg_brush = QG.QBrush(color)


class LabelParam_MS(LabelParam):
    _multiselection = True


ItemParameters.register_multiselection(LabelParam, LabelParam_MS)


class LegendParam(LabelParam):
    _legend = True
    label = StringItem(_("Title"), default="").set_prop("display", hide=True)

    def update_label(self, obj):
        """

        :param obj:
        """
        super().update_label(obj)
        if not self._multiselection:
            obj.setTitle(self.get_title())


class LegendParam_MS(LegendParam):
    _multiselection = True


ItemParameters.register_multiselection(LegendParam, LegendParam_MS)


class LabelParamWithContents(LabelParam):
    """ """

    _no_contents = False

    def __init__(self, title=None, comment=None, icon=""):
        self.plain_text = None
        super().__init__(title, comment, icon)

    def update_param(self, obj):
        """

        :param obj:
        """
        super().update_param(obj)
        self.contents = self.plain_text = obj.get_plain_text()

    def update_label(self, obj):
        """

        :param obj:
        """
        super().update_label(obj)
        if self.plain_text is not None and self.contents != self.plain_text:
            text = self.contents.replace("\n", "<br>")
            obj.set_text(text)


class LabelParamWithContents_MS(LabelParamWithContents):
    _multiselection = True


ItemParameters.register_multiselection(
    LabelParamWithContents, LabelParamWithContents_MS
)
