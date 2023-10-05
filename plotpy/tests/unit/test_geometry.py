# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Unit tests for geometry module
"""

import numpy as np

from plotpy.mathutils import geometry as geom


def test_transform_matrix() -> None:
    """Testing transform matrix functions"""
    x0 = 1.0
    y0 = 2.0
    scale_x = 2.0
    scale_y = 3.0
    delta_x = 15.3
    delta_y = 10.4
    angle = 30.0
    vect0 = geom.colvector(x0, y0)
    # print("vect0:", repr(vect0))
    vect1 = geom.scale(scale_x, scale_y) * vect0
    assert np.allclose(vect1, np.matrix([[2.0], [6.0], [1.0]]))
    # print("vect1:", repr(vect1))
    vect2 = geom.translate(delta_x, delta_y) * vect1
    assert np.allclose(vect2, np.matrix([[17.3], [16.4], [1.0]]))
    # print("vect2:", repr(vect2))
    vect3 = geom.rotate(angle) * vect2
    assert np.allclose(vect3, np.matrix([[18.87226872], [-14.56322332], [1.0]]))
    # print("vect3:", repr(vect3))
    trmat = (
        geom.scale(1.0 / scale_x, 1.0 / scale_y)
        * geom.translate(-delta_x, -delta_y)
        * geom.rotate(-angle)
    )
    vect4 = trmat * vect3
    # print("vect4:", repr(vect4))
    assert np.allclose(vect0, vect4)


def test_vector_operations() -> None:
    """Test vector operation functions"""
    xa = 1.0
    ya = 2.0
    xb = 3.0
    yb = 4.0
    vect = np.array([5.0, 6.0])
    angle = np.deg2rad(30.0)
    norm = geom.vector_norm(xa, ya, xb, yb)
    assert np.allclose(norm, np.sqrt(8.0))
    proj = geom.vector_projection(vect, xa, ya, xb, yb)
    # print("proj:", repr(proj))
    assert np.allclose(proj, np.array([8.5, 9.5]))
    vrot = geom.vector_rotation(angle, vect[0], vect[1])
    # print("vrot:", repr(vrot))
    assert np.allclose(vrot, np.array([1.33012702, 7.69615242]))
    angle = geom.vector_angle(vect[0], vect[1])
    # print("angle:", repr(angle))
    assert np.allclose(angle, np.arctan2(vect[1], vect[0]))


def test_coordinates_computations() -> None:
    """Testing coordinates computation functions"""
    x1 = 1.0
    y1 = 2.0
    x2 = 3.0
    y2 = 4.0
    xc, yc = geom.compute_center(x1, y1, x2, y2)
    assert np.allclose(xc, 2.0) and np.allclose(yc, 3.0)
    width, height = geom.compute_rect_size(x1, y1, x2, y2)
    assert np.allclose(width, 2.0) and np.allclose(height, 2.0)
    dist = geom.compute_distance(x1, y1, x2, y2)
    assert np.allclose(dist, np.sqrt(8.0))
    angle = geom.compute_angle(x1, y1, x2, y2)
    assert np.allclose(angle, np.rad2deg(-np.arctan2(2.0, 2.0)))
    angle_inv = geom.compute_angle(x1, y1, x2, y2, True)
    assert np.allclose(angle_inv, np.rad2deg(np.arctan2(2.0, 2.0)))


if __name__ == "__main__":
    test_transform_matrix()
    test_vector_operations()
    test_coordinates_computations()
