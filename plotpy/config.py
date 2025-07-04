# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Configuration
-------------

Handle *plotpy* module configuration
(options, images and icons)
"""

from __future__ import annotations

import os.path as osp
import warnings
from typing import Literal

from guidata import qthelpers as qth
from guidata.configtools import add_image_module_path, get_translation
from guidata.userconfig import UserConfig


def get_main_colors() -> tuple[str, str]:
    """Return main foreground and background colors depending on dark mode"""
    is_dark = qth.is_dark_theme()
    return "white" if is_dark else "#000000", "#222222" if is_dark else "white"


MAIN_FG_COLOR, MAIN_BG_COLOR = get_main_colors()


def make_title(basename, count):
    """Make item title with *basename* and *count* number"""
    return "{} {}{:d}".format(basename, _("#"), count)


APP_PATH = osp.dirname(__file__)
add_image_module_path("plotpy", "data/icons")
_ = get_translation("plotpy")


def get_plotpy_defaults() -> dict[str, int | float | str | bool]:
    """Return default configuration values"""
    global MAIN_FG_COLOR, MAIN_BG_COLOR
    return {
        "plot": {
            "selection/distance": 6,
            "antialiasing": False,
            "title/font/size": 12,
            "title/font/bold": False,
            "selected_curve_symbol/marker": "Rect",
            "selected_curve_symbol/edgecolor": "#a0a0a4",
            "selected_curve_symbol/facecolor": MAIN_FG_COLOR,
            "selected_curve_symbol/alpha": 0.3,
            "selected_curve_symbol/size": 7,
            # Default parameters for plot axes
            "axis/title": "",
            "axis/unit": "",
            "axis/color": MAIN_FG_COLOR,
            "axis/title_font/size": 8,
            "axis/title_font/family": "default",
            "axis/title_font/bold": False,
            "axis/title_font/italic": False,
            "axis/ticks_font/size": 8,
            "axis/ticks_font/family": "default",
            "axis/ticks_font/bold": False,
            "axis/ticks_font/italic": False,
            # Default parameters for X/Y image axes
            "image_axis/title": "",
            "image_axis/unit": _("pixels"),
            "image_axis/color": MAIN_FG_COLOR,
            "image_axis/title_font/size": 8,
            "image_axis/title_font/family": "default",
            "image_axis/title_font/bold": False,
            "image_axis/title_font/italic": False,
            "image_axis/ticks_font/size": 8,
            "image_axis/ticks_font/family": "default",
            "image_axis/ticks_font/bold": False,
            "image_axis/ticks_font/italic": False,
            # Default parameters for color scale
            "color_axis/title": _("Intensity"),
            "color_axis/unit": _("lsb"),
            "color_axis/color": MAIN_FG_COLOR,
            "color_axis/title_font/size": 8,
            "color_axis/title_font/family": "default",
            "color_axis/title_font/bold": False,
            "color_axis/title_font/italic": False,
            "color_axis/ticks_font/size": 8,
            "color_axis/ticks_font/family": "default",
            "color_axis/ticks_font/bold": False,
            "color_axis/ticks_font/italic": False,
            "grid/background": MAIN_BG_COLOR,
            "grid/maj_xenabled": True,
            "grid/maj_yenabled": True,
            "grid/maj_line/color": "#808080",
            "grid/maj_line/width": 1,
            "grid/maj_line/style": "DotLine",
            "grid/min_xenabled": True,
            "grid/min_yenabled": True,
            "grid/min_line/color": "#454545" if qth.is_dark_theme() else "#eaeaea",
            "grid/min_line/width": 1,
            "grid/min_line/style": "DotLine",
            "marker/curve/symbol/marker": "Rect",
            "marker/curve/symbol/edgecolor": "#0000ff",
            "marker/curve/symbol/facecolor": "#00ffff",
            "marker/curve/symbol/alpha": 0.8,
            "marker/curve/symbol/size": 7,
            "marker/curve/text/font/size": 8,
            "marker/curve/text/font/family": "default",
            "marker/curve/text/font/bold": False,
            "marker/curve/text/font/italic": False,
            "marker/curve/text/textcolor": "#000000",
            "marker/curve/text/background_color": "#ffffff",
            "marker/curve/text/background_alpha": 0.8,
            "marker/curve/line/style": "SolidLine",
            "marker/curve/line/color": MAIN_FG_COLOR,
            "marker/curve/line/width": 0,
            "marker/curve/sel_symbol/marker": "Rect",
            "marker/curve/sel_symbol/edgecolor": "#0000ff",
            "marker/curve/sel_symbol/facecolor": "#00ffff",
            "marker/curve/sel_symbol/alpha": 0.8,
            "marker/curve/sel_symbol/size": 7,
            "marker/curve/sel_text/font/size": 8,
            "marker/curve/sel_text/font/family": "default",
            "marker/curve/sel_text/font/bold": False,
            "marker/curve/sel_text/font/italic": False,
            "marker/curve/sel_text/textcolor": "#000000",
            "marker/curve/sel_text/background_color": "#ffffff",
            "marker/curve/sel_text/background_alpha": 0.8,
            "marker/curve/sel_line/style": "SolidLine",
            "marker/curve/sel_line/color": MAIN_FG_COLOR,
            "marker/curve/sel_line/width": 0,
            "marker/curve/markerstyle": "NoLine",
            "marker/curve/spacing": 7,
            "marker/cross/symbol/marker": "Cross",
            "marker/cross/symbol/edgecolor": MAIN_FG_COLOR,
            "marker/cross/symbol/facecolor": "#ff0000",
            "marker/cross/symbol/alpha": 1.0,
            "marker/cross/symbol/size": 8,
            "marker/cross/text/font/family": "default",
            "marker/cross/text/font/size": 8,
            "marker/cross/text/font/bold": False,
            "marker/cross/text/font/italic": False,
            "marker/cross/text/textcolor": "#000000",
            "marker/cross/text/background_color": "#ffffff",
            "marker/cross/text/background_alpha": 0.8,
            "marker/cross/line/style": "DashLine",
            "marker/cross/line/color": "#ffff00",
            "marker/cross/line/width": 1,
            "marker/cross/sel_symbol/marker": "Cross",
            "marker/cross/sel_symbol/edgecolor": MAIN_FG_COLOR,
            "marker/cross/sel_symbol/facecolor": "#ff0000",
            "marker/cross/sel_symbol/alpha": 1.0,
            "marker/cross/sel_symbol/size": 8,
            "marker/cross/sel_text/font/family": "default",
            "marker/cross/sel_text/font/size": 8,
            "marker/cross/sel_text/font/bold": False,
            "marker/cross/sel_text/font/italic": False,
            "marker/cross/sel_text/textcolor": "#000000",
            "marker/cross/sel_text/background_color": "#ffffff",
            "marker/cross/sel_text/background_alpha": 0.8,
            "marker/cross/sel_line/style": "DashLine",
            "marker/cross/sel_line/color": "#ffff00",
            "marker/cross/sel_line/width": 1,
            "marker/cross/markerstyle": "Cross",
            "marker/cross/spacing": 7,
            "marker/selectpoint/symbol/marker": "Rect",
            "marker/selectpoint/symbol/edgecolor": "#0000ff",
            "marker/selectpoint/symbol/facecolor": "#00ffff",
            "marker/selectpoint/symbol/alpha": 0.8,
            "marker/selectpoint/symbol/size": 7,
            "marker/selectpoint/text/font/size": 8,
            "marker/selectpoint/text/font/family": "default",
            "marker/selectpoint/text/font/bold": False,
            "marker/selectpoint/text/font/italic": False,
            "marker/selectpoint/text/textcolor": "#000000",
            "marker/selectpoint/text/background_color": "#ffffff",
            "marker/selectpoint/text/background_alpha": 0.8,
            "marker/selectpoint/line/style": "SolidLine",
            "marker/selectpoint/line/color": MAIN_FG_COLOR,
            "marker/selectpoint/line/width": 0,
            "marker/selectpoint/sel_symbol/marker": "Rect",
            "marker/selectpoint/sel_symbol/edgecolor": "#0000ff",
            "marker/selectpoint/sel_symbol/facecolor": "#00ffff",
            "marker/selectpoint/sel_symbol/alpha": 0.8,
            "marker/selectpoint/sel_symbol/size": 7,
            "marker/selectpoint/sel_text/font/size": 8,
            "marker/selectpoint/sel_text/font/family": "default",
            "marker/selectpoint/sel_text/font/bold": False,
            "marker/selectpoint/sel_text/font/italic": False,
            "marker/selectpoint/sel_text/textcolor": "#000000",
            "marker/selectpoint/sel_text/background_color": "#ffffff",
            "marker/selectpoint/sel_text/background_alpha": 0.8,
            "marker/selectpoint/sel_line/style": "SolidLine",
            "marker/selectpoint/sel_line/color": MAIN_FG_COLOR,
            "marker/selectpoint/sel_line/width": 0,
            "marker/selectpoint/markerstyle": "NoLine",
            "marker/selectpoint/spacing": 7,
            "marker/cursor/line/style": "SolidLine",
            "marker/cursor/line/color": "#ff9393",
            "marker/cursor/line/width": 1.0,
            "marker/cursor/symbol/marker": "Ellipse",
            "marker/cursor/symbol/size": 7,
            "marker/cursor/symbol/edgecolor": MAIN_BG_COLOR,
            "marker/cursor/symbol/facecolor": "#ff9393",
            "marker/cursor/symbol/alpha": 1.0,
            "marker/cursor/text/font/size": 8,
            "marker/cursor/text/font/family": "default",
            "marker/cursor/text/font/bold": False,
            "marker/cursor/text/font/italic": False,
            "marker/cursor/text/textcolor": "#ff9393",
            "marker/cursor/text/background_color": "#ffffff",
            "marker/cursor/text/background_alpha": 0.8,
            "marker/cursor/sel_line/style": "SolidLine",
            "marker/cursor/sel_line/color": "#ff0000",
            "marker/cursor/sel_line/width": 2.0,
            "marker/cursor/sel_symbol/marker": "Ellipse",
            "marker/cursor/sel_symbol/size": 9,
            "marker/cursor/sel_symbol/edgecolor": MAIN_BG_COLOR,
            "marker/cursor/sel_symbol/facecolor": "#ff0000",
            "marker/cursor/sel_symbol/alpha": 0.9,
            "marker/cursor/sel_text/font/size": 8,
            "marker/cursor/sel_text/font/family": "default",
            "marker/cursor/sel_text/font/bold": True,
            "marker/cursor/sel_text/font/italic": False,
            "marker/cursor/sel_text/textcolor": "#ff0000",
            "marker/cursor/sel_text/background_color": "#ffffff",
            "marker/cursor/sel_text/background_alpha": 0.8,
            "marker/cursor/markerstyle": "NoLine",
            "marker/cursor/spacing": 7,
            "shape/drag/line/style": "SolidLine",
            "shape/drag/line/color": "#ffff00",
            "shape/drag/line/width": 1,
            "shape/drag/fill/style": "SolidPattern",
            "shape/drag/fill/color": MAIN_BG_COLOR,
            "shape/drag/fill/alpha": 0.1,
            "shape/drag/symbol/marker": "Rect",
            "shape/drag/symbol/size": 3,
            "shape/drag/symbol/edgecolor": "#ffff00",
            "shape/drag/symbol/facecolor": "#ffff00",
            "shape/drag/symbol/alpha": 1.0,
            "shape/drag/sel_line/style": "SolidLine",
            "shape/drag/sel_line/color": "#00ff00",
            "shape/drag/sel_line/width": 1,
            "shape/drag/sel_fill/style": "SolidPattern",
            "shape/drag/sel_fill/color": MAIN_BG_COLOR,
            "shape/drag/sel_fill/alpha": 0.1,
            "shape/drag/sel_symbol/marker": "Rect",
            "shape/drag/sel_symbol/size": 9,
            "shape/drag/sel_symbol/edgecolor": "#00aa00",
            "shape/drag/sel_symbol/facecolor": "#00ff00",
            "shape/drag/sel_symbol/alpha": 0.7,
            "shape/imageborder/line/style": "NoPen",
            "shape/imageborder/line/color": "#a0a0a4",
            "shape/imageborder/line/width": 0,
            "shape/imageborder/fill/style": "NoBrush",
            "shape/imageborder/fill/color": "#000000",
            "shape/imageborder/fill/alpha": 0.0,
            "shape/imageborder/fill/angle": 0.0,
            "shape/imageborder/fill/sx": 1.0,
            "shape/imageborder/fill/sy": 1.0,
            "shape/imageborder/symbol/marker": "NoSymbol",
            "shape/imageborder/symbol/size": 7,
            "shape/imageborder/symbol/edgecolor": "#a0a0a4",
            "shape/imageborder/symbol/facecolor": MAIN_FG_COLOR,
            "shape/imageborder/symbol/alpha": 0.3,
            "shape/imageborder/sel_line/style": "SolidLine",
            "shape/imageborder/sel_line/color": "#a0a0a4",
            "shape/imageborder/sel_line/width": 3,
            "shape/imageborder/sel_symbol/marker": "Rect",
            "shape/imageborder/sel_symbol/size": 7,
            "shape/imageborder/sel_symbol/edgecolor": "#a0a0a4",
            "shape/imageborder/sel_symbol/facecolor": MAIN_FG_COLOR,
            "shape/imageborder/sel_symbol/alpha": 0.8,
            "shape/imageborder/sel_fill/style": "NoBrush",
            "shape/imageborder/sel_fill/color": "#a0a0a4",
            "shape/imageborder/sel_fill/alpha": 0.5,
            "shape/imageborder/sel_fill/angle": 0.0,
            "shape/imageborder/sel_fill/sx": 1.0,
            "shape/imageborder/sel_fill/sy": 1.0,
            "shape/imagefilter/line/style": "SolidLine",
            "shape/imagefilter/line/color": "#ffff00",
            "shape/imagefilter/line/width": 1,
            "shape/imagefilter/sel_line/style": "SolidLine",
            "shape/imagefilter/sel_line/color": "#00ffff",
            "shape/imagefilter/sel_line/width": 2,
            "shape/imagefilter/fill/style": "NoBrush",
            "shape/imagefilter/fill/color": MAIN_BG_COLOR,
            "shape/imagefilter/fill/alpha": 0.0,
            "shape/imagefilter/sel_fill/style": "SolidPattern",
            "shape/imagefilter/sel_fill/color": MAIN_BG_COLOR,
            "shape/imagefilter/sel_fill/alpha": 0.2,
            "shape/imagefilter/symbol/marker": "Rect",
            "shape/imagefilter/symbol/size": 3,
            "shape/imagefilter/symbol/edgecolor": "#ffff00",
            "shape/imagefilter/symbol/facecolor": "#ffff00",
            "shape/imagefilter/symbol/alpha": 1.0,
            "shape/imagefilter/sel_symbol/marker": "Ellipse",
            "shape/imagefilter/sel_symbol/size": 7,
            "shape/imagefilter/sel_symbol/edgecolor": "#0000ff",
            "shape/imagefilter/sel_symbol/facecolor": "#00ffff",
            "shape/imagefilter/sel_symbol/alpha": 0.8,
            # Contour ------------------------------------------------------------------
            "shape/contour/line/style": "SolidLine",
            "shape/contour/line/color": "#000000",
            "shape/contour/line/width": 1,
            "shape/contour/fill/style": "NoBrush",
            "shape/contour/symbol/marker": "NoSymbol",
            "shape/contour/sel_line/style": "SolidLine",
            "shape/contour/sel_line/color": "#00ff00",
            "shape/contour/sel_line/width": 1,
            "shape/contour/sel_fill/style": "SolidPattern",
            "shape/contour/sel_fill/color": MAIN_BG_COLOR,
            "shape/contour/sel_fill/alpha": 0.1,
            "shape/contour/sel_symbol/marker": "NoSymbol",
            # RectZoom -----------------------------------------------------------------
            "shape/rectzoom/line/style": "SolidLine",
            "shape/rectzoom/line/color": "#bbbbbb",
            "shape/rectzoom/line/width": 2,
            # not used -- start
            "shape/rectzoom/sel_line/style": "SolidLine",
            "shape/rectzoom/sel_line/color": "#00ff00",
            "shape/rectzoom/sel_line/width": 2,
            # not used -- end
            "shape/rectzoom/fill/color": "#ffff00",
            "shape/rectzoom/fill/style": "SolidPattern",
            "shape/rectzoom/fill/alpha": 0.1,
            # not used -- start
            "shape/rectzoom/symbol/marker": "NoSymbol",
            "shape/rectzoom/symbol/size": 0,
            "shape/rectzoom/symbol/edgecolor": MAIN_FG_COLOR,
            "shape/rectzoom/symbol/facecolor": "#ffff00",
            "shape/rectzoom/symbol/alpha": 1.0,
            "shape/rectzoom/sel_symbol/marker": "Rect",
            "shape/rectzoom/sel_symbol/size": 5,
            "shape/rectzoom/sel_symbol/edgecolor": MAIN_FG_COLOR,
            "shape/rectzoom/sel_symbol/facecolor": "#ffff00",
            "shape/rectzoom/sel_symbol/alpha": 1.0,
            # not used -- end
            "shape/axes/border/line/style": "SolidLine",
            "shape/axes/border/line/color": "#ff00ff",
            "shape/axes/border/line/width": 1,
            "shape/axes/border/sel_line/style": "SolidLine",
            "shape/axes/border/sel_line/color": "#ff00ff",
            "shape/axes/border/sel_line/width": 2,
            "shape/axes/border/fill/style": "NoBrush",
            "shape/axes/border/fill/color": "#ff00ff",
            "shape/axes/border/fill/alpha": 0.0,
            "shape/axes/border/sel_fill/style": "SolidPattern",
            "shape/axes/border/sel_fill/color": "#ff00ff",
            "shape/axes/border/sel_fill/alpha": 0.3,
            "shape/axes/border/symbol/marker": "NoSymbol",
            "shape/axes/border/symbol/size": 0,
            "shape/axes/border/symbol/edgecolor": MAIN_FG_COLOR,
            "shape/axes/border/symbol/facecolor": "#ffff00",
            "shape/axes/border/symbol/alpha": 1.0,
            "shape/axes/border/sel_symbol/marker": "NoSymbol",
            "shape/axes/border/sel_symbol/size": 5,
            "shape/axes/border/sel_symbol/edgecolor": MAIN_FG_COLOR,
            "shape/axes/border/sel_symbol/facecolor": "#ffff00",
            "shape/axes/border/sel_symbol/alpha": 1.0,
            "shape/axes/arrow_size": 8,
            "shape/axes/arrow_angle": 30,
            "shape/axes/xarrow_pen/style": "SolidLine",
            "shape/axes/xarrow_pen/color": "#ff0000",
            "shape/axes/xarrow_pen/width": 1,
            "shape/axes/xarrow_brush/color": "#ff0000",
            "shape/axes/xarrow_brush/alpha": 0.2,
            "shape/axes/yarrow_pen/style": "SolidLine",
            "shape/axes/yarrow_pen/color": "#00ff00",
            "shape/axes/yarrow_pen/width": 1,
            "shape/axes/yarrow_brush/color": "#00ff00",
            "shape/axes/yarrow_brush/alpha": 0.2,
            "shape/image_stats/line/style": "DashLine",
            "shape/image_stats/line/color": "#ff88dc",
            "shape/image_stats/line/width": 1,
            "shape/image_stats/fill/style": "SolidPattern",
            "shape/image_stats/fill/color": MAIN_BG_COLOR,
            "shape/image_stats/fill/alpha": 0.1,
            "shape/image_stats/symbol/marker": "Rect",
            "shape/image_stats/symbol/size": 3,
            "shape/image_stats/symbol/edgecolor": "#ff55dc",
            "shape/image_stats/symbol/facecolor": "#ff88dc",
            "shape/image_stats/symbol/alpha": 0.6,
            "shape/image_stats/sel_line/style": "DashLine",
            "shape/image_stats/sel_line/color": "#ff00dc",
            "shape/image_stats/sel_line/width": 1,
            "shape/image_stats/sel_fill/style": "SolidPattern",
            "shape/image_stats/sel_fill/color": MAIN_BG_COLOR,
            "shape/image_stats/sel_fill/alpha": 0.1,
            "shape/image_stats/sel_symbol/marker": "Rect",
            "shape/image_stats/sel_symbol/size": 5,
            "shape/image_stats/sel_symbol/edgecolor": "#ff00dc",
            "shape/image_stats/sel_symbol/facecolor": "#ff88dc",
            "shape/image_stats/sel_symbol/alpha": 0.7,
            "shape/cross_section/line/style": "DotLine",
            "shape/cross_section/line/color": "#ff5555",
            "shape/cross_section/line/width": 1,
            "shape/cross_section/fill/style": "SolidPattern",
            "shape/cross_section/fill/color": MAIN_BG_COLOR,
            "shape/cross_section/fill/alpha": 0.1,
            "shape/cross_section/symbol/marker": "Cross",
            "shape/cross_section/symbol/size": 100,
            "shape/cross_section/symbol/edgecolor": "#00ffff",
            "shape/cross_section/symbol/facecolor": "#00ffff",
            "shape/cross_section/symbol/alpha": 0.6,
            "shape/cross_section/sel_line/style": "DotLine",
            "shape/cross_section/sel_line/color": "#ff0000",
            "shape/cross_section/sel_line/width": 1,
            "shape/cross_section/sel_fill/style": "SolidPattern",
            "shape/cross_section/sel_fill/color": MAIN_BG_COLOR,
            "shape/cross_section/sel_fill/alpha": 0.1,
            "shape/cross_section/sel_symbol/marker": "Cross",
            "shape/cross_section/sel_symbol/size": 10000,
            "shape/cross_section/sel_symbol/edgecolor": "#00ffff",
            "shape/cross_section/sel_symbol/facecolor": "#00ffff",
            "shape/cross_section/sel_symbol/alpha": 0.7,
            "shape/average_cross_section/line/style": "DotLine",
            "shape/average_cross_section/line/color": "#ff5555",
            "shape/average_cross_section/line/width": 1,
            "shape/average_cross_section/fill/style": "SolidPattern",
            "shape/average_cross_section/fill/color": MAIN_BG_COLOR,
            "shape/average_cross_section/fill/alpha": 0.1,
            "shape/average_cross_section/symbol/marker": "Diamond",
            "shape/average_cross_section/symbol/size": 7,
            "shape/average_cross_section/symbol/edgecolor": "#ff5555",
            "shape/average_cross_section/symbol/facecolor": "#ff5555",
            "shape/average_cross_section/symbol/alpha": 0.6,
            "shape/average_cross_section/sel_line/style": "DotLine",
            "shape/average_cross_section/sel_line/color": "#ff0000",
            "shape/average_cross_section/sel_line/width": 1,
            "shape/average_cross_section/sel_fill/style": "SolidPattern",
            "shape/average_cross_section/sel_fill/color": MAIN_BG_COLOR,
            "shape/average_cross_section/sel_fill/alpha": 0.1,
            "shape/average_cross_section/sel_symbol/marker": "Diamond",
            "shape/average_cross_section/sel_symbol/size": 9,
            "shape/average_cross_section/sel_symbol/edgecolor": "#aa0000",
            "shape/average_cross_section/sel_symbol/facecolor": "#ff0000",
            "shape/average_cross_section/sel_symbol/alpha": 0.7,
            "shape/mask/line/style": "DotLine",
            "shape/mask/line/color": "#5555ff",
            "shape/mask/line/width": 1,
            "shape/mask/fill/style": "SolidPattern",
            "shape/mask/fill/color": MAIN_BG_COLOR,
            "shape/mask/fill/alpha": 0.1,
            "shape/mask/symbol/marker": "Rect",
            "shape/mask/symbol/size": 7,
            "shape/mask/symbol/edgecolor": "#5555ff",
            "shape/mask/symbol/facecolor": "#5555ff",
            "shape/mask/symbol/alpha": 0.6,
            "shape/mask/sel_line/style": "DotLine",
            "shape/mask/sel_line/color": "#0000ff",
            "shape/mask/sel_line/width": 1,
            "shape/mask/sel_fill/style": "SolidPattern",
            "shape/mask/sel_fill/color": MAIN_BG_COLOR,
            "shape/mask/sel_fill/alpha": 0.1,
            "shape/mask/sel_symbol/marker": "Rect",
            "shape/mask/sel_symbol/size": 9,
            "shape/mask/sel_symbol/edgecolor": "#0000aa",
            "shape/mask/sel_symbol/facecolor": "#0000ff",
            "shape/mask/sel_symbol/alpha": 0.7,
            "shape/point/line/style": "SolidLine",
            "shape/point/line/color": "#ffff00",
            "shape/point/line/width": 1,
            "shape/point/sel_line/style": "SolidLine",
            "shape/point/sel_line/color": "#00ff00",
            "shape/point/sel_line/width": 1,
            "shape/point/fill/style": "NoBrush",
            "shape/point/sel_fill/style": "NoBrush",
            "shape/point/symbol/marker": "XCross",
            "shape/point/symbol/size": 9,
            "shape/point/symbol/edgecolor": "#ffff00",
            "shape/point/symbol/facecolor": "#ffff00",
            "shape/point/symbol/alpha": 1.0,
            "shape/point/sel_symbol/marker": "XCross",
            "shape/point/sel_symbol/size": 12,
            "shape/point/sel_symbol/edgecolor": "#00aa00",
            "shape/point/sel_symbol/facecolor": "#00ff00",
            "shape/point/sel_symbol/alpha": 0.7,
            "shape/segment/line/style": "SolidLine",
            "shape/segment/line/color": "#ffff00",
            "shape/segment/line/width": 1,
            "shape/segment/sel_line/style": "SolidLine",
            "shape/segment/sel_line/color": "#00ff00",
            "shape/segment/sel_line/width": 1,
            "shape/segment/fill/style": "NoBrush",
            "shape/segment/sel_fill/style": "NoBrush",
            "shape/segment/symbol/marker": "XCross",
            "shape/segment/symbol/size": 9,
            "shape/segment/symbol/edgecolor": "#ffff00",
            "shape/segment/symbol/facecolor": "#ffff00",
            "shape/segment/symbol/alpha": 1.0,
            "shape/segment/sel_symbol/marker": "XCross",
            "shape/segment/sel_symbol/size": 12,
            "shape/segment/sel_symbol/edgecolor": "#00aa00",
            "shape/segment/sel_symbol/facecolor": "#00ff00",
            "shape/segment/sel_symbol/alpha": 0.7,
            "shape/label/symbol/marker": "NoSymbol",
            "shape/label/symbol/size": 0,
            "shape/label/symbol/edgecolor": MAIN_BG_COLOR,
            "shape/label/symbol/facecolor": MAIN_BG_COLOR,
            "shape/label/border/style": "SolidLine",
            "shape/label/border/color": "#cbcbcb",
            "shape/label/border/width": 0,
            "shape/label/font/size": 8,
            "shape/label/font/family": "default",
            "shape/label/font/bold": False,
            "shape/label/font/italic": False,
            "shape/label/color": MAIN_BG_COLOR,
            "shape/label/bgcolor": MAIN_FG_COLOR,
            "shape/label/bgalpha": 0.25,
            "shape/label/abspos": False,
            "shape/label/move_anchor": True,
            "label/symbol/marker": "NoSymbol",
            "label/symbol/size": 0,
            "label/symbol/edgecolor": MAIN_BG_COLOR,
            "label/symbol/facecolor": MAIN_BG_COLOR,
            "label/border/style": "SolidLine",
            "label/border/color": "#cbcbcb",
            "label/border/width": 1,
            "label/font/size": 9,
            "label/font/family": "default",
            "label/font/bold": False,
            "label/font/italic": False,
            "label/color": MAIN_FG_COLOR,
            "label/bgcolor": MAIN_BG_COLOR,
            "label/bgalpha": 0.8,
            "label/anchor": "TL",
            "label/xc": 0,
            "label/yc": 0,
            "label/abspos": False,
            "label/absg": "TR",
            "label/xg": 0.0,
            "label/yg": 0.0,
            # info_label: used in builder.make.computation for example
            "info_label/symbol/marker": "NoSymbol",
            "info_label/symbol/size": 0,
            "info_label/symbol/edgecolor": MAIN_BG_COLOR,
            "info_label/symbol/facecolor": MAIN_BG_COLOR,
            "info_label/border/style": "SolidLine",
            "info_label/border/color": "#cbcbcb",
            "info_label/border/width": 1,
            "info_label/font/size": 9,
            "info_label/font/family": "default",
            "info_label/font/bold": False,
            "info_label/font/italic": False,
            "info_label/color": MAIN_FG_COLOR,
            "info_label/bgcolor": MAIN_BG_COLOR,
            "info_label/bgalpha": 0.8,
            "info_label/anchor": "TL",
            "info_label/xc": 0,
            "info_label/yc": 0,
            "info_label/abspos": True,
            "info_label/absg": "TR",
            "info_label/xg": 0.0,
            "info_label/yg": 0.0,
            "legend/border/style": "SolidLine",
            "legend/border/color": "#cbcbcb",
            "legend/border/width": 1,
            "legend/font/size": 8,
            "legend/font/family": "default",
            "legend/font/bold": False,
            "legend/font/italic": False,
            "legend/color": MAIN_FG_COLOR,
            "legend/bgcolor": MAIN_BG_COLOR,
            "legend/bgalpha": 0.8,
            "legend/anchor": "TR",
            "legend/xc": 0,
            "legend/yc": 0,
            "legend/abspos": True,
            "legend/absg": "TR",
            "legend/xg": 0.0,
            "legend/yg": 0.0,
        },
        "histogram": {
            "antialiasing": False,
            "title/font/size": 11,
            "title/font/bold": False,
            "label/font/size": 9,
            "label/font/bold": False,
            "curve/line/style": "NoPen",
            "curve/line/color": "#00ff00",
            "curve/line/width": 1,
            "curve/symbol/marker": "NoSymbol",
            "curve/symbol/size": 0,
            "curve/symbol/edgecolor": MAIN_BG_COLOR,
            "curve/symbol/facecolor": MAIN_FG_COLOR,
            "curve/symbol/alpha": 1.0,
            "curve/shade": 0.85,
            "curve/curvestyle": "Steps",
            "curve/label": "",
            "range/line/style": "SolidLine",
            "range/line/color": "#ff9393",
            "range/line/width": 1,
            "range/sel_line/style": "SolidLine",
            "range/sel_line/color": "#ff3333",
            "range/sel_line/width": 2,
            "range/fill": "#ff3333",
            "range/shade": 0.1,
            "range/symbol/marker": "Ellipse",
            "range/symbol/size": 7,
            "range/symbol/edgecolor": MAIN_BG_COLOR,
            "range/symbol/facecolor": "#ff9393",
            "range/symbol/alpha": 1.0,
            "range/sel_symbol/marker": "Ellipse",
            "range/sel_symbol/size": 9,
            "range/sel_symbol/edgecolor": MAIN_BG_COLOR,
            "range/sel_symbol/facecolor": "#ff3333",
            "range/sel_symbol/alpha": 0.9,
            "range/multi/color": "#806060",
            # Default parameters for plot axes
            "axis/title": "",
            "axis/color": MAIN_FG_COLOR,
            "axis/title_font/size": 7,
            "axis/title_font/family": "default",
            "axis/title_font/bold": False,
            "axis/title_font/italic": False,
            "axis/ticks_font/size": 7,
            "axis/ticks_font/family": "default",
            "axis/ticks_font/bold": False,
            "axis/ticks_font/italic": False,
            "grid/background": MAIN_BG_COLOR,
            "grid/maj_xenabled": True,
            "grid/maj_yenabled": True,
            "grid/maj_line/color": "#808080",
            "grid/maj_line/width": 1,
            "grid/maj_line/style": "DotLine",
            "grid/min_xenabled": True,
            "grid/min_yenabled": False,
            "grid/min_line/color": "#eaeaea",
            "grid/min_line/width": 1,
            "grid/min_line/style": "DotLine",
            "marker/curve/symbol/marker": "Ellipse",
            "marker/curve/symbol/edgecolor": MAIN_FG_COLOR,
            "marker/curve/symbol/facecolor": "#0000ff",
            "marker/curve/symbol/alpha": 0.8,
            "marker/curve/symbol/size": 8,
            "marker/curve/text/font/size": 8,
            "marker/curve/text/font/family": "default",
            "marker/curve/text/font/bold": False,
            "marker/curve/text/font/italic": False,
            "marker/curve/text/textcolor": "#000080",
            "marker/curve/text/background_color": "#0000ff",
            "marker/curve/text/background_alpha": 0.2,
            "marker/curve/pen/style": "SolidLine",
            "marker/curve/pen/color": MAIN_FG_COLOR,
            "marker/curve/pen/width": 0,
            "marker/curve/markerstyle": "NoLine",
            "marker/cross/symbol/marker": "Cross",
            "marker/cross/symbol/edgecolor": MAIN_FG_COLOR,
            "marker/cross/symbol/facecolor": "#ff0000",
            "marker/cross/symbol/alpha": 1.0,
            "marker/cross/symbol/size": 8,
            "marker/cross/text/font/family": "default",
            "marker/cross/text/font/size": 8,
            "marker/cross/text/font/bold": False,
            "marker/cross/text/font/italic": False,
            "marker/cross/text/textcolor": "#000080",
            "marker/cross/text/background_color": "#0000ff",
            "marker/cross/text/background_alpha": 0.2,
            "marker/cross/pen/style": "SolidLine",
            "marker/cross/pen/color": MAIN_FG_COLOR,
            "marker/cross/pen/width": 1,
            "marker/cross/markerstyle": "Cross",
        },
        "cross_section": {
            "antialiasing": False,
            "title/font/size": 11,
            "title/font/bold": False,
            "label/font/size": 9,
            "label/font/bold": False,
            "curve/line/style": "SolidLine",
            "curve/line/color": "#0000ff",
            "curve/line/width": 1,
            "curve/symbol/marker": "NoSymbol",
            "curve/symbol/size": 0,
            "curve/symbol/edgecolor": MAIN_BG_COLOR,
            "curve/symbol/facecolor": MAIN_FG_COLOR,
            "curve/symbol/alpha": 1.0,
            "curve/shade": 0.0,
            "curve/label": "",
            "range/line/style": "SolidLine",
            "range/line/color": "#ff9393",
            "range/line/width": 1,
            "range/sel_line/style": "SolidLine",
            "range/sel_line/color": "#ff0000",
            "range/sel_line/width": 2,
            "range/fill": "#ff0000",
            "range/shade": 0.15,
            "range/symbol/marker": "NoSymbol",
            "range/symbol/size": 5,
            "range/symbol/edgecolor": MAIN_FG_COLOR,
            "range/symbol/facecolor": "#ffff00",
            "range/symbol/alpha": 1.0,
            "range/sel_symbol/marker": "Ellipse",
            "range/sel_symbol/size": 9,
            "range/sel_symbol/edgecolor": MAIN_BG_COLOR,
            "range/sel_symbol/facecolor": "#ff0000",
            "range/sel_symbol/alpha": 0.9,
            "range/multi/color": "#806060",
            # Default parameters for plot axes
            "axis/title": "",
            "axis/color": MAIN_FG_COLOR,
            "axis/title_font/size": 7,
            "axis/title_font/family": "default",
            "axis/title_font/bold": False,
            "axis/title_font/italic": False,
            "axis/ticks_font/size": 7,
            "axis/ticks_font/family": "default",
            "axis/ticks_font/bold": False,
            "axis/ticks_font/italic": False,
            "grid/background": MAIN_BG_COLOR,
            "grid/maj_xenabled": True,
            "grid/maj_yenabled": True,
            "grid/maj_line/color": "#808080",
            "grid/maj_line/width": 1,
            "grid/maj_line/style": "DotLine",
            "grid/min_xenabled": False,
            "grid/min_yenabled": False,
            "grid/min_line/color": "#eaeaea",
            "grid/min_line/width": 1,
            "grid/min_line/style": "DotLine",
            "marker/curve/symbol/marker": "Ellipse",
            "marker/curve/symbol/edgecolor": MAIN_FG_COLOR,
            "marker/curve/symbol/facecolor": "#0000ff",
            "marker/curve/symbol/alpha": 0.8,
            "marker/curve/symbol/size": 8,
            "marker/curve/text/font/size": 8,
            "marker/curve/text/font/family": "default",
            "marker/curve/text/font/bold": False,
            "marker/curve/text/font/italic": False,
            "marker/curve/text/textcolor": "#000080",
            "marker/curve/text/background_color": "#0000ff",
            "marker/curve/text/background_alpha": 0.2,
            "marker/curve/pen/style": "SolidLine",
            "marker/curve/pen/color": MAIN_FG_COLOR,
            "marker/curve/pen/width": 0,
            "marker/curve/markerstyle": "NoLine",
            "marker/cross/symbol/marker": "Cross",
            "marker/cross/symbol/edgecolor": MAIN_FG_COLOR,
            "marker/cross/symbol/facecolor": "#ff0000",
            "marker/cross/symbol/alpha": 1.0,
            "marker/cross/symbol/size": 8,
            "marker/cross/text/font/family": "default",
            "marker/cross/text/font/size": 8,
            "marker/cross/text/font/bold": False,
            "marker/cross/text/font/italic": False,
            "marker/cross/text/textcolor": "#000080",
            "marker/cross/text/background_color": "#0000ff",
            "marker/cross/text/background_alpha": 0.2,
            "marker/cross/pen/style": "SolidLine",
            "marker/cross/pen/color": MAIN_FG_COLOR,
            "marker/cross/pen/width": 1,
            "marker/cross/markerstyle": "Cross",
        },
        # colormaps options
        "colormaps": {
            "colormaps/default": "colormaps_default.json",
            "colormaps/custom": "colormaps_custom.json",
        },
    }


DEFAULTS = get_plotpy_defaults()

CONF = UserConfig(DEFAULTS)


def update_plotpy_defaults() -> None:
    """Update the defaults with the current configuration"""
    global DEFAULTS, MAIN_BG_COLOR, MAIN_FG_COLOR
    MAIN_FG_COLOR, MAIN_BG_COLOR = get_main_colors()
    DEFAULTS = get_plotpy_defaults()
    CONF.update_defaults(DEFAULTS)


def update_plotpy_color_mode() -> None:
    """Update the color mode for Plotpy"""
    update_plotpy_defaults()

    # Iterate over all `BasePlot` widgets by browsing the QApplication:
    from qtpy.QtWidgets import QApplication

    from plotpy.plot import BasePlot

    app = QApplication.instance()
    if app is not None:
        # Iterate over all widgets and children to find BasePlot instances:
        for widget in app.topLevelWidgets():
            for child in widget.findChildren(BasePlot):
                child.update_color_mode()


def set_plotpy_dark_mode(state: bool) -> None:
    """Set dark mode for Qt application

    Args:
        state (bool): True to enable dark mode
    """
    mode = "dark" if state else "light"
    warnings.warn(
        f"`set_plotpy_dark_mode` is deprecated and will be removed in a future "
        f"version. Use `set_plotpy_color_mode('{mode}')` instead.",
        DeprecationWarning,
    )
    set_plotpy_color_mode(mode)


def set_plotpy_color_mode(mode: Literal["light", "dark", "auto"] | None = None):
    """Set the color mode for Plotpy

    Args:
        mode: Color mode ('light', 'dark' or 'auto'). If 'auto', the system color mode
        is used. If None, the `QT_COLOR_MODE` environment variable is used.
    """
    qth.set_color_mode(mode)
    update_plotpy_color_mode()
