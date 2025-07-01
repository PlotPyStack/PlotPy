# -*- coding: utf-8 -*-
import numpy as np
from qtpy.QtCore import QTimer
from qtpy.QtGui import QColor
from qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QWidget,
)

from plotpy.builder import make
from plotpy.plot import PlotOptions, PlotWidget


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


def get_data(variable_size: bool) -> tuple[np.ndarray, np.ndarray]:
    """Compute 1D Gaussian data and add a narrower Gaussian on top with a random
    position and amplitude."""
    size = np.random.randint(10, 200) if variable_size else 100
    amp = 0.3
    x, y = gen_1d_gaussian(size, sigma=10.0, x0=0.0, amp=amp)
    # Choose a random position: x0 has to be in the range [-10.0, 10.0]
    x0 = np.random.uniform(-10.0, 10.0)
    # Choose a random amplitude: a has to be in the range [0.1, 0.5]
    a = np.random.uniform(0.1, 0.7)
    # Add the narrower Gaussian on top
    y += gen_1d_gaussian(size, sigma=4.0, x0=x0, amp=a)[1]
    return x, y


def add_shadow_effect(
    widget: QWidget,
    xoffset: int = 4,
    yoffset: int = 4,
    blur_radius: int = 8,
    color: QColor = QColor(63, 63, 63, 80),
) -> QGraphicsDropShadowEffect:
    shadow = QGraphicsDropShadowEffect()
    shadow.setXOffset(xoffset)
    shadow.setYOffset(yoffset)
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)
    return shadow


class TestWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        plot_widget = PlotWidget(options=PlotOptions("Test Plot", type="curve"))
        self.item = make.curve(
            *get_data(False),
            color="blue",
            marker="o",
            markersize=5,
            markerfacecolor="cyan",
            markeredgecolor="blue",
        )
        self.plot = plot = plot_widget.get_plot()
        plot.add_item(self.item)
        plot.set_active_item(self.item, select=False)

        cb = QCheckBox("test")

        layout.addWidget(plot_widget, 0, 0)
        layout.addWidget(cb, 1, 0)

        add_shadow_effect(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_curve)
        self.timer.start(100)

    def update_curve(self) -> None:
        data = get_data(False)
        self.item.set_data(data[0], data[1])
        self.plot.do_autoscale()


def main():
    app = QApplication([])
    w = QWidget()
    w.setLayout(QGridLayout())
    w.layout().addWidget(TestWidget(), 0, 0)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
