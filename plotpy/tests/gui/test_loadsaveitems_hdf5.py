# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Load/save items from/to HDF5 file"""

# guitest: show

# WARNING:
# This script requires read/write permissions on current directory

from guidata.dataset.io import HDF5Reader, HDF5Writer

from plotpy.tests.gui.test_loadsaveitems_pickle import IOTest


class HDF5Test(IOTest):
    """Test load/save items from/to HDF5 file"""

    FNAME = "loadsavecanvas.h5"

    def restore_items(self):
        """Restore items from HDF5 file"""
        reader = HDF5Reader(self.FNAME)
        self.plot.deserialize(reader)
        reader.close()

    def save_items(self):
        """Save items to HDF5 file"""
        writer = HDF5Writer(self.FNAME)
        self.plot.serialize(writer)
        writer.close()


def test_loadsaveitems_hdf5():
    """Test load/save items from/to HDF5 file"""
    test = HDF5Test()
    test.run()


if __name__ == "__main__":
    test_loadsaveitems_hdf5()
