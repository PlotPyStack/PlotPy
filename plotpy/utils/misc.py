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
plotpy.core.utils.misc
----------------------

The ``plotpy.core.utils.misc`` module provides various utility helper functions
(pure python).
"""


def min_equals_max(min, max):
    """
    Return True if minimium value equals maximum value
    Return False if not, or if maximum or minimum value is not defined
    """
    return min is not None and max is not None and min == max


def pairs(iterable):
    """A simple generator that takes a list and generates
    pairs [ (l[0],l[1]), ..., (l[n-2], l[n-1])]
    """
    iterator = iter(iterable)
    first = next(iterator)
    while True:
        second = next(iterator)
        yield (first, second)
        first = second


def add_extension(item, value):
    """Add extension to filename
    `item`: data item representing a file path
    `value`: possible value for data item"""
    value = str(value)
    formats = item.get_prop("data", "formats")
    if len(formats) == 1 and formats[0] != "*":
        if not value.endswith("." + formats[0]) and len(value) > 0:
            return value + "." + formats[0]
    return value


def bind(fct, value):
    """
    Returns a callable representing the function "fct" with it"s
    first argument bound to the value

    if g = bind(f,1) and f is a function of x,y,z
    then g(y,z) will return f(1,y,z)
    """

    def callback(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return fct(value, *args, **kwargs)

    return callback


def trace(fct):
    """A decorator that traces function entry/exit
    used for debugging only
    """
    from functools import wraps

    @wraps(fct)
    def wrapper(*args, **kwargs):
        """Tracing function entry/exit (debugging only)"""
        print("enter:", fct.__name__)
        res = fct(*args, **kwargs)
        print("leave:", fct.__name__)
        return res

    return wrapper
