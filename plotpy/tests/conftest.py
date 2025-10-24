# content of conftest.py

import gc
import os

import guidata
import h5py
import numpy
import PIL
import pytest
import qtpy
import qwt
import scipy
import tifffile
from guidata.config import ValidationMode, set_validation_mode
from guidata.env import execenv
from guidata.utils.gitreport import format_git_info_for_pytest, get_git_info_for_modules

import plotpy

# Set validation mode to STRICT for the sigima package
set_validation_mode(ValidationMode.STRICT)

# Turn on unattended mode for executing tests without user interaction
execenv.unattended = True
execenv.verbose = "quiet"


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--show-windows",
        action="store_true",
        default=False,
        help="Display Qt windows during tests (disables QT_QPA_PLATFORM=offscreen)",
    )


def pytest_configure(config):
    """Configure pytest based on command line options."""
    if config.option.durations is None:
        config.option.durations = 10  # Default to showing 10 slowest tests
    config.addinivalue_line(
        "markers",
        "requires_display: mark test as requiring a display "
        "(skipped in offscreen mode)",
    )
    if not config.getoption("--show-windows"):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_runtest_setup(item):
    """Run setup before each test."""
    if "requires_display" in item.keywords:
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
            pytest.skip("Skipped in offscreen mode (requires display)")


@pytest.fixture(scope="session", autouse=True)
def disable_gc_for_tests():
    """Disable garbage collection for all tests in the session."""
    # Important note:
    # ---------------
    # We need to disable garbage collection for all tests in the session because
    # this test suite is not representative of a typical application.
    # The high level of stress on the garbage collector can lead to false positives
    # in tests that rely on reference counting or finalization.
    # In a typical application, the garbage collector should be left enabled.

    gc.disable()
    yield
    gc.enable()


def pytest_report_header(config):
    """Add additional information to the pytest report header."""
    qtbindings_version = qtpy.PYSIDE_VERSION
    if qtbindings_version is None:
        qtbindings_version = qtpy.PYQT_VERSION
    infolist = [
        f"PlotPy {plotpy.__version__}",
        f"  guidata {guidata.__version__}, PythonQwt {qwt.__version__}, "
        f"{qtpy.API_NAME} {qtbindings_version} [Qt version: {qtpy.QT_VERSION}]",
        f"  NumPy {numpy.__version__}, SciPy {scipy.__version__}, "
        f"h5py {h5py.__version__}, Pillow {PIL.__version__}, "
        f"tifffile {tifffile.__version__}",
    ]

    # Git information for all modules using the gitreport module
    modules_config = [
        ("PlotPy", plotpy, "."),  # PlotPy uses current directory
        ("guidata", guidata, None),
    ]
    git_repos = get_git_info_for_modules(modules_config)
    git_info_lines = format_git_info_for_pytest(git_repos, "PlotPy")
    if git_info_lines:
        infolist.extend(git_info_lines)

    return infolist
