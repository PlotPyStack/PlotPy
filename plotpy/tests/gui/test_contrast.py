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


def test_contrast():
    """Test"""
    # -- Create QApplication
    with qt_app_context(exec_loop=True):
        filename = osp.join(osp.dirname(__file__), "brain.png")
        image = make.image(filename=filename, title="Original", colormap="gray")
        win = make.dialog(
            edit=False,
            toolbar=True,
            wintitle="Contrast test",
            show_contrast=True,
            type="image",
        )
        plot = win.manager.get_plot()
        plot.add_item(image)
        win.resize(600, 600)
        win.show()
        fname = "contrast.png"
        try:
            plot.save_widget(fname)
        except IOError:
            # Skipping this part of the test
            # because user has no write permission on current directory
            pass
        if execenv.unattended and osp.isfile(fname):
            os.unlink(fname)


if __name__ == "__main__":
    test_contrast()
