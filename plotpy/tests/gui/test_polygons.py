# -*- coding: utf-8 -*-
#
# Copyright © 2011 CEA
# Ludovic Aubry
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""PolygonMapItem test

PolygonMapItem is intended to display maps ie items containing
several hundreds of independent polygons.
"""


import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.core.items.polygon import PolygonMapItem
from plotpy.core.plot.plotwidget import PlotDialog

SHOW = True  # Show test in GUI-based test launcher

# Create a sample dataset consisting of tesselated circles randomly placed
# in a box
RMAX = 0.5
XMAX = YMAX = 10.0
NSEGMIN = 4
NSEGMAX = 300


def create_circle():
    x, y, rmax = np.random.rand(3)
    rmax *= RMAX
    x *= XMAX
    y *= YMAX
    nseg = np.random.randint(NSEGMIN, NSEGMAX)
    th = np.linspace(0, 2 * np.pi, nseg)
    PTS = np.empty((nseg, 2), float)
    PTS[:, 0] = x + rmax * np.cos(th)
    PTS[:, 1] = y + rmax * np.sin(th)
    return PTS


NCIRC = 1000
COLORS = [
    (0xFF000000, 0x8000FF00),
    (0xFF0000FF, 0x800000FF),
    (0xFF000000, 0x80FF0000),
    (0xFF00FF00, 0x80000000),
]


def test_polygons():
    """Test"""
    with qt_app_context(exec_loop=True):
        win = PlotDialog(edit=True, toolbar=True, wintitle="Sample multi-polygon item")
        plot = win.manager.get_plot()
        plot.set_aspect_ratio(lock=True)
        plot.set_antialiasing(False)
        plot.set_axis_direction("left", False)
        plot.set_axis_title("bottom", "Lon")
        plot.set_axis_title("left", "Lat")

        points = []
        offsets = np.zeros((NCIRC, 2), np.int32)
        colors = np.zeros((NCIRC, 2), np.uint32)
        npts = 0
        for k in range(NCIRC):
            pts = create_circle()
            offsets[k, 0] = k
            offsets[k, 1] = npts
            npts += pts.shape[0]
            points.append(pts)
            colors[k, 0] = COLORS[k % len(COLORS)][0]
            colors[k, 1] = COLORS[(3 * k) % len(COLORS)][1]
        points = np.concatenate(points)

        print(NCIRC, "Polygons")
        print(points.shape[0], "Points")

        crv = PolygonMapItem()
        crv.set_data(points, offsets, colors)
        plot.add_item(crv, z=0)
        win.show()


if __name__ == "__main__":
    test_polygons()
