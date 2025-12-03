# Version 2.5 #

## PlotPy Version 2.5.1 (2024-08-01) ##

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
