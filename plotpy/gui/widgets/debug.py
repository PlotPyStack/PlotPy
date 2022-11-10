# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
plotpy.gui.widgets.debug
------------------------

The `debug` module contains some debugging functions (mostly dumping attributes
of Qt Objects).
"""

from __future__ import print_function

import io

from plotpy.gui.widgets.ext_gui_lib import QEvent, QImage, QInputEvent, Qt


def buttons_to_str(buttons):
    """Conversion des flags Qt en chaine"""
    string = ""
    if buttons & Qt.LeftButton:
        string += "L"
    if buttons & Qt.MidButton:
        string += "M"
    if buttons & Qt.RightButton:
        string += "R"
    return string


def evt_type_to_str(type):
    """Représentation textuelle d'un type d'événement (debug)"""
    if type == QEvent.MouseButtonPress:
        return "Mpress"
    elif type == QEvent.MouseButtonRelease:
        return "Mrelease"
    elif type == QEvent.MouseMove:
        return "Mmove"
    elif type == QEvent.ContextMenu:
        return "Context"
    else:
        return f"{type:d}"


def print_event(evt):
    """Représentation textuelle d'un événement (debug)"""
    string = ""
    if isinstance(evt, QInputEvent):
        string += evt_type_to_str(evt.type())
        string += "%08x:" % evt.modifiers()
        if hasattr(evt, "buttons"):
            buttons = evt.buttons()
        elif hasattr(evt, "button"):
            buttons = evt.button()
        else:
            buttons = 0
        string += buttons_to_str(buttons)
    if string:
        print(string)
    else:
        print(evt)


def qimage_format(fmt):
    """

    :param fmt:
    :return:
    """
    for attr in dir(QImage):
        if attr.startswith("Format"):
            val = getattr(QImage, attr)
            if val == fmt:
                return attr[len("Format_") :]
    return str(fmt)


def qimage_to_str(img, indent=""):
    """

    :param img:
    :param indent:
    :return:
    """
    fd = io.StringIO()
    print(indent, img, file=fd)
    indent += "  "
    print(indent, "Size:", img.width(), "x", img.height(), file=fd)
    print(indent, "Depth:", img.depth(), file=fd)
    print(indent, "Format", qimage_format(img.format()), file=fd)
    return fd.getvalue()
