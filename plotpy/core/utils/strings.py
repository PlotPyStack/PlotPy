"""
Module xxxxx
============

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

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
plotpy.core.utils.strings
-------------------------

The ``plotpy.core.utils.strings`` module provides various utility helper functions 
(pure python).
"""

import locale  # Warning: 2to3 false alarm ("import" fixer)

# Natif impors
import sys


def decode_fs_string(string):
    """Convert string from file system charset to unicode"""
    charset = sys.getfilesystemencoding()
    if charset is None:
        charset = locale.getpreferredencoding()
    return string.decode(charset)


# todo: Py3/I'm really not satisfied with this code even if it's compatible with Py3
def utf8_to_unicode(string):
    """Convert UTF-8 string to Unicode"""
    if not isinstance(string, str):
        string = str(string)
    if not isinstance(string, str):
        try:
            try:
                string = str(string, "utf-8")
            except Exception:
                pass
        except UnicodeDecodeError:
            # This is border line... but we admit here string which has been
            # erroneously encoded in file system charset instead of UTF-8
            string = decode_fs_string(string)
    return string


# Findout the encoding used for stdout or use ascii as default
STDOUT_ENCODING = "ascii"
if hasattr(sys.stdout, "encoding"):
    if sys.stdout.encoding:
        STDOUT_ENCODING = sys.stdout.encoding


def unicode_to_stdout(ustr):
    """convert a unicode string to a byte string encoded
    for stdout output"""
    return ustr.encode(STDOUT_ENCODING, "replace")
