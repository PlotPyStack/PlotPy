"""
Module path
===========

:synopsis: give util functions relative to path

:moduleauthor: CEA

:platform: All

"""
import os
import os.path as osp
import sys

SUBFOLDER = "plotpy"


def get_conf_path(filename=None):
    """Return absolute path to the config file with the specified filename."""
    # Define conf_dir
    if sys.platform.startswith("linux"):
        # This makes us follow the XDG standard to save our settings
        # on Linux, as it was requested on Issue 2629
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")
        if not xdg_config_home:
            xdg_config_home = osp.join(get_home_dir(), ".config")
        if not osp.isdir(xdg_config_home):
            os.makedirs(xdg_config_home)
        conf_dir = osp.join(xdg_config_home, SUBFOLDER)
    else:
        conf_dir = osp.join(get_home_dir(), SUBFOLDER)

    # Create conf_dir
    if not osp.isdir(conf_dir):
        os.mkdir(conf_dir)
    if filename is None:
        return conf_dir
    else:
        return osp.join(conf_dir, filename)


def get_home_dir():
    """
    Return user home directory
    """
    try:
        # expanduser() returns a raw byte string which needs to be
        # decoded with the codec that the OS is using to represent
        # file paths.
        path = os.fsdecode(osp.expanduser("~"))
    except Exception:
        path = ""

    if osp.isdir(path):
        return path
    else:
        # Get home from alternative locations
        for env_var in ("HOME", "USERPROFILE", "TMP"):
            # os.environ.get() returns a raw byte string which needs to be
            # decoded with the codec that the OS is using to represent
            # environment variables.
            path = os.fsdecode(os.environ.get(env_var, ""))
            if osp.isdir(path):
                return path
            else:
                path = ""

        if not path:
            raise RuntimeError(
                "Please set the environment variable HOME to "
                "your user/home directory path so Spyder can "
                "start properly."
            )


def getcwd_or_home():
    """Safe version of getcwd that will fallback to home user dir.

    This will catch the error raised when the current working directory
    was removed for an external program.
    """
    try:
        return os.getcwd()
    except OSError:
        print(
            "WARNING: Current working directory was deleted, "
            "falling back to home directory"
        )
        return get_home_dir()


def remove_backslashes(path):
    """Remove backslashes in *path*

    For Windows platforms only.
    Returns the path unchanged on other platforms.

    This is especially useful when formatting path strings on
    Windows platforms for which folder paths may contain backslashes
    and provoke unicode decoding errors in Python 3 (or in Python 2
    when future 'unicode_literals' symbol has been imported)."""
    if os.name == "nt":
        # Removing trailing single backslash
        if path.endswith("\\") and not path.endswith("\\\\"):
            path = path[:-1]
        # Replacing backslashes by slashes
        path = path.replace("\\", "/")
        path = path.replace("/'", "\\'")
    return path
