# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""FontParam test"""

from guidata.qthelpers import qt_app_context

from plotpy.core.styles.base import FontParam


def test_fontparam():
    with qt_app_context(exec_loop=True):
        fp = FontParam()
        fp.edit()
        fp.edit()


if __name__ == "__main__":
    test_fontparam()
