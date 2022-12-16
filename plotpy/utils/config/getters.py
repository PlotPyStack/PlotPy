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

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
plotpy.gui.config.misc
----------------------

The ``plotpy.gui.config.misc`` module provides configuration related tools.
"""
import os

from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtCore import Qt

from plotpy.utils.config.misc import get_image_file_path

IMG_PATH = []


def get_icon(name, default="not_found.png"):
    """
    Construct a QIcon from the file with specified name
    name, default: filenames with extensions
    """
    return QG.QIcon(get_image_file_path(name, default))


def get_image_label(name, default="not_found.png"):
    """
    Construct a QLabel from the file with specified name
    name, default: filenames with extensions
    """
    label = QW.QLabel()
    pixmap = QG.QPixmap(get_image_file_path(name, default))
    label.setPixmap(pixmap)
    return label


def get_image_layout(imagename, text="", tooltip="", alignment=Qt.AlignLeft):
    """
    Construct a QHBoxLayout including image from the file with specified name,
    left-aligned text [with specified tooltip]
    Return (layout, label)
    """
    layout = QW.QHBoxLayout()
    if alignment in (Qt.AlignCenter, Qt.AlignRight):
        layout.addStretch()
    layout.addWidget(get_image_label(imagename))
    label = QW.QLabel(text)
    label.setToolTip(tooltip)
    layout.addWidget(label)
    if alignment in (Qt.AlignCenter, Qt.AlignLeft):
        layout.addStretch()
    return layout, label


def get_pen(conf, section, option="", color="black", width=1, style="SolidLine"):
    """
    Construct a QPen from the specified configuration file entry
    conf: UserConfig instance
    section [, option]: configuration entry
    [color]: default color
    [width]: default width
    [style]: default style
    """
    if "pen" not in option:
        option += "/pen"
    color = conf.get(section, option + "/color", color)
    color = QG.QColor(color)
    width = conf.get(section, option + "/width", width)
    style_name = conf.get(section, option + "/style", style)
    style = getattr(Qt, style_name)
    return QG.QPen(color, width, style)


def get_brush(conf, section, option="", color="black", alpha=1.0):
    """
    Construct a QBrush from the specified configuration file entry
    conf: UserConfig instance
    section [, option]: configuration entry
    [color]: default color
    [alpha]: default alpha-channel
    """
    if "brush" not in option:
        option += "/brush"
    color = conf.get(section, option + "/color", color)
    color = QG.QColor(color)
    alpha = conf.get(section, option + "/alphaF", alpha)
    color.setAlphaF(alpha)
    return QG.QBrush(color)


def get_font(conf, section, option=""):
    """
    Construct a QFont from the specified configuration file entry
    conf: UserConfig instance
    section [, option]: configuration entry
    """
    if not option:
        option = "font"
    if "font" not in option:
        option += "/font"
    font = QG.QFont()
    if conf.has_option(section, option + "/family/nt"):
        families = conf.get(section, option + "/family/" + os.name)
    elif conf.has_option(section, option + "/family"):
        families = conf.get(section, option + "/family")
    else:
        families = None
    if families is not None:
        if not isinstance(families, list):
            families = [families]
        family = None
        for family in families:
            if font_is_installed(family):
                break
        font.setFamily(family)
    if conf.has_option(section, option + "/size"):
        font.setPointSize(conf.get(section, option + "/size"))
    if conf.get(section, option + "/bold", False):
        font.setWeight(QG.QFont.Bold)
    else:
        font.setWeight(QG.QFont.Normal)
    return font


def font_is_installed(font):
    """Check if font is installed"""
    return [fam for fam in QG.QFontDatabase().families() if str(fam) == font]


MONOSPACE = [
    "Courier New",
    "Bitstream Vera Sans Mono",
    "Andale Mono",
    "Liberation Mono",
    "Monaco",
    "Courier",
    "monospace",
    "Fixed",
    "Terminal",
]


def get_family(families):
    """Return the first installed font family in family list"""
    if not isinstance(families, list):
        families = [families]
    for family in families:
        if font_is_installed(family):
            return family
    else:
        print(f"Warning: None of the following fonts is installed: {families!r}")
        return ""
