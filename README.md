# plotpy: Curve and image plotting tools for Python/Qt applications

[![pypi version](https://img.shields.io/pypi/v/plotpy.svg)](https://pypi.org/project/plotpy/)
[![PyPI status](https://img.shields.io/pypi/status/plotpy.svg)](https://github.com/PlotPyStack/plotpy/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/plotpy.svg)](https://pypi.python.org/pypi/plotpy/)
[![download count](https://img.shields.io/conda/dn/conda-forge/plotpy.svg)](https://www.anaconda.com/download/)

ℹ️ Created in 2016 by Pierre Raybaut and maintained by the [PlotPyStack](https://github.com/PlotPyStack) organization.

ℹ️ `plotpy` is the new major release of [`guiqwt`](https://github.com/PierreRaybaut/guiqwt): same team 🏋️, same goal 🎯, same long-term support ⏳.

## Overview

`plotpy` is is a Python library providing efficient 2D data-plotting features
for interactive computing and signal/image processing application development.

`plotpy` is based on:

* [Python](http://www.python.org) language and [Qt](https://doc.qt.io/) GUI toolkit (via [PySide](https://doc.qt.io/qtforpython-6/) or [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro))
* [guidata](https://pypi.python.org/pypi/guidata) automatic GUI generation library
* [PythonQwt](https://pypi.python.org/pypi/PythonQwt) plotting widgets library
* [NumPy](https://pypi.python.org/pypi/NumPy) and [SciPy](https://pypi.python.org/pypi/SciPy) scientific computing libraries

Based on PythonQwt and on the scientific modules NumPy and SciPy, plotpy is a
Python library providing efficient 2D data-plotting features (curve/image
visualization and related tools) for interactive computing and signal/image
processing application development.

<img src="https://raw.githubusercontent.com/PlotPyStack/plotpy/master/doc/images/panorama.png">

See [documentation](https://plotpy.readthedocs.io/en/latest/) for more details on
the library and [changelog](CHANGELOG.md) for recent history of changes.

Copyrights and licensing:

* Copyright © 2023 [CEA](https://www.cea.fr), [Codra](https://codra.net/), [Pierre Raybaut](https://github.com/PierreRaybaut).
* Licensed under the terms of the BSD 3-Clause (see [LICENSE](LICENSE)).

### Features

The `plotpy` library also provides the following features:

* Ready-to-use [plot widgets and dialog boxes](https://plotpy.readthedocs.io/en/latest/features/plot/index.html)

* [pyplot](https://plotpy.readthedocs.io/en/latest/features/pyplot.html): interactive plotting widgets, equivalent to `matplotlib.pyplot`, at
  least for the implemented functions

* supported [plot items](https://plotpy.readthedocs.io/en/latest/features/items/index.html): curve, image, histogram, label, shape, annotation, ...

* interactive features:

  * multiple object selection for moving objects or editing their
    properties through automatically generated dialog boxes

  * item list panel: move objects from foreground to background,
    show/hide objects, remove objects, ...

  * customizable aspect ratio for images

  * tons of ready-to-use tools: plot canvas export to image file, image
    snapshot, interval selection, image rectangular filter, etc.

  * curve fitting tool with automatic fit, manual fit with sliders, ...

  * contrast adjustment panel for images: select the LUT by moving a range selection
    object on the image levels histogram, eliminate outliers, ...

  * X-axis and Y-axis cross-sections: support for multiple images, average
    cross-section tool on a rectangular area, ...

  * apply any affine transform to displayed images in real-time (rotation,
    magnification, translation, horizontal/vertical flip, ...)

* application development helpers:

  * ready-to-use [plot widgets and dialog boxes](https://plotpy.readthedocs.io/en/latest/features/plot/index.html)
  * load/save graphical objects (curves, images, shapes)
  * a lot of test scripts which demonstrate `plotpy` features (see [examples](https://plotpy.readthedocs.io/en/latest/intro/examples.html))

## Dependencies

### Requirements

* Python 3.8+
* [PyQt5](https://pypi.python.org/pypi/PyQt5) (Python Qt bindings)
* [QtPy](https://pypi.org/project/QtPy/) (abstraction layer for Python-Qt binding libraries)
* [PythonQwt](https://pypi.org/project/PythonQwt/) (Python wrapper for the Qwt C++ class library)
* [guidata](https://pypi.org/project/guidata/) (Python library generating graphical user interfaces for easy dataset editing and display)

### Build requirements

* [setuptools](https://pypi.org/project/setuptools/) (Python packages management)
* [wheel](https://pypi.org/project/wheel/) (Python built-package format)
* [build](https://pypi.org/project/build/) (Python package builder)
* [numpy](https://pypi.org/project/numpy/) (Python package for scientific computing)
* [Cython](https://pypi.org/project/Cython/) (Python package for writing C extensions for the Python language)
* C++ compiler (e.g. [GCC](https://gcc.gnu.org/), [MSVC](https://visualstudio.microsoft.com/vs/features/cplusplus/))

## Installation

### From PyPI

Using ``pip``:

```bash
pip install plotpy
```

### From the source package

Using ``build``:

```bash
python -m build
```
