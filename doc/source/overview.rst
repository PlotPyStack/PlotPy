========
Overview
========

plotpy.core
===========

When developping scientific software, from the simplest script to the 
most complex application, one systematically needs to manipulate data sets 
(e.g. parameters for a data processing feature).
These data sets may consist of various data types: real numbers (e.g. physical 
quantities), integers (e.g. array indexes), strings (e.g. filenames), 
booleans (e.g. enable/disable an option), and so on.

Most of the time, the programmer will need the following features:

    * allow the user to enter each parameter through a graphical user interface,
      using widgets which are adapted to data types (e.g. a single combo box or 
      check boxes are suitable for presenting an option selection among 
      multiple choices)

    * entered values have to be stored by the program with a convention which 
      is again adapted to data types (e.g. when storing a combo box selection 
      value, should we store the option string, the list index or an 
      associated key?)

    * using the stored values easily (e.g. for data processing) by regrouping 
      parameters in data structures
      
    * showing the stored values in a dialog box or within a graphical user 
      interface layout, again with widgets adapted to data types

This library aims to provide these features thanks to automatic graphical user 
interface generation for data set editing and display. Widgets inside GUIs are 
automatically generated depending on each data item type.

The `plotpy.core` library also provides the following features:

    * :py:mod:`plotpy.core.utils.disthelpers`: `py2ex` helpers
    * :py:mod:`plotpy.core.config.userconfig`: `.ini` configuration management helpers
      (based on Python standard module :py:mod:`configparser`)
    * :py:mod:`plotpy.core.config.misc`: library/application data management
    * :py:mod:`plotpy.core.utils.misc`: miscelleneous utilities


plotpy.gui
==========

Based on `PythonQwt` (plotting widgets for Python-Qt graphical user
interfaces) and on the scientific modules `NumPy` and `SciPy`, `plotpy` is a
Python library providing efficient 2D data-plotting features (curve/image
visualization and related tools) for interactive computing and signal/image
processing application development.

Performances
~~~~~~~~~~~~

The most popular Python module for data plotting is currently `matplotlib`,
an open-source library providing a lot of plot types and an API (the `pylab`
interface) which is very close to MATLAB's plotting interface.

`plotpy.gui` plotting features are quite limited in terms of plot types compared
to `matplotlib`. However the currently implemented plot types are much more
efficient.
For example, the `plotpy` image showing function (:py:func:`plotpy.gui.widgets.pyplot.imshow`)
do not make any copy of the displayed data, hence allowing to show images which
are much larger than with its `matplotlib`'s counterpart. In other terms, when
showing a 30-MB image (16-bits unsigned integers for example) with `plotpu`,
no additional memory is wasted to display the image (except for the offscreen
image of course which depends on the window size) whereas `matplotlib` takes
more than 600-MB of additional memory (the original array is duplicated four
times using 64-bits float data types).

Features
~~~~~~~~

The `plotpy.gui` library also provides the following features:

    * :py:mod:`.pyplot`: equivalent to :py:mod:`matplotlib.pyplot`, at
      least for the implemented functions

    * supported `plot items`:

        - :py:mod:`.histogram`: 1D histograms
        - :py:mod:`.items.curve`: curves and error bar curves
        - :py:mod:`.items.image`: images (RGB images are not supported),
          images with non-linear x/y scales, images with specified pixel size
          (e.g. loaded from DICOM files), 2D histograms, pseudo-color images
          (`pcolor`)
        - :py:mod:`.items.label`: labels, curve plot legends
        - :py:mod:`.items.shapes`: polygon, polylines, rectangle, circle,
          ellipse and segment
        - :py:mod:`.items.annotations`: annotated shapes (shapes with labels
          showing position and dimensions): rectangle with center position and
          size, circle with center position and diameter, ellipse with center
          position and diameters (these items are very useful to measure things
          directly on displayed images)

    * curves, images and shapes:

        * multiple object selection for moving objects or editing their
          properties through automatically generated dialog boxes (``plotpy.core``)
        * item list panel: move objects from foreground to background,
          show/hide objects, remove objects, ...
        * customizable aspect ratio
        * a lot of ready-to-use tools: plot canvas export to image file, image
          snapshot, image rectangular filter, etc.

    * curves:

        * interval selection tools with labels showing results of computing on
          selected area
        * curve fitting tool with automatic fit, manual fit with sliders, ...

    * images:

        * contrast adjustment panel: select the LUT by moving a range selection
          object on the image levels histogram, eliminate outliers, ...
        * X-axis and Y-axis cross-sections: support for multiple images,
          average cross-section tool on a rectangular area, ...
        * apply any affine transform to displayed images in real-time (rotation,
          magnification, translation, horizontal/vertical flip, ...)

    * application development helpers:

        * ready-to-use curve and image plot widgets and dialog boxes
          (see :py:mod:`.plot`)
        * load/save graphical objects (curves, images, shapes)
        * a lot of test scripts which demonstrate `plotpy.gui` features
          (see :ref:`examples`)

How it works
~~~~~~~~~~~~

A `plotpy.gui`-based plotting widget may be constructed using one of the following
methods:

    * *Interactive mode*: when manipulating and visualizing data in an interactive
      Python or IPython interpreter, the :py:mod`.pyplot` module provide
      the easiest way to plot curves, show images and more. Syntax is similar
      to MATLAB's, thus very easy to learn and to use interactively.

    * *Script mode*: when manipulating and visualizing data using a script, the
      :py:mod`.pyplot` module is still a good choice as long as you don't
      need to customize the figure graphical user interface (GUI) layout.
      However, if you want to add other widgets to the GUI, like menus, buttons
      and so on, you should rather use plotting widget classes instead of
      the `pyplot` helper functions.

There are two kinds of plotting widgets defined in `plotpy.gui`:

    * low-level plotting widget: :py:class:`.baseplot.BasePlot`

    * high-level plotting widgets (ready-to-use widgets with integrated tools
      and panels): :py:class:`.plot.PlotWidget` and corresponding dialog box
      :py:class:`.plot.PlotDialog` and window 
      :py:class:`.plot.PlotWindow`

Curve-related widgets with integrated plot manager:

.. image:: images/curve_widgets.png

Image-related widgets with integrated plot manager:

.. image:: images/image_widgets.png

.. seealso::

    Module :py:mod:`.items.curve`
        Module providing curve-related plot items

    Module :py:mod:`.items.image`
        Module providing image-related plot items

    Module :py:mod:`.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes
