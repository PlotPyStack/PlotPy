# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
plotpy.widget.interfaces
-----------------------------

The `interfaces` module provides object interface classes for :mod:`plotpy`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    import guidata.dataset.io
    from qtpy.QtCore import QPointF

    from plotpy.styles.base import ItemParameters


class IItemType:
    """Item types are used to categorized items in a
    broader way than objects obeying IBasePlotItem.

    The necessity arises from the fact that Plotpy Items
    can inherit from different base classes and still
    provide functionalities akin to a given ItemType

    the types() method of an item returns a list of interfaces
    this item supports
    """


class ITrackableItemType(IItemType):
    def get_closest_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """
        Get the closest coordinates to the given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            tuple[float, float]: Closest coordinates
        """

    def get_coordinates_label(self, x: float, y: float) -> str:
        """
        Get the coordinates label for the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            str: Coordinates label
        """


class IDecoratorItemType(IItemType):
    """represents a decorative item (usually not active)
    such as grid, or axes markers"""


class ICurveItemType(IItemType):
    """A curve"""


class IImageItemType(IItemType):
    """An image"""


class IVoiImageItemType(IItemType):
    """An image with set_lut_range, get_lut_range"""

    def set_lut_range(self, lut_range: tuple[float, float]) -> None:
        """
        Set the current active lut range

        Args:
            lut_range: Lut range, tuple(min, max)

        Example:
            >>> item.set_lut_range((0.0, 1.0))
        """

    def get_lut_range(self) -> tuple[float, float]:
        """Get the current active lut range

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        return 0.0, 1.0

    def get_lut_range_full(self) -> tuple[float, float]:
        """Return full dynamic range

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        return 10.0, 20.0

    def get_lut_range_max(self) -> tuple[float, float]:
        """Get maximum range for this dataset

        Returns:
            tuple[float, float]: Lut range, tuple(min, max)
        """
        return 0.0, 255.0


class IColormapImageItemType(IItemType):
    """An image with an associated colormap"""


class IExportROIImageItemType(IItemType):
    """An image with export_roi"""

    def export_roi(
        self,
        src_rect: tuple[float, float, float, float],
        dst_rect: tuple[float, float, float, float],
        dst_image: np.ndarray,
        apply_lut: bool = False,
        apply_interpolation: bool = False,
        original_resolution: bool = False,
        force_interp_mode: str | None = None,
        force_interp_size: int | None = None,
    ) -> None:
        """
        Export a rectangular area of the image to another image

        Args:
            src_rect: Source rectangle
            dst_rect: Destination rectangle
            dst_image: Destination image
            apply_lut: Apply lut (Default value = False)
            apply_interpolation: Apply interpolation (Default value = False)
            original_resolution: Original resolution (Default value = False)
            force_interp_mode: Force interpolation mode (Default value = None)
            force_interp_size: Force interpolation size (Default value = None)
        """
        pass


class IStatsImageItemType(IItemType):
    """An image supporting stats computations"""

    def get_stats(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        show_surface: bool = False,
        show_integral: bool = False,
    ) -> str:
        """Return formatted string with stats on image rectangular area
        (output should be compatible with AnnotatedShape.get_infos)

        Args:
            x0: X0
            y0: Y0
            x1: X1
            y1: Y1
            show_surface: Show surface (Default value = False)
            show_integral: Show integral (Default value = False)
        """


class ICSImageItemType(IItemType):
    """An image supporting X/Y cross sections"""

    def get_xsection(self, y0: float | int, apply_lut: bool = False) -> np.ndarray:
        """Return cross section along x-axis at y=y0

        Args:
            y0: Y0
            apply_lut: Apply lut (Default value = False)

        Returns:
            np.ndarray: Cross section along x-axis at y=y0
        """

    def get_ysection(self, x0: float | int, apply_lut: bool = False) -> np.ndarray:
        """Return cross section along y-axis at x=x0

        Args:
            x0: X0
            apply_lut: Apply lut (Default value = False)

        Returns:
            np.ndarray: Cross section along y-axis at x=x0
        """

    def get_average_xsection(
        self, x0: float, y0: float, x1: float, y1: float, apply_lut: bool = False
    ) -> np.ndarray:
        """Return average cross section along x-axis for the given rectangle

        Args:
            x0: X0 of top left corner
            y0: Y0 of top left corner
            x1: X1 of bottom right corner
            y1: Y1 of bottom right corner
            apply_lut: Apply lut (Default value = False)

        Returns:
            np.ndarray: Average cross section along x-axis
        """

    def get_average_ysection(
        self, x0: float, y0: float, x1: float, y1: float, apply_lut: bool = False
    ) -> np.ndarray:
        """Return average cross section along y-axis

        Args:
            x0: X0 of top left corner
            y0: Y0 of top left corner
            x1: X1 of bottom right corner
            y1: Y1 of bottom right corner
            apply_lut: Apply lut (Default value = False)

        Returns:
            np.ndarray: Average cross section along y-axis
        """


class IShapeItemType(IItemType):
    """A shape (annotation)"""

    pass


class ISerializableType(IItemType):
    """An item that can be serialized"""

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


class IBasePlotItem:
    """
    This is the interface that QwtPlotItem objects must implement
    to be handled by *BasePlot* widgets
    """

    selected = False  # True if this item is selected
    _readonly = False
    _private = False
    _can_select = True  # Indicate this item can be selected
    _can_move = True
    _can_resize = True
    _can_rotate = True

    def set_selectable(self, state: bool) -> None:
        """Set item selectable state

        Args:
            state: True if item is selectable, False otherwise
        """
        self._can_select = state

    def set_resizable(self, state: bool) -> None:
        """Set item resizable state
        (or any action triggered when moving an handle, e.g. rotation)

        Args:
            state: True if item is resizable, False otherwise
        """
        self._can_resize = state

    def set_movable(self, state: bool) -> None:
        """Set item movable state

        Args:
            state: True if item is movable, False otherwise
        """
        self._can_move = state

    def set_rotatable(self, state: bool) -> None:
        """Set item rotatable state

        Args:
            state: True if item is rotatable, False otherwise
        """
        self._can_rotate = state

    def can_select(self) -> bool:
        """
        Returns True if this item can be selected

        Returns:
            bool: True if item can be selected, False otherwise
        """
        return self._can_select

    def can_resize(self) -> bool:
        """
        Returns True if this item can be resized

        Returns:
            bool: True if item can be resized, False otherwise
        """
        return self._can_resize

    def can_move(self) -> bool:
        """
        Returns True if this item can be moved

        Returns:
            bool: True if item can be moved, False otherwise
        """
        return self._can_move

    def can_rotate(self) -> bool:
        """
        Returns True if this item can be rotated

        Returns:
            bool: True if item can be rotated, False otherwise
        """
        return self._can_rotate

    def types(self) -> tuple[type[IItemType], ...]:
        """Returns a group or category for this item.
        This should be a tuple of class objects inheriting from IItemType

        Returns:
            tuple: Tuple of class objects inheriting from IItemType
        """

    def set_readonly(self, state: bool) -> None:
        """Set object readonly state

        Args:
            state: True if object is readonly, False otherwise
        """
        self._readonly = state

    def is_readonly(self) -> bool:
        """Return object readonly state

        Returns:
            bool: True if object is readonly, False otherwise
        """
        return self._readonly

    def set_private(self, state: bool) -> None:
        """Set object as private

        Args:
            state: True if object is private, False otherwise
        """
        self._private = state

    def is_private(self) -> bool:
        """Return True if object is private

        Returns:
            bool: True if object is private, False otherwise
        """
        return self._private

    def select(self) -> None:
        """
        Select the object and eventually change its appearance to highlight the
        fact that it's selected
        """
        # should call plot.invalidate() or replot to force redraw

    def unselect(self) -> None:
        """
        Unselect the object and eventually restore its original appearance to
        highlight the fact that it's not selected anymore
        """
        # should call plot.invalidate() or replot to force redraw

    def hit_test(self, pos: QPointF) -> tuple[float, float, bool, None]:
        """Return a tuple (distance, attach point, inside, other_object)

        Args:
            pos: Position

        Returns:
            tuple: Tuple with four elements: (distance, attach point, inside,
             other_object).

        Description of the returned values:

        * distance: distance in pixels (canvas coordinates) to the closest
           attach point
        * attach point: handle of the attach point
        * inside: True if the mouse button has been clicked inside the object
        * other_object: if not None, reference of the object which will be
           considered as hit instead of self
        """

    def update_item_parameters(self) -> None:
        """Update item parameters (dataset) from object properties"""

    def get_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Appends datasets to the list of DataSets describing the parameters
        used to customize apearance of this item

        Args:
            itemparams: Item parameters
        """

    def set_item_parameters(self, itemparams: ItemParameters) -> None:
        """
        Change the appearance of this item according
        to the parameter set provided

        Args:
            itemparams: Item parameters
        """

    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """


class IBaseImageItem:
    """
    QwtPlotItem image objects handled by *BasePlot* widgets must implement
    _both_ the IBasePlotItem interface and this one
    """

    _can_sethistogram = False  # A levels histogram will be bound to image

    def can_sethistogram(self) -> bool:
        """
        Returns True if this item can be associated with a levels histogram

        Returns:
            bool: True if item can be associated with a levels histogram,
             False otherwise
        """
        return self._can_sethistogram


class IHistDataSource:
    def get_histogram(
        self, nbins: int, drange: tuple[float, float] | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Return a tuple (hist, bins) where hist is a list of histogram values

        Args:
            nbins: number of bins
            drange: lower and upper range of the bins. If not provided, range is
             simply (data.min(), data.max()). Values outside the range are ignored.

        Returns:
            Tuple (hist, bins)

        Example of implementation:

        def get_histogram(self, nbins, drange=None):
            data = self.get_data()
            return np.histogram(data, bins=nbins, range=drange)
        """
        pass
