# -*- coding: utf-8 -*-
import os
import os.path as osp
import sys
from distutils.core import setup

import numpy
from setuptools import Distribution, Extension

try:
    from Cython.Compiler import Main
except ImportError:

    class Main:
        """Fake class so that tox can analyse the setup before installing cython"""

        @staticmethod
        def compile(*args, **kwargs):
            print("Skipping compilation of %r %r" % (args, kwargs))


LIBNAME = "plotpy"
BASEPATH = "."
SRCPATH = osp.join(BASEPATH, "src")


# We create requirements for C/pyx dependencies compilation and integration into wheel
# file
def is_msvc():
    """Detect if Microsoft Visual C++ compiler was chosen to build package"""
    # checking if mingw is the compiler
    # mingw32 compiler configured in %USERPROFILE%\pydistutils.cfg
    # or distutils\distutils.cfg
    dist = Distribution()
    dist.parse_config_files()
    bld = dist.get_option_dict("build")
    if bld:
        comp = bld.get("compiler")
        if comp is not None and "mingw32" in comp:
            return False  # mingw is the compiler
    return os.name == "nt" and "mingw" not in "".join(sys.argv)


CFLAGS = ["-Wall"]
if is_msvc():
    CFLAGS.insert(0, "/EHsc")
for arg, compile_arg in (("--sse2", "-msse2"), ("--sse3", "-msse3")):
    if arg in sys.argv:
        sys.argv.pop(sys.argv.index(arg))
        CFLAGS.insert(0, compile_arg)


for fname in os.listdir(SRCPATH):
    if osp.splitext(fname)[1] == ".pyx":
        Main.compile(osp.join(SRCPATH, fname), language_level=2)

setup(
    ext_modules=[
        Extension(
            name=f"{LIBNAME}.mandelbrot",
            sources=[osp.join(SRCPATH, "mandelbrot.c")],
            include_dirs=[SRCPATH, numpy.get_include()],
        ),
        Extension(
            name=f"{LIBNAME}.histogram2d",
            sources=[osp.join(SRCPATH, "histogram2d.c")],
            include_dirs=[SRCPATH, numpy.get_include()],
        ),
        Extension(
            name=f"{LIBNAME}.contour2d",
            sources=[osp.join(SRCPATH, "contour2d.c")],
            include_dirs=[SRCPATH, numpy.get_include()],
        ),
        Extension(
            name=f"{LIBNAME}._scaler",
            sources=[osp.join(SRCPATH, "scaler.cpp"), osp.join(SRCPATH, "pcolor.cpp")],
            extra_compile_args=CFLAGS,
            depends=[
                osp.join(SRCPATH, "traits.hpp"),
                osp.join(SRCPATH, "points.hpp"),
                osp.join(SRCPATH, "arrays.hpp"),
                osp.join(SRCPATH, "scaler.hpp"),
                osp.join(SRCPATH, "debug.hpp"),
            ],
            include_dirs=[SRCPATH, numpy.get_include()],
        ),
    ]
)
