# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Load/save items from/to HDF5 file"""

# guitest: show

# WARNING:
# This script requires read/write permissions on current directory

import os

import h5py
from guidata.dataset.io import HDF5Reader, HDF5Writer
from guidata.qthelpers import qt_app_context

from plotpy.tests.gui.test_loadsaveitems_pickle import IOTest

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_FILE_NAME = "loadsavecanvas.h5"
IMG_BRAIN = "brain.png"


def rewrite_test_file_content():
    """
    Function used to rewrite image path for ImageItem_001, TrImageItem_001 and
    MaskedImageItem_001 objects in h5 test file
    """
    with h5py.File(os.path.join(DIR_PATH, TEST_FILE_NAME), "r+") as f:
        image_name_list = ("ImageItem_001", "TrImageItem_001", "MaskedImageItem_001")
        # grp = f["plot_items"]
        for item in list(f.keys()):
            if item not in image_name_list:
                continue
            # print(f[item].attrs["fname"])
            f[item].attrs["fname"] = os.path.join(DIR_PATH, IMG_BRAIN)


rewrite_test_file_content()


class HDF5Test(IOTest):
    FNAME = os.path.join(DIR_PATH, TEST_FILE_NAME)

    def restore_items(self):
        reader = HDF5Reader(self.FNAME)
        self.plot.deserialize(reader)
        reader.close()

    def save_items(self):
        writer = HDF5Writer(self.FNAME)
        self.plot.serialize(writer)
        writer.close()


def test_loadsaveitems_hdf5():
    with qt_app_context(exec_loop=True):
        test = HDF5Test()
        test.run()


if __name__ == "__main__":
    test_loadsaveitems_hdf5()
