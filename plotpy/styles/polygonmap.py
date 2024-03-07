# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.dataset import DataSet, GetAttrProp, StringItem

from plotpy.config import _
from plotpy.styles.base import ItemParameters

if TYPE_CHECKING:
    from plotpy.items import PolygonMapItem


class PolygonMapParam(DataSet):
    """Dataset defining the parameters of a PolygonMapItem instance"""

    _multiselection = False
    label = StringItem(_("Title"), default="").set_prop(
        "display", hide=GetAttrProp("_multiselection")
    )

    def update_param(self, item: PolygonMapItem) -> None:
        """Updates the parameters using values from a given PolygonMapItem

        Args:
            item: reference PolygonMapItem instance
        """
        self.label = str(item.title().text())

    def update_item(self, item: PolygonMapItem) -> None:
        """Updates a given PolygonMapItem using the current parameters

        Args:
            item: instance of PolygonMapItem to update
        """
        plot = item.plot()
        if plot is not None:
            plot.blockSignals(True)  # Avoid unwanted calls of update_param
            # triggered by the setter methods below
        if not self._multiselection:
            # Non common parameters
            item.setTitle(self.label)
        if plot is not None:
            plot.blockSignals(False)


class PolygonParam_MS(PolygonMapParam):
    """Same as PolygonParam but for multiselection"""

    _multiselection = True


ItemParameters.register_multiselection(PolygonMapParam, PolygonParam_MS)
