"""
Module dll
==========

:synopsis: module to provide dll tools for plotpy

:moduleauthor: CEA

:platform: All

"""


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


import os
import os.path as osp
import sys
import warnings
from subprocess import PIPE, Popen


def get_msvc_version(python_version):
    """Return Microsoft Visual C++ version used to build this Python version"""
    # see https://wiki.python.org/moin/WindowsCompilers
    if python_version is None:
        python_version = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
        warnings.warn("Assuming Python {} target".format(python_version))
    if python_version in ("2.6", "2.7", "3.0", "3.1", "3.2"):
        # Python 2.6-2.7, 3.0-3.2 were built with Visual Studio 9.0.21022.8
        # (i.e. Visual C++ 2008, not Visual C++ 2008 SP1!)
        return "9.0.21022.8"
    elif python_version in ("3.3", "3.4"):
        # Python 3.3+ were built with Visual Studio 10.0.30319.1
        # (i.e. Visual C++ 2010)
        return "10.0"
    elif python_version in ("3.5", "3.6"):
        # Python 3.5+ were built with Visual Studio 14
        # (i.e. Visual Studio 2015
        return "14.0"
    else:
        raise RuntimeError("Unsupported Python version {}".format(python_version))


def get_dll_architecture(path):
    """Return DLL architecture (32 or 64bit) using Microsoft dumpbin.exe"""
    os.environ[
        "PATH"
    ] += r";C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\IDE\;C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\BIN;C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\;C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\BIN"
    process = Popen(
        ["dumpbin", "/HEADERS", osp.basename(path)],
        stdout=PIPE,
        stderr=PIPE,
        cwd=osp.dirname(path),
        shell=True,
    )
    output = process.stdout.read()
    error = process.stderr.read()
    if error:
        raise RuntimeError(error)
    elif "x86" in output:
        return 32
    elif "x64" in output:
        return 64
    else:
        raise ValueError("Unable to get DLL architecture")


def get_msvc_dlls(msvc_version, architecture=None, check_architecture=False):
    """Get the list of Microsoft Visual C++ DLLs associated to
    architecture and Python version, create the manifest file.

    architecture: integer (32 or 64) -- if None, take the Python build arch
    python_version: X.Y"""
    current_architecture = 64 if sys.maxsize > 2 ** 32 else 32
    if architecture is None:
        architecture = current_architecture
    assert architecture in (32, 64)

    filelist = []

    msvc_major = msvc_version.split(".")[0]
    msvc_minor = msvc_version.split(".")[1]

    if msvc_major == "9":
        key = "1fc8b3b9a1e18e3b"
        atype = "" if architecture == 64 else "win32"
        arch = "amd64" if architecture == 64 else "x86"

        groups = {
            "CRT": ("msvcr90.dll", "msvcp90.dll", "msvcm90.dll"),
            #                  "OPENMP": ("vcomp90.dll",)
        }

        for group, dll_list in groups.items():
            dlls = ""
            for dll in dll_list:
                dlls += '    <file name="{}" />{}'.format(dll, os.linesep)

            manifest = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <!-- Copyright (c) Microsoft Corporation.  All rights reserved. -->
                <assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
                    <noInheritable/>
                    <assemblyIdentity
                        type="{atype}"
                        name="Microsoft.VC90.{group}"
                        version="{msvc_version}"
                        processorArchitecture="{arch}"
                        publicKeyToken="{key}"
                    />
                {dlls}</assembly>
                """

            vc90man = "Microsoft.VC90.{}.manifest".format(group)
            open(vc90man, "w").write(manifest)
            # todo to treat: _remove_later(vc90man)
            filelist += [vc90man]

            winsxs = osp.join(os.environ["windir"], "WinSxS")
            vcstr = "{}_Microsoft.VC90.{}_{}_{}".format(arch, group, key, msvc_version)
            for fname in os.listdir(winsxs):
                path = osp.join(winsxs, fname)
                if osp.isdir(path) and fname.lower().startswith(vcstr.lower()):
                    for dllname in os.listdir(path):
                        filelist.append(osp.join(path, dllname))
                    break
            else:
                raise RuntimeError(
                    f"Microsoft Visual C++ {group} DLLs version {msvc_version} were not found"
                )

    elif msvc_major in ("10", "14"):
        if msvc_version == "10":
            dlls = ("msvcp{}.dll", "msvcr{}.dll", "vcomp{}.dll")
        else:
            dlls = ("msvcp{}.dll", "vcomp{}.dll")
        namelist = [name.format(msvc_major + msvc_minor) for name in dlls]

        windir = os.environ["windir"]
        is_64bit_windows = osp.isdir(osp.join(windir, "SysWOW64"))

        # Reminder: WoW64 (*W*indows 32-bit *o*n *W*indows *64*-bit) is a
        # subsystem of the Windows operating system capable of running 32-bit
        # applications and is included on all 64-bit versions of Windows
        # (source: http://en.wikipedia.org/wiki/WoW64)
        # In other words, "SysWOW64" contains 32-bit DLL and applications,
        # whereas "System32" contains 64-bit DLL and applications on a 64-bit
        # system.
        if architecture == 64:
            # 64-bit DLLs are located in...
            if is_64bit_windows:
                sysdir = "System32"  # on a 64-bit OS
            else:
                # ...no directory to be found!
                raise RuntimeError("Can't find 64-bit DLLs on a 32-bit OS")
        else:
            # 32-bit DLLs are located in...
            if is_64bit_windows:
                sysdir = "SysWOW64"  # on a 64-bit OS
            else:
                sysdir = "System32"  # on a 32-bit OS

        for dllname in namelist:
            fname = osp.join(windir, sysdir, dllname)
            if osp.exists(fname):
                filelist.append(fname)
            else:
                raise RuntimeError(
                    "Microsoft Visual C++ DLLs {} version {} "
                    "were not found".format(dllname, msvc_version)
                )

    else:
        raise RuntimeError("Unsupported MSVC version {}".format(msvc_version))

    if check_architecture:
        for path in filelist:
            if path.endswith(".dll"):
                try:
                    arch = get_dll_architecture(path)
                except RuntimeError:
                    return
                if arch != architecture:
                    raise RuntimeError(
                        "{}: expecting {}bit, found {}bit".format(
                            path, architecture, arch
                        )
                    )

    return filelist


def create_msvc_data_files(architecture=None, python_version=None, verbose=False):
    """Including Microsoft Visual C++ DLLs"""
    msvc_version = get_msvc_version(python_version)
    filelist = get_msvc_dlls(msvc_version, architecture=architecture)
    print(create_msvc_data_files.__doc__)
    if verbose:
        for name in filelist:
            print("  ", name)
    msvc_major = msvc_version.split(".")[0]
    if msvc_major == "9":
        return [("Microsoft.VC90.CRT", filelist)]
    else:
        return [("", filelist)]
