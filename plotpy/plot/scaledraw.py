# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Scale draw classes for custom axis formatting"""

from __future__ import annotations

from datetime import datetime

from qtpy import QtCore as QC
from qwt import QwtScaleDraw, QwtText


class DateTimeScaleDraw(QwtScaleDraw):
    """Scale draw for datetime axis

    This class formats axis labels as date/time strings from Unix timestamps.

    Args:
        format: Format string for datetime display (default: "%Y-%m-%d %H:%M:%S").
                Uses Python datetime.strftime() format codes.
        rotate: Rotation angle for labels in degrees (default: -45)
        spacing: Spacing between labels (default: 4)

    Examples:
        >>> # Create a datetime scale with default format
        >>> scale = DateTimeScaleDraw()

        >>> # Create a datetime scale with custom format (time only)
        >>> scale = DateTimeScaleDraw(format="%H:%M:%S")

        >>> # Create a datetime scale with date only
        >>> scale = DateTimeScaleDraw(format="%Y-%m-%d", rotate=0)
    """

    def __init__(
        self,
        format: str = "%Y-%m-%d %H:%M:%S",
        rotate: float = -45,
        spacing: int = 4,
    ):
        super().__init__()
        self._format = format
        self.setLabelRotation(rotate)
        self.setLabelAlignment(QC.Qt.AlignHCenter | QC.Qt.AlignVCenter)
        self.setSpacing(spacing)

    def label(self, value: float) -> QwtText:
        """Convert a timestamp value to a formatted date/time label

        Args:
            value: Unix timestamp (seconds since epoch)

        Returns:
            QwtText: Formatted label
        """
        try:
            dt = datetime.fromtimestamp(value)
            return QwtText(dt.strftime(self._format))
        except (ValueError, OSError):
            # Handle invalid timestamps
            return QwtText("")

    def get_format(self) -> str:
        """Get the current datetime format string

        Returns:
            str: Format string
        """
        return self._format

    def set_format(self, format: str) -> None:
        """Set the datetime format string

        Args:
            format: Format string for datetime display
        """
        self._format = format
