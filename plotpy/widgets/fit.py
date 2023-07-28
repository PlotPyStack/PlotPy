# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Curve fitting widgets
=====================

Overview
--------

The :mod:`.widgets.fit` module provides interactive curve fitting widgets allowing:

* to fit data manually (by moving sliders)
* or automatically (with standard optimization algorithms provided by `scipy`).

The :func:`guifit` function is a factory function that returns a dialog box
allowing to fit data with a given function.

Example
-------

Here is an example of use of the :func:`guifit` function:

.. literalinclude:: ../../plotpy/tests/gui/test_fit.py
   :start-after: guitest:


.. image:: /images/screenshots/fit.png

Reference
---------

.. autofunction:: guifit

.. autoclass:: FitDialog
   :members:
.. autoclass:: FitParam
   :members:
.. autoclass:: AutoFitParam
   :members:
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import guidata
import numpy as np
from guidata.configtools import get_icon
from guidata.dataset.dataitems import (
    BoolItem,
    ChoiceItem,
    FloatItem,
    IntItem,
    StringItem,
)
from guidata.dataset.datatypes import DataSet
from guidata.qthelpers import create_groupbox, exec_dialog
from guidata.utils import restore_dataset, update_dataset
from numpy import inf  # Do not remove this import (used by optimization funcs)
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QWidget  # only to help intersphinx find QWidget
from scipy.optimize import fmin, fmin_bfgs, fmin_cg, fmin_l_bfgs_b, fmin_powell, leastsq

from plotpy.config import _
from plotpy.core.builder import make
from plotpy.core.plot.base import PlotType
from plotpy.core.plot.plotwidget import PlotDialog, PlotWidget

if TYPE_CHECKING:
    from plotpy.core.items.shapes.range import XRangeSelection
    from plotpy.core.panels.base import PanelWidget


class AutoFitParam(DataSet):
    """Automatic fit parameters"""

    xmin = FloatItem("xmin")
    xmax = FloatItem("xmax")
    method = ChoiceItem(
        _("Method"),
        [
            ("simplex", "Simplex"),
            ("powel", "Powel"),
            ("bfgs", "BFGS"),
            ("l_bfgs_b", "L-BFGS-B"),
            ("cg", _("Conjugate Gradient")),
            ("lq", _("Least squares")),
        ],
        default="lq",
    )
    err_norm = StringItem(
        "enorm",
        default=2.0,
        help=_("for simplex, powel, cg and bfgs norm used " "by the error function"),
    )
    xtol = FloatItem(
        "xtol", default=0.0001, help=_("for simplex, powel, least squares")
    )
    ftol = FloatItem(
        "ftol", default=0.0001, help=_("for simplex, powel, least squares")
    )
    gtol = FloatItem("gtol", default=0.0001, help=_("for cg, bfgs"))
    norm = StringItem(
        "norm", default="inf", help=_("for cg, bfgs. inf is max, -inf is min")
    )


class FitParamDataSet(DataSet):
    """Fit parameter dataset"""

    name = StringItem(_("Name"))
    value = FloatItem(_("Value"), default=0.0)
    min = FloatItem(_("Min"), default=-1.0)
    max = FloatItem(_("Max"), default=1.0).set_pos(col=1)
    steps = IntItem(_("Steps"), default=5000)
    format = StringItem(_("Format"), default="%.3f").set_pos(col=1)
    logscale = BoolItem(_("Logarithmic"), _("Scale"))
    unit = StringItem(_("Unit"), default="").set_pos(col=1)


class FitParam:
    """Fit parameters

    Args:
        name (str): name of the parameter
        value (float): value of the parameter
        min (float): minimum value of the parameter
        max (float): maximum value of the parameter
        logscale (bool): if True, the parameter is fitted in logscale. Default is False.
        steps (int): number of steps for the slider. Default is 5000.
        format (str): format of the parameter. Default is "%.3f".
        size_offset (int): size offset of the parameter. Default is 0.
        unit (str): unit of the parameter. Default is "".
    """

    def __init__(
        self,
        name: str,
        value: float,
        min: float,
        max: float,
        logscale: bool = False,
        steps: int = 5000,
        format: str = "%.3f",
        size_offset: int = 0,
        unit: str = "",
    ):
        self.name = name
        self.value = value
        self.min = min
        self.max = max
        self.logscale = logscale
        self.steps = steps
        self.format = format
        self.unit = unit
        self.prefix_label = None
        self.lineedit = None
        self.unit_label = None
        self.slider = None
        self.button = None
        self._widgets = []
        self._size_offset = size_offset
        self._refresh_callback = None
        self.dataset = FitParamDataSet(title=_("Curve fitting parameter"))

    def copy(self) -> FitParam:
        """Return a copy of this fitparam

        Returns:
            FitParam: copy of this fitparam
        """
        return self.__class__(
            self.name,
            self.value,
            self.min,
            self.max,
            self.logscale,
            self.steps,
            self.format,
            self._size_offset,
            self.unit,
        )

    def create_widgets(self, parent: QWidget, refresh_callback: Callable) -> None:
        """Create widgets

        Args:
            parent (QWidget): parent widget
            refresh_callback (Callable): callback function to refresh the plot
        """
        self._refresh_callback = refresh_callback
        self.prefix_label = QW.QLabel()
        font = self.prefix_label.font()
        font.setPointSize(font.pointSize() + self._size_offset)
        self.prefix_label.setFont(font)
        self.button = QW.QPushButton()
        self.button.setIcon(get_icon("settings.png"))
        self.button.setToolTip(
            _("Edit '{name}' fit parameter properties").format(name=self.name)
        )
        self.button.clicked.connect(lambda: self.edit_param(parent))
        self.lineedit = QW.QLineEdit()
        self.lineedit.editingFinished.connect(self.line_editing_finished)
        self.unit_label = QW.QLabel(self.unit)
        self.slider = QW.QSlider()
        self.slider.setOrientation(QC.Qt.Horizontal)
        self.slider.setRange(0, self.steps - 1)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.update(refresh=False)
        self.add_widgets(
            [
                self.prefix_label,
                self.lineedit,
                self.unit_label,
                self.slider,
                self.button,
            ]
        )

    def add_widgets(self, widgets: list[QWidget]) -> None:
        """Add widgets

        Args:
            widgets (list[QWidget]): list of widgets to add
        """
        self._widgets += widgets

    def get_widgets(self) -> list[QWidget]:
        """Get widgets

        Returns:
            list[QWidget]: list of widgets
        """
        return self._widgets

    def set_scale(self, state: int) -> None:
        """Set scale

        Args:
            state (int): state
        """
        self.logscale = state > 0
        self.update_slider_value()

    def set_text(self, fmt: str = None) -> None:
        """Set text

        Args:
            fmt (str): format (default: None)
        """
        style = "<span style='color: #444444'><b>{}</b></span>"
        self.prefix_label.setText(style.format(self.name))
        if self.value is None:
            value_str = ""
        else:
            if fmt is None:
                fmt = self.format
            value_str = fmt % self.value
        self.lineedit.setText(value_str)
        self.lineedit.setDisabled(bool(self.value == self.min and self.max == self.min))

    def line_editing_finished(self):
        """Line editing finished"""
        try:
            self.value = float(self.lineedit.text())
        except ValueError:
            self.set_text()
        self.update_slider_value()
        self._refresh_callback()

    def slider_value_changed(self, int_value: int) -> None:
        """Slider value changed

        Args:
            int_value (int): integer value
        """
        if self.logscale:
            total_delta = np.log10(1 + self.max - self.min)
            self.value = (
                self.min + 10 ** (total_delta * int_value / (self.steps - 1)) - 1
            )
        else:
            total_delta = self.max - self.min
            self.value = self.min + total_delta * int_value / (self.steps - 1)
        self.set_text()
        self._refresh_callback()

    def update_slider_value(self):
        """Update slider value"""
        if self.value is None or self.min is None or self.max is None:
            self.slider.setEnabled(False)
            if self.slider.parent() and self.slider.parent().isVisible():
                self.slider.show()
        elif self.value == self.min and self.max == self.min:
            self.slider.hide()
        else:
            self.slider.setEnabled(True)
            if self.slider.parent() and self.slider.parent().isVisible():
                self.slider.show()
            if self.logscale:
                value_delta = max([np.log10(1 + self.value - self.min), 0.0])
                total_delta = np.log10(1 + self.max - self.min)
            else:
                value_delta = self.value - self.min
                total_delta = self.max - self.min
            intval = int(self.steps * value_delta / total_delta)
            self.slider.blockSignals(True)
            self.slider.setValue(intval)
            self.slider.blockSignals(False)

    def edit_param(self, parent: QWidget) -> None:
        """Edit param

        Args:
            parent (QWidget): parent widget
        """
        update_dataset(self.dataset, self)
        if self.dataset.edit(parent=parent):
            restore_dataset(self.dataset, self)
            if self.value > self.max:
                self.max = self.value
            if self.value < self.min:
                self.min = self.value
            self.update()

    def update(self, refresh: bool = True) -> None:
        """Update

        Args:
            refresh (bool | None): refresh (default: True)
        """
        self.unit_label.setText(self.unit)
        self.slider.setRange(0, self.steps - 1)
        self.update_slider_value()
        self.set_text()
        if refresh:
            self._refresh_callback()


def add_fitparam_widgets_to(
    layout: QW.QGridLayout,
    fitparams: list[FitParam],
    refresh_callback: Callable,
    param_cols: int = 1,
    stretch_col: int = 1,
) -> None:
    """Add fitparam widgets to layout

    Args:
        layout (QGridLayout): layout
        fitparams (list[FitParam]): list of fitparams
        refresh_callback (Callable): refresh callback
        param_cols (int | None): number of columns (default: 1)
        stretch_col (int | None): stretch column (default: 1)
    """
    row_contents = []
    row_nb = 0
    col_nb = 0
    for i, param in enumerate(fitparams):
        param.create_widgets(layout.parent(), refresh_callback)
        widgets = param.get_widgets()
        w_colums = len(widgets) + 1
        row_contents += [
            (widget, row_nb, j + col_nb * w_colums) for j, widget in enumerate(widgets)
        ]
        col_nb += 1
        if col_nb == param_cols:
            row_nb += 1
            col_nb = 0
    for widget, row, col in row_contents:
        layout.addWidget(widget, row, col)
    if fitparams:
        for col_nb in range(param_cols):
            layout.setColumnStretch(stretch_col + col_nb * w_colums, 5)
            if col_nb > 0:
                layout.setColumnStretch(col_nb * w_colums - 1, 1)


class FitWidget(QWidget):
    """Fit widget

    Args:
        parent (QWidget | None): parent widget (default: None)
        param_cols (int | None): number of columns (default: 1)
        legend_anchor (str | None): legend anchor (default: "TR")
        auto_fit (bool | None): auto fit (default: False)
    """

    SIG_TOGGLE_VALID_STATE = QC.Signal(bool)

    def __init__(
        self,
        parent: QWidget = None,
        param_cols: int = 1,
        legend_anchor: str = "TR",
        auto_fit: bool = False,
    ) -> None:
        super().__init__(parent)
        self.x = None
        self.y = None
        self.fitfunc = None
        self.fitargs = None
        self.fitkwargs = None
        self.fitparams = None
        self.autofit_prm = None

        self.data_curve = None
        self.fit_curve = None
        self.legend = None
        self.legend_anchor = legend_anchor
        self.xrange = None
        self.show_xrange = False

        self.param_cols = param_cols
        self.auto_fit_enabled = auto_fit
        self.button_list: list[QW.QPushButton] = []

        self.params_layout: QW.QGridLayout = None
        self.plot_widget: PlotWidget = None

        self.setup_widget()

    def set_plot_widget(self, plot_widget: PlotWidget) -> None:
        """Set plot widget

        Args:
            plot_widget (PlotWidget): plot widget
        """
        self.plot_widget = plot_widget
        plot_widget.plot.SIG_RANGE_CHANGED.connect(self.range_changed)
        self.refresh()

    def resizeEvent(self, event) -> None:
        """Reimplement Qt method

        Args:
            event (QEvent): event
        """
        super().resizeEvent(event)
        if self.plot_widget is not None:
            self.plot_widget.plot.replot()

    def setup_widget(self) -> None:
        """Setup widget"""
        fit_layout = QW.QHBoxLayout()
        self.params_layout = QW.QGridLayout()
        params_group = create_groupbox(
            self, _("Fit parameters"), layout=self.params_layout
        )
        if self.auto_fit_enabled:
            auto_group = self.create_autofit_group()
            fit_layout.addWidget(auto_group)
        fit_layout.addWidget(params_group)
        self.setLayout(fit_layout)

    def create_autofit_group(self) -> QW.QGroupBox:
        """Create autofit group

        Returns:
            QGroupBox: autofit group
        """
        auto_button = QW.QPushButton(get_icon("apply.png"), _("Run"), self)
        auto_button.clicked.connect(self.autofit)
        autoprm_button = QW.QPushButton(get_icon("settings.png"), _("Settings"), self)
        autoprm_button.clicked.connect(self.edit_parameters)
        xrange_button = QW.QPushButton(get_icon("xrange.png"), _("Bounds"), self)
        xrange_button.setCheckable(True)
        xrange_button.toggled.connect(self.toggle_xrange)
        auto_layout = QW.QVBoxLayout()
        auto_layout.addWidget(auto_button)
        auto_layout.addWidget(autoprm_button)
        auto_layout.addWidget(xrange_button)
        self.button_list += [auto_button, autoprm_button, xrange_button]
        return create_groupbox(self, _("Automatic fit"), layout=auto_layout)

    # Public API ---------------------------------------------------------------
    def set_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        fitfunc: Callable = None,
        fitparams: list[FitParam] | None = None,
        fitargs: tuple | None = None,
        fitkwargs: dict | None = None,
    ) -> None:
        """Set fit data

        Args:
            x (numpy.ndarray): x data
            y (numpy.ndarray): y data
            fitfunc (Callable | None): fit function. Defaults to None.
            fitparams (list[FitParam] | None): fit parameters. Defaults to None.
            fitargs (tuple | None): fit args. Defaults to None.
            fitkwargs (dict | None): fit kwargs. Defaults to None.
        """
        if self.fitparams is not None and fitparams is not None:
            self.clear_params_layout()
        self.x = x
        self.y = y
        if fitfunc is not None:
            self.fitfunc = fitfunc
        if fitparams is not None:
            self.fitparams = fitparams
        if fitargs is not None:
            self.fitargs = fitargs
        if fitkwargs is not None:
            self.fitkwargs = fitkwargs
        self.autofit_prm = AutoFitParam(title=_("Automatic fitting options"))
        self.autofit_prm.xmin = x.min()
        self.autofit_prm.xmax = x.max()
        self.compute_imin_imax()
        if self.fitparams is not None and fitparams is not None:
            self.populate_params_layout()
        self.refresh()

    def set_fit_data(
        self,
        fitfunc: Callable,
        fitparams: list[FitParam],
        fitargs: tuple | None = None,
        fitkwargs: dict | None = None,
    ) -> None:
        """Set fit data

        Args:
            fitfunc (Callable): fit function
            fitparams (list[FitParam]): fit parameters
            fitargs (tuple | None): fit args. Defaults to None.
            fitkwargs (dict | None): fit kwargs. Defaults to None.
        """
        if self.fitparams is not None:
            self.clear_params_layout()
        self.fitfunc = fitfunc
        self.fitparams = fitparams
        self.fitargs = fitargs
        self.fitkwargs = fitkwargs
        self.populate_params_layout()
        self.refresh()

    def clear_params_layout(self) -> None:
        """Clear params layout"""
        for i, param in enumerate(self.fitparams):
            for widget in param.get_widgets():
                if widget is not None:
                    self.params_layout.removeWidget(widget)
                    widget.hide()

    def populate_params_layout(self) -> None:
        """Populate params layout"""
        add_fitparam_widgets_to(
            self.params_layout, self.fitparams, self.refresh, param_cols=self.param_cols
        )

    def get_fitfunc_arguments(self) -> tuple[list, dict]:
        """Return fitargs and fitkwargs

        Returns:
            tuple[list, dict]: fitargs and fitkwargs
        """
        fitargs = self.fitargs
        if self.fitargs is None:
            fitargs = []
        fitkwargs = self.fitkwargs
        if self.fitkwargs is None:
            fitkwargs = {}
        return fitargs, fitkwargs

    def refresh(self) -> None:
        """Refresh Fit Tool dialog box"""
        # Update button states
        enable = (
            self.x is not None
            and self.y is not None
            and self.x.size > 0
            and self.y.size > 0
            and self.fitfunc is not None
            and self.fitparams is not None
            and len(self.fitparams) > 0
        )
        for btn in self.button_list:
            btn.setEnabled(enable)
        self.SIG_TOGGLE_VALID_STATE.emit(enable)

        if not enable:
            # Fit widget is not yet configured
            return

        fitargs, fitkwargs = self.get_fitfunc_arguments()
        yfit = self.fitfunc(
            self.x, [p.value for p in self.fitparams], *fitargs, **fitkwargs
        )

        plot = self.plot_widget.plot

        if self.legend is None:
            self.legend = make.legend(anchor=self.legend_anchor)
            plot.add_item(self.legend)

        if self.xrange is None:
            self.xrange = make.range(0.0, 1.0)
            plot.add_item(self.xrange)
        self.xrange.set_range(self.autofit_prm.xmin, self.autofit_prm.xmax)
        self.xrange.setVisible(self.show_xrange)

        if self.data_curve is None:
            self.data_curve = make.curve([], [], _("Data"), color="b", linewidth=2)
            plot.add_item(self.data_curve)
        self.data_curve.set_data(self.x, self.y)

        if self.fit_curve is None:
            self.fit_curve = make.curve([], [], _("Fit"), color="r", linewidth=2)
            plot.add_item(self.fit_curve)
        self.fit_curve.set_data(self.x, yfit)

        plot.replot()
        plot.disable_autoscale()

    def range_changed(
        self, xrange_obj: XRangeSelection, xmin: float, xmax: float
    ) -> None:  # pylint: disable=unused-argument
        """Range changed

        Args:
            xrange_obj (XRangeSelection): xrange object
            xmin (float): xmin
            xmax (float): xmax
        """
        self.autofit_prm.xmin, self.autofit_prm.xmax = xmin, xmax
        self.compute_imin_imax()

    def toggle_xrange(self, state: bool) -> None:
        """Toggle xrange visibility

        Args:
            state (bool): state
        """
        self.xrange.setVisible(state)
        self.plot_widget.plot.replot()
        if state:
            self.plot_widget.plot.set_active_item(self.xrange)
        self.show_xrange = state

    def edit_parameters(self) -> None:
        """Edit fit parameters"""
        if self.autofit_prm.edit(parent=self):
            self.xrange.set_range(self.autofit_prm.xmin, self.autofit_prm.xmax)
            self.plot_widget.plot.replot()
            self.compute_imin_imax()

    def compute_imin_imax(self) -> None:
        """Compute i_min and i_max"""
        self.i_min = self.x.searchsorted(self.autofit_prm.xmin)
        self.i_max = self.x.searchsorted(self.autofit_prm.xmax, side="right")

    def errorfunc(self, params: list[float]) -> np.ndarray:
        """Get error function

        Args:
            params (list[float]): fit parameter values

        Returns:
            numpy.ndarray: error function
        """
        x = self.x[self.i_min : self.i_max]
        y = self.y[self.i_min : self.i_max]
        fitargs, fitkwargs = self.get_fitfunc_arguments()
        return y - self.fitfunc(x, params, *fitargs, **fitkwargs)

    def autofit(self) -> None:
        """Autofit"""
        meth = self.autofit_prm.method
        x0 = np.array([p.value for p in self.fitparams])
        if meth == "lq":
            x = self.autofit_lq(x0)
        elif meth == "simplex":
            x = self.autofit_simplex(x0)
        elif meth == "powel":
            x = self.autofit_powel(x0)
        elif meth == "bfgs":
            x = self.autofit_bfgs(x0)
        elif meth == "l_bfgs_b":
            x = self.autofit_l_bfgs(x0)
        elif meth == "cg":
            x = self.autofit_cg(x0)
        else:
            return
        for v, p in zip(x, self.fitparams):
            p.value = v
        self.refresh()
        for prm in self.fitparams:
            prm.update()

    def get_norm_func(self) -> Callable:
        """Get norm function

        Returns:
            function: norm function
        """
        prm = self.autofit_prm
        err_norm = eval(prm.err_norm)

        def func(params):
            """

            :param params:
            :return:
            """
            err = np.linalg.norm(self.errorfunc(params), err_norm)
            return err

        return func

    def autofit_simplex(self, x0: float) -> np.ndarray:
        """Autofit using simplex

        Args:
            x0 (float): initial value

        Returns:
            numpy.ndarray: fitted values
        """
        prm = self.autofit_prm

        x = fmin(self.get_norm_func(), x0, xtol=prm.xtol, ftol=prm.ftol)
        return x

    def autofit_powel(self, x0: float) -> np.ndarray:
        """Autofit using Powell

        Args:
            x0 (float): initial value

        Returns:
            numpy.ndarray: fitted values
        """
        prm = self.autofit_prm

        x = fmin_powell(self.get_norm_func(), x0, xtol=prm.xtol, ftol=prm.ftol)
        return x

    def autofit_bfgs(self, x0: float) -> np.ndarray:
        """Autofit using BFGS

        Args:
            x0 (float): initial value

        Returns:
            numpy.ndarray: fitted values
        """
        prm = self.autofit_prm

        x = fmin_bfgs(self.get_norm_func(), x0, gtol=prm.gtol, norm=eval(prm.norm))
        return x

    def autofit_l_bfgs(self, x0: float) -> np.ndarray:
        """Autofit using L-BFGS-B

        Args:
            x0 (float): initial value

        Returns:
            numpy.ndarray: fitted values
        """
        prm = self.autofit_prm
        bounds = [(p.min, p.max) for p in self.fitparams]

        x, _f, _d = fmin_l_bfgs_b(
            self.get_norm_func(), x0, pgtol=prm.gtol, approx_grad=1, bounds=bounds
        )
        return x

    def autofit_cg(self, x0: float) -> np.ndarray:
        """Autofit using conjugate gradient

        Args:
            x0 (float): initial value

        Returns:
            numpy.ndarray: fitted values
        """
        prm = self.autofit_prm

        x = fmin_cg(self.get_norm_func(), x0, gtol=prm.gtol, norm=eval(prm.norm))
        return x

    def autofit_lq(self, x0: float) -> np.ndarray:
        """Autofit using leastsq

        Args:
            x0 (float): initial value

        Returns:
            numpy.ndarray: fitted values
        """
        prm = self.autofit_prm

        def func(params: list[float]) -> np.ndarray:
            """Error function

            Args:
                params (list[float]): fit parameter values

            Returns:
                numpy.ndarray: error function
            """
            err = self.errorfunc(params)
            return err

        x, _ier = leastsq(func, x0, xtol=prm.xtol, ftol=prm.ftol)
        return x

    def get_values(self) -> list[float]:
        """Convenience method to get fit parameter values

        Returns:
            list[float]: fit parameter values
        """
        return [param.value for param in self.fitparams]


class FitDialog(PlotDialog):
    """Fit dialog box

    Args:
        wintitle (str | None): window title. Defaults to None.
        icon (str | None): window icon. Defaults to "plotpy.svg".
        edit (bool | None): enable/disable edit menu. Defaults to True.
        toolbar (bool | None): enable/disable toolbar. Defaults to False.
        auto_tools (bool | None): enable/disable auto tools. Defaults to True.
        options (dict | None): plot options. Defaults to None.
        parent (QWidget | None): parent widget. Defaults to None.
        panels (list[PanelWidget] | None): list of panel widgets. Defaults to None.
        param_cols (int | None): number of columns for parameter table.
         Defaults to 1.
        legend_anchor (str | None): legend anchor. Defaults to "TR".
        auto_fit (bool | None): enable/disable auto fit. Defaults to False.
    """

    def __init__(
        self,
        wintitle: str | None = None,
        icon: str = "plotpy.svg",
        edit: bool = True,
        toolbar: bool = False,
        auto_tools: bool = True,
        options: dict | None = None,
        parent: QWidget | None = None,
        panels: list[PanelWidget] | None = None,
        param_cols: int = 1,
        legend_anchor: str = "TR",
        auto_fit: bool = False,
    ):
        super().__init__(
            wintitle=wintitle if wintitle is not None else _("Curve fitting"),
            icon=icon,
            edit=edit,
            toolbar=toolbar,
            auto_tools=auto_tools,
            options=options,
            parent=parent,
            panels=panels,
        )
        self.fit_widget = fitw = FitWidget(
            self,
            param_cols=param_cols,
            legend_anchor=legend_anchor,
            auto_fit=auto_fit,
        )
        fitw.set_plot_widget(self.plot_widget)
        self.add_widget(self.fit_widget)
        ok_btn = self.button_box.button(QW.QDialogButtonBox.Ok)
        self.fit_widget.SIG_TOGGLE_VALID_STATE.connect(ok_btn.setEnabled)
        self.setWindowFlags(QC.Qt.Window)

    def set_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        fitfunc: Callable = None,
        fitparams: list[FitParam] | None = None,
        fitargs: tuple | None = None,
        fitkwargs: dict | None = None,
    ) -> None:
        """Set fit data

        Args:
            x (numpy.ndarray): x data
            y (numpy.ndarray): y data
            fitfunc (Callable | None): fit function. Defaults to None.
            fitparams (list[FitParam] | None): fit parameters. Defaults to None.
            fitargs (tuple | None): fit args. Defaults to None.
            fitkwargs (dict | None): fit kwargs. Defaults to None.
        """
        self.fit_widget.set_data(x, y, fitfunc, fitparams, fitargs, fitkwargs)

    def get_values(self) -> list[float]:
        """Returns fit parameter values

        Returns:
            list[float]: fit parameter values
        """
        return self.fit_widget.get_values()


def guifit(
    x: np.ndarray,
    y: np.ndarray,
    fitfunc: Callable,
    fitparams: list[FitParam] | None = None,
    fitargs: tuple | None = None,
    fitkwargs: dict | None = None,
    wintitle: str | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    param_cols: int = 1,
    auto_fit: bool = True,
    winsize: tuple[int, int] | None = None,
    winpos: tuple[int, int] | None = None,
) -> list[float] | None:
    """GUI-based curve fitting tool

    Args:
        x (numpy.ndarray): x data
        y (numpy.ndarray): y data
        fitfunc (Callable): fit function
        fitparams (list[FitParam] | None): fit parameters. Defaults to None.
        fitargs (tuple | None): fit args. Defaults to None.
        fitkwargs (dict | None): fit kwargs. Defaults to None.
        wintitle (str | None): window title. Defaults to None.
        title (str | None): plot title. Defaults to None.
        xlabel (str | None): x label. Defaults to None.
        ylabel (str | None): y label. Defaults to None.
        param_cols (int | None): number of columns for fit parameters. Defaults to 1.
        auto_fit (bool | None): auto fit. Defaults to True.
        winsize (tuple[int, int] | None): window size. Defaults to None.
        winpos (tuple[int, int] | None): window position. Defaults to None.

    Returns:
        list[float] | None: fit parameter values
    """
    _app = guidata.qapplication()
    win = FitDialog(
        edit=True,
        wintitle=wintitle,
        toolbar=True,
        param_cols=param_cols,
        auto_fit=auto_fit,
        options=dict(title=title, xlabel=xlabel, ylabel=ylabel, type=PlotType.CURVE),
    )
    win.set_data(x, y, fitfunc, fitparams, fitargs, fitkwargs)
    if winsize is not None:
        win.resize(*winsize)
    if winpos is not None:
        win.move(*winpos)
    if exec_dialog(win):
        return win.get_values()


if __name__ == "__main__":
    x = np.linspace(-10, 10, 1000)
    y = np.cos(1.5 * x) + np.random.rand(x.shape[0]) * 0.2

    def fit(x: np.ndarray, params: list[float]) -> np.ndarray:
        """
        Fit function

        Args:
            x (numpy.ndarray): x data
            params (list[float]): fit parameter values

        Returns:
            numpy.ndarray: fit values
        """
        a, b = params
        return np.cos(b * x) + a

    a = FitParam("Offset", 1.0, 0.0, 2.0)
    b = FitParam("Frequency", 1.05, 0.0, 10.0, logscale=True)
    params = [a, b]
    values = guifit(x, y, fit, params, auto_fit=True)
    print(values)
    print([param.value for param in params])
