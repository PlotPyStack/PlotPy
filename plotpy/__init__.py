# -*- coding: utf-8 -*-
"""
plotpy
======

Based on `PythonQwt` (plotting widgets for Qt graphical user interfaces) and
on the scientific modules NumPy and SciPy, :mod:`plotpy` is a Python library
providing efficient 2D data-plotting features (curve/image visualization
and related tools) for interactive computing and signal/image processing
application development.

.. image:: images/panorama.png


External resources:
    * Python Package Index: `PyPI`_
    * Bug reports and feature requests: `GitHub`_

.. _PyPI: https://pypi.python.org/pypi/plotpy
.. _GitHub: https://github.com/PierreRaybaut/plotpy
"""

__version__ = "2.2.0"
__VERSION__ = tuple([int(number) for number in __version__.split(".")])

# --- Important note: DATAPATH and LOCALEPATH are used by guidata.configtools
# ---                 to retrieve data and translation files paths
#
# Dear (Debian, RPM, ...) package makers, please feel free to customize the
# following path to module's data (images) and translations:
DATAPATH = LOCALEPATH = ""
