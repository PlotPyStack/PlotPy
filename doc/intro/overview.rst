Overview
========

Main features
-------------

:mod:`plotpy` is a Python module providing a set of high-level widgets and
functions to ease plotting data with Python and Qt.

:mod:`plotpy` is based on the following Python modules:

* :mod:`qwt` (PythonQwt): a Python reimplementation of the Qwt C++ library which
  provides a lot of plotting types and a flexible widget class
  (:py:class:`qwt.plot.QwtPlot`) which may be used to create custom plotting
  widgets.

* :mod:`guidata`: a Python library generating graphical user interfaces
  (GUIs) for easy dataset editing and display. It also provides helpers and
  application development tools for PyQt5.

* :mod:`numpy`: a Python module providing efficient array manipulation
  facilities.

* :mod:`scipy`: a Python module providing scientific computing tools.

The :mod:`plotpy` library provides the following main features:

* Curve and image ready-to-use plotting widgets and dialog boxes
* Components for custom plotting widgets and Qt applications
* Curve fitting tools
* Interactive plotting tools
* And more...

Performance
-----------

The most popular Python module for data plotting for desktop applications is
`matplotlib`. It is a very powerful module providing a lot of plotting types
and an API (the `pylab` interface) which is very close to MATLAB's plotting
interface.

Even if :mod:`plotpy` plotting features are quite limited in terms of plot
types compared to `matplotlib`, the currently implemented plot types are
much more efficient.

For example, the :mod:`plotpy` image showing features do not make any copy
of the displayed data, hence allowing to show images that are much larger
than what is possible with `matplotlib`. Moreover, the memory footprint of
:mod:`plotpy` is much smaller than `matplotlib`'s one. For example, a 30-MB
image is displayed using 30-MB of memory with `plotpy` whereas `matplotlib`
uses more than 600-MB of memory to display the same image. This is due to
the fact that `matplotlib` makes multiple copies of the original data array:
the original array is duplicated four times using 64-bits float data types.

Detailed features
-----------------

The :mod:`plotpy` library provides the following features:

* :mod:`pyplot`: equivalent to :py:mod:`matplotlib.pyplot`, at least for
  the implemented functions

* :ref:`items`: 1D histogram, curve, error bar curve, image, label, shapes
  (polygon, polyline, rectangle, circle, ellipse, segment, etc.), annotations
  (shapes with labels showing position and dimensions), markers, etc.

* :ref:`plot`:

  - ready-to-use plotting widgets (widget, dialog box, window)

  - multiple curve/image selection for moving curves or editing their
    properties through automatically generated dialog boxes

  - item list panel: move curves/images from foreground to background,
    show/hide curves/images, remove curves/images, ...

  - specific curve features:

    - interval selection tools with labels showing results of computing on
      selected area

    - curve fitting tool with automatic fit, manual fit with sliders, ...

  - specific image features:

    - contrast adjustment panel: select the LUT by moving a range selection
      object on the image levels histogram, eliminate outliers, ...

    - X-axis and Y-axis cross-sections: support for multiple images,
      average cross-section tool on a rectangular area, ...

    - apply any affine transform to displayed images in real-time (rotation,
      magnification, translation, horizontal/vertical flip, ...)

    - ready-to-use tools (plot canvas export to image file, image snapshot,
      image rectangular filter, ...)

* application development helpers:

  - ready-to-use curve and image plot widgets, dialog boxes and windows
  - graphical objects (curves, images, shapes) serialization/deserialization
    to/from ``.ini``, ``.h5`` or ``.json`` files
  - a lot of test scripts (see :ref:`examples`)
