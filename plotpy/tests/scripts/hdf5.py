# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
HDF5 I/O demo

DataSet objects may be saved in HDF5 files, a universal hierarchical dataset
file type. This script shows how to save in and then reload data from a HDF5
file.
"""
import os

from guidata.dataset.dataitems import StringItem

from plotpy.tests.scripts.all_items import TestParameters
from plotpy.utils.io.hdf5io import HDF5Reader, HDF5Writer

SHOW = True  # Show test in GUI-based test launcher


class TestParameters_Light(TestParameters):
    date = StringItem("D1", default="Replacement for unsupported DateItem")
    dtime = StringItem("D2", default="Replacement for unsupported DateTimeItem")


if __name__ == "__main__":
    # Create QApplication
    import plotpy.config
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()

    # FIXME: test.h5 is versioned
    # It may be removed if code fails
    if os.path.exists("test.h5"):
        os.unlink("test.h5")

    e = TestParameters()
    if e.edit():
        writer = HDF5Writer("test.h5")
        e.serialize(writer)
        writer.close()

        e = TestParameters()
        reader = HDF5Reader("test.h5")
        e.deserialize(reader)
        reader.close()
        e.edit()
