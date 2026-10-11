# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Tests for supported Python versions in package metadata."""

from __future__ import annotations

from importlib.metadata import metadata

import pytest


@pytest.mark.parametrize("minor", range(9, 16))
def test_python_classifiers(minor):
    """Check that package metadata advertises every supported Python version."""
    classifiers = metadata("PlotPy").get_all("Classifier")
    assert f"Programming Language :: Python :: 3.{minor}" in classifiers
