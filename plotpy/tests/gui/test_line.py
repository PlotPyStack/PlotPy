# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Internal test related to pcolor feature"""


import numpy as np
import pytest

from plotpy._scaler import _line_test as line

N = 10
imin = np.full((N,), N, dtype=int)
imax = np.full((N,), 0, dtype=int)

test_line_data = [(0, 0, 9, 9), (9, 9, 0, 0), (0, 5, 0, 9), (2, 5, 7, 5), (0, 1, 2, 9)]
test_tri_data = [(0, 1, 2, 9, 8, 7)]


def print_tri(imin, imax):
    for i in range(N):
        for j in range(N):
            if j < imin[i] or j > imax[i]:
                print(".", end=" ")
            else:
                print("*", end=" ")
        print()


@pytest.mark.parametrize("x0,y0,x1,y1", test_line_data)
def test_line(x0, y0, x1, y1):
    print(x0, ",", y0, "->", x1, ",", y1)
    imin = np.full((N,), N, dtype=int)
    imax = np.full((N,), 0, dtype=int)
    line(x0, y0, x1, y1, N, imin, imax)
    print_tri(imin, imax)


@pytest.mark.parametrize("x0,y0,x1,y1,x2,y2", test_tri_data)
def test_tri(x0, y0, x1, y1, x2, y2):
    print(x0, ",", y0, "->", x1, ",", y1)
    imin[:] = N + 1
    imax[:] = -1
    line(x0, y0, x1, y1, N, imin, imax)
    line(x0, y0, x2, y2, N, imin, imax)
    line(x1, y1, x2, y2, N, imin, imax)
    print_tri(imin, imax)


if __name__ == "__main__":
    test_tri(0, 1, 2, 9, 8, 7)
    test_line(0, 0, 9, 9)
    test_line(9, 9, 0, 0)
    test_line(0, 5, 0, 9)
    test_line(2, 5, 7, 5)
    test_line(0, 1, 2, 9)
