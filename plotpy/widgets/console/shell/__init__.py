# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
spyder.widgets
==============

Widgets defined in this module may be used in any other Qt-based application

They are also used in Spyder through the Plugin interface
(see spyder.plugins)
"""
from plotpy.widgets.console.shell.base import ShellBaseWidget
from plotpy.widgets.console.shell.internal import (
    InternalShell,
    SysOutput,
    WidgetProxy,
    WidgetProxyData,
    create_action,
)
from plotpy.widgets.console.shell.python import PythonShellWidget
