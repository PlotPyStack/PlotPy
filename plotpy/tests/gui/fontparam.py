# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""FontParam test"""


from plotpy.widgets.styles.base import FontParam

SHOW = False  # Do not show test in GUI-based test launcher


def test():

    import plotpy.widgets

    _app = plotpy.widgets.qapplication()

    fp = FontParam()
    fp.edit()
    fp.edit()


if __name__ == "__main__":
    test()
