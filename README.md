# PlotPy: Curve and image plotting tools for Python/Qt applications

[![pypi version](https://img.shields.io/pypi/v/plotpy.svg)](https://pypi.org/project/plotpy/)
[![PyPI status](https://img.shields.io/pypi/status/plotpy.svg)](https://github.com/PlotPyStack/plotpy/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/plotpy.svg)](https://pypi.python.org/pypi/plotpy/)
[![download count](https://img.shields.io/conda/dn/conda-forge/plotpy.svg)](https://www.anaconda.com/download/)

ℹ️ Created in 2016 by [Pierre Raybaut](https://github.com/PierreRaybaut) and maintained by the [PlotPyStack](https://github.com/PlotPyStack) organization.

ℹ️ PlotPy ***V2*** is the new major release of [`guiqwt`](https://github.com/PierreRaybaut/guiqwt): same team 🏋️, same goal 🎯, same long-term support ⏳.

## Overview

`plotpy` is is a Python library providing efficient 2D data-plotting features
for interactive computing and signal/image processing application development.
It is part of the [PlotPyStack](https://github.com/PlotPyStack) project, aiming at
providing a unified framework for creating scientific GUIs with Python and Qt.

`plotpy` is based on:

* [Python](http://www.python.org) language and [Qt](https://doc.qt.io/) GUI toolkit (via [PySide](https://doc.qt.io/qtforpython-6/) or [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro))
* [guidata](https://pypi.python.org/pypi/guidata) automatic GUI generation library
* [PythonQwt](https://pypi.python.org/pypi/PythonQwt) plotting widgets library
* [NumPy](https://pypi.python.org/pypi/NumPy) and [SciPy](https://pypi.python.org/pypi/SciPy) scientific computing libraries

<img src="https://raw.githubusercontent.com/PlotPyStack/plotpy/master/doc/images/panorama.png">

See [documentation](https://plotpy.readthedocs.io/en/latest/) for more details on
the library and [changelog](CHANGELOG.md) for recent history of changes.

Copyrights and licensing:

* Copyright © 2023 [CEA](https://www.cea.fr), [Codra](https://codra.net/), [Pierre Raybaut](https://github.com/PierreRaybaut).
* Licensed under the terms of the BSD 3-Clause (see [LICENSE](LICENSE)).

## Features

The `plotpy` library also provides the following features.

General plotting features:

* Ready-to-use [plot widgets and dialog boxes](https://plotpy.readthedocs.io/en/latest/features/plot/index.html)
* [pyplot](https://plotpy.readthedocs.io/en/latest/features/pyplot.html): interactive
  plotting widgets, equivalent to `matplotlib.pyplot`, at least for the implemented functions
* Supported [plot items](https://plotpy.readthedocs.io/en/latest/features/items/index.html):
  curves, images, contours, histograms, labels, shapes, annotations, ...

Interactive features (i.e. not only programmatic plotting but also with mouse/keyboard):

* Multiple object selection for moving objects or editing their properties through
  automatically generated dialog boxes
* Item list panel: move objects from foreground to background, show/hide objects,
  remove objects, ...
* Customizable aspect ratio for images
* Tons of ready-to-use tools: plot canvas export to image file, image snapshot,
  interval selection, image rectangular filter, etc.
* Curve fitting tool with automatic fit, manual fit with sliders, ...
* Contrast adjustment panel for images: select the LUT by moving a range selection
  object on the image levels histogram, eliminate outliers, ...
* X-axis and Y-axis cross-sections: support for multiple images, average
  cross-section tool on a rectangular area, ...
* Apply any affine transform to displayed images in real-time (rotation,
  magnification, translation, horizontal/vertical flip, ...)

Application development helpers:

* Ready-to-use [plot widgets and dialog boxes](https://plotpy.readthedocs.io/en/latest/features/plot/index.html)
* Load/save graphical objects (curves, images, shapes) into HDF5, JSON or INI files
* A lot of test scripts which demonstrate `plotpy` features
  (see [examples](https://plotpy.readthedocs.io/en/latest/intro/examples.html))

## Dependencies and installation

See [Installation](https://plotpy.readthedocs.io/en/latest/intro/installation.html)
section in the documentation for more details.
