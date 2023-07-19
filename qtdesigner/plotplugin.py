# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
plotplugin
==========

A plotpy plot widget plugin for Qt Designer
"""
from plotpy.widgets.qtdesigner import create_qtdesigner_plugin

Plugin = create_qtdesigner_plugin(
    "plotpy", "plotpy.core.plot", "PlotWidget", icon="curve.png"
)
