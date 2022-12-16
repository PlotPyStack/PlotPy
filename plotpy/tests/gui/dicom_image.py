# -*- coding: utf-8 -*-
#
# Copyright © 2015 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""DICOM image test

Requires pydicom (>=0.9.3)"""

SHOW = True  # Show test in GUI-based test launcher

try: 
    import pydicom
except ImportError:
    print("Pydicom not installed, dicom_image.py can not run")
    pydicom = False

import os.path as osp

import plotpy
from plotpy.gui.widgets.baseplot import PlotType
from plotpy.gui.widgets.plot import PlotDialog
from plotpy.gui.widgets.builder import make


def test():    
    win = PlotDialog(
        edit=False,
        toolbar=True,
        wintitle="DICOM I/O test",
        options=dict(show_contrast=True, type=PlotType.IMAGE),
    )    
    if pydicom:
        filename = osp.join(osp.dirname(__file__), "mr-brain.dcm")
        image = make.image(filename=filename, title="DICOM img", colormap="gray")
        plot = win.get_plot()
        plot.add_item(image)
        plot.select_item(image)
        contrast = win.get_contrast_panel()
        contrast.histogram.eliminate_outliers(54.0)
        win.resize(600, 700)
        
    return win


if __name__ == "__main__":
    _app = plotpy.gui.qapplication()
    win = test()
    win.exec_()
