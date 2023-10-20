# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test PlotBuilder shape factory methods"""

import numpy as np
import pytest

from plotpy.builder import make
from plotpy.tests import get_path
from plotpy.tests.unit.test_builder_curve import show_items_qtbot

DEFAULT_ARGS = {
    make.segment: [0.0, 0.0, 1.0, 1.0],
    make.rectangle: [0.0, 0.0, 1.0, 1.0],
    make.circle: [0.0, 0.0, 1.0, 1.0],
    make.ellipse: [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
}


def _make_standard_shape(
    method,
    title: str = None,
):
    """Make annotation"""
    args = DEFAULT_ARGS[method]
    return method(
        *args,
        title=title,
    )


@pytest.mark.parametrize(
    "method",
    [make.segment, make.rectangle, make.circle, make.ellipse],
)
def test_builder_standard_shape(qtbot, method):
    items = []
    items.append(_make_standard_shape(method, title="title"))
    show_items_qtbot(qtbot, items)


def test_builder_polygon(qtbot):
    items = []
    x = np.linspace(0, 1, 10)
    y = x**2
    for closed in [True, False]:
        items.append(make.polygon(x, y, closed=closed, title="title"))
    show_items_qtbot(qtbot, items)


def test_builder_svgshape(qtbot):
    items = []
    svg_path = get_path("svg_target.svg")
    with open(svg_path, "rb") as f:
        svg_data = f.read()
    x = np.linspace(0, 1, 10)
    y = x**2
    for shape_str in ("circle", "rectangle", "square"):
        for data_or_path in (svg_data, svg_path):
            items.append(
                make.svg(shape_str, data_or_path, 0.0, 0.0, 1.0, 1.0, title="title")
            )
    show_items_qtbot(qtbot, items)
