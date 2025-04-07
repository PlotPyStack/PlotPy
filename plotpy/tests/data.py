# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Data for tests"""

from __future__ import annotations

import numpy as np


def gen_image1(N: int = 2000, grid: bool = True) -> np.ndarray:
    """Generates a cosine image with a grid, and 4 corners with different values

    Args:
        N: image size
        grid: if True, a grid is added to the image

    Returns:
        image array
    """
    T = np.float32
    x = np.array(np.linspace(-5, 5, N), T)
    img = np.zeros((N, N), T)
    x.shape = (1, N)
    img += x**2
    x.shape = (N, 1)
    img += x**2
    np.cos(img, img)  # inplace cosine
    if not grid:
        return img
    x.shape = (N,)
    for k in range(-5, 5):
        i = x.searchsorted(k)
        if k < 0:
            v = -1.1
        else:
            v = 1.1
        img[i, :] = v
        img[:, i] = v
    m1, m2, m3, m4 = -1.1, -0.3, 0.3, 1.1
    K = 100
    img[:K, :K] = m1  # (0,0)
    img[:K, -K:] = m2  # (0,N)
    img[-K:, -K:] = m3  # (N,N)
    img[-K:, :K] = m4  # (N,0)
    return img


def gen_image2(N: int = 1000, grid: bool = True) -> np.ndarray:
    """Generates a cosine image with a grid, and 4 corners with different values.
    It is a bit different from gen_image1, because the cosine frequency is
    higher and the grid step is smaller.

    Args:
        N: image size
        grid: if True, a grid is added to the image

    Returns:
        image array
    """
    T = np.float64
    TMAX = 32000
    TMIN = 32000
    S = 5.0
    x = np.array(np.linspace(-5 * S, 5 * S, N), T)
    img = np.zeros((N, N), T)
    x.shape = (1, N)
    img += x**2
    x.shape = (N, 1)
    img += x**2
    img = TMAX * np.cos(img / S) + TMIN
    if not grid:
        return img
    x.shape = (N,)
    #    dx = dy = x[1]-x[0]
    for k in range(-5, 5):
        i = x.searchsorted(k)
        if k < 0:
            v = -1.1
        else:
            v = 1.1
        img[i, :] = v
        img[:, i] = v
    m1, m2, m3, m4 = -1.1, -0.3, 0.3, 1.1
    K = 100
    img[:K, :K] = TMAX * m1 + TMIN  # (0,0)
    img[:K, -K:] = TMAX * m2 + TMIN  # (0,N)
    img[-K:, -K:] = TMAX * m3 + TMIN  # (N,N)
    img[-K:, :K] = TMAX * m4 + TMIN  # (N,0)
    return img


def gen_image3(N: int = 1000) -> np.ndarray:
    """Generates a grid image with horizontal and vertical ramps

    Args:
        N: image size

    Returns:
        image array
    """
    NK = 20
    T = float
    img = np.zeros((N, N), T)
    x = np.arange(N, dtype=float)
    x.shape = (1, N)
    DK = N // NK
    for i in range(NK):
        S = i + 1
        y = S * (x // S)
        img[DK * i : DK * (i + 1), :] = y
    return img


def gen_image4(NX: int, NY: int) -> np.ndarray:
    """Generates image data based on a random normal distribution with FFT operations

    Args:
        NX: image size in X
        NY: image size in Y

    Returns:
        image array
    """
    BX, BY = 40, 40
    img = np.random.normal(0, 100, size=(BX, BY))
    timg = np.fft.fftshift(np.fft.fft2(img))
    print(timg.shape)
    cx = NX // 2
    cy = NY // 2
    bx2 = BX // 2
    by2 = BY // 2
    z = np.zeros((NX, NY), np.complex64)
    z[cx - bx2 : cx - bx2 + BX, cy - by2 : cy - by2 + BY] = timg
    z = np.fft.ifftshift(z)
    rev = np.fft.ifft2(z)
    return np.abs(rev)


def gen_xyimage(N: int = 1000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generates a cosine image with a grid, and 4 corners with different values

    Args:
        N: image size
        grid: if True, a grid is added to the image

    Returns:
        x, y, data
    """
    N = 1000
    data = gen_image1(N=N)
    x = np.array(np.linspace(-5, 5, N), np.float32)
    data += np.random.normal(0.0, 0.05, size=(N, N))
    return x, (x + 5) ** 0.6, data


def gen_2d_gaussian(size, dtype, x0=0, y0=0, mu=0.0, sigma=2.0, amp=None) -> np.ndarray:
    """Creating 2D Gaussian (-10 <= x <= 10 and -10 <= y <= 10)"""
    xydata = np.linspace(-10, 10, size)
    x, y = np.meshgrid(xydata, xydata)
    if amp is None:
        amp = np.iinfo(dtype).max * 0.5
    t = (np.sqrt((x - x0) ** 2 + (y - y0) ** 2) - mu) ** 2
    return np.array(amp * np.exp(-t / (2.0 * sigma**2)), dtype=dtype)


def gen_1d_gaussian(
    size, x0=0, mu=0.0, sigma=2.0, amp=None
) -> tuple[np.ndarray, np.ndarray]:
    """Creating 1D Gaussian (-10 <= x <= 10)"""
    x = np.linspace(-10, 10, size)
    if amp is None:
        amp = 1.0
    t = (np.abs(x - x0) - mu) ** 2
    y = np.array(amp * np.exp(-t / (2.0 * sigma**2)), dtype=float)
    return x, y


def gen_xyz_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a X, Y, Z data set for contour detection features"""
    delta = 0.025
    x, y = np.arange(-3.0, 3.0, delta), np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-(X**2) - Y**2)
    Z2 = np.exp(-((X - 1) ** 2) - (Y - 1) ** 2)
    Z = (Z1 - Z2) * 2
    return X, Y, Z
