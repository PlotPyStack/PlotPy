# ==============================================================================
# Tests
# ==============================================================================
import datetime
import sys

import numpy as np
import PIL

from plotpy.widgets import qapplication
from plotpy.widgets.variableexplorer.objecteditor.editor import oedit

_qapp = qapplication()


class Foobar(object):
    """ """

    def __init__(self):
        self.text = "toto"


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

    foobar = Foobar()

    oedit(foobar)
    oedit(example)
    oedit(np.random.rand(10, 10))
    oedit(oedit.__doc__)


if __name__ == "__main__":

    def catch_exceptions(type, value, traceback):
        """Méthode custom pour récupérer les exceptions de la boucle Qt."""
        system_hook(type, value, traceback)
        sys.exit(1)

    system_hook = sys.excepthook
    sys.excepthook = catch_exceptions
    test()
