# Version 2.2 #

## PlotPy Version 2.2.0 (2024-03-04) ##

In this release, test coverage is 75%.

New features:

* Added `SIG_ITEM_PARAMETERS_CHANGED` signal to `BasePlot` class:
  * This signal is emitted when the parameters of an item are changed using the parameters dialog, or a specific tool (e.g. the colormap selection tool, or the lock/unlock tool for image items)
  * This signal is emitted with the item as argument
  * It is often emitted before the `SIG_ITEMS_CHANGED` signal, which is global to all items, but not necessarily. For example, when the colormap of an image is changed, the `SIG_ITEM_PARAMETERS_CHANGED` signal is emitted for the image item, but the `SIG_ITEMS_CHANGED` signal is not emitted.
* Added new colormap presets:
  * `viridis`, `plasma`, `inferno`, `magma`, `cividis`
  * `afmhot`
  * `coolwarm`, `bwr`, `seismic`
  * `gnuplot2`, `CMRmap`, `rainbow`, `turbo`
* Fixed all qualitative colormaps:
  * All qualitative colormaps have been re-computed because they are not supposed to be interpolated, which was the case and made them unusable
  * The qualitative colormaps are now usable and look like the ones from Matplotlib
* Colormap manager:
  * Added a button to remove a custom colormap
  * The preset colormaps *and* the currently selected colormap are read-only
* Added automatic unit tests for interactive tools:
  * `AnnotatedCircleTool`, `AnnotatedEllipseTool`, `AnnotatedObliqueRectangleTool`, `AnnotatedPointTool`, `AnnotatedRectangleTool`, `AnnotatedSegmentTool`
  * `AverageCrossSectionTool`, `CrossSectionTool`, `ObliqueCrossSectionTool`, `LineCrossSectionTool`
  * `EditPointTool`, `SelectPointsTool`, `SelectPointTool`
  * `AspectRatioTool`, `ImageStatsTool`, `SnapshotTool`
  * `DisplayCoordsTool`, `RectZoomTool`
  * `CircleTool`, `EllipseTool`, `FreeFormTool`, `MultiLineTool`, `ObliqueRectangleTool`, `PointTool`, `RectangleTool`, `SegmentTool`
* Internal package reorganization: moved icons to `plotpy/data/icons` folder
