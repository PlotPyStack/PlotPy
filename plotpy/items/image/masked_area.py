# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import guidata.dataset.io


class MaskedArea:
    """Defines masked areas for a masked image item

    Args:
        geometry: Geometry of the area ('rectangular' or anything else for circular)
        x0: X coordinate of first point
        y0: Y coordinate of first point
        x1: X coordinate of second point
        y1: Y coordinate of second point
        inside: True if the area is inside the geometry, False if it is outside
    """

    def __init__(
        self,
        geometry: str | None = None,
        x0: float | None = None,
        y0: float | None = None,
        x1: float | None = None,
        y1: float | None = None,
        inside: bool | None = None,
    ) -> None:
        self.geometry = geometry
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.inside = inside

    def __eq__(self, other):
        return (
            self.geometry == other.geometry
            and self.x0 == other.x0
            and self.y0 == other.y0
            and self.x1 == other.x1
            and self.y1 == other.y1
            and self.inside == other.inside
        )

    def serialize(
        self,
        writer: guidata.dataset.io.HDF5Writer
        | guidata.dataset.io.INIWriter
        | guidata.dataset.io.JSONWriter,
    ) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        for name in ("geometry", "inside", "x0", "y0", "x1", "y1"):
            writer.write(getattr(self, name), name)

    def deserialize(
        self,
        reader: guidata.dataset.io.HDF5Reader
        | guidata.dataset.io.INIReader
        | guidata.dataset.io.JSONReader,
    ) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        self.geometry = reader.read("geometry")
        self.inside = reader.read("inside")
        for name in ("x0", "y0", "x1", "y1"):
            setattr(self, name, reader.read(name, func=reader.read_float))
