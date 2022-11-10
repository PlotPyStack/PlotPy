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
plotpy.core.utils.datetime
--------------------------

The ``plotpy.core.utils`` module provides various utility helper functions
(pure python).
"""


import time


def localtime_to_isodate(time_struct):
    """Convert local time to ISO date"""
    s = time.strftime("%Y-%m-%d %H:%M:%S ", time_struct)
    s += "%+05d" % time.timezone
    return s


def isodate_to_localtime(datestr):
    """Convert ISO date to local time"""
    return time.strptime(datestr[:16], "%Y-%m-%d %H:%M:%S")


class FormatTime(object):
    """Helper object that substitute as a string to
    format seconds into (nn H mm min ss s)"""

    def __init__(self, hours_fmt="%d H ", min_fmt="%d min ", sec_fmt="%d s"):
        self.sec_fmt = sec_fmt
        self.hours_fmt = hours_fmt
        self.min_fmt = min_fmt

    def __mod__(self, val):
        val = val[0]
        hours = val // 3600.0
        minutes = (val % 3600.0) // 60
        seconds = val % 60.0
        if hours:
            return (
                (self.hours_fmt % hours)
                + (self.min_fmt % minutes)
                + (self.sec_fmt % seconds)
            )
        elif minutes:
            return (self.min_fmt % minutes) + (self.sec_fmt % seconds)
        else:
            return self.sec_fmt % seconds


format_hms = FormatTime()


class Timer(object):
    """MATLAB-like timer: tic, toc"""

    def __init__(self):
        self.t0_dict = {}

    def tic(self, cat):
        """Starting timer"""
        print(">", cat)
        self.t0_dict[cat] = time.clock()

    def toc(self, cat, msg="delta:"):
        """Stopping timer"""
        print("<", cat, ":", msg, time.clock() - self.t0_dict[cat])


_TIMER = Timer()
tic = _TIMER.tic
toc = _TIMER.toc
