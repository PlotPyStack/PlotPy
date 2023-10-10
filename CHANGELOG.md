# PlotPy Releases #

## Version 1.99.0 (experimental) ##

This version is a preliminary release of the 2.0 series.

New major release:

* New BSD 3-Clause License
* Black code formatting on all Python files
* New automated test suite:
  * Added support for an "unattended" execution mode (Qt loop is bypassed)
  * Added support for pytest fixtures
  * Added support for coverage testing: 71% coverage to date
* Documentation was entirely rewritten using Sphinx
* Reorganized modules: see documentation for details (section "Development")
* Removed "Sift" demo as there is now a far better real-world example with the
  [DataLab](https://codra-ingenierie-informatique.github.io/DataLab/) project
* Integrated more than 30 bug fixes thanks to the merge with the [guiqwt](https://github.com/PlotPyStack/guiqwt) project
* Added dozen of new features thanks to the merge with the [guiqwt]()
* Added other new features:
  * ``widgets.selectdialog.SelectDialog``: a dialog box to select items using a shape tool (segment, rectangle or custom)

## Version 1.2.1 ##

Changes:

* Stabilized version based on PythonQwt
* packaging_helpers.py included into plotpy.core.utils
* some GUI bug fixed
* mscv option added into packaging_helpers.py
* tests improved

## Version 1.0.5 ##

Changes:

* packaging.py renamed into packaging_helpers.py in order to be compatible with Sphinx
