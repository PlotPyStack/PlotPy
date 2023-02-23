# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

"""
plotpy.widgets.tools
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

.. literalinclude:: ../../../tests/gui/image_plot_tools.py
   :start-after: SHOW


.. image:: /images/screenshots/image_plot_tools.png


Reference
~~~~~~~~~
.. autoclass:: InteractiveTool
   :members:
.. autoclass:: RectZoomTool
   :members:
   :inherited-members:
.. autoclass:: SelectTool
   :members:
   :inherited-members:
.. autoclass:: SelectPointTool
   :members:
   :inherited-members:
.. autoclass:: RotationCenterTool
   :members:
   :inherited-members:
.. autoclass:: MultiLineTool
   :members:
   :inherited-members:
.. autoclass:: FreeFormTool
   :members:
   :inherited-members:
.. autoclass:: LabelTool
   :members:
   :inherited-members:
.. autoclass:: RectangleTool
   :members:
   :inherited-members:
.. autoclass:: PointTool
   :members:
   :inherited-members:
.. autoclass:: SegmentTool
   :members:
   :inherited-members:
.. autoclass:: CircleTool
   :members:
   :inherited-members:
.. autoclass:: EllipseTool
   :members:
   :inherited-members:
.. autoclass:: PlaceAxesTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedRectangleTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedCircleTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedEllipseTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedPointTool
   :members:
   :inherited-members:
.. autoclass:: AnnotatedSegmentTool
   :members:
   :inherited-members:
.. autoclass:: HRangeTool
   :members:
   :inherited-members:
.. autoclass:: DummySeparatorTool
   :members:
   :inherited-members:
.. autoclass:: AntiAliasingTool
   :members:
   :inherited-members:
.. autoclass:: DisplayCoordsTool
   :members:
   :inherited-members:
.. autoclass:: ReverseYAxisTool
   :members:
   :inherited-members:
.. autoclass:: AspectRatioTool
   :members:
   :inherited-members:
.. autoclass:: PanelTool
   :members:
   :inherited-members:
.. autoclass:: ItemListPanelTool
   :members:
   :inherited-members:
.. autoclass:: ContrastPanelTool
   :members:
   :inherited-members:
.. autoclass:: ColormapTool
   :members:
   :inherited-members:
.. autoclass:: XCSPanelTool
   :members:
   :inherited-members:
.. autoclass:: YCSPanelTool
   :members:
   :inherited-members:
.. autoclass:: CrossSectionTool
   :members:
   :inherited-members:
.. autoclass:: AverageCrossSectionTool
   :members:
   :inherited-members:
.. autoclass:: SaveAsTool
   :members:
   :inherited-members:
.. autoclass:: CopyToClipboardTool
   :members:
   :inherited-members:
.. autoclass:: OpenFileTool
   :members:
   :inherited-members:
.. autoclass:: OpenImageTool
   :members:
   :inherited-members:
.. autoclass:: SnapshotTool
   :members:
   :inherited-members:
.. autoclass:: PrintTool
   :members:
   :inherited-members:
.. autoclass:: SaveItemsTool
   :members:
   :inherited-members:
.. autoclass:: LoadItemsTool
   :members:
   :inherited-members:
.. autoclass:: AxisScaleTool
   :members:
   :inherited-members:
.. autoclass:: HelpTool
   :members:
   :inherited-members:
.. autoclass:: ExportItemDataTool
   :members:
   :inherited-members:
.. autoclass:: EditItemDataTool
   :members:
   :inherited-members:
.. autoclass:: ItemCenterTool
   :members:
   :inherited-members:
.. autoclass:: DeleteItemTool
   :members:
   :inherited-members:
.. autoclass:: ImageMaskTool
   :members:
   :inherited-members:
"""
