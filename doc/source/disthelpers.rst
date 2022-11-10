Making executable Windows programs
==================================

Applications developed with Python may be deployed using specialized tools 
like `cx_Freeze` or `py2exe`. These tools work as extensions to Python builtin
`distutils` module and converts Python scripts into executable Windows 
programs which may be executed without requiring a Python installation.

Making such an executable program may be a non trivial task when the script 
dependencies include libraries with data or extensions, such as `PyQt5` or
`plotpy`. This task has been considerably simplified thanks to
the helper functions provided by :py:mod:`plotpy.core.utils.packaging_helpers`.

.. note::

    `cx_freeze` (or `py2exe`) must be installed.
    Run ``pip install -r requirements/create_exe.txt`` to install cx_Freeze
    package.

Example
~~~~~~~

Simple example script named ``simpledialog.pyw`` which is based on `plotpy`:

.. literalinclude:: deployment_example/simpledialog.pyw


The ``create_exe.py`` script may be written as the following:

.. literalinclude:: deployment_example/create_exe.py


Make the Windows executable program by simply running the script::

    python create_exe.py
