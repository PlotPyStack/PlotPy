# -*- coding: utf-8 -*-
#
# Copyright © 2010-2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
SIFT, the Signal and Image Filtering Tool
Simple signal and image processing application based on plotpy
"""

# guitest: show

import pytest

from sift.app import run


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_sift():
    """run method"""
    run()


if __name__ == "__main__":
    test_sift()
