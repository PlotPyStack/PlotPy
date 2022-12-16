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
plotpy.core.utils.program
-----

The ``plotpy.core.utils.program`` module provides various utility helper functions
(pure python).
"""

import os
import os.path as osp
import subprocess


class ProgramError(Exception):
    """Exception raised when a shell command failed to execute."""

    pass


def is_program_installed(basename):
    """Return program absolute path if installed in PATH
    Otherwise, return None"""
    for path in os.environ["PATH"].split(os.pathsep):
        abspath = osp.join(path, basename)
        if osp.isfile(abspath):
            return abspath


def alter_subprocess_kwargs_by_platform(**kwargs):
    """
    Given a dict, populate kwargs to create a generally
    useful default setup for running subprocess processes
    on different platforms. For example, `close_fds` is
    set on posix and creation of a new console window is
    disabled on Windows.

    This function will alter the given kwargs and return
    the modified dict.
    """
    kwargs.setdefault("close_fds", os.name == "posix")
    if os.name == "nt":
        CONSOLE_CREATION_FLAGS = 0  # Default value
        # See: https://msdn.microsoft.com/en-us/library/windows/desktop/ms684863%28v=vs.85%29.aspx
        CREATE_NO_WINDOW = 0x08000000
        # We "or" them together
        CONSOLE_CREATION_FLAGS |= CREATE_NO_WINDOW
        kwargs.setdefault("creationflags", CONSOLE_CREATION_FLAGS)
    return kwargs


def run_shell_command(cmdstr, **subprocess_kwargs):
    """
    Execute the given shell command.

    Note that *args and **kwargs will be passed to the subprocess call.

    If 'shell' is given in subprocess_kwargs it must be True,
    otherwise ProgramError will be raised.
    .
    If 'executable' is not given in subprocess_kwargs, it will
    be set to the value of the SHELL environment variable.

    Note that stdin, stdout and stderr will be set by default
    to PIPE unless specified in subprocess_kwargs.

    :str cmdstr: The string run as a shell command.
    :subprocess_kwargs: These will be passed to subprocess.Popen.
    """
    if "shell" in subprocess_kwargs and not subprocess_kwargs["shell"]:
        raise ProgramError(
            'The "shell" kwarg may be omitted, but if ' "provided it must be True."
        )
    else:
        subprocess_kwargs["shell"] = True

    if "executable" not in subprocess_kwargs:
        subprocess_kwargs["executable"] = os.getenv("SHELL")

    for stream in ["stdin", "stdout", "stderr"]:
        subprocess_kwargs.setdefault(stream, subprocess.PIPE)
    subprocess_kwargs = alter_subprocess_kwargs_by_platform(**subprocess_kwargs)
    return subprocess.Popen(cmdstr, **subprocess_kwargs)


def run_program(name, args="", cwd=None, shell=True, wait=False):
    """Run program in a separate process"""
    path = is_program_installed(name)
    if not path:
        raise RuntimeError("Program {} was not found".format(name))
    command = [path]
    if args:
        command.append(args)
    if wait:
        subprocess.call(" ".join(command), cwd=cwd, shell=shell)
    else:
        subprocess.Popen(" ".join(command), cwd=cwd, shell=shell)
