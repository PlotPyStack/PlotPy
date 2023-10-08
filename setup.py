# -*- coding: utf-8 -*-

import os
import os.path as osp
import sys
from distutils.core import setup

import numpy
from Cython.Compiler import Main
from setuptools import Distribution, Extension

LIBNAME = "plotpy"
SRCPATH = osp.join(".", "src")


def is_msvc():
    """Detect if Microsoft Visual C++ compiler was chosen to build package"""
    dist = Distribution()
    dist.parse_config_files()
    bld = dist.get_option_dict("build")
    if bld:
        comp = bld.get("compiler")
        if comp is not None and "mingw32" in comp:
            return False  # mingw is the compiler
    return os.name == "nt" and "mingw" not in "".join(sys.argv)


def get_compiler_flags():
    """Get compiler flags for C++ dependencies compilation"""
    if is_msvc():
        cflags = ["/EHsc"]
    else:
        cflags = ["-Wall"]
    for arg, compile_arg in (("--sse2", "-msse2"), ("--sse3", "-msse3")):
        if arg in sys.argv:
            sys.argv.pop(sys.argv.index(arg))
            cflags.insert(0, compile_arg)
    return cflags


CFLAGS_CPP = get_compiler_flags()


def compile_cython_extensions():
    """Compile Cython extensions"""
    for fname in os.listdir(SRCPATH):
        if osp.splitext(fname)[1] == ".pyx":
            Main.compile(osp.join(SRCPATH, fname), language_level=2)


compile_cython_extensions()

INCLUDE_DIRS = [SRCPATH, numpy.get_include()]

# -------------------------------------------------------------------------------------
# TODO: When dropping support for Cython < 3.0, we can remove the following line
# and uncomment the next one.
# In the meantime, we hide the deprecation warnings when building the package.
DEFINE_MACROS_CYTHON = []
CFLAGS_CYTHON = ["-Wno-cpp"]
# DEFINE_MACROS_CYTHON = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
# CFLAGS_CYTHON = []
# -------------------------------------------------------------------------------------

DEFINE_MACROS_CPP = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]

setup(
    ext_modules=[
        Extension(
            name=f"{LIBNAME}.mandelbrot",
            sources=[osp.join(SRCPATH, "mandelbrot.c")],
            include_dirs=INCLUDE_DIRS,
            extra_compile_args=CFLAGS_CYTHON,
            define_macros=DEFINE_MACROS_CYTHON,
        ),
        Extension(
            name=f"{LIBNAME}.histogram2d",
            sources=[osp.join(SRCPATH, "histogram2d.c")],
            include_dirs=INCLUDE_DIRS,
            extra_compile_args=CFLAGS_CYTHON,
            define_macros=DEFINE_MACROS_CYTHON,
        ),
        Extension(
            name=f"{LIBNAME}.contour2d",
            sources=[osp.join(SRCPATH, "contour2d.c")],
            include_dirs=INCLUDE_DIRS,
            extra_compile_args=CFLAGS_CYTHON,
            define_macros=DEFINE_MACROS_CYTHON,
        ),
        Extension(
            name=f"{LIBNAME}._scaler",
            sources=[osp.join(SRCPATH, "scaler.cpp"), osp.join(SRCPATH, "pcolor.cpp")],
            extra_compile_args=CFLAGS_CPP,
            depends=[
                osp.join(SRCPATH, "traits.hpp"),
                osp.join(SRCPATH, "points.hpp"),
                osp.join(SRCPATH, "arrays.hpp"),
                osp.join(SRCPATH, "scaler.hpp"),
                osp.join(SRCPATH, "debug.hpp"),
            ],
            include_dirs=INCLUDE_DIRS,
            define_macros=DEFINE_MACROS_CPP,
        ),
    ]
)
