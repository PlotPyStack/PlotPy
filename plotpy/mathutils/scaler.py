# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Scaling functions
-----------------

Overview
^^^^^^^^

The :py:mod:`.scaler` module provides scaling functions for images, thanks to
the C++ scaler engine (`_scaler` extension).

The following functions are available:

* :py:func:`.resize`: resize an image using the scaler engine

Reference
^^^^^^^^^

.. autofunction:: resize
"""

# TODO: Move all _scaler imports in this module and do something to avoid
# the need to import INTERP_LINEAR, INTERP_AA, ... in all modules using the
# scaler (code refactoring between pyplot.imshow,
# styles.BaseImageParam.update_item)

# TODO: Other functions like resize could be written in the future

import numpy as np

from plotpy._scaler import INTERP_AA, INTERP_LINEAR, INTERP_NEAREST, _scale_rect


def resize(data, shape, interpolation=None):
    """Resize array *data* to *shape* (tuple)
    interpolation: 'nearest', 'linear' (default), 'antialiasing'"""
    interpolate = (INTERP_NEAREST,)
    if interpolation is not None:
        interp_dict = {
            "nearest": INTERP_NEAREST,
            "linear": INTERP_LINEAR,
            "antialiasing": INTERP_AA,
        }
        assert interpolation in interp_dict, "invalid interpolation option"
        interp_mode = interp_dict[interpolation]
        if interp_mode in (INTERP_NEAREST, INTERP_LINEAR):
            interpolate = (interp_mode,)
        if interp_mode == INTERP_AA:
            aa = np.ones((5, 5), data.dtype)
            interpolate = (interp_mode, aa)
    out = np.empty(shape)
    src_rect = (0, 0, data.shape[1], data.shape[0])
    dst_rect = (0, 0, out.shape[1], out.shape[0])
    _scale_rect(data, src_rect, out, dst_rect, (1.0, 0.0, None), interpolate)
    return out
