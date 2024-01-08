from typing import Sequence

import qtpy.QtCore as QC
import qtpy.QtGui as QG
import qtpy.QtWidgets as QW

from plotpy.widgets.external.sliders import QDoubleRangeSlider


class QColorMapSlider(QDoubleRangeSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def pressed_index(self):
        return self._pressedIndex

    def widget_pos_to_value(self, pos: int) -> float:
        return self._pixelPosToRangeValue(pos)

    def filter_first_last_positions(self, value: Sequence[float]) -> Sequence[float]:
        if value[0] != self._minimum or value[-1] != self._maximum:
            value = list(value)
            value[0], value[-1] = self._minimum, self._maximum
        return value

    def _setPosition(self, value: Sequence[float]) -> None:
        return super()._setPosition(self.filter_first_last_positions(value))

    def setValue(self, value: Sequence[float]) -> None:
        return super().setValue(self.filter_first_last_positions(value))
