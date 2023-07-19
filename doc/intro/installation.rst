Installation
============

Dependencies
------------

Requirements:

.. include:: ../install_requires.txt

.. note::

    Python 3.11 is the reference for production release

Optional modules for development and testing:

.. include:: ../extras_require-dev.txt

Optional modules for building the documentation:

.. include:: ../extras_require-doc.txt

Installation using the wheel
----------------------------

It's recommended to install plotpy using the precompiled wheel.

You can install plotpy in a dedicated :py:mod:`Virtual environment <venv>`.

On Windows, run:
    ``pip install plotpy-1.0.0-cp36-cp36m-win_amd64.whl``

Manual installation
-------------------

If a wheel is not available for your platform, you must get the source
and run the following command:

All platforms:

    The ``setup.py`` script supports the following extra options for
    optimizing the image scaler engine with SSE2/SSE3 processors:
    ``--sse2`` and ``--sse3``

On GNU/Linux and MacOS platforms:
    ``python setup.py build install``

On Windows platforms with MinGW:
    ``python setup.py build -c mingw32 install``

On Windows platforms with Microsoft Visual C++ compiler:
    ``python setup.py build -c msvc install``
