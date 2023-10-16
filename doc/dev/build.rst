How to build, test and deploy
-----------------------------

Build instructions
^^^^^^^^^^^^^^^^^^

To build the wheel, you need:

* Python
* numpy
* Cython
* A C++ compiler like gcc or `Build Tools for Visual Studio 2017 <https://visualstudio.microsoft.com/downloads/>`_

Then run the following command::

    python setup.py bdist_wheel

It should generate a ``.whl`` file in the `dist` directory.


Running unittests
^^^^^^^^^^^^^^^^^

To run the unittests, you need:

* Python
* pytest
* coverage (optional)

Then run the following command::

    pytest plotpy

To run test with coverage support, use the following command::

    pytest -v --cov --cov-report=html plotpy


Code formatting
^^^^^^^^^^^^^^^

The code is formatted with `black <https://black.readthedocs.io/en/stable/>`_
and `isort <https://isort.readthedocs.io/en/stable/>`_.

If you are using `Visual Studio Code <https://code.visualstudio.com/>`_,
the formatting is done automatically when you save a file, thanks to the
project settings in the `.vscode` directory.
