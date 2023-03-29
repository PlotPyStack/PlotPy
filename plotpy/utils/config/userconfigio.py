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
plotpy.core.config.userconfigio
-------------------------------

Reader and Writer for the serialization of DataSets into .ini files,
using the open-source `userconfig` Python package

UserConfig reader/writer objects
(see :py:mod:`.hdf5io` for another example of reader/writer)
"""


import collections
import datetime

import numpy


class GroupContext:
    """Group context object"""

    def __init__(self, handler, group_name):
        self.handler = handler
        self.group_name = group_name

    def __enter__(self):
        self.handler.begin(self.group_name)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.handler.end(self.group_name)
        return False


class BaseIOHandler:
    """Base I/O Handler with group context manager
    (see plotpy.core.io.hdf5io for another example of this handler usage)"""

    def __init__(self):
        self.option: list = []

    def group(self, group_name):
        """Enter a group. This returns a context manager, to be used with
        the `with` statement"""
        return GroupContext(self, group_name)

    def begin(self, section):
        """

        :param section:
        """
        try:
            print(self.sender())
        except:
            print(self, section)
        self.option.append(section)

    def end(self, section):
        """

        :param section:
        """
        sect = self.option.pop(-1)
        assert sect == section, "Error: {} != {}".format(sect, section)


class UserConfigIOHandler(BaseIOHandler):
    """ """

    def __init__(self, conf, section, option):
        self.conf = conf
        self.section = section
        self.option = [option]

    def begin(self, section):
        """

        :param section:
        """
        self.option.append(section)

    def end(self, section):
        """

        :param section:
        """
        sect = self.option.pop(-1)
        assert sect == section

    def group(self, option):
        """Enter a HDF5 group. This returns a context manager, to be used with
        the `with` statement"""
        return GroupContext(self, option)


class WriterMixin(object):
    def write(self, val, group_name=None):
        """Write value using the appropriate routine depending on value type

        group_name: if None, writing the value in current group"""

        if group_name:
            self.begin(group_name)
        if isinstance(val, bool):
            self.write_bool(val)
        elif isinstance(val, int):
            self.write_int(val)
        elif isinstance(val, float):
            self.write_float(val)
        elif isinstance(val, str):
            self.write_unicode(val)
        elif isinstance(val, str):
            self.write_any(val)
        elif isinstance(val, numpy.ndarray):
            self.write_array(val)
        elif numpy.isscalar(val):
            self.write_any(val)
        elif val is None:
            self.write_none()
        elif isinstance(val, (list, tuple)):
            self.write_sequence(val)
        elif isinstance(val, datetime.datetime):
            self.write_float(val.timestamp())
        elif isinstance(val, datetime.date):
            self.write_int(val.toordinal())
        elif hasattr(val, "serialize") and isinstance(
            val.serialize,
            collections.Callable,  # TODO collections has not attr Callable
        ):
            # The object has a DataSet-like `serialize` method
            val.serialize(self)
        else:
            raise NotImplementedError(
                "cannot serialize {!r} of type {!r}".format(val, type(val))
            )
        if group_name:
            self.end(group_name)


class UserConfigWriter(UserConfigIOHandler, WriterMixin):
    def write_any(self, val):
        """

        :param val:
        """
        option = "/".join(self.option)
        self.conf.set(self.section, option, val)

    write_bool = write_int = write_float = write_any
    write_array = write_sequence = write_str = write_any
    write_unicode = write_str

    def write_none(self):
        """ """
        self.write_any(None)


class UserConfigReader(UserConfigIOHandler):
    def read_any(self):
        """

        :return:
        """
        option = "/".join(self.option)
        val = self.conf.get(self.section, option)
        return val

    read_bool = read_int = read_float = read_any
    read_array = read_sequence = read_none = read_str = read_any
    read_unicode = read_str
