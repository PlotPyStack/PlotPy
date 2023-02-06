# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
plotpy.core.config.misc
-----------------------

The ``plotpy.core.config.misc`` module provides configuration related tools.
"""

import gettext
import os
import os.path as osp
import sys

from plotpy.utils.module import get_module_path
from plotpy.utils.strings import decode_fs_string

IMG_PATH = []


def get_module_data_path(modname, relpath=None):
    """Return module *modname* data path
    Handles py2exe/cx_Freeze distributions"""
    datapath = getattr(sys.modules[modname], "DATAPATH", "")
    if not datapath:
        datapath = get_module_path(modname)
        parentdir = osp.normpath(osp.join(datapath, osp.pardir))
        if osp.isfile(parentdir):
            # Parent directory is not a directory but the "library.zip" file:
            # this is either a py2exe or a cx_Freeze distribution
            datapath = osp.abspath(
                osp.join(osp.join(parentdir, osp.pardir, os.pardir), modname)
            )
    if relpath is not None:
        datapath = osp.abspath(osp.join(datapath, relpath))
    return datapath


def get_translation(modname, dirname=None):
    """Return translation callback for module *modname*"""
    if dirname is None:
        dirname = modname
    # fixup environment var LANG in case it's unknown
    if "LANG" not in os.environ:
        import locale  # Warning: 2to3 false alarm ("import" fixer)

        lang = locale.getdefaultlocale()[0]
        if lang is not None:
            os.environ["LANG"] = lang
    try:
        trans = gettext.translation(
            modname, get_module_locale_path(dirname), codeset="utf-8"
        )
        return trans.gettext
    except IOError as _e:
        # print("Not using translations ({})".format(e))
        def translate_dumb(x):
            """Dummy translation function that returns the original text"""
            if not isinstance(x, str):
                return str(x, "utf-8")
            return x

        return translate_dumb


def get_module_locale_path(modname):
    """Return module *modname* gettext translation path"""
    localepath = getattr(sys.modules[modname], "LOCALEPATH", "")
    if not localepath:
        localepath = get_module_data_path(modname, relpath="locale")
    return localepath


def add_image_path(path, subfolders=True):
    """Append image path (opt. with its subfolders) to global list IMG_PATH"""
    if not isinstance(path, str):
        path = decode_fs_string(path)
    global IMG_PATH
    IMG_PATH.append(path)
    if subfolders:
        for fileobj in os.listdir(path):
            pth = osp.join(path, fileobj)
            if osp.isdir(pth):
                IMG_PATH.append(pth)


def add_image_module_path(modname, relpath, subfolders=True):
    """
    Appends image data path relative to a module name.
    Used to add module local data that resides in a module directory
    but will be shipped under sys.prefix / share/ ...

    modname must be the name of an already imported module as found in
    sys.modules
    """
    add_image_path(get_module_data_path(modname, relpath=relpath), subfolders)


def get_image_file_path(name, default="not_found.png"):
    """
    Return the absolute path to image with specified name
    name, default: filenames with extensions
    """
    for pth in IMG_PATH:
        full_path = osp.join(pth, name)
        if osp.isfile(full_path):
            return osp.abspath(full_path)
    if default is not None:
        try:
            return get_image_file_path(default, None)
        except RuntimeError:
            raise RuntimeError(f"Image file {name!r} not found")
    else:
        raise RuntimeError()
