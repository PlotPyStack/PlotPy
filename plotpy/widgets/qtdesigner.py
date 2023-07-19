# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.widgets.qtdesigner
-----------------------------

The `qtdesigner` module provides QtDesigner helper functions for :mod:`plotpy`:
    * :py:func:`.qtdesigner.loadui`
    * :py:func:`.qtdesigner.compileui`
    * :py:func:`.qtdesigner.create_qtdesigner_plugins`

Reference
~~~~~~~~~

.. autofunction:: loadui
.. autofunction:: compileui
.. autofunction:: create_qtdesigner_plugin
"""

import io

from guidata.configtools import get_icon
from qtpy import QtGui as QG
from qtpy import uic
from qtpy.QtDesigner import QPyDesignerCustomWidgetPlugin


def loadui(fname, replace_class="QwtPlot"):
    """
    Return Widget or Window class from QtDesigner ui file 'fname'

    The loadUiType function (PyQt5.uic) doesn't work correctly with plotpy
    QtDesigner plugins because they don't inheritate from a PyQt5.QtGui
    object.
    """
    uifile_text = open(fname).read().replace(replace_class, "QFrame")
    ui, base_class = uic.loadUiType(io.StringIO(uifile_text))

    class Form(base_class, ui):
        """ """

        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            self.setupUi(self)

    return Form


def compileui(fname, replace_class="QwtPlot"):
    """

    :param fname:
    :param replace_class:
    """
    uifile_text = open(fname).read().replace("QwtPlot", "QFrame")
    uic.compileUi(
        io.StringIO(uifile_text),
        open(fname.replace(".ui", "_ui.py"), "w"),
        pyqt3_wrapper=True,
    )


def create_qtdesigner_plugin(
    group,
    module_name,
    class_name,
    widget_options={},
    icon=None,
    tooltip="",
    whatsthis="",
):
    """Return a custom QtDesigner plugin class

    Example:
    create_qtdesigner_plugin(group = "plotpy", module_name = "plotpy.baseplot",
                             class_name = "PlotWidget",
                             widget_options={"type": PlotType.IMAGE},
                             icon = "image.png", tooltip = "", whatsthis = ""):
    """
    Widget = getattr(__import__(module_name, fromlist=[class_name]), class_name)

    class CustomWidgetPlugin(QPyDesignerCustomWidgetPlugin):
        """ """

        def __init__(self, parent=None):
            QPyDesignerCustomWidgetPlugin.__init__(self)
            self.initialized = False

        def initialize(self, core):
            """

            :param core:
            :return:
            """
            if self.initialized:
                return
            self.initialized = True

        def isInitialized(self):
            """

            :return:
            """
            return self.initialized

        def createWidget(self, parent):
            """

            :param parent:
            :return:
            """
            return Widget(parent, **widget_options)

        def name(self):
            """

            :return:
            """
            return class_name

        def group(self):
            """

            :return:
            """
            return group

        def icon(self):
            """

            :return:
            """
            if icon is not None:
                return get_icon(icon)
            else:
                return QG.QIcon()

        def toolTip(self):
            """

            :return:
            """
            return tooltip

        def whatsThis(self):
            """

            :return:
            """
            return whatsthis

        def isContainer(self):
            """

            :return:
            """
            return False

        def domXml(self):
            """

            :return:
            """
            return f'<widget class="{class_name}" name="{class_name.lower()}" />\n'

        def includeFile(self):
            """

            :return:
            """
            return module_name

    return CustomWidgetPlugin
