# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Contrast tool test"""

# guitest: show

import os
import os.path as osp

from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.tests.data import gen_image1


def __create_dialog_with_contrast(item):
    """Create plot dialog with contrast panel

    Args:
        Item: item to be added to the plot
    """
    win = make.dialog(
        edit=False,
        toolbar=True,
        wintitle="Contrast test",
        show_contrast=True,
        type="image",
        size=(600, 600),
    )
    plot = win.get_plot()
    plot.add_item(item)
    plot.set_active_item(item)
    item.unselect()
    win.show()
    return win


def test_contrast1():
    """Contrast test 1"""
    with qt_app_context(exec_loop=True):
        item = make.image(filename=get_path("brain.png"), colormap="gray")
        win = __create_dialog_with_contrast(item)
        fname = "contrast.png"
        try:
            win.get_plot().save_widget(fname)
        except IOError:
            # Skipping this part of the test
            # because user has no write permission on current directory
            pass
        if execenv.unattended and osp.isfile(fname):
            os.unlink(fname)


def test_contrast2():
    """Contrast test 2

    Test if level histogram is really removed when the associated image is removed from
    the plot (the validation is not automatic)
    """
    with qt_app_context(exec_loop=True):
        item1 = make.image(filename=get_path("brain.png"), colormap="gray")
        win = __create_dialog_with_contrast(item1)
        plot = win.get_plot()
        plot.del_item(item1)
        item2 = make.image(gen_image1())
        plot.add_item(item2)
        plot.set_active_item(item2)


if __name__ == "__main__":
    # test_contrast1()
    test_contrast2()
