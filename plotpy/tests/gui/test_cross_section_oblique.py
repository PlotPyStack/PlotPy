# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Oblique averaged cross section test"""


import os.path as osp

import plotpy.widgets.plot.cross_section
from plotpy.widgets.builder import make
from plotpy.widgets.plot.cross_section.cswidget import ObliqueCrossSection
from plotpy.widgets.plot.plotwidget import PlotDialog, PlotType
from plotpy.widgets.tools.cross_section import ObliqueCrossSectionTool, OCSPanelTool
from plotpy.widgets.tools.image import ImageMaskTool

# debug mode shows the ROI in the top-left corner of the image plot:
plotpy.widgets.plot.cross_section.csitem.DEBUG = True

SHOW = True  # Show test in GUI-based test launcher


class OCSImageDialog(PlotDialog):
    def register_image_tools(self):
        PlotDialog.register_image_tools(self)
        for tool in (ObliqueCrossSectionTool, OCSPanelTool, ImageMaskTool):
            self.manager.add_tool(tool)

    def create_plot(self, options, row=0, column=0, rowspan=1, columnspan=1):
        PlotDialog.create_plot(self, options, row, column, rowspan, columnspan)
        ra_panel = ObliqueCrossSection(self)
        splitter = self.plot_widget.xcsw_splitter
        splitter.addWidget(ra_panel)
        splitter.setStretchFactor(splitter.count() - 1, 1)
        splitter.setSizes(list(splitter.sizes()) + [2])
        self.add_panel(ra_panel)


def test_cross_section_oblique():
    """Test"""
    # -- Create QApplication
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    # --
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
    win.exec_()


if __name__ == "__main__":
    test_cross_section_oblique()
