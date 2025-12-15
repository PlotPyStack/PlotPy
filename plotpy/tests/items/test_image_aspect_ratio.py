# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Image and shapes with unlock aspect ratio test"""

# guitest: show

from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv


def test_image_aspect_ratio():
    """Testing image and shapes with unlock aspect ratio"""
    with qt_app_context(exec_loop=True):
        data = ptd.gen_image4(500, 700)
        image = make.image(data)
        image.hide()
        circle = make.circle(200, 200, 500, 300)
        circle.select()
        txt = "This test is considered passed if<br>the ellipse is drawn properly."
        win = ptv.show_items(
            [image, circle, make.label(txt, "C", (0, 0), "C")],
            plot_type="image",
            wintitle=test_image_aspect_ratio.__doc__,
            lock_aspect_ratio=False,
        )
        win.plot_widget.plot.set_aspect_ratio(0.25)


if __name__ == "__main__":
    test_image_aspect_ratio()
