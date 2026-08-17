# Version 2.10 #

## PlotPy Version 2.10.0 ##

✨ New features:

* **Per-axis autoscale strategy**: Added configurable autoscale behavior for each axis via the axis parameters dialog. Three strategies are available: *Auto* (default — compute bounds from items), *Fixed range* (apply user-defined Min/Max values) and *Disabled* (leave the axis untouched on autoscale). New API: `BasePlot.set_axis_autoscale_strategy()` / `BasePlot.get_axis_autoscale_strategy()` (closes [Issue #63](https://github.com/PlotPyStack/PlotPy/issues/63), partial)
* **Symbol border width**: Added an `edgewidth` parameter to `SymbolParam` for customizable marker border thickness — previously the border was always 1 pixel wide

🛠️ Bug fixes:

* **Rectangular snapshot tool** — Fixed the "Original size" computation (closes [Issue #57](https://github.com/PlotPyStack/PlotPy/issues/57)):
  * The preview no longer displays negative dimensions when the X or Y axis is
    reversed
  * The "Original size" is now computed from pixel coordinates instead of axis
    units, so it is correct for `XYImageItem` (and any item with non-uniform
    axis scaling) regardless of axis orientation
  * The `ValueError` raised by the resize dialog when the selection produced
    negative dimensions on a reversed axis is gone
  * Selecting a region larger than the plotted image now reports the same
    native pixel resolution for both `ImageItem` and `XYImageItem`
    (previously `XYImageItem` reported ``shape - 1`` while `ImageItem`
    reported the full oversized resolution): exporting at "Original size"
    now consistently preserves the source pixel density and avoids
    upsampling, regardless of the item type
* **Snapshot tool cursor** — Fixed the mouse cursor remaining stuck as a cross (`+`) outside the plot canvas (axes, toolbar) after using the snapshot tool. The modal dialogs are now opened after Qt has released the implicit pointer grab, so the cursor is correctly restored (closes [Issue #58](https://github.com/PlotPyStack/PlotPy/issues/58))
* **Z-axis log tool** — Fixed the `ZAxisLogTool` being always disabled for non-`ImageItem` image types (`XYImageItem`, `MaskedImageItem`, `MaskedXYImageItem`, `TrImageItem`, `RGBImageItem`). The Z-axis log API (`get_zaxis_log_state` / `set_zaxis_log_state`) was moved from `ImageItem` up to `BaseImageItem` so all image item types support it. This notably fixes the tool being permanently greyed out in DataLab's image panel (closes [Issue #59](https://github.com/PlotPyStack/PlotPy/issues/59))
* **Z-axis log data update** — Fixed image data not being recomputed when calling `set_data()` while Z-axis log scale is active — the log-transformed data is now refreshed and the LUT range preserved in log mode
* **`YRangeCursorTool`** — Fixed incorrect inequality display and negative ∆y when the Y-range cursors are inverted (dragging the top cursor below the bottom one). Values are now sorted and ∆y is always positive (closes [Issue #55](https://github.com/PlotPyStack/PlotPy/issues/55))
* **`CurveStatsTool`** — Replaced `min`/`max`/`mean`/`std`/`sum` with their NaN-safe equivalents (`nanmin`, `nanmax`, `nanmean`, `nanstd`, `nansum`) so that signal statistics are computed correctly when the data contains NaN values

⚙️ Dependencies:

* Bumped minimum PythonQwt version from 0.15 to **0.16** to benefit from the Qt6 performance optimizations (closes [Issue #22](https://github.com/PlotPyStack/PlotPy/issues/22) — see [PythonQwt#93](https://github.com/PlotPyStack/PythonQwt/issues/93) for the full optimization log)