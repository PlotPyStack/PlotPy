# Version 2.7 #

## PlotPy Version 2.7.5 (2025-07-15) ##

🛠️ Bug fixes:

* [Issue #44](https://github.com/PlotPyStack/PlotPy/issues/44) - Incorrect calculation method for "∑(y)" in `CurveStatsTool`: replaced `spt.trapezoid` with `np.sum`, which is more consistent with the summation operation
* Fix `update_status` method in all cross-section tools (intensity profile tools):
  * Use `get_items` instead of `get_selected_items` to retrieve the image items
  * This allows the tools to work properly when no image item is selected, but there are image items in the plot
  * This closes [Issue #47](https://github.com/PlotPyStack/PlotPy/issues/47) - Intensity profile tools do not work when no image item is selected

Other changes:

* Updated `guidata` dependency to V3.10.0
* Using new `guidata` translation utility based on `babel`

## PlotPy Version 2.7.4 (2025-04-26) ##

In this release, test coverage is 80%.

🛠️ Bug fixes:

* [Issue #42](https://github.com/PlotPyStack/PlotPy/issues/42) - Image profiles: when moving/resizing image, profile plots are not refreshed
* [Issue #41](https://github.com/PlotPyStack/PlotPy/issues/41) - Average profile visualization: empty profile is displayed when the target rectangular area is outside the image area

## PlotPy Version 2.7.3 (2025-04-05) ##

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

## PlotPy Version 2.7.2 (2025-02-14) ##

🛠️ Bug fixes:

* [Issue #32](https://github.com/PlotPyStack/PlotPy/issues/32) - Plot item list panel's parameters dialog box is empty for non-selectable items
* [Issue #30](https://github.com/PlotPyStack/PlotPy/issues/30) - `handle_final_shape_cb` argument doesn't work on `MultilineTool`, `PolygonTool`, `AnnotatedPolygonTool`

## PlotPy Version 2.7.1 (2025-01-15) ##

🛠️ Bug fixes:

* Fixed update `canvasRect` type to `QRectF` for intersection checks in `CircleSVGShape`, following [this bug fix](https://github.com/PlotPyStack/PythonQwt/commit/d0b5e26d8f78a9a65939503553f1bc1b56826e4e) in `PythonQwt` V0.14.4
* Fixed regression with respect to `guiqwt` regarding plot items instantiation:
  * `guiqwt` was allowing to instantiate plot items without needing to create a `QApplication` instance (no GUI event loop was required)
  * This was not the case with `plotpy`, so that it was not possible -for example- to serialize/deserialize plot items to JSON without creating a `QApplication` instance
  * This has been fixed by removing the `QIcon` instantiation from the plot items constructors (call to `QwtPlotItem.setIcon` method). Note that -in the meantime- `QwtPlotItem.setIcon` and `QwtPlotItem.icon` methods have also been removed in PythonQwt V0.14.3. Code relying on this feature should thus be updated to use the new `get_icon_name` method instead, i.e. `get_icon(item.get_icon_name())` instead of `item.icon()`.
* [Issue #26](https://github.com/PlotPyStack/PlotPy/issues/26) - Item list panel should not allow to select a non-selectable item

## PlotPy Version 2.7.0 (2024-11-07) ##

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
