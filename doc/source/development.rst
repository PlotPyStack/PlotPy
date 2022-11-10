===========
Development
===========

How to contribute
=================

Submitting changes
------------------

Due to confidentiality issues, we are not able *for now* to publish any source-
controlled repository (even if we do have a `Mercurial` repository for the 
project). However, this does not prevent motivated users from contributing to 
the project by sending patches applied to the last published version of the 
library. To compensate the absence of source repository, we try to update the 
library as often as we can in order to keep the public source archive version 
as close as possible to the internal development version.

Coding guidelines
-----------------

In general, we try to follow the standard Python coding guidelines, which cover 
all the important coding aspects (docstrings, comments, naming conventions, 
import statements, ...) as described here:

* `Style Guide for Python Code  <http://www.python.org/peps/pep-0008.html>`_  

The easiest way to check that your code is following those guidelines is to 
run `pylint` (a note greater than 8/10 seems to be a reasonable goal).

PyQt5 compatibility
-------------------

In its current implementation, the code base has to be compatible with PyQt5,
which means that the following recommendations should be followed:

* `QVariant` objects must not be used (API #2 compatibility)

* Use exclusively new-style signals and slots

* Read carefully PyQt5 documentation regarding class inheritance behavior: it 
  is quite different than the old PyQt4 implementation. Producing code 
  compatible with both PyQt4 and PyQt5 can be tricky: testing is essential.


Python 3
--------

The minimal supported version is Python 3.6.


Build instructions
==================

To build the wheel, you need:

* Python 3.6
* numpy
* Cython
* A C++ compiler like gcc or `Build Tools for Visual Studio 2017 <https://visualstudio.microsoft.com/downloads/>`_

Then run the following command:
    ``python setup.py bdist_wheel``

It should generate a ``.whl`` file in the :file:`dist` directory.

User of `tox <https://tox.readthedocs.io/en/latest/>`_ can run ``tox -e wheel``
to generate the wheel from a clean virtual environment.


Running unittests
=================

To run the unittests, run ``tox -e tests``.


Code formatting
===============

The code is formatted with `black <https://black.readthedocs.io/en/stable/>`_
and `isort <https://isort.readthedocs.io/en/stable/>`_.

To format the code, you should run ``tox -e quality``.


Deploying tox in an environment without an internet connection
==============================================================

To deploy and use tox without an internet connection, you must first
download all packages.

To do that, run the command ``pip download -d packages -r requirements/bundle.txt``
on a machine that can access internet and runs the same Python and operating system
than the target.
It will download all packages (tox, plotpy's dependencies and testing dependencies) in
the :file:`packages` directory.

Copy the :file:`packages` directory on the target machine (for example in :file:`C:\\PythonPackages\\`).

Then, you must configure pip to tell it where it can find the packages.

Run the two commands:

* ``pip config set global.no-index True``
* ``pip config set global.find-links file:///c:/PythonPackages``

Alternatively, you can also set the environment variables ``PIP_NO_INDEX`` and ``PIP_FIND_LINKS``.

You can now install tox:

* ``pip install tox``
