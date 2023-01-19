# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Little translation test"""


from plotpy.config import _

SHOW = False  # Do not show test in GUI-based test launcher

translations = (_("Some required entries are incorrect"),)

if __name__ == "__main__":
    for text in translations:
        print(text)
