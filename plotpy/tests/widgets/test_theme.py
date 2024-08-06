# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see guidata/LICENSE for details)

"""
Test dark/light theme switching
"""

from __future__ import annotations

import sys
from typing import Literal

import pytest
from guidata import qthelpers as qth
from guidata.tests.widgets.test_theme import TestWidget as GuidataTestWidget
from qtpy import QtWidgets as QW

from plotpy.builder import make
from plotpy.config import update_plotpy_color_mode
from plotpy.plot import PlotOptions, PlotWidget
from plotpy.tests import data as ptd


class TestWidget(GuidataTestWidget):
    """Testing color mode switching for PlotPy and guidata widgets"""

    SIZE = (1400, 600)

    def __init__(self, default: Literal["light", "dark", "auto"] = qth.AUTO) -> None:
        self.plot_widget: PlotWidget | None = None
        super().__init__(default=default)

    def setup_widgets(self):
        """Setup widgets"""
        super().setup_widgets()
        options = PlotOptions(type="image", show_contrast=True)
        self.plot_widget = widget = PlotWidget(self, options=options)
        plot = self.plot_widget.get_plot()
        item = make.image(ptd.gen_image4(300, 200))
        plot.add_item(item)
        plot.set_active_item(item, select=False)
        widget.setSizePolicy(QW.QSizePolicy.Expanding, QW.QSizePolicy.Expanding)
        self.grid_layout.addWidget(widget, 1, 2)

    def change_color_mode(self, mode: str) -> None:
        """Change color mode"""
        super().change_color_mode(mode)
        update_plotpy_color_mode()


@pytest.mark.skipif(reason="Not suitable for automated testing")
def test_dark_light_themes(
    default: Literal["light", "dark", "auto"] | None = None,
) -> None:
    """Test dark/light theme switching"""
    with qth.qt_app_context(exec_loop=True):
        widget = TestWidget(default=qth.AUTO if default is None else default)
        widget.show()


if __name__ == "__main__":
    test_dark_light_themes(None if len(sys.argv) < 2 else sys.argv[1])
