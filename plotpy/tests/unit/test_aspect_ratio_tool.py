from __future__ import annotations

from guidata.qthelpers import exec_dialog, qt_app_context

from plotpy.interfaces.items import IImageItemType
from plotpy.tests.unit.utils import create_window
from plotpy.tools import AspectRatioTool


def test_aspect_ratio_tool():
    """Test the aspect ratio tool."""
    with qt_app_context(exec_loop=False):
        win, tool = create_window(AspectRatioTool, active_item_type=IImageItemType)
        plot = win.manager.get_plot()

        initial_aspect_ratio: float = plot.get_aspect_ratio()

        new_ratio = 0.5

        plot.set_aspect_ratio(new_ratio)
        tool.edit_aspect_ratio()
        assert plot.get_aspect_ratio() == new_ratio

        plot.set_aspect_ratio(initial_aspect_ratio)
        tool.edit_aspect_ratio()
        assert plot.get_aspect_ratio() == initial_aspect_ratio

        tool.lock_aspect_ratio(True)
        assert plot.lock_aspect_ratio is True
        tool.lock_aspect_ratio(False)
        assert plot.lock_aspect_ratio is False

        exec_dialog(win)


if __name__ == "__main__":
    test_aspect_ratio_tool()
