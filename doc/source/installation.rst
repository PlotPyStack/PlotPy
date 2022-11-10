Installation
============

Dependencies
------------

Requirements:

    * Python 3.6
    * PyQt5 5.x (x>=5)
    * PythonQwt >=0.5
    * NumPy
    * SciPy
    * Pillow
    
Optional Python modules:

    * h5py (HDF5 files I/O)
    * cx_Freze or py2exe (application deployment on Windows platforms)
    * spyderlib 2.1 for Sift embedded Python console
    * pydicom >=0.9.3 for DICOM files I/O features

Other optional modules for developers:

    * gettext (text translation support)

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

Help and support
----------------

External resources:

    * Bug reports and feature requests: `GitHub`_
    * Help, support and discussions around the project: `GoogleGroup`_

.. _GitHub: https://github.com/PierreRaybaut/guiqwt
.. _GoogleGroup: http://groups.google.fr/group/guidata_guiqwt
