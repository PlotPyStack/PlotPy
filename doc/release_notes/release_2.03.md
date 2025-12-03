# Version 2.3 #

## PlotPy Version 2.3.5 (2024-06-21) ##

This release is mainly intended to fix the Windows binary distribution, which was not supporting NumPy 2.0.

🛠️ Bug fixes:

* Moved back `conftest.py` to the `tests` folder (was in the root folder), so that `pytest` can be executed with proper configuration when running the test suite from the installed package

* Removed benchmarks from automated test suite (not relevant for the end user): added `plotpy-benchmarks` script to run the benchmarks

## PlotPy Version 2.3.4 (2024-06-20) ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* Add support for NumPy 2.0:
  * Updated build system to use NumPy 2.0 on Python > 3.8 and NumPy 1 on Python 3.8
  * Use `numpy.asarray` instead of `numpy.array(..., copy=False)`
  * Use `numpy.isin` instead of `numpy.in1d`
  * Use `scipy.integrate.trapezoid` instead of `numpy.trapz`

* `ColorMapManager`: fix segmentation fault with PySide6 on Linux

## PlotPy Version 2.3.3 (2024-06-13) ##

In this release, test coverage is 79%.

🛠️ Bug fixes:

* Moved up `LineCrossSection` import for consistency with other cross-section panels
* Unexpected behavior regarding `io.load_items` and `io.save_items` functions:
  * Those functions were serializing and deserializing most of the parameters of the plot items, but not their visibility state
  * This is now fixed: the visibility state of the plot items is now saved and restored as expected

ℹ️ Other changes:

* Explicitely exclude NumPy V2 from the dependencies (not compatible yet)

## PlotPy Version 2.3.2 (2024-05-07) ##

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

## PlotPy Version 2.3.0 (2024-03-11) ##

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
