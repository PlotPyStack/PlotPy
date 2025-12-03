# Version 2.4 #

## PlotPy Version 2.4.2 (2024-07-16) ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* [Issue #17](https://github.com/PlotPyStack/PlotPy/issues/17):
  * Debian's Python team has reported that the contour unit test was failing on `arm64` architecture
  * This is the opportunity to replace the `contour2d` Cython extension by scikit-image's `find_contours` function, thus avoiding to reinvent the wheel by relying on a more robust and tested implementation
  * The `contour2d` Cython extension is removed from the source code
  * The contour related features remain the same, but the implementation is now based on scikit-image's `find_contours` function
  * The scikit-image dependency is added to the package requirements

## PlotPy Version 2.4.1 (2024-07-09) ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* Contrast adjustment panel:
  * A regression was introduced in V2.0.0: levels histogram was no longer removed from contrast adjustment panel when the associated image was removed from the plot
  * This is now fixed: when an image is removed, the histogram is removed as well and the contrast panel is refreshed (which was not the case even before the regression)

## PlotPy Version 2.4.0 (2024-06-26) ##

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
