# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Load/save items from/to HDF5 file"""


# WARNING:
# This script requires read/write permissions on current directory

from plotpy.utils.io.hdf5io import HDF5Reader, HDF5Writer

try:
    from tests.gui.loadsaveitems_pickle import IOTest
except ImportError:
    from plotpy.tests.gui.loadsaveitems_pickle import IOTest

SHOW = True  # Show test in GUI-based test launcher


class HDF5Test(IOTest):
    FNAME = "loadsavecanvas.h5"

    def restore_items(self):
        reader = HDF5Reader(self.FNAME)
        self.plot.deserialize(reader)
        reader.close()

    def save_items(self):
        writer = HDF5Writer(self.FNAME)
        self.plot.serialize(writer)
        writer.close()


if __name__ == "__main__":
    import plotpy.widgets

    _app = plotpy.widgets.qapplication()
    test = HDF5Test()
    test.run()
