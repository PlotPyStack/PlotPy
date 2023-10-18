# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Widget/plot builder
-------------------

This module provides a set of factory functions to simplify the creation of
plot widgets and grid items.
"""

# Note: when adding method to builder classes, please do not forget to update the
# documentation (see builder.rst file). Because of class inheritance, the methods
# are not automatically documented (otherwise, they would be sorted alphabetically,
# due to a limitation of sphinx auto-doc).

from __future__ import annotations

from typing import TYPE_CHECKING

from plotpy.config import CONF, _
from plotpy.items import GridItem
from plotpy.plot import PlotDialog, PlotOptions, PlotWidget, PlotWindow
from plotpy.styles import COLORS, GridParam, LineStyleParam

if TYPE_CHECKING:  # pragma: no cover
    from qtpy.QtWidgets import QWidget

    from plotpy.constants import PlotType
    from plotpy.panels import PanelWidget


class WidgetBuilder:
    """Class regrouping a set of factory functions to simplify the creation
    of plot widgets and grid items."""

    # ---- Plot widgets ---------------------------------------------------------------
    def widget(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        panels: tuple[PanelWidget] | None = None,
        auto_tools: bool = True,
        title: str | None = None,
        xlabel: str | tuple[str, str] | None = None,
        ylabel: str | tuple[str, str] | None = None,
        zlabel: str | None = None,
        xunit: str | tuple[str, str] | None = None,
        yunit: str | tuple[str, str] | None = None,
        zunit: str | None = None,
        yreverse: bool | None = None,
        aspect_ratio: float = 1.0,
        lock_aspect_ratio: bool | None = None,
        curve_antialiasing: bool | None = None,
        gridparam: GridParam | None = None,
        section: str = "plot",
        type: str | PlotType = "auto",
        axes_synchronised: bool = False,
        force_colorbar_enabled: bool = False,
        no_image_analysis_widgets: bool = False,
        show_contrast: bool = False,
        show_itemlist: bool = False,
        show_xsection: bool = False,
        show_ysection: bool = False,
        xsection_pos: str = "top",
        ysection_pos: str = "right",
    ) -> PlotWidget:
        """Make a plot widget (:py:class:`.PlotWidget` object)

        Args:
            parent: Parent widget
            toolbar: Show/hide toolbar
            panels: Additionnal panels
            auto_tools: If True, the plot tools are automatically registered.
             If False, the user must register the tools manually.
            title: The plot title
            xlabel: (bottom axis title, top axis title) or bottom axis title only
            ylabel: (left axis title, right axis title) or left axis title only
            zlabel: The Z-axis label
            xunit: (bottom axis unit, top axis unit) or bottom axis unit only
            yunit: (left axis unit, right axis unit) or left axis unit only
            zunit: The Z-axis unit
            yreverse: If True, the Y-axis is reversed
            aspect_ratio: The plot aspect ratio
            lock_aspect_ratio: If True, the aspect ratio is locked
            curve_antialiasing: If True, the curve antialiasing is enabled
            gridparam: The grid parameters
            section: The plot configuration section name ("plot", by default)
            type: The plot type ("auto", "manual", "curve" or "image")
            axes_synchronised: If True, the axes are synchronised
            force_colorbar_enabled: If True, the colorbar is always enabled
            no_image_analysis_widgets: If True, the image analysis widgets are not added
            show_contrast: If True, the contrast adjustment panel is visible
            show_itemlist: If True, the itemlist panel is visible
            show_xsection: If True, the X-axis cross section panel is visible
            show_ysection: If True, the Y-axis cross section panel is visible
            xsection_pos: The X-axis cross section panel position ("top" or "bottom")
            ysection_pos: The Y-axis cross section panel position ("left" or "right")
        """
        options = PlotOptions(
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            zlabel=zlabel,
            xunit=xunit,
            yunit=yunit,
            zunit=zunit,
            yreverse=yreverse,
            aspect_ratio=aspect_ratio,
            lock_aspect_ratio=lock_aspect_ratio,
            curve_antialiasing=curve_antialiasing,
            gridparam=gridparam,
            section=section,
            type=type,
            axes_synchronised=axes_synchronised,
            force_colorbar_enabled=force_colorbar_enabled,
            no_image_analysis_widgets=no_image_analysis_widgets,
            show_contrast=show_contrast,
            show_itemlist=show_itemlist,
            show_xsection=show_xsection,
            show_ysection=show_ysection,
            xsection_pos=xsection_pos,
            ysection_pos=ysection_pos,
        )
        return PlotWidget(
            parent,
            toolbar=toolbar,
            options=options,
            panels=panels,
            auto_tools=auto_tools,
        )

    def dialog(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        panels: tuple[PanelWidget] | None = None,
        auto_tools: bool = True,
        wintitle: str = "PlotPy",
        icon: str = "plotpy.svg",
        edit: bool = False,
        title: str | None = None,
        xlabel: str | tuple[str, str] | None = None,
        ylabel: str | tuple[str, str] | None = None,
        zlabel: str | None = None,
        xunit: str | tuple[str, str] | None = None,
        yunit: str | tuple[str, str] | None = None,
        zunit: str | None = None,
        yreverse: bool | None = None,
        aspect_ratio: float = 1.0,
        lock_aspect_ratio: bool | None = None,
        curve_antialiasing: bool | None = None,
        gridparam: GridParam | None = None,
        section: str = "plot",
        type: str | PlotType = "auto",
        axes_synchronised: bool = False,
        force_colorbar_enabled: bool = False,
        no_image_analysis_widgets: bool = False,
        show_contrast: bool = False,
        show_itemlist: bool = False,
        show_xsection: bool = False,
        show_ysection: bool = False,
        xsection_pos: str = "top",
        ysection_pos: str = "right",
    ) -> PlotDialog:
        """Make a plot dialog (:py:class:`.PlotDialog` object)

        Args:
            parent: Parent widget
            toolbar: Show/hide toolbar
            panels: Additionnal panels
            auto_tools: If True, the plot tools are automatically registered.
             If False, the user must register the tools manually.
            wintitle: The window title
            icon: The window icon
            edit: If True, the plot is editable
            title: The plot title
            xlabel: (bottom axis title, top axis title) or bottom axis title only
            ylabel: (left axis title, right axis title) or left axis title only
            zlabel: The Z-axis label
            xunit: (bottom axis unit, top axis unit) or bottom axis unit only
            yunit: (left axis unit, right axis unit) or left axis unit only
            zunit: The Z-axis unit
            yreverse: If True, the Y-axis is reversed
            aspect_ratio: The plot aspect ratio
            lock_aspect_ratio: If True, the aspect ratio is locked
            curve_antialiasing: If True, the curve antialiasing is enabled
            gridparam: The grid parameters
            section: The plot configuration section name ("plot", by default)
            type: The plot type ("auto", "manual", "curve" or "image")
            axes_synchronised: If True, the axes are synchronised
            force_colorbar_enabled: If True, the colorbar is always enabled
            no_image_analysis_widgets: If True, the image analysis widgets are not added
            show_contrast: If True, the contrast adjustment panel is visible
            show_itemlist: If True, the itemlist panel is visible
            show_xsection: If True, the X-axis cross section panel is visible
            show_ysection: If True, the Y-axis cross section panel is visible
            xsection_pos: The X-axis cross section panel position ("top" or "bottom")
            ysection_pos: The Y-axis cross section panel position ("left" or "right")
        """
        options = PlotOptions(
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            zlabel=zlabel,
            xunit=xunit,
            yunit=yunit,
            zunit=zunit,
            yreverse=yreverse,
            aspect_ratio=aspect_ratio,
            lock_aspect_ratio=lock_aspect_ratio,
            curve_antialiasing=curve_antialiasing,
            gridparam=gridparam,
            section=section,
            type=type,
            axes_synchronised=axes_synchronised,
            force_colorbar_enabled=force_colorbar_enabled,
            no_image_analysis_widgets=no_image_analysis_widgets,
            show_contrast=show_contrast,
            show_itemlist=show_itemlist,
            show_xsection=show_xsection,
            show_ysection=show_ysection,
            xsection_pos=xsection_pos,
            ysection_pos=ysection_pos,
        )
        return PlotDialog(
            parent,
            toolbar=toolbar,
            options=options,
            panels=panels,
            auto_tools=auto_tools,
            title=wintitle,
            icon=icon,
            edit=edit,
        )

    def window(
        self,
        parent: QWidget | None = None,
        toolbar: bool = False,
        panels: tuple[PanelWidget] | None = None,
        auto_tools: bool = True,
        wintitle: str = "PlotPy",
        icon: str = "plotpy.svg",
        title: str | None = None,
        xlabel: str | tuple[str, str] | None = None,
        ylabel: str | tuple[str, str] | None = None,
        zlabel: str | None = None,
        xunit: str | tuple[str, str] | None = None,
        yunit: str | tuple[str, str] | None = None,
        zunit: str | None = None,
        yreverse: bool | None = None,
        aspect_ratio: float = 1.0,
        lock_aspect_ratio: bool | None = None,
        curve_antialiasing: bool | None = None,
        gridparam: GridParam | None = None,
        section: str = "plot",
        type: str | PlotType = "auto",
        axes_synchronised: bool = False,
        force_colorbar_enabled: bool = False,
        no_image_analysis_widgets: bool = False,
        show_contrast: bool = False,
        show_itemlist: bool = False,
        show_xsection: bool = False,
        show_ysection: bool = False,
        xsection_pos: str = "top",
        ysection_pos: str = "right",
    ) -> PlotWindow:
        """Make a plot window (:py:class:`.PlotWindow` object)

        Args:
            parent: Parent widget
            toolbar: Show/hide toolbar
            panels: Additionnal panels
            auto_tools: If True, the plot tools are automatically registered.
             If False, the user must register the tools manually.
            wintitle: The window title
            icon: The window icon
            title: The plot title
            xlabel: (bottom axis title, top axis title) or bottom axis title only
            ylabel: (left axis title, right axis title) or left axis title only
            zlabel: The Z-axis label
            xunit: (bottom axis unit, top axis unit) or bottom axis unit only
            yunit: (left axis unit, right axis unit) or left axis unit only
            zunit: The Z-axis unit
            yreverse: If True, the Y-axis is reversed
            aspect_ratio: The plot aspect ratio
            lock_aspect_ratio: If True, the aspect ratio is locked
            curve_antialiasing: If True, the curve antialiasing is enabled
            gridparam: The grid parameters
            section: The plot configuration section name ("plot", by default)
            type: The plot type ("auto", "manual", "curve" or "image")
            axes_synchronised: If True, the axes are synchronised
            force_colorbar_enabled: If True, the colorbar is always enabled
            no_image_analysis_widgets: If True, the image analysis widgets are not added
            show_contrast: If True, the contrast adjustment panel is visible
            show_itemlist: If True, the itemlist panel is visible
            show_xsection: If True, the X-axis cross section panel is visible
            show_ysection: If True, the Y-axis cross section panel is visible
            xsection_pos: The X-axis cross section panel position ("top" or "bottom")
            ysection_pos: The Y-axis cross section panel position ("left" or "right")
        """
        options = PlotOptions(
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            zlabel=zlabel,
            xunit=xunit,
            yunit=yunit,
            zunit=zunit,
            yreverse=yreverse,
            aspect_ratio=aspect_ratio,
            lock_aspect_ratio=lock_aspect_ratio,
            curve_antialiasing=curve_antialiasing,
            gridparam=gridparam,
            section=section,
            type=type,
            axes_synchronised=axes_synchronised,
            force_colorbar_enabled=force_colorbar_enabled,
            no_image_analysis_widgets=no_image_analysis_widgets,
            show_contrast=show_contrast,
            show_itemlist=show_itemlist,
            show_xsection=show_xsection,
            show_ysection=show_ysection,
            xsection_pos=xsection_pos,
            ysection_pos=ysection_pos,
        )
        return PlotWindow(
            parent,
            toolbar=toolbar,
            options=options,
            panels=panels,
            auto_tools=auto_tools,
            title=wintitle,
            icon=icon,
        )

    def gridparam(
        self,
        background: str | None = None,
        major_enabled: tuple[bool, bool] | None = None,
        minor_enabled: tuple[bool, bool] | None = None,
        major_style: tuple[str, str, int] | None = None,
        minor_style: tuple[str, str, int] | None = None,
    ) -> GridParam:
        """Make :py:class:`.GridParam` instance

        Args:
            background: canvas background color
            major_enabled: major grid enabled (x, y)
            minor_enabled: minor grid enabled (x, y)
            major_style: major grid style (linestyle, color, width)
            minor_style: minor grid style (linestyle, color, width)

        Returns:
            :py:class:`.GridParam`: grid parameters
        """
        gridparam = GridParam(title=_("Grid"), icon="lin_lin.png")
        gridparam.read_config(CONF, "plot", "grid")
        if background is not None:
            gridparam.background = background
        if major_enabled is not None:
            gridparam.maj_xenabled, gridparam.maj_yenabled = major_enabled
        if minor_enabled is not None:
            gridparam.min_xenabled, gridparam.min_yenabled = minor_enabled
        if major_style is not None:
            style = LineStyleParam()
            linestyle, color, style.width = major_style
            style.set_style_from_matlab(linestyle)
            style.color = COLORS.get(color, color)  # MATLAB-style
        if minor_style is not None:
            style = LineStyleParam()
            linestyle, color, style.width = minor_style
            style.set_style_from_matlab(linestyle)
            style.color = COLORS.get(color, color)  # MATLAB-style
        return gridparam

    def grid(
        self,
        background: str | None = None,
        major_enabled: tuple[bool, bool] | None = None,
        minor_enabled: tuple[bool, bool] | None = None,
        major_style: tuple[str, str, int] | None = None,
        minor_style: tuple[str, str, int] | None = None,
    ) -> GridItem:
        """Make a grid `plot item` (:py:class:`.GridItem` object)

        Args:
            background: canvas background color
            major_enabled: major grid enabled (x, y)
            minor_enabled: minor grid enabled (x, y)
            major_style: major grid style (linestyle, color, width)
            minor_style: minor grid style (linestyle, color, width)

        Returns:
            :py:class:`.GridItem`: grid item
        """
        gridparam = self.gridparam(
            background, major_enabled, minor_enabled, major_style, minor_style
        )
        return GridItem(gridparam)
