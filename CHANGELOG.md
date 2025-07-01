# Changelog #

## Version 2.8.0 ##

💥 New features / Enhancements:

* [Issue #45](https://github.com/PlotPyStack/PlotPy/issues/45) - Add support for new curve Y-range cursor tool `YRangeCursorTool`:
  * This tool is similar to the existing `CurveStatsTool`, but it simply shows the Y-range values (min, max and interval).
  * It can be added to the plot widget using `plot_widget.manager.add_tool(YRangeCursorTool)`

🛠️ Bug fixes:

* [Issue #44](https://github.com/PlotPyStack/PlotPy/issues/44) - Incorrect calculation method for "∑(y)" in `CurveStatsTool`: replaced `spt.trapezoid` with `np.sum`, which is more consistent with the summation operation

Other changes:

* Updated `guidata` dependency to V3.10.0
* Using new `guidata` translation utility based on `babel`

## Version 2.7.4 ##

In this release, test coverage is 80%.

🛠️ Bug fixes:

* [Issue #42](https://github.com/PlotPyStack/PlotPy/issues/42) - Image profiles: when moving/resizing image, profile plots are not refreshed
* [Issue #41](https://github.com/PlotPyStack/PlotPy/issues/41) - Average profile visualization: empty profile is displayed when the target rectangular area is outside the image area

## Version 2.7.3 ##

In this release, test coverage is 80%.

🛠️ Bug fixes:

* [Issue #40](https://github.com/PlotPyStack/PlotPy/issues/40) - Z-axis logarithmic scale (`ZAxisLogTool` tool) is not compatible with anti-aliasing interpolation
* Fix intersection check for destination rectangle in `XYImageFilterItem`
* [Issue #36](https://github.com/PlotPyStack/PlotPy/issues/36) - Image items are not properly scaling along Y-axis with logarithmic scale:
  * Actually, image items do not support non-linear scales (this is an historical limitation)
  * This is not documented at all, so we've added an explicit warning: a red colored message is displayed at the center of the image frame when any non-linear scale is applied to either X or Y axis
  * When dealing with non-linear scales, PlotPy provides an alternative solution: the user may rely on `XYImageItem` (e.g. by using `make.xyimage`) as this item supports arbitrary X and Y pixel coordinates
* [Issue #34](https://github.com/PlotPyStack/PlotPy/issues/34) - `ValueError` when trying to plot 2D histogram items with `PyQt6`

Other changes:

* Replace deprecated icon files with new SVG icons for selection tools

## Version 2.7.2 ##

🛠️ Bug fixes:

* [Issue #32](https://github.com/PlotPyStack/PlotPy/issues/32) - Plot item list panel's parameters dialog box is empty for non-selectable items
* [Issue #30](https://github.com/PlotPyStack/PlotPy/issues/30) - `handle_final_shape_cb` argument doesn't work on `MultilineTool`, `PolygonTool`, `AnnotatedPolygonTool`

## Version 2.7.1 ##

🛠️ Bug fixes:

* Fixed update `canvasRect` type to `QRectF` for intersection checks in `CircleSVGShape`, following [this bug fix](https://github.com/PlotPyStack/PythonQwt/commit/d0b5e26d8f78a9a65939503553f1bc1b56826e4e) in `PythonQwt` V0.14.4
* Fixed regression with respect to `guiqwt` regarding plot items instantiation:
  * `guiqwt` was allowing to instantiate plot items without needing to create a `QApplication` instance (no GUI event loop was required)
  * This was not the case with `plotpy`, so that it was not possible -for example- to serialize/deserialize plot items to JSON without creating a `QApplication` instance
  * This has been fixed by removing the `QIcon` instantiation from the plot items constructors (call to `QwtPlotItem.setIcon` method). Note that -in the meantime- `QwtPlotItem.setIcon` and `QwtPlotItem.icon` methods have also been removed in PythonQwt V0.14.3. Code relying on this feature should thus be updated to use the new `get_icon_name` method instead, i.e. `get_icon(item.get_icon_name())` instead of `item.icon()`.
* [Issue #26](https://github.com/PlotPyStack/PlotPy/issues/26) - Item list panel should not allow to select a non-selectable item

## Version 2.7.0 ##

Supported versions of Python have been updated (drop support for Python 3.8, add support for Python 3.13):

* PlotPy < 2.7.0: Python 3.8, 3.9, 3.10, 3.11 and 3.12
* PlotPy >= 2.7.0: Python 3.9, 3.10, 3.11, 3.12 and 3.13

Other dependencies have been updated:

* Updated versions to those available at the time of the release of the oldest supported Python version (3.9)
* Exception: Cython 3.0 is required for Python 3.13

💥 New features / Enhancements:

* Added `AnnotatedPolygon` annotation to items
* Added `make.annotated_polygon` function to `plotpy.builder` module
* Customization of annotation information:
  * Added `info_callback` argument to all annotation class constructors
  * Added `set_info_callback` method to all annotation classes
  * The `info_callback` is a function that takes the annotation object and returns a string with the information to display
  * Default `info_callback` is redirected to the `get_info` method of the annotation object (this makes the feature backward compatible)

🛠️ Bug fixes:

* Fixed `pydicom` support: use `dcmread` instead of `read_file` to read DICOM files

## Version 2.6.3 ##

🧯 In this release, test coverage is 79%.

🛠️ Bug fixes:

* [Issue #25](https://github.com/PlotPyStack/PlotPy/issues/25) - `OverflowError` with Contrast Adjustment panel for constant images
* When updating image parameters (`ImageParam`) from the associated item object:
  * If `xmin`, `xmax`, `ymin`, `ymax` attributes are not yet set (i.e. `None`), do not update them with the image data bounds
  * Previous behavior was to update them with the image data bounds, which was leading to breaking the automatic bounds update when the image data is updated
* [Issue #24](https://github.com/PlotPyStack/PlotPy/issues/24) - Colormap: side effect on image axes when changing the colormap
* [Issue #23](https://github.com/PlotPyStack/PlotPy/issues/23) - Windows: Image `_scaler` engine performance regression
* PySide6 compatibility issues:
  * Fixed deprecated call to `QMouseEvent` in `tests/unit/utils.py`
  * Added workaround for `QPolygonF` shape point slicing
* [Issue #21](https://github.com/PlotPyStack/PlotPy/issues/21) - PySide6 on Linux: segfault in test_colormap_editor.py
* Fixed `sliderMoved` signal connection in `ColorMapEditor`
* Fixed `AssertionError` in test_rect_zoom.py (Linux, Python 3.12, PyQt6)
* Fixed typing issues in `plotpy.events` module:
  * Event objects were not properly typed (`QtCore.QEvent` instead of `QtGui.QMouseEvent`)
  * Event position arguments were not properly typed (`QtCore.QPoint` instead of `QtCore.QPointF`)
* Fix NumPy `FutureWarning: Format strings passed to MaskedConstant are ignored [...]` when displaying masked pixel coordinates

## Version 2.6.2 ##

💥 New features / Enhancements:

* Added Wheel packages for all major platforms on PyPI:
  * Windows (32/64bits), MacOS, Linux
  * Python 3.8 to 3.12

🛠️ Bug fixes:

* Fixed color theme support (dark/light mode), leveraging the new `guidata` V3.6 feature

## Version 2.6.1 ##

ℹ️ Release V2.6.0 was a fugitive release that was replaced by V2.6.1 due to a critical bug in the segment line cross section computation for masked images.

💥 New features / Enhancements:

* Added support for color theme change at execution (relies on guidata V3.6)
* Changed strategy for default plot widget size:
  * No default size is applied to the plot widget anymore (before, the default size was 800x600 pixels)
  * Added parameter `size` to `PlotDialog`, `PlotWindow` classes, and `make.dialog`, `make.window` functions to set the initial size of the plot widget

🛠️ Bug fixes:

* Fixed segment line cross section computation for masked images:
  * Avoided warning message when encountering masked values in the image data
  * Replacing masked values by NaNs when computing the segment line cross section (as before, but explicitely, to avoid the warning message)

## Version 2.5.1 ##

ℹ️ Release V2.5.0 was a fugitive release that was replaced by V2.5.1 due to packaging issues.

In this release, test coverage is 79%.

💥 New features / Enhancements:

* Alternative dictionary argument for plot options:
  * This new feature was introduced in the context of the cyclic import bug fix, to avoid importing the `plotpy.plot` module just to get the `PlotOptions` or `BasePlotOptions` classes
  * All classes (and a few functions) that used to take an `options` argument as a `BasePlotOptions` or `PlotOptions` instance now also accept a dictionary argument with the same keys as the `BasePlotOptions` or `PlotOptions` class attributes, and the same values as the corresponding attributes
  * This concerns the following classes and functions:
    * `plotpy.plot.BasePlot`
    * `plotpy.plot.PlotWidget`
    * `plotpy.plot.PlotDialog`
    * `plotpy.plot.PlotWindow`
    * `plotpy.plot.SubPlotWidget`
    * `plotpy.plot.SyncPlotWindow`
    * `plotpy.tools.RotateCropTool`
    * `plotpy.widgets.fit.FitDialog`
    * `plotpy.widgets.fliprotate.FlipRotateDialog`
    * `plotpy.widgets.rotatecrop.RotateCropDialog`
    * `plotpy.widgets.selectdialog.SelectDialog`
    * `plotpy.widgets.selectdialog.select_with_shape_tool`

* Added "Lock LUT range" option for image items:
  * This new option is disabled by default, which matches the previous behavior: when updating an image item data, the LUT range is automatically adjusted to the new data range (if not passed as an argument to the `BaseImageItem.set_data` method)
  * When enabled, the LUT range is locked and the LUT range is not adjusted when updating the image item data
  * The option is available in image parameters dialog
  * A new tool `LockLUTRangeTool` has been implemented to toggle the option from the plot context menu: the tool is not registered by default in the plot widget, but can be added by the host application if needed
  * See test script `tests.features.test_image_data_update` for an example of usage of the new option and tool

* Added missing `set_style` method to `XRangeSelection` class: this method is used to set the style of the range selection item from configuration options

🛠️ Bug fixes:

* [Issue #19](https://github.com/PlotPyStack/PlotPy/issues/19) - Fix `distutils` deprecation in setup.py: replaced `distutils.core` by `setuptools` in the setup.py script to avoid the deprecation warning when building the package with Python 3.10 and 3.11, and to ensure compatibility with earlier Python versions (PlotPy is already compatible with the most recent Python versions: this only concerns the build system)
* Fix cyclic import in `plotpy.tools` module:
  * Some tools in `plotpy.tools` subpackage were importing the `plotpy.plot` module, which was importing the `plotpy.tools` module, causing a cyclic import issue
  * This is now fixed by introducing new constants for axis IDs in the `plotpy.constants` module, and using them everywhere in the code, thus avoiding to import the `plotpy.plot` module just to get the axis IDs
* Fix empty label in X/Y cross section plots:
  * This is a regression introduced in V2.1.0
  * When showing the X/Y cross section plots (using the plot context menu), an empty label was displayed at the center of each of those plots
  * The label now shows "Enable a marker" as previously
* Fix historic unexpected behavior of interactive tools:
  * When triggering an interactive tool (e.g. by clicking on the corresponding toolbar button), the tool `activate` method was called twice, which was not expected, but was not causing any issue given the current implementation
  * However, when defining custom interactive tools, this behavior could lead to unexpected results (i.e. really executing activation actions twice)
  * This is now fixed: the `activate` method is called only once when triggering an interactive tool

## Version 2.4.2 ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* [Issue #17](https://github.com/PlotPyStack/PlotPy/issues/17):
  * Debian's Python team has reported that the contour unit test was failing on `arm64` architecture
  * This is the opportunity to replace the `contour2d` Cython extension by scikit-image's `find_contours` function, thus avoiding to reinvent the wheel by relying on a more robust and tested implementation
  * The `contour2d` Cython extension is removed from the source code
  * The contour related features remain the same, but the implementation is now based on scikit-image's `find_contours` function
  * The scikit-image dependency is added to the package requirements

## Version 2.4.1 ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* Contrast adjustment panel:
  * A regression was introduced in V2.0.0: levels histogram was no longer removed from contrast adjustment panel when the associated image was removed from the plot
  * This is now fixed: when an image is removed, the histogram is removed as well and the contrast panel is refreshed (which was not the case even before the regression)

## Version 2.4.0 ##

In this release, test coverage is 79%.

💥 New features / Enhancements:

* Contrast adjustment panel:
  * New layout: the vertical toolbar (which was constrained in a small area on the right side of the panel) is now a horizontal toolbar at the top of the panel, beside the title
  * New "Set range" button: allows the user to set manually the minimum and maximum values of the histogram range
* New Z-axis logarithmic scale feature:
  * Added new tool `ZAxisLogTool` to toggle the Z-axis logarithmic scale
  * The tool is registered by default in the plot widget, like the `ColormapTool`
  * When enabled, the active image item is displayed after applying a base-10 logarithm to its pixel values
* Curve statistics tool `CurveStatsTool` is now customizable:
  * When adding the tool: `plot_widget.manager.add_tool(CurveStatsTool, labelfuncs=(...))`
  * Or after: `plot_widget.manager.get_tool(CurveStatsTool).set_labelfuncs(...)`
  * The `labelfuncs` parameter is a list of tuples `(label, func)` where `label` is the label displayed in the statistics table, and `func` is a function that takes the curve data and returns the corresponding statistic value (see the documentation for more details)
* Image statistics tool `ImageStatsTool` is now customizable:
  * When adding the tool: `plot_widget.manager.add_tool(ImageStatsTool, stats_func=...)`
  * Or after: `plot_widget.manager.get_tool(ImageStatsTool).set_stats_func(...)`
  * The `stats_func` parameter is a function that takes the image item and selected rectangle coordinates, and returns a string with the statistics to display
* New `SIG_AXIS_PARAMETERS_CHANGED` signal emitted by `BasePlot` when the axes parameters are changed (e.g. when the axes are inverted, or the scale is changed)
* New "Reverse X axis" feature:
  * Added new tool `ReverseXAxisTool` to toggle the X-axis direction
  * The tool is registered by default in the plot widget, like its Y-axis counterpart

🛠️ Bug fixes:

* Contrast adjustment panel:
  * Fixed histogram update issues when no image was currently selected (even if the an image was displayed and was selected before)
  * Histogram range was not updated when either the minimum or maximum value was set using the "Minimum value" or "Maximum value" buttons (which have been renamed to "Min." and "Max." in this release)
  * Histogram range was not updated when the "Set full range" button was clicked
* Image parameters: contrast range was not updated when the image Z axis bounds were changed using the "Parameters" dialog

🧹 API cleanup:

* Deprecated `AnnotationParam.update_annotation` method: use `update_item` instead
* Deprecated `AxesShapeParam.update_axes` method: use `update_item` instead
* Deprecated `AxesParam.update_axes` method: use `update_item` instead
* Deprecated `ImageAxesParam.update_axes` method: use `update_item` instead
* Deprecated `LabelParam.update_label` method: use `update_item` instead
* Deprecated `MarkerParam.update_marker` method: use `update_item` instead
* Deprecated `RangeShapeParam.update_range` method: use `update_item` instead
* Deprecated `ShapeParam.update_shape` method: use `update_item` instead

## Version 2.3.5 ##

This release is mainly intended to fix the Windows binary distribution, which was not supporting NumPy 2.0.

🛠️ Bug fixes:

* Moved back `conftest.py` to the `tests` folder (was in the root folder), so that `pytest` can be executed with proper configuration when running the test suite from the installed package

* Removed benchmarks from automated test suite (not relevant for the end user): added `plotpy-benchmarks` script to run the benchmarks

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
  * Those functions were serializing and deserializing most of the parameters of the plot items, but not their visibility state
  * This is now fixed: the visibility state of the plot items is now saved and restored as expected

ℹ️ Other changes:

* Explicitely exclude NumPy V2 from the dependencies (not compatible yet)

## Version 2.3.2 ##

In this release, test coverage is 79%.

Version 2.3.2 fixes a blocking issue with the colormap editor unit test introduced in version 2.3.1. The latter is a fugitive release that was not announced.

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

* Image statistics tool: fixed "No available data" message when the tool rectangular region top Y coordinate is above the image top Y coordinate
* Label items (`LabelItem`, `LegendBoxItem`, `DataInfoLabel`, ...) were not emitting the `SIG_ITEM_MOVED` signal when moved interactively (with the mouse) if the item anchor was attached to the canvas
* Colormap: fixed context menu entry update (colormap icon was updated as expected, but the colormap name was not)
* Rotate/crop dialog: added missing toolbar on plot widget
* Flip/rotate dialog: added missing toolbar on plot widget
* Fixed issue with oblique averaged cross section computation (`AttributeError` when clicking on the empty cross section plot)

## Version 2.3.0 ##

In this release, test coverage is 75%.

💥 New features:

* Added support for colormap inversion:
  * The user can now invert the colormap of an image item:
    * From the image parameters dialog ("Invert colormap" checkbox)
    * From the plot context menu (right-click on the image item)
  * `BaseImageItem.set_color_map` method takes a new `invert` parameter (which defaults to `None`, meaning that the behavior is unchanged)
  * New `ReverseColormapTool`: registered by default in the plot widget, like the `ColormapTool` (add the "Invert colormap" entry in the context menu of the image)

🛠️ Bug fixes:

* `ErrorBarCurveItem`: fixed NumPy deprecation warning ("Conversion of an array with ndim > 0 to a scalar is deprecated [...]")

ℹ️ Other changes:

* Image plot items deserialization:
  * When an image plot item is deserialized, and needs to be reloaded from a file, the file path is adapted to the current working directory if file is not found (this is the legacy behavior).
  * An unnecessary call to `ImageIOHandler.adapt_path` method was removed from the `RawImageItem.deserialize` method: this issue has to be handled by the host application, not by the PlotPy library.
  * `ImageIOHandler`: removed `add_change_path` and `adapt_path` methods
* Fix typo in `tests.features.test_colormap_editor` module: renamed function `test_colormap_manager` to `test_colormap_editor`
* Removed unnecessary `BaseImageItem.get_color_map_name` method

## Version 2.2.0 ##

In this release, test coverage is 75%.

New features:

* Added `SIG_ITEM_PARAMETERS_CHANGED` signal to `BasePlot` class:
  * This signal is emitted when the parameters of an item are changed using the parameters dialog, or a specific tool (e.g. the colormap selection tool, or the lock/unlock tool for image items)
  * This signal is emitted with the item as argument
  * It is often emitted before the `SIG_ITEMS_CHANGED` signal, which is global to all items, but not necessarily. For example, when the colormap of an image is changed, the `SIG_ITEM_PARAMETERS_CHANGED` signal is emitted for the image item, but the `SIG_ITEMS_CHANGED` signal is not emitted.
* Added new colormap presets:
  * `viridis`, `plasma`, `inferno`, `magma`, `cividis`
  * `afmhot`
  * `coolwarm`, `bwr`, `seismic`
  * `gnuplot2`, `CMRmap`, `rainbow`, `turbo`
* Fixed all qualitative colormaps:
  * All qualitative colormaps have been re-computed because they are not supposed to be interpolated, which was the case and made them unusable
  * The qualitative colormaps are now usable and look like the ones from Matplotlib
* Colormap manager:
  * Added a button to remove a custom colormap
  * The preset colormaps *and* the currently selected colormap are read-only
* Added automatic unit tests for interactive tools:
  * `AnnotatedCircleTool`, `AnnotatedEllipseTool`, `AnnotatedObliqueRectangleTool`, `AnnotatedPointTool`, `AnnotatedRectangleTool`, `AnnotatedSegmentTool`
  * `AverageCrossSectionTool`, `CrossSectionTool`, `ObliqueCrossSectionTool`, `LineCrossSectionTool`
  * `EditPointTool`, `SelectPointsTool`, `SelectPointTool`
  * `AspectRatioTool`, `ImageStatsTool`, `SnapshotTool`
  * `DisplayCoordsTool`, `RectZoomTool`
  * `CircleTool`, `EllipseTool`, `FreeFormTool`, `MultiLineTool`, `ObliqueRectangleTool`, `PointTool`, `RectangleTool`, `SegmentTool`
* Internal package reorganization: moved icons to `plotpy/data/icons` folder

## Version 2.1.2 ##

New features:

* Added `Echelon` alpha function to the image parameters:
  * The `Echelon` alpha function is a step function, so that the alpha channel is 0 (full transparency) for the lowest value of the Lookup Table (LUT) and opaque (transparency level set by the `Global alpha` parameter) for the other values
  * This feature is added to the other existing alpha functions: `Constant`, `Linear`, `Sigmoid`, and `Hyperbolic tangent`

Bug fixes:

* Compatibility with PythonQwt 0.12.

## Version 2.1.1 ##

Bug fixes:

* API breakage (unintentional) in V2.1.0:
  * In V2.1.0, `mathutils.colormap` module was renamed to `mathutils.colormaps`
  * Original `mathutils.colormap` module naming is restored in this release
* Colormap selection from the toolbar was not triggering the `SIG_ITEMS_CHANGED` signal (every time an item parameter is changed, the `SIG_ITEMS_CHANGED` signal has to be emitted by the `BasePlot` instance to notify the application that the plot has been modified)

## Version 2.1.0 ##

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

This version is the first release of the 2.0 series, which is distributed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

PlotPy 2.0 is a major release that brings a lot of new features and bug fixes.

When initiated in 2016, PlotPy 1.0 was the result of the merge of two projects (as well as some other changes, e.g. a redesign of the API):

* [guidata](https://pypi.org/project/guidata/), a Python library generating graphical user interfaces for easy dataset editing and display
* [guiqwt](https://pypi.org/project/guiqwt/), a Python library providing efficient 2D data-plotting features (curve/image visualization and related tools) for interactive computing and signal/image processing application development

With PlotPy 2.0, the [guidata](https://pypi.org/project/guidata/) code base has been reextracted: PlotPy now relies on [guidata](https://pypi.org/project/guidata/) as a dependency, like before the merge.

PlotPy 2.0 also integrates all the bug fixes (>30) and new features that were added to [guiqwt](https://pypi.org/project/guiqwt/) since the merge (i.e. between 2016 and 2023).

Supported versions of Python and Qt bindings have been updated:

* Python: 3.8, 3.9, and 3.10 (3.11 should work too, but will be officially supported when dropping support for Python 3.8, to keep a 3-year support period)
* Qt bindings: PyQt5 (even if PyQt6 and PySide6 are not officially supported, efforts have been made and will continue to be made to support them)

PlotPy 2.0 is a major release because it also brings a lot of new features:

* `plot.PlotWidget`, `plot.PlotDialog`, and `plot.PlotWindow`: API overhaul (simple, more consistent, more flexible, more extensible - see documentation for details)
* `plot.SyncPlotWindow`: new class to show multiple plots in a single window, in a synchronized way (zoom, pan, etc.)
* `widgets.selectdialog.SelectDialog`: a dialog box to select items using a shape tool (segment, rectangle or custom)
* Image lookup table (LUT):
  * Initially, the LUT alpha channel was either constant (input parameter `alpha` was a float between 0 and 1) or linearly dependent on the image pixel values (when the `alpha_mask` parameter was enabled)
  * Now, the LUT may be either constant (same as before) or dependent on the image pixel values but not only linearly: the LUT alpha channel may follow a linear, a sigmoid or an hyperbolic tangent function (see the new `alpha_function` parameter). The old `alpha_mask` parameter was removed
* Image pixels are now centered on their coordinates:
  * This means that the pixel at row `i` and column `j` is centered on the point `(j, i)` (before, the top-left corner of the pixel at row `i` and column `j` was centered on the point `(j, i)`)
  * This convention is more consistent with the way images are displayed in other scientific image processing tools
  * This is one of the benefits of porting back [guiqwt](https://pypi.org/project/guiqwt/) changes since the merge (i.e. between 2016 and 2023)
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
    * `make.svg()` for `items.RectangleSVGShape`, `items.SquareSVGShape`, and `items.CircleSVGShape`
* Added JSON serialization support for all plot items (curve, image, etc.)

* Brand new documentation, based on Sphinx with links to other projects API, examples and tutorials (e.g. on development related topics).
* Black code formatting on all Python files
* New automated test suite:
  * Automatic execution: `--unattended` command line option (Qt loop is bypassed)
  * Test suite based on `pytest`, supporting `pytest-cov` for coverage testing, `pytest-xvfb` for headless testing, and `pytest-qt` for Qt testing
  * Added support for Coverage: test coverage improved up to 70%
* Added typing annotations on (almost) all Python files
* Distribution: switched to `pyproject.toml` (still relying on `setuptools` and `setup.py` for building Cython/C++ extensions)
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
* Ported all [guiqwt](https://pypi.org/project/guiqwt/) bug fixes since the merge (i.e. between 2016 and 2023):
  * Added support for Visual Studio 2015 and earlier
  * Speeding-up image alpha channel calculation
  * Optimized colormap icon caching
  * X-axis direction and auto-scale
  * Added load test (with a very large number of plot widgets)
  * Coordinates inversion in `EllipseShape`
  * ValueError with levels histogram
  * Various fixes regarding plot item creation, cross-section features, PyQt5 support, DICOM support, TIFF support, etc.
  * Etc.
