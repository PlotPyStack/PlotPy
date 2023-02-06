# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
GUI-based test launcher
"""

import os
import subprocess
import sys

from guidata.configtools import MONOSPACE, get_family, get_icon
from guidata.widgets.codeeditor import CodeEditor
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from plotpy.config import _
from plotpy.utils.icons import get_std_icon


def get_tests(test_package):
    tests = []
    test_path = os.path.dirname(os.path.realpath(test_package.__file__))
    for fname in sorted(os.listdir(test_path)):
        module_name, ext = os.path.splitext(fname)
        if ext not in (".py", ".pyw"):
            continue
        if not module_name.startswith("_"):
            _temp = __import__(test_package.__name__, fromlist=[module_name])
            test_module = getattr(_temp, module_name)
            test = TestModule(test_module)
            if test.is_visible():
                tests.append(test)
    return tests


class TestModule(object):
    def __init__(self, test_module):
        self.module = test_module
        self.filename = (
            os.path.splitext(os.path.abspath(test_module.__file__))[0] + ".py"
        )
        if not os.path.isfile(self.filename):
            self.filename += "w"

    def is_visible(self):
        return hasattr(self.module, "SHOW") and self.module.SHOW

    def get_description(self):
        doc = self.module.__doc__
        if doc is None or not doc.strip():
            return _("No description available")
        else:
            lines = doc.strip().splitlines()
            format = "<span style='color: #2222FF'><b>{}</b></span>"
            lines[0] = format.format(lines[0])
            return "<br>".join(lines)

    def run(self, args=""):
        # Keep the same sys.path environment in child process:
        # (useful when the program is executed from Spyder, for example)
        os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)

        command = [sys.executable, '"' + self.filename + '"']
        if args:
            command.append(args)
        subprocess.Popen(" ".join(command), shell=True)


class TestPropertiesWidget(QW.QWidget):
    def __init__(self, parent):
        QW.QWidget.__init__(self, parent)
        font = QG.QFont(get_family(MONOSPACE), 10, QG.QFont.Normal)

        info_icon = QW.QLabel()
        icon = get_std_icon("MessageBoxInformation").pixmap(24, 24)
        info_icon.setPixmap(icon)
        info_icon.setFixedWidth(32)
        info_icon.setAlignment(QC.Qt.AlignTop)
        self.desc_label = QW.QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(QC.Qt.AlignTop)
        self.desc_label.setFont(font)
        group_desc = QW.QGroupBox(_("Description"), self)
        layout = QW.QHBoxLayout()
        layout.addWidget(info_icon)
        layout.addWidget(self.desc_label)
        group_desc.setLayout(layout)

        self.editor = CodeEditor(self)
        self.editor.setup_editor(linenumbers=True, font=font)
        self.editor.setReadOnly(True)
        group_code = QW.QGroupBox(_("Source code"), self)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.editor)
        group_code.setLayout(layout)

        self.run_button = QW.QPushButton(
            get_icon("apply.png"), _("Run this script"), self
        )
        self.quit_button = QW.QPushButton(get_icon("exit.png"), _("Quit"), self)
        hlayout = QW.QHBoxLayout()
        hlayout.addWidget(self.run_button)
        hlayout.addStretch()
        hlayout.addWidget(self.quit_button)

        vlayout = QW.QVBoxLayout()
        vlayout.addWidget(group_desc)
        vlayout.addWidget(group_code)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)

    def set_item(self, test):
        self.desc_label.setText(test.get_description())
        self.editor.set_text_from_file(test.filename)


class TestLauncherWindow(QW.QSplitter):
    def __init__(self, package, test_package_name, parent=None):
        QW.QSplitter.__init__(self, parent)
        self.setWindowTitle(_("Tests - {} module").format(package.__name__))
        self.setWindowIcon(get_icon("{}.svg".format(package.__name__), "guidata.svg"))

        if test_package_name is None:
            test_package_name = "{}.tests".format(package.__name__)
        try:
            _temp = __import__(test_package_name)
        except ImportError:
            test_package_name = "plotpy.{}".format(test_package_name)
            _temp = __import__(test_package_name)
        test_package = sys.modules[test_package_name]

        tests = get_tests(test_package)
        listwidget = QW.QListWidget(self)
        listwidget.addItems([os.path.basename(test.filename) for test in tests])

        self.properties = TestPropertiesWidget(self)

        self.addWidget(listwidget)
        self.addWidget(self.properties)

        self.properties.run_button.clicked.connect(
            lambda: tests[listwidget.currentRow()].run()
        )
        self.properties.quit_button.clicked.connect(self.close)
        listwidget.currentRowChanged.connect(
            lambda row: self.properties.set_item(tests[row])
        )
        listwidget.itemActivated.connect(lambda: tests[listwidget.currentRow()].run())
        listwidget.setCurrentRow(0)

        QW.QShortcut(QG.QKeySequence("Escape"), self, self.close)

        self.setSizes([150, 1])
        self.setStretchFactor(1, 1)
        self.resize(QC.QSize(950, 600))
        self.properties.set_item(tests[0])


def run_testlauncher(package, test_package_name=None):
    """Run test launcher"""

    app = QW.QApplication([])
    win = TestLauncherWindow(package, test_package_name)
    win.show()
    app.exec_()
