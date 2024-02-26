# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Line cross section test"""

# guitest: show
from __future__ import annotations

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.panels.csection.cswidget import CrossSectionWidget, LineCrossSection
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests import get_path
from plotpy.tools import ImageMaskTool, LCSPanelTool, LineCrossSectionTool


class BaseCSImageDialog(PlotDialog):
    """Base cross section test

    This class is used to test the LineCrossSection and ObliqueCrossSection
    """

    TOOLCLASSES = ()
    PANELCLASS = CrossSectionWidget  # to be overridden by subclasses

    def __init__(self, parent=None, toolbar=True, title=None, options=None):
        super().__init__(
            parent=parent,
            toolbar=toolbar,
            title=title,
            options=options,
            auto_tools=True,
        )
        for tool in self.TOOLCLASSES:
            self.manager.add_tool(tool)

    def populate_plot_layout(self):
        """Populate the plot layout"""
        super().populate_plot_layout()
        cs_panel = self.PANELCLASS(self)
        splitter = self.plot_widget.xcsw_splitter
        splitter.addWidget(cs_panel)
        splitter.setSizes([0, 1, 0])
        self.manager.add_panel(cs_panel)


class LCSImageDialog(BaseCSImageDialog):
    """Line cross section test"""

    TOOLCLASSES = (LineCrossSectionTool, LCSPanelTool, ImageMaskTool)
    PANELCLASS = LineCrossSection


def generic_cross_section_dialog(title, dialogclass):
    """Generic function used to test the cross section tools"""
    with qt_app_context(exec_loop=True):
        win = dialogclass(
            toolbar=True,
            title=title,
            options=PlotOptions(type="image"),
        )
        win.resize(600, 600)
        filename = get_path("brain_cylinder.png")
        image = make.maskedimage(filename=filename, colormap="bone")
        plot = win.manager.get_plot()
        plot.add_item(image)
        plot.set_active_item(image)
        image.unselect()
        win.show()


def test_cross_section_line():
    """Test cross section oblique"""
    generic_cross_section_dialog("Line cross section test", LCSImageDialog)


if __name__ == "__main__":
    test_cross_section_line()
