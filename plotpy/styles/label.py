# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from guidata.dataset import (
    BeginGroup,
    BeginTabGroup,
    BoolItem,
    ChoiceItem,
    ColorItem,
    DataSet,
    EndGroup,
    EndTabGroup,
    FloatItem,
    GetAttrProp,
    IntItem,
    NotProp,
    Obj,
    StringItem,
    TextItem,
    update_dataset,
)
from qtpy import QtGui as QG

from plotpy.config import _
from plotpy.styles.base import FontItem, ItemParameters, LineStyleItem, SymbolItem

if TYPE_CHECKING:
    from plotpy.items import LabelItem, LegendBoxItem


class LabelParam(DataSet):
    """Parameters for a label item."""

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
    contents = TextItem("", default="").set_prop(
        "display", hide=GetAttrProp("_no_contents")
    )
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

    def update_param(self, item: LabelItem) -> None:
        """Update the parameters associated with the label item.

        Args:
            item: The label item from which to update the parameters.
        """
        # The following is necessary only for shape labels:
        # when shape is just created (and not yet moved), we need to update
        # these attributes
        update_dataset(self, item.labelparam)
        if self.abspos:
            self.absg = item.G
        else:
            self.xg, self.yg = item.G
        self.xc, self.yc = item.C
        self.label = item.title().text()

    def update_item(self, item: LabelItem) -> None:
        """Update the label item with the parameters.

        Args:
            item: The label item to update.
        """
        if not self._multiselection:
            if self.abspos:
                item.G = self.absg
            else:
                item.G = (self.xg, self.yg)
            item.C = self.xc, self.yc
            item.anchor = self.anchor
            item.setTitle(self.label)
        item.marker = self.symbol.build_symbol()
        item.border_pen = self.border.build_pen()
        item.set_text_style(self.font.build_font(), self.color)
        color = QG.QColor(self.bgcolor)
        color.setAlphaF(self.bgalpha)
        item.bg_brush = QG.QBrush(color)

    # TODO: remove this method in a future release
    def update_label(self, obj: LabelItem) -> None:
        """Update the label item with the parameters. This method is deprecated.

        Args:
            obj: The label item to update.
        """
        warnings.warn(
            "`LabelParam.update_label` method is deprecated and will be removed "
            "in a future release. Please use `update_item` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.update_item(obj)


class LabelParam_MS(LabelParam):
    """Parameters for a label item in multiselection mode."""

    _multiselection = True


ItemParameters.register_multiselection(LabelParam, LabelParam_MS)


class LegendParam(LabelParam):
    """Parameters for a legend box item."""

    _legend = True
    label = StringItem(_("Title"), default="").set_prop("display", hide=True)

    def update_item(self, item: LegendBoxItem) -> None:
        """Update the legend item with the parameters.

        Args:
            item: The legend item to update.
        """
        super().update_item(item)
        if not self._multiselection:
            item.setTitle(self.get_title())


class LegendParam_MS(LegendParam):
    """Parameters for a legend box item in multiselection mode."""

    _multiselection = True


ItemParameters.register_multiselection(LegendParam, LegendParam_MS)


class LabelParamWithContents(LabelParam):
    """Parameters for a label item with contents.

    Args:
        title: The title of the label item.
        comment: The comment associated with the label item.
        icon: The icon associated with the label item.
    """

    _no_contents = False

    def __init__(
        self, title: str | None = None, comment: str | None = None, icon: str = ""
    ) -> None:
        self.plain_text = None
        super().__init__(title, comment, icon)

    def update_param(self, item: LabelItem) -> None:
        """Update the parameters associated with the label item.

        Args:
            item: The label item from which to update the parameters.
        """
        super().update_param(item)
        self.contents = self.plain_text = item.get_plain_text()

    def update_item(self, item: LabelItem) -> None:
        """Update the label item with the parameters.

        Args:
            item: The label item to update.
        """
        super().update_item(item)
        if self.plain_text is not None and self.contents != self.plain_text:
            text = self.contents.replace("\n", "<br>")
            item.set_text(text)


class LabelParamWithContents_MS(LabelParamWithContents):
    """Parameters for a label item with contents in multiselection mode."""

    _multiselection = True


ItemParameters.register_multiselection(
    LabelParamWithContents, LabelParamWithContents_MS
)
