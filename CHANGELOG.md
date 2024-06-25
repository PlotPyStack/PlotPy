# Changelog #

## Version 2.4.0 ##

In this release, test coverage is 79%.

💥 New features / Enhancements:

* Curve statistics tool `CurveStatsTool` is now customizable:
  * When adding the tool: `plot_widget.manager.add_tool(CurveStatsTool, labelfuncs=(...))`
  * Or after: `plot_widget.manager.get_tool(CurveStatsTool).set_labelfuncs(...)`
  * The `labelfuncs` parameter is a list of tuples `(label, func)` where `label` is the
    label displayed in the statistics table, and `func` is a function that takes the
    curve data and returns the corresponding statistic value (see the documentation for
    more details)
* Image statistics tool `ImageStatsTool` is now customizable:
  * When adding the tool: `plot_widget.manager.add_tool(ImageStatsTool, stats_func=...)`
  * Or after: `plot_widget.manager.get_tool(ImageStatsTool).set_stats_func(...)`
  * The `stats_func` parameter is a function that takes the image item and selected
    rectangle coordinates, and returns a string with the statistics to display

## Version 2.3.5 ##

This release is mainly intended to fix the Windows binary distribution, which was not
supporting NumPy 2.0.

🛠️ Bug fixes:

* Moved back `conftest.py` to the `tests` folder (was in the root folder), so that
  `pytest` can be executed with proper configuration when running the test suite
  from the installed package

* Removed benchmarks from automated test suite (not relevant for the end user):
  added `plotpy-benchmarks` script to run the benchmarks

## Version 2.3.4 ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* Add support for NumPy 2.0:
  * Updated build system to use NumPy 2.0 on Python > 3.8 and NumPy 1 on Python 3.8
  * Use `numpy.asarray` instead of `numpy.array(..., copy=False)`
  * Use `numpy.isin` instead of `numpy.in1d`
  * Use `scipy.integrate.trapezoid` instead of `numpy.trapz`

* `ColorMapManager`: fix segmentation fault with PySide6 on Linux

## Version 2.3.3 ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* Moved up `LineCrossSection` import for consistency with other cross-section panels
* Unexpected behavior regarding `io.load_items` and `io.save_items` functions:
  * Those functions were serializing and deserializing most of the parameters of the
    plot items, but not their visibility state
  * This is now fixed: the visibility state of the plot items is now saved and restored
    as expected

ℹ️ Other changes:

* Explicitely exclude NumPy V2 from the dependencies (not compatible yet)

## Version 2.3.2 ##

In this release, test coverage is 79%.

Version 2.3.2 fixes a blocking issue with the colormap editor unit test introduced
in version 2.3.1. The latter is a fugitive release that was not announced.

💥 New features / Enhancements:

* Colormap: added "Apply" button to the colormap manager
* Automated test suite:
  * Test coverage has been improved from 75% to 79%
  * The following features are now covered by unit tests:
    * Panning with the mouse move events
    * Zooming with the mouse wheel/move events
    * Curve statistics tool
    * Image rotation and translations via `SelectTool` (simulating mouse events)
    * Masked areas in images and `ImageMaskTool`
    * `LockTrImageTool`
    * Cursor tools (`HCursorTool`, `VCursorTool`, `XCursorTool` and `HRangeTool`)
    * `DisplayCoordsTool`: simulation of 'Alt' and 'Ctrl' keys
    * Complete coverage for `MultiLineTool` and `FreeFormTool`
    * Selection tools (`RectangularSelectionTool` and `SelectTool`)

🛠️ Bug fixes:

* Image statistics tool: fixed "No available data" message when the tool rectangular
  region top Y coordinate is above the image top Y coordinate
* Label items (`LabelItem`, `LegendBoxItem`, `DataInfoLabel`, ...) were not emitting
  the `SIG_ITEM_MOVED` signal when moved interactively (with the mouse) if the item
  anchor was attached to the canvas
* Colormap: fixed context menu entry update (colormap icon was updated as expected, but
  the colormap name was not)
* Rotate/crop dialog: added missing toolbar on plot widget
* Flip/rotate dialog: added missing toolbar on plot widget
* Fixed issue with oblique averaged cross section computation (`AttributeError` when
  clicking on the empty cross section plot)


## Version 2.3.0 ##

In this release, test coverage is 75%.

💥 New features:

* Added support for colormap inversion:
  * The user can now invert the colormap of an image item:
    * From the image parameters dialog ("Invert colormap" checkbox)
    * From the plot context menu (right-click on the image item)
  * `BaseImageItem.set_color_map` method takes a new `invert` parameter (which
    defaults to `None`, meaning that the behavior is unchanged)
  * New `ReverseColormapTool`: registered by default in the plot widget, like the
    `ColormapTool` (add the "Invert colormap" entry in the context menu of the image)

🛠️ Bug fixes:

* `ErrorBarCurveItem`: fixed NumPy deprecation warning
  ("Conversion of an array with ndim > 0 to a scalar is deprecated [...]")

ℹ️ Other changes:

* Image plot items deserialization:
  * When an image plot item is deserialized, and needs to be reloaded from a file,
    the file path is adapted to the current working directory if file is not found
    (this is the legacy behavior).
  * An unnecessary call to `ImageIOHandler.adapt_path` method was removed from the
    `RawImageItem.deserialize` method: this issue has to be handled by the host
    application, not by the PlotPy library.
  * `ImageIOHandler`: removed `add_change_path` and `adapt_path` methods
* Fix typo in `tests.features.test_colormap_editor` module: renamed function
  `test_colormap_manager` to `test_colormap_editor`
* Removed unnecessary `BaseImageItem.get_color_map_name` method

## Version 2.2.0 ##

In this release, test coverage is 75%.

New features:

* Added `SIG_ITEM_PARAMETERS_CHANGED` signal to `BasePlot` class:
  * This signal is emitted when the parameters of an item are changed using the
    parameters dialog, or a specific tool (e.g. the colormap selection tool,
    or the lock/unlock tool for image items)
  * This signal is emitted with the item as argument
  * It is often emitted before the `SIG_ITEMS_CHANGED` signal, which is global to all
    items, but not necessarily. For example, when the colormap of an image is changed,
    the `SIG_ITEM_PARAMETERS_CHANGED` signal is emitted for the image item, but the
    `SIG_ITEMS_CHANGED` signal is not emitted.
* Added new colormap presets:
  * `viridis`, `plasma`, `inferno`, `magma`, `cividis`
  * `afmhot`
  * `coolwarm`, `bwr`, `seismic`
  * `gnuplot2`, `CMRmap`, `rainbow`, `turbo`
* Fixed all qualitative colormaps:
  * All qualitative colormaps have been re-computed because they are not supposed to be
    interpolated, which was the case and made them unusable
  * The qualitative colormaps are now usable and look like the ones from Matplotlib
* Colormap manager:
  * Added a button to remove a custom colormap
  * The preset colormaps *and* the currently selected colormap are read-only
* Added automatic unit tests for interactive tools:
  * `AnnotatedCircleTool`, `AnnotatedEllipseTool`, `AnnotatedObliqueRectangleTool`,
    `AnnotatedPointTool`, `AnnotatedRectangleTool`, `AnnotatedSegmentTool`
  * `AverageCrossSectionTool`, `CrossSectionTool`, `ObliqueCrossSectionTool`,
    `LineCrossSectionTool`
  * `EditPointTool`, `SelectPointsTool`, `SelectPointTool`
  * `AspectRatioTool`, `ImageStatsTool`, `SnapshotTool`
  * `DisplayCoordsTool`, `RectZoomTool`
  * `CircleTool`, `EllipseTool`, `FreeFormTool`, `MultiLineTool`,
    `ObliqueRectangleTool`, `PointTool`, `RectangleTool`, `SegmentTool`
* Internal package reorganization: moved icons to `plotpy/data/icons` folder

## Version 2.1.2 ##

New features:

* Added `Echelon` alpha function to the image parameters:
  * The `Echelon` alpha function is a step function, so that the alpha channel is
    0 (full transparency) for the lowest value of the Lookup Table (LUT) and opaque
    (transparency level set by the `Global alpha` parameter) for the other values
  * This feature is added to the other existing alpha functions: `Constant`, `Linear`,
    `Sigmoid`, and `Hyperbolic tangent`

Bug fixes:

* Compatibility with PythonQwt 0.12.

## Version 2.1.1 ##

Bug fixes:

* API breakage (unintentional) in V2.1.0:
  * In V2.1.0, `mathutils.colormap` module was renamed to `mathutils.colormaps`
  * Original `mathutils.colormap` module naming is restored in this release
* Colormap selection from the toolbar was not triggering the `SIG_ITEMS_CHANGED` signal
  (every time an item parameter is changed, the `SIG_ITEMS_CHANGED` signal has to be
  emitted by the `BasePlot` instance to notify the application that the plot has been
  modified)

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
