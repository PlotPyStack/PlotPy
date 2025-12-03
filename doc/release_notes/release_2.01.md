# Version 2.1 #

## PlotPy Version 2.1.2 (2024-02-16) ##

New features:

* Added `Echelon` alpha function to the image parameters:
  * The `Echelon` alpha function is a step function, so that the alpha channel is 0 (full transparency) for the lowest value of the Lookup Table (LUT) and opaque (transparency level set by the `Global alpha` parameter) for the other values
  * This feature is added to the other existing alpha functions: `Constant`, `Linear`, `Sigmoid`, and `Hyperbolic tangent`

Bug fixes:

* Compatibility with PythonQwt 0.12.

## PlotPy Version 2.1.1 (2024-02-09) ##

Bug fixes:

* API breakage (unintentional) in V2.1.0:
  * In V2.1.0, `mathutils.colormap` module was renamed to `mathutils.colormaps`
  * Original `mathutils.colormap` module naming is restored in this release
* Colormap selection from the toolbar was not triggering the `SIG_ITEMS_CHANGED` signal (every time an item parameter is changed, the `SIG_ITEMS_CHANGED` signal has to be emitted by the `BasePlot` instance to notify the application that the plot has been modified)

## PlotPy Version 2.1.0 (2024-02-08) ##

In this release, test coverage is 71%.

New features:

* Curve-related features:
  * New `tools.SelectPointsTool` to select graphically multiple points on a plot
  * New `tools.EditPointTool` to edit graphically the position of a point on a plot
  * New downsampling feature:
    * The user may enable it to reduce the number of points displayed on a curve (e.g. when the curve is too dense)
    * The downsampling factor is adjustable (default to 10, i.e. 1 point out of 10 is displayed)
    * The feature is disabled by default
* Image-related features:
  * New "Colormap Manager":
    * Before this release, the colormap selection was limited to presets (e.g. "gray", "jet", etc.)
    * Now, the user can select a preset, edit it, or create a new one from scratch thanks to the new "Colormap Manager" dialog
  * New line cross section feature:
    * Before this release, the cross section feature was limited to either horizontal or vertical lines, or an average cross section withing a rectangle (aligned with the axes, or oblique)
    * Now, the user can draw a line cross section with the new "Line Cross Section" tool: the intensity profile associated to the drawn segment is displayed in a dedicated plot
* Added support for gestures:
  * Zooming in/out with the a two-finger pinch gesture
  * Panning with a two-finger drag gesture

Documentation:

* Reorganized some sections
* Added sections on new features

Bug fixes:

* Fixed critical bug in oblique cross section feature (regression introduced in 2.0.0)
* Removed dependency to `pytest-qt` for the test suite (due to Qt6 compatibility issues)
