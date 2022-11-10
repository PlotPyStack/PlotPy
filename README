Plotpy: Plotting library based on Qwt
=====================================


Copyright © 20018-2019 CEA, licensed under the terms of the 
CECILL License (see ``Licence_CeCILL_V2-en.txt``).


Overview
--------


plotpy.core
***********

When developing scientific software, from the simplest script to the 
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


plotpy.gui
**********

Based on PythonQwt and on the scientific modules NumPy and SciPy, plotpy is a
Python library providing efficient 2D data-plotting features (curve/image
visualization and related tools) for interactive computing and signal/image
processing application development.

Features
********

The plotpy.gui library also provides the following features:

* pyplot: equivalent to matplotlib.pyplot, at
  least for the implemented functions

* supported `plot items`:

    * histogram: 1D histograms
    * items.curve: curves and error bar curves
    * items.image: images (RGB images are not supported),
      images with non-linear x/y scales, images with specified pixel size
      (e.g. loaded from DICOM files), 2D histograms, pseudo-color images
      (`pcolor`)
    * items.label: labels, curve plot legends
    * items.shapes: polygon, polylines, rectangle, circle,
      ellipse and segment
    * items.annotations: annotated shapes (shapes with labels
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
      (see plot)
    * load/save graphical objects (curves, images, shapes)
    * a lot of test scripts which demonstrate `plotpy.gui` features
      (see `examples`)


Dependencies
------------

Requirements:
*************

    * Python 3.6
    * PythonQwt > 0.9.0
    * NumPy
    * SciPy
    * Pillow
    
Optional Python modules:
************************

    * h5py (HDF5 files I/O)
    * cx_Freze or py2exe (application deployment on Windows platforms)
    * pydicom >=0.9.3 for DICOM files I/O features

Other optional modules for developers:
**************************************

    * gettext (text translation support)


Installation
------------

From the source package:

```bash
python setup.py install
```
