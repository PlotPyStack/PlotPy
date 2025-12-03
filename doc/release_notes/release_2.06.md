# Version 2.6 #

## PlotPy Version 2.6.3 (2024-10-01) ##

🧯 In this release, test coverage is 79%.

🛠️ Bug fixes:

* [Issue #25](https://github.com/PlotPyStack/PlotPy/issues/25) - `OverflowError` with Contrast Adjustment panel for constant images
* When updating image parameters (`ImageParam`) from the associated item object:
  * If `xmin`, `xmax`, `ymin`, `ymax` attributes are not yet set (i.e. `None`), do not update them with the image data bounds
  * Previous behavior was to update them with the image data bounds, which was leading to breaking the automatic bounds update when the image data is updated
* [Issue #24](https://github.com/PlotPyStack/PlotPy/issues/24) - Colormap: side effect on image axes when changing the colormap
* [Issue #23](https://github.com/PlotPyStack/PlotPy/issues/23) - Windows: Image `_scaler` engine performance regression
* PySide6 compatibility issues:
  * Fixed deprecated call to `QMouseEvent` in `tests/unit/utils.py`
  * Added workaround for `QPolygonF` shape point slicing
* [Issue #21](https://github.com/PlotPyStack/PlotPy/issues/21) - PySide6 on Linux: segfault in test_colormap_editor.py
* Fixed `sliderMoved` signal connection in `ColorMapEditor`
* Fixed `AssertionError` in test_rect_zoom.py (Linux, Python 3.12, PyQt6)
* Fixed typing issues in `plotpy.events` module:
  * Event objects were not properly typed (`QtCore.QEvent` instead of `QtGui.QMouseEvent`)
  * Event position arguments were not properly typed (`QtCore.QPoint` instead of `QtCore.QPointF`)
* Fix NumPy `FutureWarning: Format strings passed to MaskedConstant are ignored [...]` when displaying masked pixel coordinates

## PlotPy Version 2.6.2 (2024-08-06) ##

💥 New features / Enhancements:

* Added Wheel packages for all major platforms on PyPI:
  * Windows (32/64bits), MacOS, Linux
  * Python 3.8 to 3.12

🛠️ Bug fixes:

* Fixed color theme support (dark/light mode), leveraging the new `guidata` V3.6 feature

## PlotPy Version 2.6.1 (2024-08-02) ##

ℹ️ Release V2.6.0 was a fugitive release that was replaced by V2.6.1 due to a critical bug in the segment line cross section computation for masked images.

💥 New features / Enhancements:

* Added support for color theme change at execution (relies on guidata V3.6)
* Changed strategy for default plot widget size:
  * No default size is applied to the plot widget anymore (before, the default size was 800x600 pixels)
  * Added parameter `size` to `PlotDialog`, `PlotWindow` classes, and `make.dialog`, `make.window` functions to set the initial size of the plot widget

🛠️ Bug fixes:

* Fixed segment line cross section computation for masked images:
  * Avoided warning message when encountering masked values in the image data
  * Replacing masked values by NaNs when computing the segment line cross section (as before, but explicitely, to avoid the warning message)
