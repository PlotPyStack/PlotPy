#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script for locked fit parameters feature"""

import numpy as np

from plotpy.widgets.fit import FitParam, guifit


def test_locked_fit():
    """Test the curve fitting tool with locked parameters"""
    # Generate test data: y = cos(1.5*x) + 0.2
    x = np.linspace(-10, 10, 1000)
    true_offset = 0.2
    true_freq = 1.5
    y = np.cos(true_freq * x) + true_offset + np.random.rand(x.shape[0]) * 0.1

    def fit(x, params):
        """Fit function: a + cos(b*x)"""
        a, b = params
        return np.cos(b * x) + a

    # Create fit parameters
    # Lock the frequency parameter at the true value
    a = FitParam("Offset", 0.0, -1.0, 1.0)
    b = FitParam("Frequency", true_freq, 0.3, 3.0, logscale=True, locked=True)

    params = [a, b]

    print("Initial values:")
    print(f"  Offset (unlocked): {a.value}")
    print(f"  Frequency (locked): {b.value}")

    values = guifit(
        x,
        y,
        fit,
        params,
        xlabel="Time (s)",
        ylabel="Amplitude (a.u.)",
        wintitle="Locked Parameter Test",
        auto_fit=True,
    )

    if values:
        print("\nFinal values after fit:")
        print(f"  Offset: {values[0]:.4f} (should be close to {true_offset})")
        print(f"  Frequency: {values[1]:.4f} (should remain {true_freq})")
        print("\nNote: The frequency parameter was locked and should not have changed.")
        print("Only the offset parameter should have been optimized.")


if __name__ == "__main__":
    test_locked_fit()
