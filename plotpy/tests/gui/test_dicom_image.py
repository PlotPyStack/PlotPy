# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""DICOM image test

Requires pydicom (>=0.9.3)"""

# guitest: show

import os

import pytest
from guidata.qthelpers import qt_app_context

from plotpy.core.builder import make
from plotpy.core.constants import PlotType
from plotpy.core.plot import PlotDialog

try:
    import pydicom  # type:ignore
except ImportError:
    pydicom = None


@pytest.mark.skipif(pydicom is None, reason="pydicom not installed")
def test_dicom_image():
    with qt_app_context(exec_loop=True):
        win = PlotDialog(
            edit=False,
            toolbar=True,
            wintitle="DICOM I/O test",
            options=dict(show_contrast=True, type=PlotType.IMAGE),
        )
        filename = os.path.join(os.path.dirname(__file__), "mr-brain.dcm")
        image = make.image(filename=filename, title="DICOM img", colormap="gray")
        plot = win.manager.get_plot()
        plot.add_item(image)
        plot.select_item(image)
        contrast = win.manager.get_contrast_panel()
        contrast.histogram.eliminate_outliers(54.0)
        win.resize(600, 700)


if __name__ == "__main__":
    win = test_dicom_image()
