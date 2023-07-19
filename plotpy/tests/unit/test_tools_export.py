# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Export tools unit tests"""

from unittest.mock import patch

import numpy as np
from qtpy import QtWidgets as QW

from plotpy.core.builder import make
from plotpy.core.tools.curve import export_curve_data


def test_export_curve(tmpdir):
    """Test export of a curve"""
    x = np.linspace(-10, 10, 200)
    y = x + 1
    curve = make.curve(x, y, color="g")

    dest = tmpdir / "output.txt"
    with patch.object(QW.QFileDialog, "getSaveFileName") as gsf_mock:
        gsf_mock.return_value = (str(dest), "")
        export_curve_data(curve)

    assert dest.exists()
    data = dest.readlines()
    assert len(data) == 200
    for line in data:
        x, y = line.split(",")
        assert float(y) == float(x) + 1
