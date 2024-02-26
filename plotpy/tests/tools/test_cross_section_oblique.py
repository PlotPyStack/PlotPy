# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Oblique averaged cross section test"""

# guitest: show

from __future__ import annotations

from plotpy.panels.csection.csitem import ObliqueCrossSectionItem
from plotpy.panels.csection.cswidget import ObliqueCrossSection
from plotpy.tests.tools import test_cross_section_line
from plotpy.tools import ImageMaskTool, ObliqueCrossSectionTool, OCSPanelTool

# debug mode shows the ROI in the top-left corner of the image plot:
ObliqueCrossSectionItem.DEBUG = False


class OCSImageDialog(test_cross_section_line.BaseCSImageDialog):
    """Oblique averaged cross section test"""

    TOOLCLASSES = (ObliqueCrossSectionTool, OCSPanelTool, ImageMaskTool)
    PANELCLASS = ObliqueCrossSection


def test_cross_section_oblique():
    """Test cross section oblique"""
    test_cross_section_line.generic_cross_section_dialog(
        "Oblique averaged cross section test", OCSImageDialog
    )


if __name__ == "__main__":
    test_cross_section_oblique()
