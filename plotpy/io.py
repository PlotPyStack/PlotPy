# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Input/Output helper functions
-----------------------------

Overview
^^^^^^^^

The `io` module provides the following input/output helper functions:

* :py:func:`.io.imread`: load an image (.png, .tiff,
    .dicom, etc.) and return its data as a NumPy array
* :py:func:`.io.imwrite`: save an array to an image file
* :py:func:`.io.load_items`: load plot items from HDF5
* :py:func:`.io.save_items`: save plot items to HDF5

Reference
^^^^^^^^^

.. autofunction:: imread
.. autofunction:: imwrite
.. autofunction:: load_items
.. autofunction:: save_items
"""

from __future__ import annotations

import logging
import os.path as osp
import re
import sys
from typing import TYPE_CHECKING, Any

import numpy as np
import PIL.Image
import PIL.TiffImagePlugin  # py2exe

from plotpy.config import _

if TYPE_CHECKING:
    import guidata.io


def scale_data_to_dtype(data: np.ndarray, dtype: np.dtype) -> np.ndarray:
    """Scale data to fit datatype dynamic range

    Args:
        data: data to scale
        dtype: target datatype

    Returns:
        scaled data

    .. warning::

        This function modifies data in place
    """
    info = np.iinfo(dtype)
    dmin = data.min()
    dmax = data.max()
    data -= dmin
    data = data * float(info.max - info.min) / (dmax - dmin)
    data = data + float(info.min)
    return np.array(data, dtype)


# ===============================================================================
# I/O File type definitions
# ===============================================================================
class FileType:
    """Filetype object:
    * `name` : description of filetype,
    * `read_func`, `write_func` : I/O callbacks,
    * `extensions`: filename extensions (with a dot!) or filenames,
    (list, tuple or space-separated string)
    * `data_types`: supported data types"""

    def __init__(
        self,
        name,
        extensions,
        read_func=None,
        write_func=None,
        data_types=None,
        requires_template=False,
    ):
        self.name = name
        if isinstance(extensions, str):
            extensions = extensions.split()
        self.extensions = [osp.splitext(" " + ext)[1] for ext in extensions]
        self.read_func = read_func
        self.write_func = write_func
        self.data_types = data_types
        self.requires_template = requires_template

    def matches(self, action, dtype, template):
        """Return True if file type matches passed data type and template
        (or if dtype is None)"""
        assert action in ("load", "save")
        matches = dtype is None or self.data_types is None or dtype in self.data_types
        if action == "save" and self.requires_template:
            matches = matches and template is not None
        return matches

    @property
    def wcards(self):
        """

        :return:
        """
        return "*" + (" *".join(self.extensions))

    def filters(self, action, dtype, template):
        """

        :param action:
        :param dtype:
        :param template:
        :return:
        """
        assert action in ("load", "save")
        if self.matches(action, dtype, template):
            return f"\n{self.name} ({self.wcards})"
        else:
            return ""


class ImageIOHandler:
    """I/O handler: regroup all FileType objects"""

    def __init__(self):
        self.filetypes = []

    def allfilters(self, action, dtype, template):
        """

        :param action:
        :param dtype:
        :param template:
        :return:
        """
        wcards = " ".join(
            [
                ftype.wcards
                for ftype in self.filetypes
                if ftype.matches(action, dtype, template)
            ]
        )
        return "{} ({})".format(_("All supported files"), wcards)

    def get_filters(self, action, dtype=None, template=None):
        """Return file type filters for `action` (string: 'save' or 'load'),
        `dtype` data type (None: all data types), and `template` (True if save
        function requires a template (e.g. DICOM files), False otherwise)"""
        filters = self.allfilters(action, dtype, template)
        for ftype in self.filetypes:
            filters += ftype.filters(action, dtype, template)
        return filters

    def add(
        self,
        name,
        extensions,
        read_func=None,
        write_func=None,
        import_func=None,
        data_types=None,
        requires_template=None,
    ):
        """

        :param name:
        :param extensions:
        :param read_func:
        :param write_func:
        :param import_func:
        :param data_types:
        :param requires_template:
        :return:
        """
        if import_func is not None:
            try:
                import_func()
            except ImportError:
                return
        assert read_func is not None or write_func is not None
        ftype = FileType(
            name,
            extensions,
            read_func=read_func,
            write_func=write_func,
            data_types=data_types,
            requires_template=requires_template,
        )
        self.filetypes.append(ftype)

    def _get_filetype(self, ext):
        """Return FileType object associated to file extension `ext`"""
        for ftype in self.filetypes:
            if ext.lower() in ftype.extensions:
                return ftype
        else:
            raise RuntimeError(f"Unsupported file type: '{ext}'")

    def get_readfunc(self, ext):
        """Return read function associated to file extension `ext`"""
        ftype = self._get_filetype(ext)
        if ftype.read_func is None:
            raise RuntimeError(f"Unsupported file type (read): '{ext}'")
        else:
            return ftype.read_func

    def get_writefunc(self, ext):
        """Return read function associated to file extension `ext`"""
        ftype = self._get_filetype(ext)
        if ftype.write_func is None:
            raise RuntimeError(f"Unsupported file type (write): '{ext}'")
        else:
            return ftype.write_func


iohandler = ImageIOHandler()


# ==============================================================================
# tifffile-based Private I/O functions
# ==============================================================================


def _imread_tiff(filename):
    """Open a TIFF image and return a NumPy array"""
    try:
        import tifffile

        return tifffile.imread(filename)
    except ImportError:
        return _imread_pil(filename)


def _imwrite_tiff(filename, arr):
    """Save a NumPy array to a TIFF file"""
    try:
        import tifffile

        return tifffile.imwrite(filename, arr)
    except ImportError:
        return _imwrite_pil(filename, arr)


# ==============================================================================
# PIL-based Private I/O functions
# ==============================================================================
if sys.byteorder == "little":
    _ENDIAN = "<"
else:
    _ENDIAN = ">"

DTYPES = {
    "1": ("|b1", None),
    "L": ("|u1", None),
    "I": ("%si4" % _ENDIAN, None),
    "F": ("%sf4" % _ENDIAN, None),
    "I;16": ("%su2" % _ENDIAN, None),
    "I;16B": ("%su2" % _ENDIAN, None),
    "I;16S": ("%si2" % _ENDIAN, None),
    "P": ("|u1", None),
    "RGB": ("|u1", 3),
    "RGBX": ("|u1", 4),
    "RGBA": ("|u1", 4),
    "CMYK": ("|u1", 4),
    "YCbCr": ("|u1", 4),
}


def _imread_pil(filename, to_grayscale=False, **kwargs):
    """Open image with PIL and return a NumPy array"""
    PIL.TiffImagePlugin.OPEN_INFO[(PIL.TiffImagePlugin.II, 0, 1, 1, (16,), ())] = (
        "I;16",
        "I;16",
    )
    img = PIL.Image.open(filename)
    base, ext = osp.splitext(filename)
    ext = ext.lower()
    if ext in [".tif", ".tiff"]:
        # try to know if multiple pages
        nb_pages = 0
        while True:
            try:
                img.seek(nb_pages)
                nb_pages += 1
            except EOFError:
                break
        if nb_pages > 1:
            for i in range(nb_pages):
                img.seek(i)
                filename = base
                filename += "_{i:d}".format(i=i)
                filename += ext
                img.save(filename)
            if nb_pages == 2:
                # possibility to be TIFF file with thumbnail and full image
                # --> try to load full image (second one)
                filename = base + "_{i:d}".format(i=1) + ext
            else:
                # we don't know which one must be loaded --> load first image
                filename = base + "_{i:d}".format(i=0) + ext

    img = PIL.Image.open(filename)
    if img.mode in ("CMYK", "YCbCr"):
        # Converting to RGB
        img = img.convert("RGB")
    if to_grayscale and img.mode in ("RGB", "RGBA", "RGBX"):
        # Converting to grayscale
        img = img.convert("L")
    elif "A" in img.mode or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    elif img.mode == "P":
        img = img.convert("RGB")
    try:
        dtype, extra = DTYPES[img.mode]
    except KeyError:
        raise RuntimeError(f"{img.mode} mode is not supported")
    shape = (img.size[1], img.size[0])
    if extra is not None:
        shape += (extra,)
    try:
        return np.array(img, dtype=np.dtype(dtype)).reshape(shape)
    except SystemError:
        return np.array(img.getdata(), dtype=np.dtype(dtype)).reshape(shape)


def _imwrite_pil(filename, arr):
    """Write `arr` NumPy array to `filename` using PIL"""
    for mode, (dtype_str, extra) in list(DTYPES.items()):
        if dtype_str == arr.dtype.str:
            if extra is None:  # mode for grayscale images
                if len(arr.shape[2:]) > 0:
                    continue  # not suitable for RGB(A) images
                else:
                    break  # this is it!
            else:  # mode for RGB(A) images
                if len(arr.shape[2:]) == 0:
                    continue  # not suitable for grayscale images
                elif arr.shape[-1] == extra:
                    break  # this is it!
    else:
        # F Chermette 2022
        if arr.dtype.str == "%sf8" % _ENDIAN:
            arr = np.array(arr, dtype="f4")
            mode = "F"
        else:
            raise RuntimeError("Cannot determine PIL data type")
    img = PIL.Image.fromarray(arr, mode)
    img.save(filename)


# ==============================================================================
# DICOM Private I/O functions
# ==============================================================================
def _import_dcm():
    """DICOM Import function (checking for required libraries):
    DICOM support requires library `pydicom`"""

    logger = logging.getLogger("pydicom")
    logger.setLevel(logging.CRITICAL)

    # This import statement must stay here because the purpose of this function
    # is to check if pydicom is installed:
    # pylint: disable=import-outside-toplevel
    # pylint: disable=import-error
    from pydicom import dicomio  # type:ignore # noqa: F401

    logger.setLevel(logging.WARNING)


def _imread_dcm(filename, **kwargs):
    """Open DICOM image with pydicom and return a NumPy array"""
    # pylint: disable=import-outside-toplevel
    # pylint: disable=import-error
    from pydicom import dicomio  # type:ignore

    dcm = dicomio.read_file(filename, force=True)
    # **********************************************************************
    # The following is necessary until pydicom numpy support is improved:
    # (after that, a simple: 'arr = dcm.PixelArray' will work the same)
    format_str = "%sint%s" % (("u", "")[dcm.PixelRepresentation], dcm.BitsAllocated)
    try:
        dtype = np.dtype(format_str)
    except TypeError:
        raise TypeError(
            "Data type not understood by NumPy: "
            "PixelRepresentation=%d, BitsAllocated=%d"
            % (dcm.PixelRepresentation, dcm.BitsAllocated)
        )
    arr = np.frombuffer(dcm.PixelData, dtype)
    try:
        # pydicom 0.9.3:
        dcm_is_little_endian = dcm.isLittleEndian
    except AttributeError:
        # pydicom 0.9.4:
        dcm_is_little_endian = dcm.is_little_endian
    if dcm_is_little_endian != (sys.byteorder == "little"):
        arr.byteswap(True)
    spp = getattr(dcm, "SamplesperPixel", 1)
    if hasattr(dcm, "NumberOfFrames") and dcm.NumberOfFrames > 1:
        if spp > 1:
            arr = arr.reshape(spp, dcm.NumberofFrames, dcm.Rows, dcm.Columns)
        else:
            arr = arr.reshape(dcm.NumberOfFrames, dcm.Rows, dcm.Columns)
    else:
        if spp > 1:
            if dcm.BitsAllocated == 8:
                arr = arr.reshape(spp, dcm.Rows, dcm.Columns)
            else:
                raise NotImplementedError(
                    "This code only handles "
                    "SamplesPerPixel > 1 if Bits Allocated = 8"
                )
        else:
            arr = arr.reshape(dcm.Rows, dcm.Columns)
    # **********************************************************************
    return arr


def _imwrite_dcm(filename, arr, template=None):
    """Save a numpy array `arr` into a DICOM image file `filename`
    based on DICOM structure `template`"""
    # Note: due to IOHandler formalism, `template` has to be a keyword argument
    assert template is not None, (
        "The `template` keyword argument is required to save DICOM files\n"
        "(that is the template DICOM structure object)"
    )
    infos = np.iinfo(arr.dtype)
    template.BitsAllocated = infos.bits
    template.BitsStored = infos.bits
    template.HighBit = infos.bits - 1
    template.PixelRepresentation = ("u", "i").index(infos.kind)
    data_vr = ("US", "SS")[template.PixelRepresentation]
    template.Rows = arr.shape[0]
    template.Columns = arr.shape[1]
    template.SmallestImagePixelValue = int(arr.min())
    template[0x00280106].VR = data_vr
    template.LargestImagePixelValue = int(arr.max())
    template[0x00280107].VR = data_vr
    if not template.PhotometricInterpretation.startswith("MONOCHROME"):
        template.PhotometricInterpretation = "MONOCHROME1"
    template.PixelData = arr.tostring()
    template[0x7FE00010].VR = "OB"
    template.save_as(filename)


# ==============================================================================
# Text files Private I/O functions
# ==============================================================================
def _imread_txt(filename, **kwargs):
    """Open text file image and return a NumPy array"""
    for delimiter in ("\t", ",", " ", ";"):
        try:
            return np.loadtxt(filename, delimiter=delimiter)
        except ValueError:
            continue
    else:
        raise ValueError(f"Could not load {filename!r}")


def _imwrite_txt(filename, arr):
    """Write `arr` NumPy array to text file `filename`"""
    if arr.dtype in (np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32):
        fmt = "%d"
    else:
        fmt = "%.18e"
    ext = osp.splitext(filename)[1]
    if ext.lower() in (".txt", ".asc", ""):
        np.savetxt(filename, arr, fmt=fmt)
    elif ext.lower() == ".csv":
        np.savetxt(filename, arr, fmt=fmt, delimiter=",")


# ==============================================================================
# Registering I/O functions
# ==============================================================================
iohandler.add(
    _("PNG files"),
    "*.png",
    read_func=_imread_pil,
    write_func=_imwrite_pil,
    data_types=(np.uint8, np.uint16),
)
iohandler.add(
    _("TIFF files"), "*.tif *.tiff", read_func=_imread_tiff, write_func=_imwrite_tiff
)
iohandler.add(
    _("8-bit images"),
    "*.jpg *.gif",
    read_func=_imread_pil,
    write_func=_imwrite_pil,
    data_types=(np.uint8,),
)
iohandler.add(_("NumPy arrays"), "*.npy", read_func=np.load, write_func=np.save)
iohandler.add(
    _("Text files"), "*.txt *.csv *.asc", read_func=_imread_txt, write_func=_imwrite_txt
)
iohandler.add(
    _("DICOM files"),
    "*.dcm",
    read_func=_imread_dcm,
    write_func=_imwrite_dcm,
    import_func=_import_dcm,
    data_types=(np.int8, np.uint8, np.int16, np.uint16),
    requires_template=True,
)


# ==============================================================================
# Generic image read/write functions
# ==============================================================================
def imread(
    fname: str, ext: str | None = None, to_grayscale: bool = False
) -> np.ndarray:
    """Read an image from a file as a NumPy array

    Args:
        fname: image filename
        ext: image file extension (if None, extension is guessed from filename)
        to_grayscale: convert RGB images to grayscale
    """
    if not isinstance(fname, str):
        fname = str(fname)  # in case filename is a QString instance
    if ext is None:
        _base, ext = osp.splitext(fname)
    arr = iohandler.get_readfunc(ext)(fname)
    dtype = arr.dtype
    if to_grayscale and arr.ndim == 3:
        # Converting to grayscale
        arr = arr[..., :4].mean(axis=2)
        arr = arr.astype(dtype)
        return arr
    else:
        return arr


def imwrite(
    fname: str,
    arr: np.ndarray,
    ext: str | None = None,
    dtype: np.dtype | None = None,
    max_range: bool | None = None,
    **kwargs,
) -> None:
    """Write a NumPy array to an image file

    Args:
        fname: image filename
        arr: NumPy array
        ext: image file extension (if None, extension is guessed from filename)
        dtype: data type (if None, data type is guessed from array)
        max_range: scale data to fit dtype dynamic range
        kwargs: additional keyword arguments passed to the image writer

    .. warning::

        If `max_range` is True, array data is modified in place
    """
    if not isinstance(fname, str):
        fname = str(fname)  # in case filename is a QString instance
    if ext is None:
        _base, ext = osp.splitext(fname)
    if max_range:
        arr = scale_data_to_dtype(arr, arr.dtype if dtype is None else dtype)
    iohandler.get_writefunc(ext)(fname, arr, **kwargs)


# ==============================================================================
# plotpy plot items I/O
# ==============================================================================

SERIALIZABLE_ITEMS = []
ITEM_MODULES = {}


def register_serializable_items(modname, classnames):
    """Register serializable item from module name and class name"""
    global SERIALIZABLE_ITEMS, ITEM_MODULES
    SERIALIZABLE_ITEMS += classnames
    ITEM_MODULES[modname] = ITEM_MODULES.setdefault(modname, []) + classnames


# Curves
register_serializable_items(
    "plotpy.items",
    [
        "CurveItem",
        "PolygonMapItem",
        "ErrorBarCurveItem",
        "RawImageItem",
        "ImageItem",
        "XYImageItem",
        "RGBImageItem",
        "TrImageItem",
        "MaskedImageItem",
        "MaskedXYImageItem",
        "Marker",
        "XRangeSelection",
        "PolygonShape",
        "PointShape",
        "SegmentShape",
        "RectangleShape",
        "ObliqueRectangleShape",
        "EllipseShape",
        "Axes",
        "AnnotatedPoint",
        "AnnotatedSegment",
        "AnnotatedRectangle",
        "AnnotatedObliqueRectangle",
        "AnnotatedEllipse",
        "AnnotatedCircle",
        "AnnotatedPolygon",
        "LabelItem",
        "LegendBoxItem",
        "SelectedLegendBoxItem",
    ],
)


def item_class_from_name(name: str) -> type[Any] | None:
    """Return plot item class from class name

    Args:
        name: plot item class name

    Returns:
        plot item class

    Raises:
        AssertionError: if class name is unknown (item is not serializable)
    """
    global SERIALIZABLE_ITEMS, ITEM_MODULES
    assert name in SERIALIZABLE_ITEMS, "Unknown class %r" % name
    for modname, names in list(ITEM_MODULES.items()):
        if name in names:
            return getattr(__import__(modname, fromlist=[name]), name)


def item_name_from_object(obj: Any) -> str | None:
    """Return plot item class name from instance

    Args:
        obj: plot item instance

    Returns:
        plot item class name
    """
    return obj.__class__.__name__


def save_item(
    writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    group_name,
    item: Any,
) -> None:
    """Save plot item to HDF5, INI or JSON file

    Args:
        writer: HDF5, INI or JSON writer
        group_name: group name
        item: serializable plot item
    """
    with writer.group(group_name):
        if item is None:
            writer.write_none()
        else:
            item.serialize(writer)
            with writer.group("item_class_name"):
                writer.write_str(item_name_from_object(item))


def load_item(
    reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
    group_name,
) -> Any | None:
    """Load plot item from HDF5, INI or JSON file

    Args:
        reader: HDF5, INI or JSON reader
        group_name: group name

    Returns:
        Plot item instance
    """
    with reader.group(group_name):
        with reader.group("item_class_name"):
            try:
                klass_name = reader.read_str()
            except ValueError:
                # None was saved instead of a real item
                return
        klass = item_class_from_name(klass_name)
        item = klass()
        item.deserialize(reader)
    return item


def save_items(
    writer: guidata.io.HDF5Writer | guidata.io.INIWriter | guidata.io.JSONWriter,
    items: list[Any],
) -> None:
    """Save items to HDF5, INI or JSON file

    Args:
        writer: HDF5, INI or JSON writer
        items: list of serializable plot items
    """
    counts = {}
    names = []

    def _get_name(item):
        basename = item_name_from_object(item)
        count = counts[basename] = counts.setdefault(basename, 0) + 1
        name = "%s_%03d" % (basename, count)
        names.append(name.encode("utf-8"))
        return name

    for item in items:
        with writer.group(_get_name(item)):
            item.serialize(writer)
            writer.write(item.isVisible(), group_name="visible")
    with writer.group("plot_items"):
        writer.write_sequence(names)


def load_items(
    reader: guidata.io.HDF5Reader | guidata.io.INIReader | guidata.io.JSONReader,
) -> list[Any]:
    """Load items from HDF5, INI or JSON file

    Args:
        reader: HDF5, INI or JSON reader

    Returns:
        list of plot item instances
    """
    with reader.group("plot_items"):
        names = reader.read_sequence()
    items = []
    for name in names:
        try:
            name_str = name.decode()
        except AttributeError:
            name_str = name
        klass_name = re.match(r"([A-Z]+[A-Za-z0-9\_]*)\_([0-9]*)", name_str).groups()[0]
        klass = item_class_from_name(klass_name)
        item = klass()
        with reader.group(name):
            item.deserialize(reader)
            item.setVisible(reader.read("visible", default=True))
        items.append(item)
    return items


if __name__ == "__main__":
    # Test if items can all be constructed from their Python module
    for name in SERIALIZABLE_ITEMS:
        print(name, "-->", item_class_from_name(name))
