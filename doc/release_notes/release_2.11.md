# Version 2.11 #

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
