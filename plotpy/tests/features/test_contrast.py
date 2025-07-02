# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Contrast tool test"""

# guitest: show

import os
import os.path as osp

import numpy as np
from guidata.env import execenv
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.tests.data import gen_image1, gen_image4


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


def test_contrast3():
    """Contrast test 3

    Test if level histogram works properly when the image has a really high dynamic
    range (the validation is not automatic)
    """
    with qt_app_context(exec_loop=True):
        data = gen_image4(512, 512)
        data = np.fft.fftshift(np.fft.fft2(data)).real
        item = make.image(data, colormap="viridis", eliminate_outliers=2.0)
        win = __create_dialog_with_contrast(item)


if __name__ == "__main__":
    test_contrast1()
    test_contrast2()
    test_contrast3()
