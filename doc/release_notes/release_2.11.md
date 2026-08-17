# Version 2.11 #

## PlotPy Version 2.11.0 ##

✨ New features:
* **Enhance contour builder with style parameters** — Add color, linestyle and linewidth parameters to ContourLine item class

🛠️ Bug fixes:

* **Image cross sections** — Restored live cross-section updates when using `Alt+Mousemove` over an image. This regression had been introduced in v2.1.0: the X/Y cross-section panels no longer received marker-change updates because method resolution order was shadowing the mixin hook that connects `SIG_MARKER_CHANGED` (closes [Issue #68](https://github.com/PlotPyStack/PlotPy/issues/68))

* **Empty Label ledend box crash prevent** — When plot items list is empty, LegendBoxItem could crashes while clicking on it. Fix and tests added
