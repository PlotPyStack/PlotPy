# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Oblique averaged cross section test"""

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.panels.csection.csitem import ObliqueCrossSectionItem
from plotpy.panels.csection.cswidget import ObliqueCrossSection
from plotpy.plot import PlotDialog, PlotOptions
from plotpy.tests import get_path
from plotpy.tools import ImageMaskTool, ObliqueCrossSectionTool, OCSPanelTool

# debug mode shows the ROI in the top-left corner of the image plot:
ObliqueCrossSectionItem.DEBUG = True


class OCSImageDialog(PlotDialog):
    """Oblique averaged cross section test"""

    def __init__(self, parent=None, toolbar=True, title=None, options=None):
        super().__init__(
            parent=parent,
            toolbar=toolbar,
            title=title,
            options=options,
            auto_tools=True,
        )
        for tool in (ObliqueCrossSectionTool, OCSPanelTool, ImageMaskTool):
            self.manager.add_tool(tool)

    def populate_plot_layout(self):
        """Populate the plot layout"""
        super().populate_plot_layout()
        ra_panel = ObliqueCrossSection(self)
        splitter = self.plot_widget.xcsw_splitter
        splitter.addWidget(ra_panel)
        splitter.setStretchFactor(splitter.count() - 1, 1)
        splitter.setSizes(list(splitter.sizes()) + [2])
        self.manager.add_panel(ra_panel)


def test_cross_section_oblique():
    """Test cross section oblique"""
    with qt_app_context(exec_loop=True):
        win = OCSImageDialog(
            toolbar=True,
            title="Oblique averaged cross section test",
            options=PlotOptions(type="image"),
        )
        win.resize(600, 600)

        filename = get_path("brain_cylinder.png")
        image = make.maskedimage(filename=filename, colormap="bone")

        plot = win.manager.get_plot()
        plot.add_item(image)
        win.show()


if __name__ == "__main__":
    test_cross_section_oblique()
