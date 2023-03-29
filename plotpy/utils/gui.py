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
plotpy.utils.gui
--------------------

The ``plotpy.utils.gui`` module provides various utility helper functions
(pure python).
"""


import collections.abc


def assert_interface_supported(klass, iface):
    """Makes sure a class supports an interface"""
    for name, func in list(iface.__dict__.items()):
        if name == "__inherits__":
            continue
        if isinstance(func, collections.abc.Callable):
            assert hasattr(klass, name), "Attribute {} missing from {}".format(
                name, klass
            )
            imp_func = getattr(klass, name)
            imp_code = imp_func.__code__
            code = func.__code__
            imp_nargs = imp_code.co_argcount
            nargs = code.co_argcount
            if imp_code.co_varnames[:imp_nargs] != code.co_varnames[:nargs]:
                assert False, "Arguments of {}.{} differ from interface: {}!={}".format(
                    klass.__name__,
                    imp_func.__name__,
                    imp_code.co_varnames[:imp_nargs],
                    code.co_varnames[:nargs],
                )
        else:
            pass  # should check class attributes for consistency


def assert_interfaces_valid(klass):
    """Makes sure a class supports the interfaces
    it declares"""
    assert hasattr(klass, "__implements__"), "Class doesn't implements anything"
    for iface in klass.__implements__:
        assert_interface_supported(klass, iface)
        if hasattr(iface, "__inherits__"):
            base = iface.__inherits__()
            assert issubclass(klass, base), "{} should be a subclass of {}".format(
                klass, base
            )
