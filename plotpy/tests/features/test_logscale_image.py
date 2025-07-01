# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Logarithmic scale image demo"""

# guitest: show

import numpy as np
from guidata.qthelpers import qt_app_context
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtCore import Qt
from qwt import QwtScaleDiv, QwtScaleDraw, QwtText
from qwt.scale_engine import QwtScaleEngine
from qwt.transform import QwtTransform

from plotpy.items import ImageItem
from plotpy.plot import BasePlot
from plotpy.styles import ImageParam

WAVELENGTHS = ["371nm", "382nm", "393nm", "404nm", "415nm"]
LOG_MIN, LOG_MAX = 1, 10**8


class WavelengthTransform(QwtTransform):
    """Transform class for wavelength axis"""

    def transform(self, value):
        """Transform value"""
        return value

    def invTransform(self, value):
        """Inverse transform value"""
        return value

    def copy(self):
        """Copy transform"""
        return WavelengthTransform()


class WavelengthScaleDraw(QwtScaleDraw):
    """Scale draw class for wavelength axis"""

    def __init__(self, wavelengths):
        super().__init__()
        self.wavelengths = wavelengths
        self.setLabelRotation(45)
        self.setLabelAlignment(Qt.AlignBottom)
        self.setSpacing(10)
        self.setPenWidth(1)

    def label(self, value):
        """Return label for value"""
        idx = int(round(value))
        if 0 <= idx < len(self.wavelengths):
            text = QwtText(self.wavelengths[idx])
            text.setFont(QG.QFont("Arial", 9))
            return text
        return QwtText("")


class WavelengthScaleEngine(QwtScaleEngine):
    """Scale engine class for wavelength axis"""

    def __init__(self, wavelengths):
        super().__init__()
        self.wavelengths = wavelengths
        self.setAttribute(QwtScaleEngine.Floating, False)
        self.setAttribute(QwtScaleEngine.Symmetric, False)
        self.setAttribute(QwtScaleEngine.IncludeReference, True)

    def transformation(self):
        """Return transformation"""
        return WavelengthTransform()

    def autoScale(self, maxNumSteps, x1, x2, stepSize, relativeMargin=0.0):
        """Auto scale axis"""
        return -1, len(self.wavelengths) + 1, 1.0

    def divideScale(self, x1, x2, maxMajor, maxMinor, stepSize=0):
        """Divide scale"""
        x1, x2 = -1, len(self.wavelengths) + 1
        major_ticks = list(range(len(self.wavelengths)))
        return QwtScaleDiv(x1, x2, [], [], major_ticks)


class Log10Transform(QwtTransform):
    """Logarithmic transform class"""

    def __init__(self):
        super().__init__()
        self.LogMin, self.LogMax = LOG_MIN, LOG_MAX

    def bounded(self, value):
        """Clip value to logarithmic range"""
        return np.clip(value, self.LogMin, self.LogMax)

    def copy(self):
        """Copy transform"""
        return Log10Transform()

    def transform(self, value):
        """Transform value"""
        return np.log10(self.bounded(value))

    def invTransform(self, value):
        """Inverse transform value"""
        return 10 ** self.bounded(value)


class Log10ScaleEngine(QwtScaleEngine):
    """Logarithmic scale engine class"""

    def transformation(self):
        return Log10Transform()

    def autoScale(self, maxNumSteps, x1, x2, stepSize, relativeMargin=0.0):
        """Auto scale axis"""
        return LOG_MIN, LOG_MAX, 1

    def divideScale(self, x1, x2, maxMajor, maxMinor, stepSize=0):
        """Divide scale"""
        x1, x2 = LOG_MIN, LOG_MAX
        major_ticks = [10**i for i in range(9)]
        minor_ticks = [
            base * j for i in range(8) for base in [10**i] for j in range(2, 10)
        ]
        return QwtScaleDiv(x1, x2, minor_ticks, [], major_ticks)


class MultiHistogramPlot(QW.QMainWindow):
    """Main window for multi-histogram plot"""

    def __init__(self, rotate=False):
        super().__init__()
        main_widget = QW.QWidget()
        self.setCentralWidget(main_widget)
        layout = QW.QVBoxLayout(main_widget)
        self.rotate = rotate
        self.plot = BasePlot(options={"yreverse": False})
        layout.addWidget(self.plot)
        self.setup_plot()

    def setup_plot(self):
        """Setup plot"""
        self.setup_axes()
        self.num_bins = 1024

        # Initialize data array based on orientation
        self.initialH = np.zeros(
            (self.num_bins, len(WAVELENGTHS))
            if not self.rotate
            else (len(WAVELENGTHS), self.num_bins)
        )

        # Configure image parameters
        param = ImageParam()
        param.lock_position = True

        # Set axis limits based on orientation
        if not self.rotate:
            param.xmin, param.xmax = -0.5, len(WAVELENGTHS) - 0.5
            param.ymin, param.ymax = LOG_MIN, LOG_MAX
        else:
            param.xmin, param.xmax = LOG_MIN, LOG_MAX
            param.ymin, param.ymax = -0.5, len(WAVELENGTHS) - 0.5

        param.colormap = "jet"

        print("Before adding image item: ")
        print(f"param.xmin: {param.xmin}, param.xmax: {param.xmax}, \
                param.ymin: {param.ymin}, param.ymax: {param.ymax}")

        # Create and add image item
        self.hist = ImageItem(self.initialH, param)
        self.plot.set_aspect_ratio(ratio=None, lock=False)  # Prevent overflow errors
        self.plot.add_item(self.hist)

        print("After adding image item: ")
        print(f"param.xmin: {param.xmin}, param.xmax: {param.xmax}, \
                param.ymin: {param.ymin}, param.ymax: {param.ymax}")

    def setup_axes(self):
        """Setup axes"""
        if not self.rotate:
            # Normal orientation
            self.plot.setAxisTitle(BasePlot.X_BOTTOM, "Wavelength")
            self.plot.setAxisTitle(BasePlot.Y_LEFT, "Intensity")
            self.plot.setAxisScaleEngine(BasePlot.Y_LEFT, Log10ScaleEngine())
            self.plot.setAxisScaleEngine(
                BasePlot.X_BOTTOM, WavelengthScaleEngine(WAVELENGTHS)
            )
            self.plot.setAxisScaleDraw(
                BasePlot.X_BOTTOM, WavelengthScaleDraw(WAVELENGTHS)
            )
        else:
            # Rotated orientation
            self.plot.setAxisTitle(BasePlot.X_BOTTOM, "Intensity")
            self.plot.setAxisTitle(BasePlot.Y_LEFT, "Wavelength")
            self.plot.setAxisScaleEngine(BasePlot.X_BOTTOM, Log10ScaleEngine())
            self.plot.setAxisScaleEngine(
                BasePlot.Y_LEFT, WavelengthScaleEngine(WAVELENGTHS)
            )
            self.plot.setAxisScaleDraw(
                BasePlot.Y_LEFT, WavelengthScaleDraw(WAVELENGTHS)
            )


def test_logscale_image():
    """Test logarithmic scale image"""
    with qt_app_context(exec_loop=True):
        window = MultiHistogramPlot(rotate=False)

        # Create logarithmic bins and generate sample data
        log_bins = np.logspace(np.log10(LOG_MIN), np.log10(LOG_MAX), window.num_bins)
        sample_data = np.zeros(
            (len(WAVELENGTHS), window.num_bins - 1)
            if window.rotate
            else (window.num_bins - 1, len(WAVELENGTHS))
        )

        # Generate histogram data for each wavelength
        for i in range(len(WAVELENGTHS)):
            # Generate raw data with multiple peaks
            num_samples = 100000
            mean1, std1 = 10 ** (2 + i * 0.7), 10 ** (2 + i * 0.7) * 0.3
            mean2, std2 = 10 ** (4 + i * 0.5), 10 ** (4 + i * 0.5) * 0.2

            # Create and combine samples
            raw_data = np.abs(
                np.concatenate(
                    [
                        np.random.normal(mean1, std1, num_samples // 2),
                        np.random.normal(mean2, std2, num_samples // 2),
                    ]
                )
            )

            # Create histogram with logarithmic bins
            hist_values, _ = np.histogram(raw_data, bins=log_bins)

            # Store histogram values in appropriate orientation
            if window.rotate:
                sample_data[i, :] = hist_values
            else:
                sample_data[:, i] = hist_values

        # Update the plot with the histogram data
        window.hist.set_data(sample_data)

        print("After setting data: ")
        param = window.hist.param
        print(f"param.xmin: {param.xmin}, param.xmax: {param.xmax}, \
                param.ymin: {param.ymin}, param.ymax: {param.ymax}")

        window.show()


if __name__ == "__main__":
    test_logscale_image()
