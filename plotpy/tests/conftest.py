# content of conftest.py

import guidata
import h5py
import numpy
import PIL
import qtpy
import qwt
import scipy
import tifffile
from guidata.env import execenv

import plotpy

# Turn on unattended mode for executing tests without user interaction
execenv.unattended = True
execenv.verbose = "quiet"


def pytest_report_header(config):
    """Add additional information to the pytest report header."""
    qtbindings_version = qtpy.PYSIDE_VERSION
    if qtbindings_version is None:
        qtbindings_version = qtpy.PYQT_VERSION
    return [
        f"PlotPy {plotpy.__version__}, guidata {guidata.__version__}, "
        f"PythonQwt {qwt.__version__}, "
        f"{qtpy.API_NAME} {qtbindings_version} [Qt version: {qtpy.QT_VERSION}]",
        f"NumPy {numpy.__version__}, SciPy {scipy.__version__}, "
        f"h5py {h5py.__version__}, "
        f"Pillow {PIL.__version__}, tifffile {tifffile.__version__}",
    ]
