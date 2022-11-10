# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Test in text mode"""

SHOW = False  # Do not show test in GUI-based test launcher

from plotpy.core.dataset.datatypes import DataSet
from plotpy.core.dataset.dataitems import FloatItem, IntItem


class Parameters(DataSet):
    height = FloatItem("Height", min=1, max=250, help="height in cm")
    width = FloatItem("Width", min=1, max=250, help="width in cm")
    number = IntItem("Number", min=3, max=20)


if __name__ == "__main__":
    p = Parameters()
    p.text_edit()
    print(p)
