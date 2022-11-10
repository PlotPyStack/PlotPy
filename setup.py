"""
Module setup
============

:synopsis: allow to configure Python to generate the output wheel to distribute plotpy library

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
from setuptools import setup
from distutils.core import Extension
from distutils.dist import Distribution

try:
    from Cython.Compiler import Main
except ImportError:

    class Main:
        """Fake class so that tox can analyse the setup before installing cython nad numpy"""

        @staticmethod
        def compile(*args, **kwargs):
            print("Skipping compilation of %r %r" % (args, kwargs))


try:
    import numpy
except ImportError:

    class numpy:
        @staticmethod
        def get_include():
            return []


import plotpy

BASEPATH = "."  # os.path.abspath(os.path.dirname(__file__))
LIBNAME = "plotpy"

LIBPATH = os.path.join(BASEPATH, LIBNAME)
IMGPATH = os.path.join(LIBPATH, "images")
LANGPATH = os.path.join(LIBPATH, "locale")
TESTSPATH = os.path.join(BASEPATH, "tests")
SIFTPATH = os.path.join(BASEPATH, "sift")
DOCPATH = os.path.join(BASEPATH, "doc")
SRCPATH = os.path.join(BASEPATH, "src")
DSTPATH = os.path.join("Lib", "site-packages", LIBNAME)


def list_datafiles(path, extensions_list, path_ref=LIBPATH):
    """Allows to automatically supply a list for setup function"""
    list_data = list()

    for folder, subfolders, filenames in os.walk(path):
        list_tmp = list()
        for filename in filenames:
            if filename[-3:].lower() in extensions_list:
                rel_path = os.path.relpath(folder, BASEPATH)
                list_tmp.append(os.path.join(rel_path, filename))

        rel_path = os.path.join(DSTPATH, os.path.relpath(folder, path_ref))

        list_data.append((rel_path, list_tmp))

    return list_data


# We create automatically data dependencies list for setup
list_data = list()
list_data.extend(list_datafiles(IMGPATH, ["png", "jpg", "svg"]))
list_data.extend(list_datafiles(LANGPATH, [".po", ".mo"]))
list_data.extend(
    list_datafiles(TESTSPATH, [".py", "png", ".ui", ".h5", "dcm"], path_ref=BASEPATH)
)
list_data.extend(list_datafiles(SIFTPATH, [".py", "pyw", "ico"], path_ref=BASEPATH))
list_data.extend(
    list_datafiles(
        DOCPATH, ["bat", "ile", "rst", "png", ".py", "pyw", "ico"], path_ref=BASEPATH
    )
)
list_data.extend([(osp.join('Lib', 'site-packages', 'plotpy', 'src'), [osp.join("src", "arrays.hpp"), 
                                                                      osp.join('src', 'contour2d.pyx'), 
                                                                      osp.join('src', 'debug.hpp'), 
                                                                      osp.join('src', 'histogram2d.pyx'), 
                                                                      osp.join('src', 'mandelbrot.pyx'), 
                                                                      osp.join('src', 'pcolor.cpp'), 
                                                                      osp.join('src', 'points.hpp'), 
                                                                      osp.join('src', 'scaler.cpp'), 
                                                                      osp.join('src', 'scaler.hpp'), 
                                                                      osp.join('src', 'traits.hpp')])])

# We create requirements for C/pyx dependencies compilation and integration into wheel file
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
        Main.compile(osp.join(SRCPATH, fname))

list_external_modules = list()
list_external_modules.append(
    Extension(
        name="{}.mandelbrot".format(LIBNAME),
        sources=[osp.join(SRCPATH, "mandelbrot.c")],
        include_dirs=[SRCPATH, numpy.get_include()],
    )
)
list_external_modules.append(
    Extension(
        name="{}.histogram2d".format(LIBNAME),
        sources=[osp.join(SRCPATH, "histogram2d.c")],
        include_dirs=[SRCPATH, numpy.get_include()],
    )
)
list_external_modules.append(
    Extension(
        name="{}._scaler".format(LIBNAME),
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
    )
)
list_external_modules.append(
    Extension(
        name="{}.contour2d".format(LIBNAME),
        sources=[osp.join(SRCPATH, "contour2d.c")],
        include_dirs=[SRCPATH, numpy.get_include()],
    )
)


setup(
    name=LIBNAME,
    version=plotpy.__version__,
    author="CEA",
    author_email="virginie.lerouzic@cea.fr",
    maintainer="CEA",
    maintainer_email="virginie.lerouzic@cea.fr",
    keywords="CEA cea PLOTPY plotpy Plotpy PlotPy",
    classifiers=[
        "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License,"
        + " version 2.1 (CeCILL-2.1)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[
        "numpy>=1.3",
        "SciPy>=0.7",
        "Pillow",
        "PythonQwt==0.9.0",
        "h5py==2.8.0",
        "chardet",
    ],
    ext_modules=list_external_modules,
    extras_require={
        "Doc": ["Sphinx>=1.1"],
    },
    packages=[
        "{}".format(LIBNAME),
        "{}.core".format(LIBNAME),
        "{}.core.config".format(LIBNAME),
        "{}.core.dataset".format(LIBNAME),
        "{}.core.io".format(LIBNAME),
        "{}.core.utils".format(LIBNAME),
        "{}.gui".format(LIBNAME),
        "{}.gui.config".format(LIBNAME),
        "{}.gui.dataset".format(LIBNAME),
        "{}.gui.utils".format(LIBNAME),
        "{}.gui".format(LIBNAME),
        "{}.console".format(LIBNAME),
        "{}.console.widgets".format(LIBNAME),
        "{}.console.widgets.sourcecode".format(LIBNAME),
        "{}.gui.widgets".format(LIBNAME),
        "{}.gui.widgets.items".format(LIBNAME),
        "{}.gui.widgets.variableexplorer".format(LIBNAME),
    ],
    data_files=list_data,
    include_package_data=True,
    description="Plotpy is a library which results from merge of guidata and guiqwt.",
    long_description=open(os.path.join(os.path.dirname(__file__), "README")).read(),
    license="CECILL-2.1",
    platforms="ALL",
    setup_requires=["cython>=0.29", "numpy"],
)
