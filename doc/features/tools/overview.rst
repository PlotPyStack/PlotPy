Overview
--------

A `plot tool` is an object providing various features to a plotting widget
(:py:class:`.BasePlot`):

* Buttons,
* Menus,
* Selection tools,
* Image I/O tools,
* Etc.

Before being used, a tool has to be registered to a plotting widget's manager,
i.e. an instance of the :py:class:`.PlotManager` class (see :ref:`plot`
for more details).

The :py:class:`.BasePlot` widget do not provide any :py:class:`.PlotManager`:
the manager has to be created separately. On the contrary, the ready-to-use widget
:py:class:`.PlotWidget` are higher-level plotting widgets with
integrated manager, tools and panels.

.. seealso::

    :ref:`plot`
        Ready-to-use curve and image plotting widgets and dialog boxes

    :ref:`items`
        Plot items: curves, images, markers, etc.


The `tools` module provides the following tools:

* :py:class:`.tools.RectZoomTool`
* :py:class:`.tools.SelectTool`
* :py:class:`.tools.SelectPointTool`
* :py:class:`.tools.RotationCenterTool`
* :py:class:`.tools.MultiLineTool`
* :py:class:`.tools.FreeFormTool`
* :py:class:`.tools.LabelTool`
* :py:class:`.tools.RectangleTool`
* :py:class:`.tools.PointTool`
* :py:class:`.tools.SegmentTool`
* :py:class:`.tools.CircleTool`
* :py:class:`.tools.EllipseTool`
* :py:class:`.tools.PlaceAxesTool`
* :py:class:`.tools.AnnotatedRectangleTool`
* :py:class:`.tools.AnnotatedCircleTool`
* :py:class:`.tools.AnnotatedEllipseTool`
* :py:class:`.tools.AnnotatedPointTool`
* :py:class:`.tools.AnnotatedSegmentTool`
* :py:class:`.tools.HRangeTool`
* :py:class:`.tools.DummySeparatorTool`
* :py:class:`.tools.AntiAliasingTool`
* :py:class:`.tools.DisplayCoordsTool`
* :py:class:`.tools.ReverseYAxisTool`
* :py:class:`.tools.AspectRatioTool`
* :py:class:`.tools.PanelTool`
* :py:class:`.tools.ItemListPanelTool`
* :py:class:`.tools.ContrastPanelTool`
* :py:class:`.tools.ColormapTool`
* :py:class:`.tools.XCSPanelTool`
* :py:class:`.tools.YCSPanelTool`
* :py:class:`.tools.CrossSectionTool`
* :py:class:`.tools.AverageCrossSectionTool`
* :py:class:`.tools.SaveAsTool`
* :py:class:`.tools.CopyToClipboardTool`
* :py:class:`.tools.OpenFileTool`
* :py:class:`.tools.OpenImageTool`
* :py:class:`.tools.SnapshotTool`
* :py:class:`.tools.PrintTool`
* :py:class:`.tools.SaveItemsTool`
* :py:class:`.tools.LoadItemsTool`
* :py:class:`.tools.AxisScaleTool`
* :py:class:`.tools.HelpTool`
* :py:class:`.tools.ExportItemDataTool`
* :py:class:`.tools.EditItemDataTool`
* :py:class:`.tools.ItemCenterTool`
* :py:class:`.tools.DeleteItemTool`
