# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Label Item builder
------------------

This module provides a set of factory functions to simplify the creation
of label items.
"""

# Note: when adding method to builder classes, please do not forget to update the
# documentation (see builder.rst file). Because of class inheritance, the methods
# are not automatically documented (otherwise, they would be sorted alphabetically,
# due to a limitation of sphinx auto-doc).

from __future__ import annotations

from collections.abc import Callable

from plotpy.config import CONF, _, make_title
from plotpy.items import (
    CurveItem,
    DataInfoLabel,
    ImageItem,
    LabelItem,
    LegendBoxItem,
    RangeComputation,
    RangeComputation2d,
    RangeInfo,
    RectangleShape,
    SelectedLegendBoxItem,
    XRangeSelection,
)
from plotpy.styles import LabelParam, LabelParamWithContents, LegendParam

# default offset positions for anchors
ANCHOR_OFFSETS = {
    "TL": (5, 5),
    "TR": (-5, 5),
    "BL": (5, -5),
    "BR": (-5, -5),
    "L": (5, 0),
    "R": (-5, 0),
    "T": (0, 5),
    "B": (0, -5),
}

LABEL_COUNT = 0


class LabelBuilder:
    """Class regrouping a set of factory functions to simplify the creation
    of label items."""

    def label(
        self,
        text: str,
        g: tuple[float, float] | str,
        c: tuple[int, int],
        anchor: str,
        title: str = "",
    ) -> LabelItem:
        """Make a label `plot item`

        Args:
            text: label text
            g: position in plot coordinates or relative position (string)
            c: position in canvas coordinates
            anchor: anchor position in relative position (string)
            title: label title. Default is ''

        Returns:
            :py:class:`.LabelItem` object

        Examples::
            make.label("Relative position", (x[0], y[0]), (10, 10), "BR")
            make.label("Absolute position", "R", (0,0), "R")
        """
        basename = _("Label")
        param = LabelParamWithContents(basename, icon="label.png")
        param.read_config(CONF, "plot", "label")
        if title:
            param.label = title
        else:
            global LABEL_COUNT
            LABEL_COUNT += 1
            param.label = make_title(basename, LABEL_COUNT)
        if isinstance(g, tuple):
            param.abspos = False
            param.xg, param.yg = g
        else:
            param.abspos = True
            param.absg = g
        if c is None:
            c = ANCHOR_OFFSETS[anchor]
        param.xc, param.yc = c
        param.anchor = anchor
        return LabelItem(text, param)

    def legend(
        self,
        anchor: str = "TR",
        c: tuple[int, int] | None = None,
        restrict_items: list | None = None,
    ) -> LegendBoxItem | SelectedLegendBoxItem:
        """Make a legend `plot item`

        Args:
            anchor: legend position in relative position (string)
            c: position in canvas coordinates
            restrict_items: list of items to be shown in legend box.
             Default is None. If None, all items are shown in legend box.
             If [], no item is shown in legend box. If [item1, item2],
             item1, item2 are shown in legend box.

        Returns:
            :py:class:`.LegendBoxItem` or
            :py:class:`.SelectedLegendBoxItem` object
        """
        param = LegendParam(_("Legend"), icon="legend.png")
        param.read_config(CONF, "plot", "legend")
        param.abspos = True
        param.absg = anchor
        param.anchor = anchor
        if c is None:
            c = ANCHOR_OFFSETS[anchor]
        param.xc, param.yc = c
        if restrict_items is None:
            return LegendBoxItem(param)
        else:
            return SelectedLegendBoxItem(param, restrict_items)

    def info_label(
        self, anchor: str, comps: list, title: str | None = None
    ) -> DataInfoLabel:
        """Make an info label `plot item`

        Args:
            anchor: anchor position. See :py:class:`.LabelParam` for details
            comps: list of :py:class:`.label.RangeComputation` objects
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        basename = _("Computation")
        param = LabelParam(basename, icon="label.png")
        param.read_config(CONF, "plot", "info_label")
        if title is not None:
            param.label = title
        else:
            global LABEL_COUNT
            LABEL_COUNT += 1
            param.label = make_title(basename, LABEL_COUNT)
        param.abspos = True
        param.absg = anchor
        param.anchor = anchor
        c = ANCHOR_OFFSETS[anchor]
        param.xc, param.yc = c
        return DataInfoLabel(param, comps)

    def range_info_label(
        self,
        range: XRangeSelection,
        anchor: str,
        label: str,
        function: Callable = None,
        title: str | None = None,
    ) -> DataInfoLabel:
        """Make an info label `plot item` showing an XRangeSelection object infos

        Args:
            range: range selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            label: label name. See :py:class:`.DataInfoLabel` for details
            function: function to apply to the range selection object
             Default is None (default function is `lambda x, dx: (x, dx)`)
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object

        Example::

            x = linspace(-10, 10, 10)
            y = sin(sin(sin(x)))
            range = make.range(-2, 2)
            disp = make.range_info_label(range, 'BL', "x = %.1f ± %.1f cm",
                                         lambda x, dx: (x, dx))
        """
        info = RangeInfo(label, range, function)
        return self.info_label(anchor, info, title=title)

    def computation(
        self,
        range: XRangeSelection,
        anchor: str,
        label: str,
        curve: CurveItem,
        function: Callable,
        title: str | None = None,
    ) -> DataInfoLabel:
        """Make a computation label `plot item`

        Args:
            range: range selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            label: label name. See :py:class:`.DataInfoLabel` for details
            curve: curve item
            function: function to apply to the range selection object
             Default is None (default function is `lambda x, dx: (x, dx)`)

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        if title is None:
            title = curve.param.label
        return self.computations(range, anchor, [(curve, label, function)], title=title)

    def computations(
        self, range: XRangeSelection, anchor: str, specs: list, title: str | None = None
    ) -> DataInfoLabel:
        """Make computation labels  `plot item`

        Args:
            range: range selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            specs: list of (curve, label, function) tuples
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        comps = []
        same_curve = True
        curve0 = None
        for curve, label, function in specs:
            comp = RangeComputation(label, curve, range, function)
            comps.append(comp)
            if curve0 is None:
                curve0 = curve
            same_curve = same_curve and curve is curve0
        if title is None and same_curve:
            title = curve.param.label
        return self.info_label(anchor, comps, title=title)

    def computation2d(
        self,
        rect: RectangleShape,
        anchor: str,
        label: str,
        image: ImageItem,
        function: Callable,
        title: str | None = None,
    ) -> RangeComputation2d:
        """Make a 2D computation label `plot item`

        Args:
            rect: rectangle selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            label: label name. See :py:class:`.DataInfoLabel` for details
            image: image item
            function: function to apply to the rectangle selection object
             Default is None (default function is `lambda x, dx: (x, dx)`)
            title: label name. Default is None

        Returns:
            :py:class:`.RangeComputation2d` object
        """
        return self.computations2d(
            rect, anchor, [(image, label, function)], title=title
        )

    def computations2d(
        self, rect: RectangleShape, anchor: str, specs: list, title: str | None = None
    ) -> DataInfoLabel:
        """Make 2D computation labels `plot item`

        Args:
            rect: rectangle selection object
            anchor: anchor position. See :py:class:`.LabelParam` for details
            specs: list of (image, label, function) tuples
            title: label name. Default is None

        Returns:
            :py:class:`.DataInfoLabel` object
        """
        comps = []
        same_image = True
        image0 = None
        for image, label, function in specs:
            comp = RangeComputation2d(label, image, rect, function)
            comps.append(comp)
            if image0 is None:
                image0 = image
            same_image = same_image and image is image0
        if title is None and same_image:
            title = image.param.label
        return self.info_label(anchor, comps, title=title)
