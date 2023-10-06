# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/__init__.py for details)

"""2D-Histogram algorithm"""

cimport cython
cimport numpy as cnp
from libc.math cimport log

cnp.import_array()

cdef inline double double_max(double a, double b): return a if a >= b else b
cdef inline double double_min(double a, double b): return a if a <= b else b

@cython.profile(False)
@cython.boundscheck(False)
def histogram2d(cnp.ndarray[double, ndim=1] X, cnp.ndarray[double, ndim=1] Y,
                double i0, double i1, double j0, double j1,
                cnp.ndarray[double, ndim=2] data, logscale):
    """Compute 2-D Histogram from data X, Y"""
    cdef double cx, cy, nmax, ix, iy
    cdef unsigned int i
    cdef Py_ssize_t n = X.shape[0]
    cdef Py_ssize_t nx = data.shape[1]
    cdef Py_ssize_t ny = data.shape[0]

    cx = nx/(i1-i0)
    cy = ny/(j1-j0)

    for i in range(n):
        #  Centered bins => - .5
        ix = (X[i] - i0) * cx - .5
        iy = (Y[i] - j0) * cy - .5
        if ix >= 0 and ix <= nx-1 and iy >= 0 and iy <= ny-1:
            data[<int> iy, <int> ix] += 1

    nmax = 0.
    if logscale:
        for j in range(ny):
            for i in range(nx):
                data[j, i] = log(1+data[j, i])
                nmax = double_max(nmax, data[j, i])
    else:
        for j in range(ny):
            for i in range(nx):
                nmax = double_max(nmax, data[j, i])
    return nmax

@cython.profile(False)
@cython.boundscheck(False)
def histogram2d_func(cnp.ndarray[double, ndim=1] X,
                     cnp.ndarray[double, ndim=1] Y,
                     cnp.ndarray[double, ndim=1] Z,
                     double i0, double i1, double j0, double j1,
                     cnp.ndarray[double, ndim=2] data_tmp,
                     cnp.ndarray[double, ndim=2] data, int computation):
    """Compute 2-D Histogram from data X, Y"""
    cdef double cx, cy, nmax, ix, iy
    cdef unsigned int i, u, v
    cdef Py_ssize_t n = X.shape[0]
    cdef Py_ssize_t nx = data.shape[1]
    cdef Py_ssize_t ny = data.shape[0]

    cx = nx/(i1-i0)
    cy = ny/(j1-j0)

    for i in range(n):
        #  Centered bins => - .5
        ix = (X[i] - i0) * cx - .5
        iy = (Y[i] - j0) * cy - .5
        if ix >= 0 and ix <= nx-1 and iy >= 0 and iy <= ny-1:
            u, v = <int> iy, <int> ix
            if computation == 0:  # max
                data_tmp[u, v] += 1
                data[u, v] = double_max(data[u, v], Z[i])
            elif computation == 1:  # min
                data_tmp[u, v] += 1
                data[u, v] = double_min(data[u, v], Z[i])
            elif computation == 2:  # sum
                data_tmp[u, v] += 1
                data[u, v] += Z[i]
            elif computation == 3:  # prod
                data_tmp[u, v] += 1
                data[u, v] *= Z[i]
            elif computation == 4:  # avg
                data_tmp[u, v] += 1
                data[u, v] += (Z[i]-data[u, v])/data_tmp[u, v]
            elif computation == 5:  # argmin
                if data[u, v] > Z[i]:
                    data_tmp[u, v] = i
                    data[u, v] = Z[i]
            elif computation == 6:  # argmax
                if data[u, v] < Z[i]:
                    data_tmp[u, v] = i
                    data[u, v] = Z[i]
