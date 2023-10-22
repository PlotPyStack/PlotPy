# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
pyplot test

Interactive plotting interface with MATLAB-like syntax
"""

# guitest: show

import numpy as np
import pytest
from numpy.random import normal

import plotpy.pyplot as plt


@pytest.mark.skip(reason="Not relevant in automated test suite")
def test_pyplot():
    x = np.linspace(-5, 5, 1000)
    plt.figure(1)
    plt.subplot(2, 1, 1)
    plt.plot(x, np.sin(x), "r+")
    plt.plot(x, np.cos(x), "g-")
    plt.errorbar(x, -1 + x**2 / 20 + 0.2 * np.random.rand(len(x)), x / 20)
    plt.xlabel("Axe x")
    plt.ylabel("Axe y")
    plt.subplot(2, 1, 2)
    img = np.fromfunction(
        lambda x, y: np.sin((x / 200.0) * (y / 200.0) ** 2), (1000, 1000)
    )
    plt.xlabel("pixels")
    plt.ylabel("pixels")
    plt.zlabel("intensity")
    plt.gray()  # pylint: disable=no-member
    plt.imshow(img)
    #    savefig("D:\\test1.pdf", draft=True)

    plt.figure("table plot")
    data = np.array([x, np.sin(x), np.cos(x)]).T
    plt.plot(data)

    plt.figure("simple plot")
    plt.subplot(1, 2, 1)
    plt.plot(x, np.tanh(x + np.sin(12 * x)), "g-", label="Tanh")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(x, np.sinh(x), "r:", label="SinH")
    #    savefig("D:\\test2.pdf")
    #    savefig("D:\\test2.png")
    plt.show()

    plt.figure("semilogx")
    plt.semilogx(x, np.sin(12 * x), "g-")
    plt.show()

    plt.figure("plotyy")
    plt.plotyy(x, np.sin(x), x, np.cos(x))
    plt.ylabel("sinus", "cosinus")
    plt.show()

    plt.figure("hist")

    data = normal(0, 1, (2000,))
    plt.hist(data)
    plt.show()

    plt.figure("pcolor 1")
    r = np.linspace(1.0, 16, 100)
    th = np.linspace(0.0, np.pi, 100)
    R, TH = np.meshgrid(r, th)
    X = R * np.cos(TH)
    Y = R * np.sin(TH)
    Z = 4 * TH + R
    plt.pcolor(X, Y, Z)

    plt.figure("pcolor 2")
    plt.pcolor(Z)
    plt.hot()  # pylint: disable=no-member
    plt.show()


if __name__ == "__main__":
    test_pyplot()
