# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Oblique averaged cross section test"""

# guitest: show

import os.path as osp

from guidata.qthelpers import qt_app_context

import plotpy.core.plot.cross_section
from plotpy.core.builder import make
from plotpy.core.plot.cross_section.cswidget import ObliqueCrossSection
from plotpy.core.plot.plotwidget import PlotDialog, PlotType
from plotpy.core.tools.cross_section import ObliqueCrossSectionTool, OCSPanelTool
from plotpy.core.tools.image import ImageMaskTool

# debug mode shows the ROI in the top-left corner of the image plot:
plotpy.core.plot.cross_section.csitem.DEBUG = True


class OCSImageDialog(PlotDialog):
    """Oblique averaged cross section test"""

    def __init__(self, parent=None, toolbar=True, wintitle=None, options=None):
        super().__init__(
            parent=parent,
            toolbar=toolbar,
            wintitle=wintitle,
            options=options,
            auto_tools=True,
        )
        for tool in (ObliqueCrossSectionTool, OCSPanelTool, ImageMaskTool):
            self.manager.add_tool(tool)

    def populate_plot_layout(self) -> None:
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
            wintitle="Oblique averaged cross section test",
            options={"type": PlotType.IMAGE},
        )
        win.resize(600, 600)

        #    from tests.gui.image import compute_image
        #    data = np.array((compute_image(4000, grid=False)+1)*32e3, dtype=np.uint16)
        #    image = make.maskedimage(data, colormap="bone", show_mask=True)

        filename = osp.join(osp.dirname(__file__), "brain_cylinder.png")
        image = make.maskedimage(filename=filename, colormap="bone")

        plot = win.manager.get_plot()
        plot.add_item(image)
        win.show()


if __name__ == "__main__":
    test_cross_section_oblique()
