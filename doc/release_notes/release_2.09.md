# Version 2.9 #

## PlotPy Version 2.9.0 ##

💥 New features:

* Added `QuiverItem` for displaying 2D vector fields (quiver plots), similar to
  Matplotlib's `quiver`. This closes
  [Issue #54](https://github.com/PlotPyStack/PlotPy/issues/54):
  * New `QuiverItem` plot item class supporting X, Y, U, V arrays (1D or 2D)
  * Auto-meshgrid expansion when X, Y are 1D and U, V are 2D
  * Configurable arrow scale, head size, and color
  * New `make.quiver()` builder method for easy item creation
  * New `quiver()` function in the interactive plotting interface (`plotpy.pyplot`)
  * Integrated with plot autoscale (initial zoom and middle-click reset)
  * Item icon displayed in the item list widget
* Added "Invert colormap" checkbox directly in the Colormap Manager dialog. This
  closes [Issue #53](https://github.com/PlotPyStack/PlotPy/issues/53):
  * Reflects the current inversion state when the dialog is opened
  * Allows toggling inversion from the colormap selection widget
  * Updates the colormap preview in real-time when toggled
  * Inversion is treated as a display parameter, independent of the colormap
    definition (toggling does not mark the colormap as having unsaved changes)

🛠️ Bug fixes:

* Fixed marker style parameters being overwritten when updating selected markers:
  * `MarkerParam.update_param` now correctly reads back the selected or unselected
    visual state into the matching parameter set, instead of overwriting the base
    (normal) style with the selected style
  * This preserves distinct normal and selected appearance for markers
* Fixed error-bar curve cursor snapping: clicking near an error-bar bound on an
  `ErrorBarCurveItem` now correctly returns the closest bar end coordinate.
  Previously a typo (`abs(y - y)` / `abs(x - x)` instead of `abs(y - yi)` /
  `abs(x - xi)`) made the snap-to-bound branches dead code, so the closest
  coordinate was always the central curve point regardless of cursor position
* Fixed image export via `Figure.print_` (`plotpy.pyplot`) leaking the underlying
  `QPainter`: the painter is now always released, even when an axis fails to
  render. This avoids "QPainter::begin: A paint device can only be painted by
  one painter at a time" warnings, GDI/GL resource leaks, and truncated output
  files on subsequent paints
* Fixed `vector_projection` raising a division-by-zero warning and returning NaN
  coordinates when the two reference points A and B coincided. The function now
  detects the degenerate zero-length AB vector and returns point B
* Fixed `scale_data_to_dtype` (`plotpy.io`) producing NaN values when the input
  array was constant (`dmax == dmin`). The function now returns a finite
  constant array set to the target dtype's minimum value instead of dividing by
  zero
* Fixed `get_nan_min` / `get_nan_max` (`plotpy.mathutils.arrayfuncs`) raising
  `ValueError` on empty arrays and emitting `RuntimeWarning` on all-NaN inputs.
  Both helpers now return NaN for empty or fully-NaN arrays without warnings

🔧 Other changes:

* CI: gate PyPI deployment on test suite passing
* Development environment: improved `scripts/run_with_env.py` to support multiple
  Python environment contexts (WinPython, venv, etc.) with legacy support for the
  `WINPYDIRBASE` environment variable
