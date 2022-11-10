# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
DataSetGroup demo

DataSet objects may be grouped into DataSetGroup, allowing them to be edited
in a single dialog box (with one tab per DataSet object).
"""

SHOW = True  # Show test in GUI-based test launcher

from plotpy.gui.dataset.datatypes import DataSetGroupGui

try:
    from tests.scripts.all_features import TestParameters
except ImportError:
    from plotpy.tests.scripts.all_features import TestParameters

if __name__ == "__main__":
    # Create QApplication
    import plotpy.gui
    import plotpy.core.config.config

    _app = plotpy.gui.qapplication()

    e1 = TestParameters("DataSet #1")
    e2 = TestParameters("DataSet #2")
    g = DataSetGroupGui([e1, e2], title="Parameters group")
    g.edit()
    print(e1)
    g.edit()
