# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# ((see plotpy/__init__.py for details))

# pylint: disable=W0613

"""
disthelpers
-----------

The ``plotpy.core.utils.disthelpers`` module provides helper functions for Python
package distribution on Microsoft Windows platforms with ``py2exe`` or on
all platforms thanks to ``cx_Freeze``.
"""

import atexit
import os
import os.path as osp
import shutil
import sys
import traceback
from subprocess import PIPE, Popen

from plotpy.core.utils.module import get_module_path


# ==============================================================================
# Dependency management
# ==============================================================================
def get_changeset(path, rev=None):
    """Return Mercurial repository *path* revision number"""
    args = ["hg", "parent"]
    if rev is not None:
        args += ["--rev", str(rev)]
    process = Popen(args, stdout=PIPE, stderr=PIPE, cwd=path, shell=True)
    try:
        return process.stdout.read().splitlines()[0].split()[1]
    except IndexError:
        raise RuntimeError(process.stderr.read())


def prepend_module_to_path(module_path):
    """
    Prepend to sys.path module located in *module_path*
    Return string with module infos: name, revision, changeset

    Use this function:
    1) In your application to import local frozen copies of internal libraries
    2) In your py2exe distributed package to add a text file containing the returned string
    """
    if not osp.isdir(module_path):
        # Assuming py2exe distribution
        return
    sys.path.insert(0, osp.abspath(module_path))
    changeset = get_changeset(module_path)
    name = osp.basename(module_path)
    prefix = "Prepending module to sys.path"
    message = prefix + ("{} [revision {}]".format(name, changeset)).rjust(
        80 - len(prefix), "."
    )
    print(message, file=sys.stderr)
    if name in sys.modules:
        sys.modules.pop(name)
        nbsp = 0
        for modname in sys.modules.keys():
            if modname.startswith(name + "."):
                sys.modules.pop(modname)
                nbsp += 1
        warning = "(removed {} from sys.modules".format(name)
        if nbsp:
            warning += " and {} subpackages".format(nbsp)
        warning += ")"
        print(warning.rjust(80), file=sys.stderr)
    return message


def prepend_modules_to_path(module_base_path):
    """Prepend to sys.path all modules located in *module_base_path*"""
    if not osp.isdir(module_base_path):
        # Assuming py2exe distribution
        return
    fnames = [osp.join(module_base_path, name) for name in os.listdir(module_base_path)]
    messages = [
        prepend_module_to_path(dirname) for dirname in fnames if osp.isdir(dirname)
    ]
    return os.linesep.join(messages)


# ==============================================================================
# Distribution helpers
# ==============================================================================
def _remove_later(fname):
    """Try to remove file later (at exit)"""

    def try_to_remove(fname):
        """Removes the file *fname* if it exists."""
        if osp.exists(fname):
            os.remove(fname)

    atexit.register(try_to_remove, osp.abspath(fname))


def to_include_files(data_files):
    """Convert data_files list to include_files list

    data_files:
      * this is the ``py2exe`` data files format
      * list of tuples (dest_dirname, (src_fname1, src_fname2, ...))

    include_files:
      * this is the ``cx_Freeze`` data files format
      * list of tuples ((src_fname1, dst_fname1),
                        (src_fname2, dst_fname2), ...))
    """
    include_files = []
    for dest_dir, fnames in data_files:
        for source_fname in fnames:
            dest_fname = osp.join(dest_dir, osp.basename(source_fname))
            include_files.append((source_fname, dest_fname))
    return include_files


def strip_version(version):
    """Return version number with digits only
    (Windows does not support strings in version numbers)"""
    return version.split("beta")[0].split("alpha")[0].split("rc")[0].split("dev")[0]


def remove_dir(dirname):
    """Remove directory *dirname* and all its contents
    Print details about the operation (progress, success/failure)"""
    print("Removing directory '{}'...".format(dirname), end=" ")
    try:
        shutil.rmtree(dirname, ignore_errors=True)
        print("OK")
    except Exception:
        print("Failed!")
        traceback.print_exc()
