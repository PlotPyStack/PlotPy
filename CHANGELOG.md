# Changelog #

## Version 2.1.0 ##

In this release, test coverage is 71%.

New features:

* Curve-related features:
  * New `tools.SelectPointsTool` to select graphically multiple points on a plot
  * New `tools.EditPointTool` to edit graphically the position of a point on a plot
  * New downsampling feature:
    * The user may enable it to reduce the number of points displayed on a curve
      (e.g. when the curve is too dense)
    * The downsampling factor is adjustable
      (default to 10, i.e. 1 point out of 10 is displayed)
    * The feature is disabled by default
* Image-related features:
  * New "Colormap Manager":
    * Before this release, the colormap selection was limited to presets (e.g. "gray",
      "jet", etc.)
    * Now, the user can select a preset, edit it, or create a new one from scratch
      thanks to the new "Colormap Manager" dialog
  * New line cross section feature:
    * Before this release, the cross section feature was limited to either horizontal
      or vertical lines, or an average cross section withing a rectangle (aligned with
      the axes, or oblique)
    * Now, the user can draw a line cross section with the new "Line Cross Section"
      tool: the intensity profile associated to the drawn segment is displayed in a
      dedicated plot
* Added support for gestures:
  * Zooming in/out with the a two-finger pinch gesture
  * Panning with a two-finger drag gesture

Documentation:

* Reorganized some sections
* Added sections on new features

Bug fixes:

* Fixed critical bug in oblique cross section feature (regression introduced in 2.0.0)
* Removed dependency to `pytest-qt` for the test suite (due to Qt6 compatibility issues)

## Version 2.0.3 ##

Bug fixes:

* [Issue #9](https://github.com/PlotPyStack/PlotPy/issues/9) - MacOS: `error: a space is required between consecutive right angle brackets (use '> >')`

## Version 2.0.2 ##

Bug fixes:

* [Issue #3](https://github.com/PlotPyStack/PlotPy/issues/3) - `PlotWidget`: `ZeroDivisionError` on resize while ignoring constraints
* [Issue #4](https://github.com/PlotPyStack/PlotPy/issues/4) - Average cross section: `RuntimeWarning: Mean of empty slice.`
* [Issue #5](https://github.com/PlotPyStack/PlotPy/issues/5) - Contrast panel: levels histogram is sometimes not updated
* [Issue #6](https://github.com/PlotPyStack/PlotPy/issues/6) - 1D Histogram items are not properly drawn
* [Issue #7](https://github.com/PlotPyStack/PlotPy/issues/7) - Contrast panel: histogram may contains zeros periodically due to improper bin sizes
* [Issue #8](https://github.com/PlotPyStack/PlotPy/issues/8) - Contrast panel: switch back to default tool after selecting min/max

## Version 2.0.1 ##

Bug fixes:

* Fixed `plotpy.tools.AnnotatedEllipseTool`: `AttributeError` when finalizing the shape
* `plotpy.widgets.select_with_shape_tool`: added missing `toolbar` and `options` parameters
* `items.XRangeSelection` is now serializable, as expected

Documentation:

* `plotpy.plot.SyncPlotWindow`: added missing documentation
* Added more information on PlotPyStack
* New "Motivation" section explaining the reasons behind the creation of PlotPy

## Version 2.0.0 ##

This version is the first release of the 2.0 series, which is distributed under the
[BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

PlotPy 2.0 is a major release that brings a lot of new features and bug fixes.

When initiated in 2016, PlotPy 1.0 was the result of the merge of two projects (as well
as some other changes, e.g. a redesign of the API):

* [guidata](https://pypi.org/project/guidata/), a Python library generating graphical
  user interfaces for easy dataset editing and display
* [guiqwt](https://pypi.org/project/guiqwt/), a Python library providing efficient 2D
  data-plotting features (curve/image visualization and related tools) for interactive
  computing and signal/image processing application development

With PlotPy 2.0, the [guidata](https://pypi.org/project/guidata/) code base has been
reextracted: PlotPy now relies on [guidata](https://pypi.org/project/guidata/) as a
dependency, like before the merge.

PlotPy 2.0 also integrates all the bug fixes (>30) and new features that were added to
[guiqwt](https://pypi.org/project/guiqwt/) since the merge (i.e. between 2016 and 2023).

Supported versions of Python and Qt bindings have been updated:

* Python: 3.8, 3.9, and 3.10 (3.11 should work too, but will be officially supported
  when dropping support for Python 3.8, to keep a 3-year support period)
* Qt bindings: PyQt5 (even if PyQt6 and PySide6 are not officially supported, efforts
  have been made and will continue to be made to support them)

PlotPy 2.0 is a major release because it also brings a lot of new features:

* `plot.PlotWidget`, `plot.PlotDialog`, and `plot.PlotWindow`: API overhaul
  (simple, more consistent, more flexible, more extensible - see documentation
  for details)
* `plot.SyncPlotWindow`: new class to show multiple plots in a single window,
  in a synchronized way (zoom, pan, etc.)
* `widgets.selectdialog.SelectDialog`: a dialog box to select items using a
  shape tool (segment, rectangle or custom)
* Image lookup table (LUT):
  * Initially, the LUT alpha channel was either constant (input parameter
  `alpha` was a float between 0 and 1) or linearly dependent on the image
  pixel values (when the `alpha_mask` parameter was enabled)
  * Now, the LUT may be either constant (same as before) or dependent on
  the image pixel values but not only linearly: the LUT alpha channel may
  follow a linear, a sigmoid or an hyperbolic tangent function (see the new
  `alpha_function` parameter). The old `alpha_mask` parameter was removed
* Image pixels are now centered on their coordinates:
  * This means that the pixel at row `i` and column `j` is centered on the point
  `(j, i)` (before, the top-left corner of the pixel at row `i` and column `j`
   was centered on the point `(j, i)`)
  * This convention is more consistent with the way images are displayed in other
    scientific image processing tools
  * This is one of the benefits of porting back [guiqwt](https://pypi.org/project/guiqwt/)
    changes since the merge (i.e. between 2016 and 2023)
* New SVG-based shapes:
  * `items.RectangleSVGShape`: rectangle shape based on SVG data or file
  * `items.SquareSVGShape`: square shape based on SVG data or file
  * `items.CircleSVGShape`: circle shape based on SVG data or file
* `builder.PlotBuilder`:
  * Renamed `PlotBuilder` (originally `guiqwt.builder.PlotItemBuilder`)
  * Builder instance is still available using `from plotpy.builder import make`
  * Plot widget creation is now supported:
    * `make.widget()` for `plot.PlotWidget`
    * `make.dialog()` for `plot.PlotDialog`
    * `make.window()` for `plot.PlotWindow`
  * Added support for more plot items:
    * `make.contours()` for generating a list of `items.ContourItem` objects
    * `make.annotated_point()` for `items.AnnotatedPoint`
    * `make.polygon()` for `items.PolygonShape`
    * `make.svg()` for `items.RectangleSVGShape`, `items.SquareSVGShape`,
      and `items.CircleSVGShape`
* Added JSON serialization support for all plot items (curve, image, etc.)

* Brand new documentation, based on Sphinx with links to other projects API, examples
  and tutorials (e.g. on development related topics).
* Black code formatting on all Python files
* New automated test suite:
  * Automatic execution: `--unattended` command line option (Qt loop is bypassed)
  * Test suite based on `pytest`, supporting `pytest-cov` for coverage testing,
    `pytest-xvfb` for headless testing, and `pytest-qt` for Qt testing
  * Added support for Coverage: test coverage improved up to 70%
* Added typing annotations on (almost) all Python files
* Distribution: switched to `pyproject.toml` (still relying on `setuptools` and
  `setup.py` for building Cython/C++ extensions)
* Added code quality configuration files:
  * `.pylintrc`: pylint configuration file
  * `.isort.cfg`: isort configuration file
  * `.coveragerc`: coverage configuration file
* Added Visual Studio Code configuration files:
  * `.vscode/settings.json`: Python interpreter, code formatting, etc.
  * `.vscode/tasks.json`: build, test, etc.
  * `.vscode/launch.json`: run current file, run tests, etc.

PlotPy 2.0 also brings a lot of bug fixes and improvements:

* Handled all Cython/C++ extensions compilation warnings
* Fixed all NumPy deprecation issues (e.g. `numpy.matrix`)
* Fixed (annotated) circle/ellipse item creation/test
* Fixed all documentation build warnings
* Fixed regressions introduced by PlotPy V1 on top of guiqwt:
  * Global references for the Debian package management
  * Major aspect ratio issues:
    * When resizing the plot widget (images were downsized indefinitely)
    * When auto-scaling the plot widget (images were not displayed entirely)
  * `TrImageItem` rotation algorithm
  * Oblique cross-section test
  * About dialog, version informations
* Ported all [guiqwt](https://pypi.org/project/guiqwt/) bug fixes since the merge
  (i.e. between 2016 and 2023):
  * Added support for Visual Studio 2015 and earlier
  * Speeding-up image alpha channel calculation
  * Optimized colormap icon caching
  * X-axis direction and auto-scale
  * Added load test (with a very large number of plot widgets)
  * Coordinates inversion in `EllipseShape`
  * ValueError with levels histogram
  * Various fixes regarding plot item creation, cross-section features,
    PyQt5 support, DICOM support, TIFF support, etc.
  * Etc.
