# -*- coding: utf-8 -*-

"""
plotpy.core.tools
------------------------

The `tools` module provides a collection of `plot tools` :
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

A `plot tool` is an object providing various features to a plotting widget
(:py:class:`.baseplot.BasePlot`):
buttons, menus, selection tools, image I/O tools, etc.
To make it work, a tool has to be registered to the plotting widget's manager,
i.e. an instance of the :py:class:`.plot.PlotManager` class (see
the :py:mod:`.plot` module for more details on the procedure).

The `BasePlot` widget do not provide any `PlotManager`: the
manager has to be created separately. On the contrary, the ready-to-use widget
:py:class:`.plot.PlotWidget` are higher-level plotting widgets with integrated manager,
tools and panels.

.. seealso::

    Module :py:mod:`.plot`
        Module providing ready-to-use curve and image plotting widgets and
        dialog boxes

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

Example
~~~~~~~

The following example add all the existing image tools to an `PlotWidget` object
for testing purpose:

.. literalinclude:: ../../plotpy/tests/gui/test_image_plot_tools.py
   :start-after: guitest:


.. image:: /images/screenshots/image_plot_tools.png


Reference
~~~~~~~~~
.. autoclass:: RectZoomTool
   :members:
.. autoclass:: SelectTool
   :members:
.. autoclass:: SelectPointTool
   :members:
.. autoclass:: RotationCenterTool
   :members:
.. autoclass:: MultiLineTool
   :members:
.. autoclass:: FreeFormTool
   :members:
.. autoclass:: LabelTool
   :members:
.. autoclass:: RectangleTool
   :members:
.. autoclass:: PointTool
   :members:
.. autoclass:: SegmentTool
   :members:
.. autoclass:: CircleTool
   :members:
.. autoclass:: EllipseTool
   :members:
.. autoclass:: PlaceAxesTool
   :members:
.. autoclass:: AnnotatedRectangleTool
   :members:
.. autoclass:: AnnotatedCircleTool
   :members:
.. autoclass:: AnnotatedEllipseTool
   :members:
.. autoclass:: AnnotatedPointTool
   :members:
.. autoclass:: AnnotatedSegmentTool
   :members:
.. autoclass:: HRangeTool
   :members:
.. autoclass:: DummySeparatorTool
   :members:
.. autoclass:: AntiAliasingTool
   :members:
.. autoclass:: DisplayCoordsTool
   :members:
.. autoclass:: ReverseYAxisTool
   :members:
.. autoclass:: AspectRatioTool
   :members:
.. autoclass:: PanelTool
   :members:
.. autoclass:: ItemListPanelTool
   :members:
.. autoclass:: ContrastPanelTool
   :members:
.. autoclass:: ColormapTool
   :members:
.. autoclass:: XCSPanelTool
   :members:
.. autoclass:: YCSPanelTool
   :members:
.. autoclass:: CrossSectionTool
   :members:
.. autoclass:: AverageCrossSectionTool
   :members:
.. autoclass:: SaveAsTool
   :members:
.. autoclass:: CopyToClipboardTool
   :members:
.. autoclass:: OpenFileTool
   :members:
.. autoclass:: OpenImageTool
   :members:
.. autoclass:: SnapshotTool
   :members:
.. autoclass:: PrintTool
   :members:
.. autoclass:: SaveItemsTool
   :members:
.. autoclass:: LoadItemsTool
   :members:
.. autoclass:: AxisScaleTool
   :members:
.. autoclass:: HelpTool
   :members:
.. autoclass:: ExportItemDataTool
   :members:
.. autoclass:: EditItemDataTool
   :members:
.. autoclass:: ItemCenterTool
   :members:
.. autoclass:: DeleteItemTool
   :members:
.. autoclass:: ImageMaskTool
   :members:
"""

# Import all tools classes (name ending with "Tool") from children modules:
from .annotations import (
    AnnotatedCircleTool,
    AnnotatedEllipseTool,
    AnnotatedObliqueRectangleTool,
    AnnotatedPointTool,
    AnnotatedRectangleTool,
    AnnotatedSegmentTool,
)
from .axes import AxisScaleTool, PlaceAxesTool
from .base import PanelTool
from .cross_section import (
    AverageCrossSectionTool,
    CrossSectionTool,
    ObliqueCrossSectionTool,
    XCSPanelTool,
    YCSPanelTool,
)
from .cursor import HCursorTool, HRangeTool, VCursorTool, XCursorTool
from .curve import AntiAliasingTool, CurveStatsTool, SelectPointTool
from .image import (
    AspectRatioTool,
    ColormapTool,
    ContrastPanelTool,
    ImageMaskTool,
    ImageStatsTool,
    OpenImageTool,
    ReverseYAxisTool,
    RotateCropTool,
    RotationCenterTool,
)
from .item import (
    DeleteItemTool,
    EditItemDataTool,
    ExportItemDataTool,
    ItemCenterTool,
    ItemListPanelTool,
    LoadItemsTool,
    SaveItemsTool,
)
from .label import LabelTool
from .misc import (
    AboutTool,
    CopyToClipboardTool,
    FilterTool,
    HelpTool,
    OpenFileTool,
    PrintTool,
    SaveAsTool,
    SnapshotTool,
)
from .plot import DisplayCoordsTool, DummySeparatorTool, RectZoomTool
from .selection import SelectTool
from .shapes import (
    CircleTool,
    EllipseTool,
    FreeFormTool,
    MultiLineTool,
    ObliqueRectangleTool,
    PointTool,
    RectangleTool,
    SegmentTool,
)
