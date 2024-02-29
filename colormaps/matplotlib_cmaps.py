import os
from typing import Callable

import matplotlib.colors as pltc
import matplotlib.pyplot as plt
import numpy as np

from plotpy.mathutils.colormap import (
    DEFAULT_COLORMAPS,
    DEFAULT_COLORMAPS_PATH,
    EditableColormap,
    save_colormaps,
)


def rgb_colors_to_hex_list(
    colors: list[tuple[int, int, int]]
) -> list[tuple[float, str]]:
    """Convert a list of RGB colors to a list of tuples with the position of the color
    and the color in hex format. Positions evenly distributed between 0 and 1.

    Args:
        colors: list of RGB colors

    Returns:
        list of tuples with the position of the color and the color in hex format
    """
    return [(i / len(colors), pltc.to_hex(color)) for i, color in enumerate(colors)]


def _interpolate(
    val: float, vmin: tuple[float, float, float], vmax: tuple[float, float, float]
):
    """Interpolate between two level of a color.

    Args:
        val: value to interpolate
        vmin: R, G or B tuple from a matplotlib segmented colormap
        vmax: R, G or B tuple from matplotlib segmented colormap

    Returns:
        The interpolated R, G or B component
    """
    interp = (val - vmin[0]) / (vmax[0] - vmin[0])
    return (1 - interp) * vmin[1] + interp * vmax[2]


def std_segmented_cmap_to_hex_list(cmdata: dict[str, list[tuple[float, float, float]]]):
    """Convert a matplotlib segmented colormap to a list of tuples with the position of
    the color and the color in hex format.

    Args:
        cmdata: segmented colormap data

    Returns:
        list of tuples with the position of the color and the color in hex format
    """
    colors: list[tuple[float, str]] = []
    red = np.array(cmdata["red"])
    green = np.array(cmdata["green"])
    blue = np.array(cmdata["blue"])
    indices = sorted(set(red[:, 0]) | set(green[:, 0]) | set(blue[:, 0]))
    for i in indices:
        idxr = red[:, 0].searchsorted(i)
        idxg = green[:, 0].searchsorted(i)
        idxb = blue[:, 0].searchsorted(i)
        compr = _interpolate(i, red[idxr - 1], red[idxr])
        compg = _interpolate(i, green[idxg - 1], green[idxg])
        compb = _interpolate(i, blue[idxb - 1], blue[idxb])
        colors.append((i, pltc.to_hex((compr, compg, compb))))
    return colors


InterpFuncT = Callable[[np.ndarray], np.ndarray]


def func_segmented_cmap_to_hex_list(
    n: int,
    cmap: pltc.LinearSegmentedColormap,
) -> list[tuple[float, str]]:
    """Convert a matplotlib segmented colormap to a list of tuples with the position of
    the color and the color in hex format. The input colormap contains function for each
    color RGB component instead of a list of colors.

    Args:
        n: number of colors to generate
        cmap: segmented colormap

    Returns:
        list of tuples with the position of the color and the color in hex format
    """
    colors = []
    arr = np.linspace(0, 1, n, dtype=float)
    colors = [(i, pltc.to_hex(rgba)) for i, rgba in zip(arr, cmap(arr))]
    return colors


def continuous_to_descrete_cmap(cmap: EditableColormap) -> EditableColormap:
    """Convert a continuous colormap to a descrete one.

    Args:
        cmap: colormap to convert

    Returns:
        descrete colormap
    """
    raw_cmap: tuple[tuple[float, str], ...] = cmap.to_tuples()
    new_raw_cmap: list[tuple[float, str]] = [raw_cmap[0]]
    n = len(raw_cmap)
    coeff = (n - 1) / n
    for i, (pos, color) in enumerate(raw_cmap[1:]):
        prev_pos, prev_color = raw_cmap[i]
        curr_pos, curr_color = pos, color
        new_pos = curr_pos * coeff
        print(curr_pos, new_pos, coeff)
        new_raw_cmap.append((new_pos, prev_color))
        new_raw_cmap.append((new_pos, curr_color))
    new_raw_cmap.append(raw_cmap[-1])

    return EditableColormap.from_iterable(new_raw_cmap, name=cmap.name)


def main():

    new_cmaps: dict[str, list[tuple[float, str]]] = {}

    # Uniform colormaps with a .colors attribute that return a list of RGB colors
    cmaps_with_colors = [
        "magma",
        "viridis",
        "inferno",
        "plasma",
        "cividis",
    ]

    # Discrete colormaps, same as uniform colormaps but the colormap must be post
    # processed to become descrete
    descrete_cmaps = [
        "Pastel1",
        "Pastel2",
        "Paired",
        "Accent",
        "Dark2",
        "Set1",
        "Set2",
        "Set3",
    ]

    cmaps_with_colors.extend(descrete_cmaps)

    # Colormaps with a _segmented_data attribute that contains the R, G and B components
    # as lists of tuples
    segmented_cmaps = [
        "coolwarm",
        "bwr",
        "seismic",
    ]

    # Colormaps with a _segmentdata attribute that contains the R, G and B components as
    # functions that return the color for a given position
    interp_cmaps = ["gnuplot2", "CMRmap", "rainbow", "turbo", "afmhot"]

    for cm_name in cmaps_with_colors:
        cmap = plt.get_cmap(cm_name)
        new_cmaps[cm_name] = rgb_colors_to_hex_list(cmap.colors)

    for cm_name in descrete_cmaps:
        cmap = EditableColormap.from_iterable(new_cmaps[cm_name], name=cm_name)
        new_cmaps[cm_name] = list(continuous_to_descrete_cmap(cmap).to_tuples())

    for cm_name in segmented_cmaps:
        cmap = plt.get_cmap(cm_name)
        new_cmaps[cm_name] = std_segmented_cmap_to_hex_list(cmap._segmentdata)

    n = 128

    for cm_name in interp_cmaps:
        cmap = plt.get_cmap(cm_name)
        new_cmaps[cm_name] = func_segmented_cmap_to_hex_list(n, cmap)

    for name, raw_cm in new_cmaps.items():
        DEFAULT_COLORMAPS[name.lower()] = EditableColormap.from_iterable(
            raw_cm, name=name
        )

    json_file = os.path.join(os.path.dirname(__file__), "new_colormaps.json")
    save_colormaps(json_file, DEFAULT_COLORMAPS_PATH)


if __name__ == "__main__":
    main()
