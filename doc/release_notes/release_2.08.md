# Version 2.8 #

## PlotPy Version 2.8.4 (2026-02-14) ##

💥 New features:

* Added official support for Python 3.14

🛠️ Bug fixes:

* Fixed PySide6 compatibility issues causing segfaults in the test suite:
  * Use `object` instead of C++ type strings (e.g., `"QMouseEvent"`, `"QEvent"`, `"QPointF"`) in `Signal` declarations — PySide6 segfaults with C++ type name strings
  * Check QObject validity via `is_qobject_valid()` before accessing widgets in `__del__`, `closeEvent`, and panel close operations — PySide6 segfaults on deleted C++ objects instead of raising `RuntimeError`
  * Restructure `BaseSyncPlot.__init__` to defer widget operations until after Qt `__init__` completes — PySide6 requires `__init__` to have fully completed before the widget can be used as a parent
  * Replace deprecated `exec_()` calls with `exec()`
* Fixed `test_multiline_tool` failing with PyQt6 due to smaller canvas size:
  * The spiral test data started at `t=0`, placing the first two points so close together that they mapped to the same pixel on PyQt6's smaller default canvas
  * Start the spiral at `t=2π` to ensure sufficient pixel spacing between consecutive points
* Fixed pytest running all tests when selecting a single test from VS Code:
  * Move `plotpy` from `addopts` to `testpaths` in `[tool.pytest.ini_options]`

🔧 Other changes:

* Add missing `setuptools` to `requirements.txt` (dev)
* Update GitHub Actions to use latest artifact upload and download versions
* Update `cibuildwheel` version to v3.3.1 for improved wheel building
* Add `.venv*` to `.gitignore` to exclude virtual environment files

## PlotPy Version 2.8.3 (2025-12-18) ##

💥 New features:

* `AnnotatedSegment` new angle display:
  * Added angle display in annotation label, showing the segment's angle relative to the horizontal direction (0° to 180°)
  * This implements the equivalent feature submitted in [Pull Request #51](https://github.com/PlotPyStack/PlotPy/pull/51) by user @deuterium33

🛠️ Bug fixes:

* Fixed `IndexError` when displaying images with a single row or column (e.g., SIF files with shape `(1, N)`):
  * The `to_bins()` function now handles single-element coordinate arrays by assuming a bin width of 1.0 centered on the point
  * Previously, loading such images in DataLab caused an `IndexError: index 1 is out of bounds for axis 0 with size 1`
* Fixed circle/ellipse shape drawing with non-uniform aspect ratios:
  * Axes were not perpendicular and did not connect to the ellipse edge when plot aspect ratio differed from 1.0
  * Now uses parametric ellipse drawing that correctly handles non-perpendicular axes in pixel space
  * The ellipse properly passes through all four handle points regardless of aspect ratio or rotation
* Fixed angle display range for `AnnotatedObliqueRectangle` and `AnnotatedEllipse`:
  * Angle is now displayed in the 0° to 180° range instead of -90° to 90° (the original implementation was also displaying 0° at vertical orientation -additionally to horizontal orientation- which was counter-intuitive)
  * This provides a more intuitive and consistent angle representation

## PlotPy Version 2.8.2 (2025-11-10) ##

🛠️ Bug fixes:

* Fixed `RuntimeWarning` when changing masked image data type from float to integer:
  * `MaskedImageItem.update_mask()` now handles NaN and None `filling_value` gracefully
  * When converting to integer dtypes, NaN/None values are replaced with 0 instead of triggering numpy cast warnings
  * When converting to float dtypes, NaN is preserved as the fill value
  * Added comprehensive tests to validate dtype conversion scenarios

## PlotPy Version 2.8.1 (2025-11-06) ##

🛠️ Bug fixes:

* [Issue #50](https://github.com/PlotPyStack/PlotPy/issues/50) - Fixed ImageStatsTool displaying "No available data" for `XYImageItem` and `MaskedXYImageItem`:
  * Added `IExportROIImageItemType` to `XYImageItem.types()` so that `get_items_in_rectangle()` can properly identify XY image items
  * Updated `__implements__` tuples for consistency across `XYImageItem`, `MaskedXYImageItem`, and `MaskedImageItem`
  * The tool now correctly displays statistics for images with non-uniform coordinates
* Fixed snapshot tool failing with `SystemError` on `XYImageItem` and `MaskedXYImageItem`:
  * Fixed `assemble_imageitems` passing list instead of tuple to C extension function `_scale_rect`
  * Added missing `export_roi` method to `XYImageItem` to properly handle non-uniform coordinate transformations
  * Snapshots of XY images now render correctly instead of producing black images

## PlotPy Version 2.8.0 (2025-10-24) ##

💥 New features / Enhancements:

* Curve fitting: added support for locked parameters:
  * New `locked` parameter in `FitParam` class to lock parameter values during automatic optimization
  * New `locked` field in `FitParamDataSet` to configure parameter locking via the settings dialog
  * When locked, parameters retain their manually-adjusted values during auto-fit
  * Visual indicators: locked parameters show a 🔒 emoji and are grayed out with disabled controls
  * All optimization algorithms (simplex, Powell, BFGS, L-BFGS-B, conjugate gradient, least squares) fully support locked parameters
  * Enables partial optimization workflows: fix well-determined parameters, optimize uncertain ones
  * Improves fit convergence by reducing problem dimensionality
* Configurable autoscale margin:
  * Added `autoscale_margin_percent` parameter to `BasePlotOptions` for intuitive percentage-based margin control
  * Users can now specify autoscale margins as percentages (e.g., `0.2` for 0.2%, `5.0` for 5%)
  * Replaces the previous decimal-based approach with more user-friendly percentage values
  * Default remains 0.2% (equivalent to previous 0.002) for backward compatibility
  * Includes validation to prevent unreasonable values (0-50% range)
* Image statistics tool improvements:
  * Enhanced `get_stats` function to display delta (Δ) values for coordinate ranges
  * Now shows Δx, Δy, and Δz values alongside the min/max ranges for better analysis
* Added optional "Axes" tab control in Parameters dialog:
  * New `show_axes_tab` option in `BasePlotOptions` and `PlotOptions` (default: `True`)
  * When set to `False`, the "Axes" tab is hidden from item parameter dialogs
  * This allows applications to provide their own axes management while using PlotPy
  * Can be configured during plot creation or changed at runtime using `plot.set_show_axes_tab(False)`
* [Issue #45](https://github.com/PlotPyStack/PlotPy/issues/45) - Add support for new curve Y-range cursor tool `YRangeCursorTool`:
  * This tool is similar to the existing `CurveStatsTool`, but it simply shows the Y-range values (min, max and interval).
  * It can be added to the plot widget using `plot_widget.manager.add_tool(YRangeCursorTool)`
* Update color configurations defaults for improved visibility
* Item list:
  * Added a new "Rename" context menu entry to rename the selected item
  * This entry is only available for editable items
* X and Y range selection items:
  * Added support for item title in parameters data set (`RangeShapeParam`)
  * This concerns the `XRangeSelection` and `YRangeSelection` items
* New annotated X and Y range selection items:
  * Added `AnnotatedXRange` and `AnnotatedYRange` items
  * These items provide X and Y range selection with an annotation label
  * They can be created using `make.annotated_xrange` and `make.annotated_yrange` functions
* New `SyncPlotDialog` class:
  * This class provides a dialog for displaying synchronized plots.
  * This is a complementary class to `SyncPlotWindow`, providing a modal dialog interface for synchronized plotting.
* Native datetime axis support:
  * Added `BasePlot.set_axis_datetime()` method to easily configure an axis for datetime display
  * Added `BasePlot.set_axis_limits_from_datetime()` method to set axis limits using datetime objects directly
  * Supports customizable datetime format strings using Python's `strftime` format codes
  * Configurable label rotation and spacing for optimal display
  * Example: `plot.set_axis_datetime("bottom", format="%H:%M:%S")` for time-only display
  * Example: `plot.set_axis_limits_from_datetime("bottom", dt1, dt2)` to zoom to a specific time range
  * Added `"datetime"` as a valid scale type (alongside `"lin"` and `"log"`) for axis configuration
  * Added datetime coordinate formatting support throughout PlotPy:
    * Cursor tools (`VCursorTool`, `HCursorTool`, `XCursorTool`) now display datetime-formatted X/Y coordinates
    * `CurveStatsTool` now displays datetime-formatted X coordinates for statistical computations
    * Marker labels automatically format coordinates as datetime when axis uses datetime scale
    * Coordinate display in the plot canvas now shows datetime format when appropriate
    * Refactored `ObjectInfo` base class to provide shared datetime formatting methods for code reuse

🧹 API cleanup: removed deprecated update methods (use `update_item` instead)

* Removed `AnnotationParam.update_annotation` method
* Removed `AxesShapeParam.update_axes` method
* Removed `AxesParam.update_axes` method
* Removed `ImageAxesParam.update_axes` method
* Removed `LabelParam.update_label` method
* Removed `MarkerParam.update_marker` method
* Removed `RangeShapeParam.update_range` method
* Removed `ShapeParam.update_shape` method

🛠️ Bug fixes:

* Fixed `RuntimeError` in `SyncPlotWindow` and `SyncPlotDialog` when closing widgets quickly:
  * Fixed "wrapped C/C++ object of type QwtScaleWidget has been deleted" error that occurred when widgets were closed before the deferred plot rescaling operation could complete
  * Replaced `QTimer.singleShot()` with controllable `QTimer` instances that can be stopped on widget close
  * Added `handle_show_event()` and `handle_close_event()` methods to `BaseSyncPlot` for proper timer lifecycle management
  * Refactored `showEvent()` and `closeEvent()` in both `SyncPlotWindow` and `SyncPlotDialog` to eliminate code duplication
  * Added early exit check in `rescale_plots()` to prevent execution if the timer has been stopped
  * This fix ensures clean widget shutdown and prevents Qt from attempting to access deleted C++ objects
* Cross-section panels: Fixed autoscaling logic in `BaseCrossSectionPlot`
  * Streamlined handling of `autoscale_mode` and `lockscales` options for consistent scaling behavior across all code paths
  * The `update_plot()` method now delegates all scaling logic to `plot_axis_changed()` to avoid code duplication and ensure consistency
  * Fixed issue where Y cross-section plots for rectangular images with non-uniform axes (e.g., Y = f(X)) were not properly scaled on initial display
  * The lockscales mode now correctly syncs the cross-section axis (CS_AXIS) to the image plot while autoscaling the intensity axis (Z_AXIS)
* [Issue #49](https://github.com/PlotPyStack/PlotPy/issues/49) - Fixed multiple coordinate handling bugs in `XYImageItem`:
  * **Root cause**: `XYImageItem` internally stores bin edges (length n+1) but several methods were incorrectly treating them as pixel centers (length n)
  * Fixed `get_x_values()` and `get_y_values()` to correctly compute and return pixel centers from stored bin edges: `(edge[i] + edge[i+1]) / 2`
  * Fixed `get_pixel_coordinates()` to correctly convert plot coordinates to pixel indices using `searchsorted()` with proper edge-to-index adjustment
  * Fixed `get_plot_coordinates()` to return pixel center coordinates instead of bin edge coordinates
  * Fixed `get_closest_coordinates()` to return pixel center coordinates instead of bin edge coordinates
  * Added comprehensive docstring documentation explaining that `XYImageItem.x` and `XYImageItem.y` store bin edges, not pixel centers
  * Removed redundant pixel centering code in `CrossSectionItem.update_curve_data()` that was working around these bugs
  * This fixes the reported issue where using cross-section tools progressively translated image data to the bottom-right corner
  * All coordinate-related methods now properly handle the bin edge vs pixel center distinction throughout the `XYImageItem` API
* Fixed index bounds calculation for image slicing compatibility:
  * Corrected the calculation of maximum indices in `get_plot_coordinates` to ensure proper bounds when using NumPy array slicing
  * Previously, the maximum indices were off by one, which could cause issues when extracting image data using the returned coordinates
  * Now returns indices that correctly align with Python/NumPy slicing conventions (e.g., `[i1:i2+1, j1:j2+1]`)
  * This fixes an historic bug that could lead to off-by-one errors when users extracted image data using the coordinates provided by this function
* Fixed plot update after inserting a point using the `EditPointTool` on non-Windows platforms
* [Issue #46](https://github.com/PlotPyStack/PlotPy/issues/46) - Contrast adjustment with 'Eliminate outliers' failed for float images with high dynamic range
* [Issue #29](https://github.com/PlotPyStack/PlotPy/issues/29) - SelectTool: Selecting Another Shape Without Unselection
  * Fixed direct selection between different shapes without requiring intermediate click on empty space
  * Users can now click directly from one shape to another for immediate selection
  * Maintains all existing functionality including multi-selection (Ctrl+click), moving, and resizing
* Fixed `ErrorBarCurveItem` handling of all-NaN data:
  * Fixed `ValueError: zero-size array to reduction operation minimum which has no identity` when error bar curves contain only NaN values
  * Added proper checks in `boundingRect()` and `draw()` methods to handle empty arrays gracefully
  * Error bar curves with all-NaN data now fall back to parent class behavior instead of crashing
* Item list: refresh tree when item parameters are changed:
  * Added `SIG_ITEM_PARAMETERS_CHANGED` signal to `BasePlot` class
  * This signal is emitted when the parameters of an item are changed using the parameters dialog, or a specific tool (e.g. the colormap selection tool, or the lock/unlock tool for image items)
  * The signal is emitted with the item as argument
  * The `ItemListWidget` now listens to this signal and refreshes the item list accordingly
* Edit tools (Edit data, center image position):
  * Exclude read-only items from the list of editable items
  * It is no longer possible to use those tools on read-only items
* Marker items (markers, cursors):
  * Setting item movable state now also sets the resizable state:
    * The PlotPy event system won't prevent the user from moving the item by dragging the handles if the item is just not movable: it has to be not resizable, which is not intuitive.
    * This is now fixed
* Range selection items (`XRangeSelection`, `YRangeSelection`):
  * Handles are now displayed only when the item is resizable
  * If the item is set as not resizable (using the `set_resizable` method), the handles will be hidden
* Fixed cursor label formatting error with percentage symbols:
  * Fixed `ValueError: unsupported format character '=' (0x3d)` when cursor labels contain percentage signs followed by format specifiers (e.g., "Crossing at 20.0% = %g")
  * The issue occurred because old-style string formatting (`label % value`) treated the `%` in percentage displays as format specifiers
  * Added robust fallback mechanism that tests label format once during cursor creation and uses regex-based replacement when needed
  * Performance optimized: format validation is done once at cursor creation time, not on every callback execution
  * Affects `vcursor`, `hcursor`, and `xcursor` methods in `CurveMarkerBuilder`

Other changes:

* API breakage: renamed annotations `AnnotatedShape.get_infos` method to `get_info`
* Updated dependencies following the latest security advisories (NumPy >= 1.22)
* Added `pre-commit` hook to run `ruff` (both `ruff check` and `ruff format`) on commit
* Added missing `build` optional dependency to development dependencies in `pyproject.toml`
* Visual Studio Code tasks:
  * Major overhaul (cleanup and simplification)
  * Removal of no longer used batch files
