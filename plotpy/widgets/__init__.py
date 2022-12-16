"""
Module plotpy.gui.widgets
=========================

:synopsis:

:moduleauthor: CEA

:platform: All

"""


# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.


def qapplication():
    """
    Return QApplication instance
    Creates it if it doesn't already exist
    """
    from plotpy.gui.widgets.ext_gui_lib import QApplication

    app = QApplication.instance()
    if not app:
        app = QApplication([])
    install_translator(app)
    return app


QT_TRANSLATOR = None


def install_translator(qapp):
    """Install Qt translator to the QApplication instance"""
    global QT_TRANSLATOR
    if QT_TRANSLATOR is None:
        from plotpy.gui.widgets.ext_gui_lib import QLibraryInfo, QLocale, QTranslator

        locale = QLocale.system().name()
        # Qt-specific translator
        qt_translator = QTranslator()
        paths = QLibraryInfo.location(QLibraryInfo.TranslationsPath)

        # in following line, modify qt_ to qtbase_ to switch from pyqt4 to pyqt5
        if qt_translator.load("qtbase_" + locale, paths):
            QT_TRANSLATOR = qt_translator  # Keep reference alive
    if QT_TRANSLATOR is not None:
        qapp.installTranslator(QT_TRANSLATOR)
