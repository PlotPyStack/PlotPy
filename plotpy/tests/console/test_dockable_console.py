import numpy as np
from guidata.configtools import get_icon
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.misc_from_gui import create_action
from plotpy.widgets.dockable_console import DockableConsole

ns = {
    "np": np,
}
msg = "numpy as np"


class MainWindow(QW.QMainWindow):
    def __init__(self):
        QW.QMainWindow.__init__(self)

        self.setWindowIcon(get_icon("sift.svg"))
        self.console = DockableConsole(None, namespace=ns, message=msg)
        self.add_dockwidget(self.console, _("Console"))

    def add_dockwidget(self, child, title):
        """Add QDockWidget and toggleViewAction"""
        dockwidget, location = child.create_dockwidget(title)
        self.addDockWidget(location, dockwidget)
        return dockwidget

    def _test_connect(self):
        print("test connect")


def test():
    _app = QW.QApplication([])
    main_window = MainWindow()
    console = DockableConsole(None, namespace=ns, message=msg)
    test_console_ac(console)
    main_window.show()
    _app.exec()


def test_console_ac(console):
    test_console_ac = create_action(
        console,
        _("Test console"),
        icon=get_icon("konsole.png"),
        triggered=test_console,
    )
    return test_console_ac


def test_console(self):
    print()
    print("**************************************************************")
    print(_("********************* BEGIN CONSOLE TEST *********************"))
    print("**************************************************************")
    print(_("[TEST CONSOLE from dmc] - An import error : "))
    try:
        import THIS_IS_AN_IMPORT_ERROR
    except ImportError:
        import traceback

        traceback.print_exc()
    print("**************************************************************")
    print(_("************ END CONSOLE TEST - IGNORE THIS ERROR ************"))
    print("**************************************************************")


if __name__ == "__main__":
    test()
