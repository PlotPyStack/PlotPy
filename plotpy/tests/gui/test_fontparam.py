# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""FontParam test"""

from guidata.qthelpers import qt_app_context

from plotpy.styles.base import FontParam


def test_fontparam():
    with qt_app_context(exec_loop=True):
        fp = FontParam()
        fp.edit()
        fp.edit()


if __name__ == "__main__":
    test_fontparam()
