# Version 2.11 #

## PlotPy Version 2.11.2 ##

🛠️ Bug fixes:

* **Curve fitting dialog** — Running the automatic fit no longer raises `OverflowError: argument 1 overflowed` errors when a fitted value ends up far outside the range of its slider (e.g. with the Powell method on a fit range restricted to the tail of a peak). These errors left the slider of the parameter unresponsive, and the values of the following parameters were not displayed. Such values are now shown with a warning icon, whose tooltip gives the slider range, while the slider stays at its nearest end. Typing `nan` or `inf` in a parameter field now restores the previous value instead of raising errors, and the number of slider steps must be at least 2 in the parameter properties dialog (closes [Issue #76](https://github.com/PlotPyStack/PlotPy/issues/76))

## PlotPy Version 2.11.1 ##

🛠️ Bug fixes:

* **`hist_range_threshold` documentation** — Fixed the docstring of `plotpy.lutrange.hist_range_threshold`, which stated that `percent` was the share of the histogram mass to *retain*, whereas it is the share to *eliminate* (half on each side). The error message raised for an out-of-range `percent` now matches the accepted range `[0, 100]`

📚 Documentation:

* **Migrating from guiqwt** — Updated the migration guide to match the current API:
  * Fixed outdated targets (`BasePlotWidget`, `BasePlot`) and the contour demo script path
  * Updated the `BasePlot` constructor section: all configuration settings now go through `BasePlotOptions`
  * Added equivalents for `canvas2plotitem`/`plotitem2canvas` (`plotpy.coords`), `mimedata2url` (`guidata.qthelpers`), `guiqwt.transitional` (`qwt` package) and guidance for `eliminate_outliers` and `guiqwt.signals`
  * Completed the compatibility table with missing guiqwt modules and classes (`builder`, `panels`, `config`, `ImagePlot`, `ImageWidget`, `ImageDialog`, `ImageWindow`, ...)

## PlotPy Version 2.11.0 ##

✨ New features:
* **Enhance contour builder with style parameters** — Add color, linestyle and linewidth parameters to ContourLine item class

🛠️ Bug fixes:

* **Image cross sections** — Restored live cross-section updates when using `Alt+Mousemove` over an image. This regression had been introduced in v2.1.0: the X/Y cross-section panels no longer received marker-change updates because method resolution order was shadowing the mixin hook that connects `SIG_MARKER_CHANGED` (closes [Issue #68](https://github.com/PlotPyStack/PlotPy/issues/68))

* **Empty Label ledend box crash prevent** — When plot items list is empty, LegendBoxItem could crashes while clicking on it. Fix and tests added
