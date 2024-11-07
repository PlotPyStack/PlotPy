# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test PlotBuilder annotation factory methods"""

import numpy as np
import pytest
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests.unit.test_builder_curve import show_items_qtbot

DEFAULT_ARGS = {
    make.annotated_point: [0.0, 0.0],
    make.annotated_segment: [0.0, 0.0, 1.0, 1.0],
    make.annotated_rectangle: [0.0, 0.0, 1.0, 1.0],
    make.annotated_circle: [0.0, 0.0, 1.0, 1.0],
    make.annotated_ellipse: [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
    make.annotated_polygon: np.array(
        [
            [150.0, 330.0],
            [270.0, 520.0],
            [470.0, 480.0],
            [520.0, 360.0],
            [460.0, 200.0],
            [250.0, 240.0],
        ]
    ),
}


def _make_annotation(
    method,
    title: str = None,
    subtitle: str = None,
    show_label: bool = None,
    show_computations: bool = None,
    show_subtitle: bool = None,
    format: str = None,
    uncertainty: float = None,
    transform_matrix: np.ndarray = None,
    readonly: bool = None,
    private: bool = None,
):
    """Make annotation"""
    args = DEFAULT_ARGS[method]
    kwargs = dict(
        title=title,
        subtitle=subtitle,
        show_label=show_label,
        show_computations=show_computations,
        show_subtitle=show_subtitle,
        format=format,
        uncertainty=uncertainty,
        transform_matrix=transform_matrix,
        readonly=readonly,
        private=private,
    )
    if isinstance(args, np.ndarray):
        return method(args, **kwargs)
    return method(*args, **kwargs)


@pytest.mark.parametrize(
    "method",
    [
        make.annotated_point,
        make.annotated_segment,
        make.annotated_rectangle,
        make.annotated_circle,
        make.annotated_ellipse,
        make.annotated_polygon,
    ],
)
def test_builder_annotation_params(method):
    """Test PlotBuilder annotation factory method parameters"""
    with qt_app_context(exec_loop=False):
        items = []
        for show_label in [True, False]:
            items.append(
                _make_annotation(
                    method,
                    title="title",
                    subtitle="subtitle",
                    show_label=show_label,
                )
            )
        for show_computations in [True, False]:
            items.append(_make_annotation(method, show_computations=show_computations))
        for show_subtitle in [True, False]:
            items.append(_make_annotation(method, show_subtitle=show_subtitle))
        for format in ["%f", "%e"]:
            items.append(_make_annotation(method, format=format))
        for uncertainty in [0.0, 1.0]:
            items.append(_make_annotation(method, uncertainty=uncertainty))
        for transform_matrix in [None, np.identity(3)]:
            items.append(_make_annotation(method, transform_matrix=transform_matrix))
        for readonly in [True, False]:
            items.append(_make_annotation(method, readonly=readonly))
        for private in [True, False]:
            items.append(_make_annotation(method, private=private))
        show_items_qtbot(items)
