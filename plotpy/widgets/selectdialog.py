# -*- coding: utf-8

"""
Select dialog
-------------

The `selectdialog` module provides a dialog box to select an area of the plot
using a tool:

    * :py:class:`.widgets.selectdialog.SelectDialog`: dialog box
    * :py:func:`.widgets.selectdialog.select_with_shape_tool`: function to
     select an area with a shape tool and return the rectangle
    * :py:func:`.widgets.selectdialog.set_items_unselectable`: function to set
     items unselectable except for the given item

Example: get segment
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/tools/test_get_segment.py

Example: get rectangle
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/tools/test_get_rectangle.py

Example: get rectangle with SVG
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/tools/test_get_rectangle_with_svg.py

Reference
~~~~~~~~~

.. autoclass:: SelectDialog
   :members:
.. autofunction:: select_with_shape_tool
.. autofunction:: set_items_unselectable
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from guidata.configtools import get_icon
from guidata.qthelpers import exec_dialog
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QWidget  # only to help intersphinx find QWidget
from qwt.plot import QwtPlotItem

from plotpy.items import AbstractShape, ImageItem
from plotpy.panels.base import PanelWidget
from plotpy.plot import BasePlot, PlotDialog, PlotOptions
from plotpy.tools import RectangularShapeTool, SelectTool

if TYPE_CHECKING:
    from plotpy.panels.base import PanelWidget


class SelectDialog(PlotDialog):
    """Plot dialog box to select an area of the plot using a tool

    Args:
        parent: parent widget
        toolbar: show/hide toolbar
        options: plot options
        panels: additionnal panels
        auto_tools: If True, the plot tools are automatically registered.
         If False, the user must register the tools manually.
        title: The window title
        icon: The window icon
        edit: If True, the plot is editable
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        options: PlotOptions | None = None,
        panels: list[PanelWidget] | None = None,
        auto_tools: bool = True,
        title: str = "PlotPy",
        icon: str = "plotpy.svg",
        edit: bool = False,
    ) -> None:
        super().__init__(
            parent, toolbar, options, panels, auto_tools, title, icon, edit
        )
        self.sel_tool: RectangularShapeTool | None = None

    def set_image_and_tool(
        self, item: ImageItem, toolclass: RectangularShapeTool, **kwargs
    ) -> None:
        """Set the image item to be displayed and the tool to be used

        Args:
            item: Image item
            toolclass: Tool class
            kwargs: Keyword arguments for the tool class
        """
        default = self.manager.add_tool(SelectTool)
        self.manager.set_default_tool(default)
        self.sel_tool: RectangularShapeTool = self.manager.add_tool(
            toolclass,
            switch_to_default_tool=True,
            **kwargs,
        )  # pylint: disable=attribute-defined-outside-init
        self.sel_tool.activate()
        set_ok_btn_enabled = self.button_box.button(QW.QDialogButtonBox.Ok).setEnabled
        set_ok_btn_enabled(False)
        self.sel_tool.SIG_TOOL_JOB_FINISHED.connect(lambda: set_ok_btn_enabled(True))
        plot = self.get_plot()
        plot.add_item(item)
        plot.set_active_item(item)
        item.set_selectable(False)
        item.set_readonly(True)
        plot.unselect_item(item)

    def get_new_shape(self) -> AbstractShape:
        """Get newly created shape

        Returns:
            Newly created shape
        """
        return self.sel_tool.get_last_final_shape()


def set_items_unselectable(plot: BasePlot, except_item: QwtPlotItem = None) -> None:
    """Set items unselectable except for the given item"""
    for item_i in plot.get_items():
        if except_item is None:
            item_i.set_selectable(False)
        else:
            item_i.set_selectable(item_i is except_item)


def select_with_shape_tool(
    parent: QW.QWidget,
    toolclass: RectangularShapeTool,
    item: ImageItem,
    title: str = None,
    size: tuple[int, int] = None,
    other_items: list[QwtPlotItem] = [],
    tooldialogclass: SelectDialog = SelectDialog,
    toolbar: bool = False,
    options: PlotOptions | None = None,
    icon=None,
    **kwargs,
) -> AbstractShape:
    """Select an area with a shape tool and return the rectangle

    Args:
        parent: Parent widget
        toolclass: Tool class
        item: Image item
        title: Dialog title
        size: Dialog size
        other_items: Other items to be displayed
        tooldialogclass: Tool dialog class
        toolbar: show/hide toolbar
        options: plot options
        icon: Icon
        kwargs: Keyword arguments for the tool class

    Returns:
        Selected shape
    """
    if title is None:
        title = "Select an area then press OK to accept"
    if icon is not None:
        icon = get_icon(icon) if isinstance(icon, str) else icon
    win: SelectDialog = tooldialogclass(
        parent, title=title, edit=True, toolbar=toolbar, options=options, icon=icon
    )
    win.set_image_and_tool(item, toolclass, **kwargs)
    plot = win.get_plot()
    for other_item in other_items:
        plot.add_item(other_item)
    set_items_unselectable(plot)
    if size is not None:
        win.resize(*size)
    win.show()
    if exec_dialog(win):
        return win.get_new_shape()
    return None
