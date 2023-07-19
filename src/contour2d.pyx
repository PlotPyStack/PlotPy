# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/__init__.py for details)


import numpy as np
cimport numpy as np
import cython
from cpython cimport array
from libc cimport math

cdef class segment:
    cdef public int p0, p1, next

    def __cinit__(self, int p0, int p1):
        self.p0 = p0
        self.p1 = p1
        self.next = -1


cdef class CoordOrtho:
    cdef double[:] _x
    cdef double[:] _y

    def __cinit__(self, double[:] x, double[:]y):
        self._x = x
        self._y = y

    cpdef double x(self, int i, int j):
        return self._x[j]
    cpdef double y(self, int i, int j):
        return self._y[i]


cdef class CoordGrid:
    cdef double[:,:] _x
    cdef double[:,:] _y

    def __cinit__(self, double[:,:] x, double[:,:] y):
        self._x = x
        self._y = y

    cpdef double x(self, int i, int j):
        return self._x[i, j]
    cpdef double y(self, int i, int j):
        return self._y[i, j]


cdef class Contour:

    cdef int m_last_first_unassigned
    cdef array.array cx, cy
    cdef list segments
    cdef dict pt_map
    cdef dict seg_map

    def __cinit__(self):
        self.m_last_first_unassigned = 0
        self.cx = array.array('d', [])
        self.cy = array.array('d', [])
        self.segments = []
        self.pt_map = {}
        self.seg_map = {}

    @cython.cdivision(True)
    cdef int add_point(self, double x, double y):
        pt = (math.floor(x * 1e10) / 1e10, math.floor(y * 1e10) / 1e10)
        cdef int p = self.pt_map.get(pt, -1)
        if p != -1:
            return p
        new_pt = len(self.pt_map)
        self.pt_map[pt] = new_pt
        self.cx.append(x)
        self.cy.append(y)

        return new_pt

    cdef void add_edge(self, double x0, double y0, double x1, double y1):
        if (x1, y1) < (x0, y0):
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        cdef int p0 = self.add_point(x0, y0)
        cdef int p1 = self.add_point(x1, y1)
        if p0 == p1:
            return
        cdef int seg = len(self.segments)
        if p1 < p0:
            p0, p1 = p1, p0

        self.segments.append(segment(p0, p1))
        if p0 not in self.seg_map:
            self.seg_map[p0] = [seg]
        else:
            self.seg_map[p0].append(seg)

        if p1 not in self.seg_map:
            self.seg_map[p1] = [seg]
        else:
            self.seg_map[p1].append(seg)

    cdef void build_contour(self, int v, array.array pts, array.array offsets, array.array val):

        # build linked list of segments according to their begin/end points
        cdef int seg, prev_pt,  p0, p1, next_pt, next_seg, s
        seg = self.find_first_unassigned_segment()
        if seg < 0:
            return
        prev_pt = self.segments[seg].p0

        # Points are saved in two arrays in order to rebuild opened lines:
        # points0 contains points computed from p0, format: [x0, y0, x1, y1...]
        # points1 contains points computed from p1 format: [y0, x0, y1, x1, ...]
        # Coordinates of points1 are reversed because the list is reversed
        cdef array.array points0 = array.array('d', [])
        cdef array.array points1 = array.array('d', [])
        cdef int start_seg = seg  # initial segment of the line
        cdef int start_point = 0  # starting point: 0 -> seg.p0, 1 -> seg.p1

        while seg >= 0:
            p0 = self.segments[seg].p0
            p1 = self.segments[seg].p1
            next_seg = -2
            if start_point == 0:
                points0.append(self.cx.data.as_doubles[prev_pt])
                points0.append(self.cy.data.as_doubles[prev_pt])
            else:
                points1.append(self.cy.data.as_doubles[prev_pt])
                points1.append(self.cx.data.as_doubles[prev_pt])
            if prev_pt == p0:
                next_pt=p1
            elif prev_pt == p1:
                next_pt=p0
            else:
                # Should never happen
                next_pt=-1

            # Find the other segment that starts/ends with p1
            for s in self.seg_map.get(next_pt, []):
                # There should be only 2 segments connected to that point
                if s != seg:
                    next_seg = s
                    break

            self.segments[seg].next = next_seg

            if next_seg == -2 and start_point == 0:
                # Line is opened, find the other part starting from start_seg.p1
                start_point = 1
                seg = start_seg
                prev_pt = self.segments[seg].p1
                continue
            elif next_seg == -2 or self.segments[next_seg].next != -1:
                # No other segment
                if start_point == 0:
                    points0.append(self.cx.data.as_doubles[next_pt])
                    points0.append(self.cy.data.as_doubles[next_pt])
                else:
                    points1.append(self.cy.data.as_doubles[next_pt])
                    points1.append(self.cx.data.as_doubles[next_pt])

                pts.extend(reversed(points1))
                pts.extend(points0)
                offsets.append(len(pts))
                val.append(v)
                points0 = array.array('d', [])
                points1 = array.array('d', [])
                seg = self.find_first_unassigned_segment()
                prev_pt = self.segments[seg].p0
                start_seg = seg
                start_point = 0
                continue

            seg = next_seg
            prev_pt = next_pt

    cdef int find_first_unassigned_segment(self):
        cdef int k
        for k in range(self.m_last_first_unassigned, len(self.segments)):
            if self.segments[k].next == -1:
                self.m_last_first_unassigned = k
                return k
        return -1

# Derivation from the fortran version of CONREC by Paul Bourke
@cython.profile(False)
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
cdef inline double xsect(int p1,int p2, double vv[5], double xx[5], double yy[5]):
    return (vv[p2]*xx[p1]-vv[p1]*xx[p2])/(vv[p2]-vv[p1])


@cython.profile(False)
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
cdef inline double ysect(int p1,int p2, double vv[5], double xx[5], double yy[5]):
    return (vv[p2]*yy[p1]-vv[p1]*yy[p2])/(vv[p2]-vv[p1])


@cython.boundscheck(False)
@cython.wraparound(False)
cdef void compute_contour_2d(double [:, :] data, coord, double[:] values, list contours):

    cdef unsigned int nx = data.shape[0]
    cdef unsigned int ny = data.shape[1]

    # Dispatch table according to sign of value for each of the 3 vertices (m1m2m3)
    # (-, = or +)
    cdef int[3][3][3] casetab = [
        [ [0,0,8],    # --- --=  --+
          [0,2,5],    # -=- -==  -=+
          [7,6,9] ],  # -+- -+=  -++
        [ [0,3,4],    # =-- =-=  =-+
          [1,3,1],    # ==- ===  ==+
          [4,3,0] ],  # =+- =+=  =++
        [ [9,6,7],    # +-- +-=  +-+
          [5,2,0],    # +=- +==  +=+
          [8,0,0] ]   # ++- ++=  +++
    ]

    cdef double vv[5]
    cdef double xx[5]
    cdef double yy[5]
    cdef int sh[5]
    cdef double x1,y1,x2,y2
    cdef int m1, m2, m3, i, j, k, caseval
    cdef double dmin, dmax;
    cdef double d1, d2, d3, d4
    cdef double val
    cdef Contour ctr
    for i in range(nx-1):
        for j in range(ny-1):
            d1 = data[i,j]
            d2 = data[i,j+1]
            d3 = data[i+1,j +1]
            d4 = data[i+1,j]
            dmin = min(d1, d2, d3, d4)
            dmax = max(d1, d2, d3, d4)
            for k in range(values.shape[0]):
                val = values[k]
                if dmax >= val and dmin <= val:
                    ctr = contours[k]
                    break
            else:
                continue
            vv[1] = d1-val; xx[1] = coord.x(i  , j  ); yy[1] = coord.y(i  , j  )
            vv[2] = d2-val; xx[2] = coord.x(i  , j+1); yy[2] = coord.y(i  , j+1)
            vv[3] = d3-val; xx[3] = coord.x(i+1, j+1); yy[3] = coord.y(i+1, j+1)
            vv[4] = d4-val; xx[4] = coord.x(i+1, j  ); yy[4] = coord.y(i+1, j  )
            xx[0] = (xx[1]+xx[2]+xx[3]+xx[4])*0.25
            yy[0] = (yy[1]+yy[2]+yy[3]+yy[4])*0.25
            vv[0] = (vv[1]+vv[2]+vv[3]+vv[4])*0.25
            for k in range(5):
                if vv[k] > 0:
                    sh[k] = 2
                elif vv[k] < 0.0:
                    sh[k] = 0
                else:
                    sh[k] = 1

            # Walk the four triangles
            for k in range(4):
                m1 = 1+k
                m2 = 0
                m3 = 1+(k+1)%4

                caseval = casetab[sh[m1]][sh[m2]][sh[m3]]
                if caseval == 0:
                    continue
                elif caseval == 1: # line m1 .. m2
                    x1 = xx[m1]; y1 = yy[m1]
                    x2 = xx[m2]; y2 = yy[m2]
                elif caseval == 2: # line m2 .. m3
                    x1 = xx[m2]; y1 = yy[m2]
                    x2 = xx[m3]; y2 = yy[m3]
                elif caseval == 3: # line m1 .. m3
                    x1 = xx[m1]; y1 = yy[m1]
                    x2 = xx[m3]; y2 = yy[m3]
                elif caseval == 4: # line m1 .. side(m2,m3)
                    x1 = xx[m1]; y1 = yy[m1]
                    x2 = xsect(m2,m3, vv, xx, yy); y2 = ysect(m2,m3, vv, xx, yy)
                elif caseval == 5: # Line m2 .. side(m3,m1)
                    x1 = xx[m2]; y1 = yy[m2]
                    x2 = xsect(m3,m1, vv, xx, yy); y2 = ysect(m3,m1, vv, xx, yy)
                elif caseval == 6: # Line m3 .. side(m1,m2)
                    x1 = xx[m3]; y1 = yy[m3]
                    x2 = xsect(m1,m2, vv, xx, yy); y2 = ysect(m1,m2, vv, xx, yy)
                elif caseval == 7: # Line between sides 1-2 .. 2-3
                    x1 = xsect(m1,m2, vv, xx, yy); y1 = ysect(m1,m2, vv, xx, yy)
                    x2 = xsect(m2,m3, vv, xx, yy); y2 = ysect(m2,m3, vv, xx, yy)
                elif caseval == 8: # Line between sides 2-3 .. 3-1
                    x1 = xsect(m2,m3, vv, xx, yy); y1 = ysect(m2,m3, vv, xx, yy)
                    x2 = xsect(m3,m1, vv, xx, yy); y2 = ysect(m3, m1, vv, xx, yy)
                elif caseval == 9: # Line between sides 3-1 .. 1-2
                    x1 = xsect(m3,m1, vv, xx, yy); y1 = ysect(m3,m1, vv, xx, yy)
                    x2 = xsect(m1,m2, vv, xx, yy); y2 = ysect(m1,m2, vv, xx, yy)

                ctr.add_edge(x1,y1,x2,y2)


cdef contour_2d_coord(double [:, :] data, coord, np.ndarray[double, ndim=1] values):

    cdef np.ndarray[double, ndim=2] points;
    cdef np.ndarray[int, ndim=2] offsets;
    cdef array.array vpts = array.array('d', [])
    cdef array.array voff = array.array('i',[0])
    cdef array.array vval = array.array('i', [0])
    cdef double val
    cdef int k
    cdef Contour cont

    contour_objects = []
    for k in range(0, values.shape[0]):
        cont = Contour()
        contour_objects.append(cont)
    compute_contour_2d(data, coord, values, contour_objects)
    for k in range(0, values.shape[0]):
        cont = contour_objects[k]
        val = values[k]
        cont.build_contour(k, vpts, voff, vval)

    points = np.zeros((int(len(vpts)/2), 2), np.double)

    for k in range(0, len(vpts), 2):
        points[k//2, 0] = vpts.data.as_doubles[k]
        points[k//2, 1] = vpts.data.as_doubles[k+1]

    offsets = np.zeros((int(len(voff)), 2), np.int32)
    for k in range(0, len(voff)):
        offsets[k,0] = vval.data.as_ints[k]
        offsets[k,1] = voff.data.as_ints[k]//2

    return (points, offsets)


@cython.profile(False)
@cython.boundscheck(False)
def contour_2d_ortho(double [:, :] data, double [:] x, double [:] y, np.ndarray[double, ndim=1] values):
    coord = CoordOrtho(x, y)
    return contour_2d_coord(data, coord, values)


@cython.profile(False)
@cython.boundscheck(False)
def contour_2d_grid(double [:, :] data, double [:, :] x, double [:, :] y, np.ndarray[double, ndim=1] values):
    coord = CoordGrid(x, y)
    return contour_2d_coord(data, coord, values)
