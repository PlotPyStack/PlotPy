# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Curve fitting tools"""

# guitest: show

import numpy as np

from plotpy.widgets.fit import FitParam, guifit


def test_fit():
    """Test the curve fitting tool"""
    x = np.linspace(-10, 10, 1000)
    y = np.cos(1.5 * x) + np.random.rand(x.shape[0]) * 0.2

    def fit(x, params):
        a, b = params
        return np.cos(b * x) + a

    a = FitParam("Offset", 0.7, -1.0, 1.0)
    b = FitParam("Frequency", 1.2, 0.3, 3.0, logscale=True)
    params = [a, b]
    values = guifit(x, y, fit, params, xlabel="Time (s)", ylabel="Power (a.u.)")

    print(values)
    print([param.value for param in params])


if __name__ == "__main__":
    test_fit()
