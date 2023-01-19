# -*- coding: utf-8 -*-

"""
userconfig

Application settings example

This should create a file named ".app.ini" in your HOME directory containing:

[main]
version = 1.0.0

[a]
b/f = 1.0
"""

from guidata.dataset.dataitems import FloatItem
from guidata.dataset.datatypes import DataSet

from plotpy.utils.config import userconfig


class DS(DataSet):
    f = FloatItem("F", 1.0)


ds = DS("")
uc = userconfig.UserConfig({})
uc.set_application("app", "1.0.0")
ds.write_config(uc, "a", "b")

print("Settings saved in: ", uc.filename())
