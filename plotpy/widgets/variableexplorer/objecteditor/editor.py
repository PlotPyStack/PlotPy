# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Generic object editor dialog
"""


import datetime
import os
import sys

import numpy as np
import PIL.Image
from qtpy import QtCore as QC

from plotpy.widgets import qapplication
from plotpy.widgets.variableexplorer.objecteditor.createdialog import create_dialog


class DialogKeeper(QC.QObject):
    """ """

    def __init__(self):
        QC.QObject.__init__(self)
        self.dialogs = {}
        self.namespace = None

    def set_namespace(self, namespace):
        """

        :param namespace:
        """
        self.namespace = namespace

    def create_dialog(self, dialog, refname, func):
        """

        :param dialog:
        :param refname:
        :param func:
        """
        self.dialogs[id(dialog)] = dialog, refname, func
        dialog.accepted.connect(lambda eid=id(dialog): self.editor_accepted(eid))
        dialog.rejected.connect(lambda eid=id(dialog): self.editor_rejected(eid))
        dialog.show()
        dialog.activateWindow()
        dialog.raise_()

    def editor_accepted(self, dialog_id):
        """

        :param dialog_id:
        """
        dialog, refname, func = self.dialogs[dialog_id]
        self.namespace[refname] = func(dialog)
        self.dialogs.pop(dialog_id)

    def editor_rejected(self, dialog_id):
        """

        :param dialog_id:
        """
        self.dialogs.pop(dialog_id)


keeper = DialogKeeper()


def oedit(obj, modal=True, namespace=None):
    """Edit the object 'obj' in a GUI-based editor and return the edited copy
    (if Cancel is pressed, return None)

    The object 'obj' is a container

    Supported container types:
    dict, list, tuple, str/unicode or numpy.array

    (instantiate a new QApplication if necessary,
    so it can be called directly from the interpreter)
    """

    app = qapplication()

    if modal:
        obj_name = ""
    else:
        assert isinstance(obj, str)
        obj_name = obj
        if namespace is None:
            namespace = globals()
        keeper.set_namespace(namespace)
        obj = namespace[obj_name]
        # keep QApplication reference alive in the Python interpreter:
        namespace["__qapp__"] = app

    result = create_dialog(obj, obj_name)
    if result is None:
        return
    dialog, end_func = result

    if modal:
        if dialog.exec_():
            return end_func(dialog)
    else:
        keeper.create_dialog(dialog, obj_name, end_func)

        if os.name == "nt":
            app.exec_()


# ==============================================================================
# Tests
# ==============================================================================
def test():
    """Run object editor test"""

    data = np.random.random_integers(255, size=(100, 100)).astype("uint8")
    image = PIL.Image.fromarray(data)
    example = {
        "str": "kjkj kj k j j kj k jkj",
        "list": [1, 3, 4, "kjkj", None],
        "dict": {"d": 1, "a": np.random.rand(10, 10), "b": [1, 2]},
        "float": 1.2233,
        "array": np.random.rand(10, 10),
        "image": image,
        "date": datetime.date(1945, 5, 8),
        "datetime": datetime.datetime(1945, 5, 8),
    }
    image = oedit(image)

    class Foobar(object):
        """ """

        def __init__(self):
            self.text = "toto"

    foobar = Foobar()

    print(oedit(foobar))  # spyder: test-skip
    print(oedit(example))  # spyder: test-skip
    print(oedit(np.random.rand(10, 10)))  # spyder: test-skip
    print(oedit(oedit.__doc__))  # spyder: test-skip
    print(example)  # spyder: test-skip


if __name__ == "__main__":

    def catch_exceptions(type, value, traceback):
        """Méthode custom pour récupérer les exceptions de la boucle Qt."""
        system_hook(type, value, traceback)
        sys.exit(1)

    system_hook = sys.excepthook
    sys.excepthook = catch_exceptions
    test()
