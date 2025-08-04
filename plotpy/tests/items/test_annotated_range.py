# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Testing `AnnotatedXRange` and `AnnotatedYRange` items"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import vistools as ptv


def test_annotated_range_selection():
    """Test AnnotatedXRange and AnnotatedYRange items"""
    x = np.linspace(-5, 15, 200)
    y = np.sin(np.sin(np.sin(x))) + 0.5
    with qt_app_context(exec_loop=True):
        items = [
            make.curve(x, y, color="b"),
            make.annotated_xrange(x0=-5, x1=0.0, title="X Range Selection"),
            make.annotated_yrange(y0=-0.2, y1=0.1, title="Y Range Selection"),
        ]
        _win = ptv.show_items(
            items,
            wintitle=test_annotated_range_selection.__doc__,
            title="Annotated Range Selection",
            plot_type="curve",
            disable_readonly_for_items=False,
        )


if __name__ == "__main__":
    test_annotated_range_selection()
