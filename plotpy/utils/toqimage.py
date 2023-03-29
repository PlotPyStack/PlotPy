# -*- coding: utf-8 -*-
# The array_to_qimage function was copied from PythonQwt version 0.5.5
# (file qwt/toqimage.py)
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut

"""
NumPy array to QImage
---------------------

.. autofunction:: array_to_qimage
"""

import numpy as np
from qtpy import QtGui as QG


def array_to_qimage(arr: np.ndarray, copy: bool = False) -> QG.QImage:
    """Convert NumPy array to QImage object

    :param numpy.array arr: NumPy array
    :param bool copy: if True, make a copy of the array
    :return: QImage object

    Args:
        arr (np.ndarray): array to convert
        copy (bool, optional): if True, make a copy of the array. Defaults to False.

    Raises:
        NotImplementedError: Unsupported array data shape
        TypeError: Invalid third axis dimension
        NotImplementedError: Unsupported array data type

    Returns:
        QG.QImage: QImage object
    """
    # https://gist.githubusercontent.com/smex/5287589/raw/toQImage.py
    if arr is None:
        return QG.QImage()
    if len(arr.shape) not in (2, 3):
        raise NotImplementedError("Unsupported array shape %r" % arr.shape)
    data = arr.data
    ny, nx = arr.shape[:2]
    stride = arr.strides[0]  # bytes per line
    color_dim = None
    if len(arr.shape) == 3:
        color_dim = arr.shape[2]
    if arr.dtype == np.uint8:
        if color_dim is None:
            qimage = QG.QImage(data, nx, ny, stride, QG.QImage.Format_Indexed8)
            #            qimage.setColorTable([qRgb(i, i, i) for i in range(256)])
            qimage.setColorCount(256)
        elif color_dim == 3:
            qimage = QG.QImage(data, nx, ny, stride, QG.QImage.Format_RGB888)
        elif color_dim == 4:
            qimage = QG.QImage(data, nx, ny, stride, QG.QImage.Format_ARGB32)
        else:
            raise TypeError("Invalid third axis dimension (%r)" % color_dim)
    elif arr.dtype == np.uint32:
        qimage = QG.QImage(data, nx, ny, stride, QG.QImage.Format_ARGB32)
    else:
        raise NotImplementedError("Unsupported array data type %r" % arr.dtype)
    if copy:
        return qimage.copy()
    return qimage
