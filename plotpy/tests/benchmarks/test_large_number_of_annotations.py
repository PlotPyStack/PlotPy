# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Large number of annotations test"""

# guitest: show

import timeit

import numpy as np
from guidata.qthelpers import qt_app_context

from plotpy.builder import make
from plotpy.tests import data as ptd
from plotpy.tests import vistools as ptv

WIN_REFS = []


def plot(items, title):
    """Plot items"""
    global WIN_REFS
    title = f"{title} - #refs: {len(WIN_REFS) + 1}"
    win = ptv.show_items(items, plot_type="image", wintitle=title, title=title)
    WIN_REFS.append(win)
    return win


def create_polygon_vertices(
    x0: float, y0: float, nb_points: int, radius_mean: float, radius_variation: float
) -> list[tuple[float, float]]:
    """Generate points for a polygon around (x0, y0)

    Args:
        x0: x coordinate of the polygon center
        y0: y coordinate of the polygon center
        nb_points: number of points to generate
        radius_mean: mean radius of the polygon
        radius_variation: variation in radius

    Returns:
        List of (x, y) points representing the polygon vertices
    """
    points = []
    # Calculate number of NaNs to append (random numbers between 0 and nb_points-10):
    num_nans = np.random.randint(0, nb_points - 10)
    for j in range(nb_points - num_nans):
        angle = j * (2 * np.pi / (nb_points - num_nans))
        radius = radius_mean + radius_variation * np.random.rand()
        x = x0 + radius * np.cos(angle)
        y = y0 + radius * np.sin(angle)
        points.append((x, y))
    for _ in range(num_nans):
        points.append((np.nan, np.nan))
    return points


def create_random_polygons(
    size: int, nb_polygons: int, nb_points_per_polygon: int
) -> np.ndarray:
    """Create random polygons

    Args:
        size: size of the area in which to create polygons
        nb_polygons: number of polygons to create
        nb_points_per_polygon: number of points per polygon

    Returns:
        Array of shape (nb_polygons, nb_points_per_polygon, 2)
    """
    polygons = []
    for _ in range(nb_polygons):
        x0 = size * np.random.rand()
        y0 = size * np.random.rand()
        points = create_polygon_vertices(
            x0, y0, nb_points_per_polygon, radius_mean=20, radius_variation=30
        )
        # Append the flattened points:
        polygons.append(points)
    return np.array(polygons)


def test_large_number_of_annotations(measure_execution_time: bool = False):
    """Test large number of annotations

    Args:
        measure_execution_time: if True, measure and print the execution time, then
         quit the application immediately.
    """
    title = "Large number of annotations test"
    size = 2000
    nb_polygons = 100
    nb_points_per_polygon = 120
    with qt_app_context(exec_loop=not measure_execution_time):
        data = ptd.gen_image4(size, size)
        x = np.linspace(0, size - 1, size)
        y = np.linspace(0, size - 1, size)
        item = make.xyimage(x, y, data)
        item.set_readonly(True)
        item.set_selectable(False)
        items = [item]
        polygons = create_random_polygons(size, nb_polygons, nb_points_per_polygon)
        for i, points in enumerate(polygons):
            polygon = make.annotated_polygon(np.array(points), title=f"Polygon {i + 1}")
            polygon.set_closed(False)
            items.append(polygon)
        if measure_execution_time:
            exec_time = timeit.timeit(lambda: plot(items, title), number=10) / 10
            print(
                f"Execution time with {nb_polygons} polygons "
                f"({nb_points_per_polygon} points per polygon): "
                f"{exec_time:.3f} seconds/plot"
            )
        else:
            win = plot(items, title)
            win.register_annotation_tools()


if __name__ == "__main__":
    test_large_number_of_annotations(measure_execution_time=True)
