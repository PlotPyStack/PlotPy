# -*- coding: utf-8 -*-

"""A custom QDoubleRangeSlider with some extra functionnalities for colormap sliders.
"""
from typing import Sequence

from plotpy.external.sliders import QDoubleRangeSlider


class QColorMapSlider(QDoubleRangeSlider):
    """Supercharged QDoubleRangeSlider with a few extra features for colormap
    sliders."""

    @property
    def pressed_index(self) -> int:
        """Simple getter for the index of the handle pressed by the user
        (mouse clicked).

        Returns:
            handled index
        """
        return self._pressedIndex

    def widget_pos_to_value(self, pos: int) -> float:
        """Returns the relative value of the slider at the given pixel position on the
        widget.

        Returns:
            slider value
        """
        return self._pixelPosToRangeValue(pos)

    def filter_first_last_positions(self, value: Sequence[float]) -> Sequence[float]:
        """Checks if the first and last handles are at the minimum and maximum values.
        If not, it sets them to the minimum and maximum values. This is required to
        prevent the application from crashing.

        Args:
            value: list of handle values

        Returns:
            Modified list of handle values if necessary
        """
        if value[0] != self._minimum or value[-1] != self._maximum:
            value = list(value)
            value[0], value[-1] = self._minimum, self._maximum
        return value

    def _setPosition(self, val: Sequence[float]) -> None:
        """Overload of the original _setPosition method to prevent the application from
        crashing if the first and last handles are moved.

        Args:
            value: list of handle values
        """
        return super()._setPosition(self.filter_first_last_positions(val))

    def setValue(self, value: Sequence[float]) -> None:
        """Overload of the original setValue method to prevent the application from
        crashing if the first and last handles are moved.

        Args:
            value: list of handle values
        """
        return super().setValue(self.filter_first_last_positions(value))
