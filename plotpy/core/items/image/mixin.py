# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from qtpy import QtCore as QC

from plotpy.core import io
from plotpy.core.coords import axes_to_canvas, canvas_to_axes
from plotpy.core.items.image.masked_area import MaskedArea
from plotpy.utils.geometry import colvector, rotate, scale, translate

if TYPE_CHECKING:
    from guidata.dataset.io import (
        HDF5Reader,
        HDF5Writer,
        INIReader,
        INIWriter,
        JSONReader,
        JSONWriter,
    )
    from qtpy.QtCore import QPointF


class TransformImageMixin:
    """Mixin that provides utilities to move/rotate/resize an image based
    on a transformation matrix.

    Subclass must initialize an attribute named *points* defined as the matrix::

        [
            [xmin, xmin, xmax, xmax],
            [ymin, ymax, ymax, ymin],
            [1, 1, 1, 1]
        ]

    where xmin, max, ymin, ymax are initial plot coordinates of the bounding image.

    This matrix must be updated when data are updated.

    Param class must define the method ``set_transform`` and ``get_transform`` to
    store the transformation matrix.

    The transformation matrix is defined by the **tr** and **itr** attributes.

    """

    _trx = 0  # subclass can update this to translate the image by .5 pixels
    _try = 0

    _can_move = True
    _can_resize = True
    _can_select = True
    _can_rotate = True

    def set_transform(self, x0, y0, angle, dx=1.0, dy=1.0, hflip=False, vflip=False):
        """
        Set the transformation

        :param x0: X translation
        :param y0: Y translation
        :param angle: rotation angle in radians
        :param dx: X-scaling factor
        :param dy: Y-scaling factor
        :param hflip: True if image if flip horizontally
        :param vflip: True if image is flip vertically
        """
        self.param.set_transform(x0, y0, angle, dx, dy, hflip, vflip)
        if self.data is None:
            return
        ni, nj = self.data.shape
        rot = rotate(-angle)
        tr1 = translate(nj / 2.0 + 0.5, ni / 2.0 + 0.5)
        xflip = -1.0 if hflip else 1.0
        yflip = -1.0 if vflip else 1.0
        sc = scale(xflip / dx, yflip / dy)
        tr2 = translate(-x0, -y0)
        self.tr = tr1 * sc * rot * tr2
        self.itr = self.tr.I
        self.compute_bounds()

    def get_transform(self):
        """
        Return the transformation parameters

        :return: tuple (x0, y0, angle, dx, dy, hflip, yflip)
        """
        return self.param.get_transform()

    def compute_bounds(self):
        """Compute the bounding box and border rect"""
        self.update_bounds()
        self.update_border()

    def update_bounds(self):
        """
        Update the bounding box after applying the transformation matrix
        """

        points = np.dot(self.itr, self.points)
        xmin = points[0].min()
        xmax = points[0].max()
        ymin = points[1].min()
        ymax = points[1].max()
        self.bounds = QC.QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def update_border(self):
        """
        Update the points of the border after applying the transformation matrix
        """
        tpos = np.dot(self.itr, self.points)
        self.border_rect.set_points(tpos.T[:, :2])

    def debug_transform(self, pt):  # pragma: no cover
        """
        Print debug data on how the given point is moved.

        :param pt: array (x, y, z=1)
        """
        x0, y0, angle, dx, dy, _hflip, _vflip = self.get_transform()
        rot = rotate(-angle)
        xmin = self.points[0].min()
        xmax = self.points[0].max()
        ymin = self.points[1].min()
        ymax = self.points[1].max()
        a, b = (xmax - xmin) / 2.0 + self._trx, (ymax - ymin) / 2.0 + self._try
        tr1 = translate(xmin + a, ymin + b)
        sc = scale(dx, dy)
        tr2 = translate(-x0, -y0)
        p1 = tr1.I * pt
        p2 = rot.I * pt
        p3 = sc.I * pt
        p4 = tr2.I * pt
        print("src=", pt.T)
        print("tr1:", p1.T)
        print("tr1+rot:", p2.T)
        print("tr1+rot+sc:", p3.T)
        print("tr1+rot+tr2:", p4.T)

    # ---- IBasePlotItem API ---------------------------------------------------
    def move_local_point_to(self, handle: int, pos: QPointF, ctrl: bool = None) -> None:
        """Move a handle as returned by hit_test to the new position

        Args:
            handle: Handle
            pos: Position
            ctrl: True if <Ctrl> button is being pressed, False otherwise
        """
        if self.is_locked():
            return
        x0, y0, angle, dx, dy, hflip, vflip = self.get_transform()
        nx, ny = canvas_to_axes(self, pos)
        handles = self.itr * self.points
        p0 = colvector(nx, ny)
        if self.can_rotate():
            if self.rotation_point is None:
                self.set_rotation_point_to_center()
            vec0 = handles[:, handle] - self.rotation_point
            vec1 = p0 - self.rotation_point
            a0 = np.arctan2(vec0[1], vec0[0])
            a1 = np.arctan2(vec1[1], vec1[0])
            # compute angles
            angle = float(angle + a1 - a0)
            tr1 = translate(-self.rotation_point[0], -self.rotation_point[1])
            rot = rotate(a1 - a0)
            tr = tr1.I * rot * tr1
            vc = colvector(x0, y0)
            new_vc = tr.A.dot(vc)
            x0, y0 = new_vc[0], new_vc[1]
            if self.plot():
                self.plot().SIG_ITEM_ROTATED.emit(self, angle)

        if self.can_resize():
            if self.rotation_point is None:
                self.set_rotation_point_to_center()
            center = handles.sum(axis=1) / 4
            vec0 = handles[:, handle] - center
            vec1 = p0 - center
            # compute pixel size
            zoom = np.linalg.norm(vec1) / np.linalg.norm(vec0)
            dx = float(zoom * dx)
            dy = float(zoom * dy)
            self.rotation_point[0] = (
                center.item(0) + (self.rotation_point[0] - center.item(0)) * zoom
            )
            self.rotation_point[1] = (
                center.item(1) + (self.rotation_point[1] - center.item(1)) * zoom
            )
            if self.plot():
                self.plot().SIG_ITEM_RESIZED.emit(self, zoom, zoom)
        self.set_transform(x0, y0, angle, dx, dy, hflip, vflip)

    def move_local_shape(self, old_pos: QPointF, new_pos: QPointF) -> None:
        """Translate the shape such that old_pos becomes new_pos in canvas coordinates

        Args:
            old_pos: Old position
            new_pos: New position
        """
        if self.is_locked():
            return
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        x0, y0, angle, dx, dy, hflip, vflip = self.get_transform()
        nx, ny = canvas_to_axes(self, new_pos)
        ox, oy = canvas_to_axes(self, old_pos)
        self.set_transform(x0 + nx - ox, y0 + ny - oy, angle, dx, dy, hflip, vflip)
        if self.rotation_point_move_with_shape:
            self.rotation_point[0] = self.rotation_point[0] + nx - ox
            self.rotation_point[1] = self.rotation_point[1] + ny - oy
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, ox, oy, nx, ny)

    def rotate_local_shape(self, old_pos, new_pos):
        """Contrairement à move_local_point_to, le déplacement se fait
        entre les deux positions et non pas depuis un handle jusqu'à un point"""
        if self.is_locked():
            return
        if not self.can_rotate():
            return
        x0, y0, angle, dx, dy, hflip, vflip = self.get_transform()
        nx, ny = canvas_to_axes(self, new_pos)
        ox, oy = canvas_to_axes(self, old_pos)
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        vec0 = colvector(ox, oy) - self.rotation_point
        vec1 = colvector(nx, ny) - self.rotation_point
        a0 = np.arctan2(vec0[1, 0], vec0[0, 0])
        a1 = np.arctan2(vec1[1, 0], vec1[0, 0])
        # compute angles
        angle += a1 - a0
        angle = float(angle)
        tr1 = translate(-self.rotation_point[0], -self.rotation_point[1])
        rot = rotate(a1 - a0)
        tr = tr1.I * rot * tr1
        vc = colvector(x0, y0)
        new_vc = tr * vc
        x0, y0 = float(new_vc[0]), float(new_vc[1])
        if self.plot():
            self.plot().SIG_ITEM_ROTATED.emit(self, angle)
        self.set_transform(x0, y0, angle, dx, dy, hflip, vflip)

    def move_with_arrows(self, dx, dy):
        """Translate the shape with arrows in canvas coordinates"""
        if not self.can_move() or self.is_locked():
            return
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        x0, y0, _angle, _dx, _dy, _hflip, _vflip = self.get_transform()
        old_pos = QC.QPointF(*axes_to_canvas(self, x0, y0))
        new_pos = QC.QPointF(old_pos.x() + dx, old_pos.y() + dy)
        nx, ny = canvas_to_axes(self, new_pos)
        ox, oy = canvas_to_axes(self, old_pos)
        self.set_transform(nx, ny, _angle, _dx, _dy, _hflip, _vflip)
        if self.rotation_point_move_with_shape:
            self.rotation_point[0] = self.rotation_point[0] + nx - ox
            self.rotation_point[1] = self.rotation_point[1] + ny - oy
        if self.plot():
            self.plot().SIG_ITEM_MOVED.emit(self, ox, oy, nx, ny)

    def rotate_with_arrows(self, dangle):
        """
        Rotate the shape with arrows in canvas coordinates
        angle0 : old rotation angle
        angle1 : new rotation angle
        """
        if not self.can_rotate() or self.is_locked():
            return
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        x0, y0, angle0, dx, dy, hflip, vflip = self.get_transform()

        tr1 = translate(-self.rotation_point[0], -self.rotation_point[1])
        rot = rotate(dangle)
        tr = tr1.I * rot * tr1
        vc = colvector(x0, y0)
        new_vc = tr * vc
        x0, y0 = float(new_vc[0]), float(new_vc[1])
        new_angle = angle0 + dangle
        self.set_transform(x0, y0, angle0 + dangle, dx, dy, hflip, vflip)
        if self.plot():
            self.plot().SIG_ITEM_ROTATED.emit(self, new_angle)

    def move_with_selection(self, delta_x: float, delta_y: float) -> None:
        """Translate the item together with other selected items

        Args:
            delta_x: Translation in plot coordinates along x-axis
            delta_y: Translation in plot coordinates along y-axis
        """
        if self.is_locked():
            return
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        x0, y0, angle, dx, dy, hflip, vflip = self.get_transform()
        if self.rotation_point_move_with_shape:
            self.rotation_point[0] = self.rotation_point[0] + delta_x
            self.rotation_point[1] = self.rotation_point[1] + delta_y
        self.set_transform(x0 + delta_x, y0 + delta_y, angle, dx, dy, hflip, vflip)

    def resize_with_selection(self, zoom_dx, zoom_dy):
        """
        Resize the shape together with other selected items
        zoom_dx, zoom_dy : zoom factor for dx and dy
        """
        if self.is_locked():
            return
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        x0, y0, angle, dx, dy, hflip, vflip = self.get_transform()
        handles = self.itr * self.points
        center = handles.sum(axis=1) / 4
        if self.rotation_point_move_with_shape:
            self.rotation_point[0] = (
                center[0] + (self.rotation_point[0] - center[0]) * zoom_dx
            )
            self.rotation_point[1] = (
                center[1] + (self.rotation_point[1] - center[1]) * zoom_dy
            )
        self.set_transform(x0, y0, angle, zoom_dx * dx, zoom_dy * dy, hflip, vflip)

    def rotate_with_selection(self, angle):
        """
        Rotate the shape together with other selected items
        angle0 : old rotation angle
        angle1 : new rotation angle
        """
        if self.is_locked():
            return
        if self.rotation_point is None:
            self.set_rotation_point_to_center()
        x0, y0, angle0, dx, dy, hflip, vflip = self.get_transform()
        dangle = float(angle - angle0)
        tr1 = translate(-self.rotation_point[0], -self.rotation_point[1])
        rot = rotate(dangle)
        tr = tr1.I * rot * tr1
        vc = colvector(x0, y0)
        new_vc = tr * vc
        x0, y0 = float(new_vc[0]), float(new_vc[1])
        self.set_transform(x0, y0, angle, dx, dy, hflip, vflip)


class ImageMixin:
    """
    Extract of old TransformImageMixin to allow to code to work properly
    """

    _trx = 0  # subclass can update this to translate the image by .5 pixels
    _try = 0

    def set_transform(self, x0, y0, angle, dx=1.0, dy=1.0, hflip=False, vflip=False):
        """
        Set the transformation

        :param x0: X translation
        :param y0: Y translation
        :param angle: rotation angle in radians
        :param dx: X-scaling factor
        :param dy: Y-scaling factor
        :param hflip: True if image if flip horizontally
        :param vflip: True if image is flip vertically
        """
        self._trx = 0.5
        self._try = 0.5
        self.param.set_transform(x0, y0, angle, dx, dy, hflip, vflip)
        if self.data is None:
            return
        rot = rotate(-angle)
        xmin = self.points[0].min()
        xmax = self.points[0].max()
        ymin = self.points[1].min()
        ymax = self.points[1].max()
        a, b = (xmax - xmin) / 2.0 + self._trx, (ymax - ymin) / 2.0 + self._try
        tr1 = translate(xmin + a, ymin + b)
        xflip = -1.0 if hflip else 1.0
        yflip = -1.0 if vflip else 1.0
        sc = scale(xflip / dx, yflip / dy)
        tr2 = translate(-x0 - xmin - a, -y0 - ymin - b)
        self.tr = tr1 * sc * rot * tr2
        self.itr = self.tr.I
        self.compute_bounds()

    def get_transform(self):
        """
        Return the transformation parameters

        :return: tuple (x0, y0, angle, dx, dy, hflip, yflip)
        """
        return self.param.get_transform()

    def compute_bounds(self):
        """Compute the bounding box and border rect"""
        self.update_bounds()
        self.update_border()

    def update_bounds(self):
        """
        Update the bounding box after applying the transformation matrix
        """

        points = np.dot(self.itr, self.points)
        xmin = points[0].min()
        xmax = points[0].max()
        ymin = points[1].min()
        ymax = points[1].max()
        self.bounds = QC.QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def update_border(self):
        """
        Update the points of the border after applying the transformation matrix
        """
        tpos = np.dot(self.itr, self.points)
        self.border_rect.set_points(tpos.T[:, :2])


class MaskedImageMixin:
    """
    Mixin used to factorize mask mechanism to the different ImageItems classes. See
    :py:class:`.MaskedImageItem` and :py:class:`.MaskedXYImageItem`

        * mask (optional): 2D NumPy array
    """

    def __init__(self, mask=None):
        self.orig_data = None
        self._mask = mask
        self._mask_filename = None
        self._masked_areas = []

    # ---- Pickle methods -------------------------------------------------------
    def serialize(self, writer: HDF5Writer | INIWriter | JSONWriter) -> None:
        """Serialize object to HDF5 writer

        Args:
            writer: HDF5, INI or JSON writer
        """
        writer.write(self.get_mask_filename(), group_name="mask_fname")
        writer.write_object_list(self._masked_areas, "masked_areas")

    def deserialize(self, reader: HDF5Reader | INIReader | JSONReader) -> None:
        """Deserialize object from HDF5 reader

        Args:
            reader: HDF5, INI or JSON reader
        """
        mask_fname = reader.read(group_name="mask_fname", func=reader.read_unicode)
        masked_areas = reader.read_object_list("masked_areas", MaskedArea)
        if mask_fname:
            self.set_mask_filename(mask_fname)
            self.load_mask_data()
        elif masked_areas and self.data is not None:
            self.set_masked_areas(masked_areas)
            self.apply_masked_areas()

    # ---- Public API -----------------------------------------------------------
    def update_mask(self):
        """ """
        if isinstance(self.data, np.ma.MaskedArray):
            self.data.set_fill_value(self.param.filling_value)

    def set_mask(self, mask):
        """Set image mask"""
        self.data.mask = mask

    def get_mask(self):
        """Return image mask"""
        return self.data.mask

    def set_mask_filename(self, fname):
        """
        Set mask filename

        There are two ways for pickling mask data of `MaskedImageItem` objects:

            1. using the mask filename (as for data itself)
            2. using the mask areas (`MaskedAreas` instance, see set_mask_areas)

        When saving objects, the first method is tried and then, if no
        filename has been defined for mask data, the second method is used.
        """
        self._mask_filename = fname

    def get_mask_filename(self):
        """

        :return:
        """
        return self._mask_filename

    def load_mask_data(self):
        """ """
        data = io.imread(self.get_mask_filename(), to_grayscale=True)
        self.set_mask(data)
        self._mask_changed()

    def set_masked_areas(self, areas):
        """Set masked areas (see set_mask_filename)"""
        self._masked_areas = areas

    def get_masked_areas(self):
        """

        :return:
        """
        return self._masked_areas

    def add_masked_area(self, geometry, x0, y0, x1, y1, inside):
        """

        :param geometry:
        :param x0:
        :param y0:
        :param x1:
        :param y1:
        :param inside:
        :return:
        """
        area = MaskedArea(geometry=geometry, x0=x0, y0=y0, x1=x1, y1=y1, inside=inside)
        for _area in self._masked_areas:
            if area == _area:
                return
        self._masked_areas.append(area)

    def _mask_changed(self):
        """Emit the :py:data:`.baseplot.BasePlot.SIG_MASK_CHANGED` signal"""
        plot = self.plot()
        if plot is not None:
            plot.SIG_MASK_CHANGED.emit(self)

    def apply_masked_areas(self):
        """Apply masked areas"""
        for area in self._masked_areas:
            if area.geometry == "rectangular":
                self.mask_rectangular_area(
                    area.x0,
                    area.y0,
                    area.x1,
                    area.y1,
                    area.inside,
                    trace=False,
                    do_signal=False,
                )
            else:
                self.mask_circular_area(
                    area.x0,
                    area.y0,
                    area.x1,
                    area.y1,
                    area.inside,
                    trace=False,
                    do_signal=False,
                )
        self._mask_changed()

    def mask_all(self):
        """Mask all pixels"""
        self.data.mask = True
        self._mask_changed()

    def unmask_all(self):
        """Unmask all pixels"""
        self.data.mask = np.ma.nomask
        self.set_masked_areas([])
        self._mask_changed()

    def mask_rectangular_area(
        self, x0, y0, x1, y1, inside=True, trace=True, do_signal=True
    ):
        """
        Mask rectangular area
        If inside is True (default), mask the inside of the area
        Otherwise, mask the outside
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        if inside:
            self.data[iy0:iy1, ix0:ix1] = np.ma.masked
        else:
            indexes = np.ones(self.data.shape, dtype=np.bool_)
            indexes[iy0:iy1, ix0:ix1] = False
            self.data[indexes] = np.ma.masked
        if trace:
            self.add_masked_area("rectangular", x0, y0, x1, y1, inside)
        if do_signal:
            self._mask_changed()

    def mask_circular_area(
        self, x0, y0, x1, y1, inside=True, trace=True, do_signal=True
    ):
        """
        Mask circular area, inside the rectangle (x0, y0, x1, y1), i.e.
        circle with a radius of ``.5/*(x1-x0)``
        If inside is True (default), mask the inside of the area
        Otherwise, mask the outside
        """
        ix0, iy0, ix1, iy1 = self.get_closest_index_rect(x0, y0, x1, y1)
        xc, yc = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        radius = 0.5 * (x1 - x0)
        xdata, ydata = self.get_x_values(ix0, ix1), self.get_y_values(iy0, iy1)

        for ix in range(ix0, ix1):
            for iy in range(iy0, iy1):
                distance = np.sqrt(
                    (xdata[ix - ix0] - xc) ** 2 + (ydata[iy - iy0] - yc) ** 2
                )
                if inside:
                    if distance <= radius:
                        self.data[iy, ix] = np.ma.masked
                elif distance > radius:
                    self.data[iy, ix] = np.ma.masked

        if not inside:
            self.mask_rectangular_area(x0, y0, x1, y1, inside, trace=False)
        if trace:
            self.add_masked_area("circular", x0, y0, x1, y1, inside)
        if do_signal:
            self._mask_changed()

    def is_mask_visible(self):
        """Return mask visibility"""
        return self.param.show_mask

    def set_mask_visible(self, state):
        """Set mask visibility"""
        self.param.show_mask = state
        plot = self.plot()
        if plot is not None:
            plot.replot()

    def _set_data(self, data):
        self.orig_data = data
        self.data = data.view(np.ma.MaskedArray)
        self.set_mask(self._mask)
        self._mask = None  # removing reference to this temporary array
        if self.param.filling_value is None:
            self.param.filling_value = self.data.get_fill_value()
        #        self.data.harden_mask()
        self.update_mask()
