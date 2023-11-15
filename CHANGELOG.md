# PlotPy Releases #

## Version 2.0.1 ##

🛠️ Bug fixes:

* Fixed `plotpy.tools.AnnotatedEllipseTool`: `AttributeError` when finalizing the shape

## Version 2.0.0 ##

This version is the first release of the 2.0 series, which is distributed under the
[BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

PlotPy 2.0 is a major release that brings a lot of new features and bug fixes.

When initiated in 2016, PlotPy 1.0 was the result of the merge of two projects (as well
as some other changes, e.g. a redesign of the API):

* [guidata](https://pypi.org/project/guidata/), a Python library generating graphical
  user interfaces for easy dataset editing and display
* [guiqwt](https://pypi.org/project/guiqwt/), a Python library providing efficient 2D
  data-plotting features (curve/image visualization and related tools) for interactive
  computing and signal/image processing application development

With PlotPy 2.0, the [guidata](https://pypi.org/project/guidata/) code base has been
reextracted: PlotPy now relies on [guidata](https://pypi.org/project/guidata/) as a
dependency, like before the merge.

PlotPy 2.0 also integrates all the bug fixes (>30) and new features that were added to
[guiqwt](https://pypi.org/project/guiqwt/) since the merge (i.e. between 2016 and 2023).

Supported versions of Python and Qt bindings have been updated:

* Python: 3.8, 3.9, and 3.10 (3.11 should work too, but will be officially supported
  when dropping support for Python 3.8, to keep a 3-year support period)
* Qt bindings: PyQt5 (even if PyQt6 and PySide6 are not officially supported, efforts
  have been made and will continue to be made to support them)

PlotPy 2.0 is a major release because it also brings a lot of new features:

* `plot.PlotWidget`, `plot.PlotDialog`, and `plot.PlotWindow`: API overhaul
  (simple, more consistent, more flexible, more extensible - see documentation
  for details)
* `plot.SyncPlotWindow`: new class to show multiple plots in a single window,
  in a synchronized way (zoom, pan, etc.)
* `widgets.selectdialog.SelectDialog`: a dialog box to select items using a
  shape tool (segment, rectangle or custom)
* Image lookup table (LUT):
  * Initially, the LUT alpha channel was either constant (input parameter
  `alpha` was a float between 0 and 1) or linearly dependent on the image
  pixel values (when the `alpha_mask` parameter was enabled)
  * Now, the LUT may be either constant (same as before) or dependent on
  the image pixel values but not only linearly: the LUT alpha channel may
  follow a linear, a sigmoid or an hyperbolic tangent function (see the new
  `alpha_function` parameter). The old `alpha_mask` parameter was removed
* Image pixels are now centered on their coordinates:
  * This means that the pixel at row `i` and column `j` is centered on the point
  `(j, i)` (before, the top-left corner of the pixel at row `i` and column `j`
   was centered on the point `(j, i)`)
  * This convention is more consistent with the way images are displayed in other
    scientific image processing tools
  * This is one of the benefits of porting back [guiqwt](https://pypi.org/project/guiqwt/)
    changes since the merge (i.e. between 2016 and 2023)
* New SVG-based shapes:
  * `items.RectangleSVGShape`: rectangle shape based on SVG data or file
  * `items.SquareSVGShape`: square shape based on SVG data or file
  * `items.CircleSVGShape`: circle shape based on SVG data or file
* `builder.PlotBuilder`:
  * Renamed `PlotBuilder` (originally `guiqwt.builder.PlotItemBuilder`)
  * Builder instance is still available using `from plotpy.builder import make`
  * Plot widget creation is now supported:
    * `make.widget()` for `plot.PlotWidget`
    * `make.dialog()` for `plot.PlotDialog`
    * `make.window()` for `plot.PlotWindow`
  * Added support for more plot items:
    * `make.contours()` for generating a list of `items.ContourItem` objects
    * `make.annotated_point()` for `items.AnnotatedPoint`
    * `make.polygon()` for `items.PolygonShape`
    * `make.svg()` for `items.RectangleSVGShape`, `items.SquareSVGShape`,
      and `items.CircleSVGShape`
* Added JSON serialization support for all plot items (curve, image, etc.)

* Brand new documentation, based on Sphinx with links to other projects API, examples
  and tutorials (e.g. on development related topics).
* Black code formatting on all Python files
* New automated test suite:
  * Automatic execution: `--unattended` command line option (Qt loop is bypassed)
  * Test suite based on `pytest`, supporting `pytest-cov` for coverage testing,
    `pytest-xvfb` for headless testing, and `pytest-qt` for Qt testing
  * Added support for Coverage: test coverage improved up to 70%
* Added typing annotations on (almost) all Python files
* Distribution: switched to `pyproject.toml` (still relying on `setuptools` and
  `setup.py` for building Cython/C++ extensions)
* Added code quality configuration files:
  * `.pylintrc`: pylint configuration file
  * `.isort.cfg`: isort configuration file
  * `.coveragerc`: coverage configuration file
* Added Visual Studio Code configuration files:
  * `.vscode/settings.json`: Python interpreter, code formatting, etc.
  * `.vscode/tasks.json`: build, test, etc.
  * `.vscode/launch.json`: run current file, run tests, etc.

PlotPy 2.0 also brings a lot of bug fixes and improvements:

* Handled all Cython/C++ extensions compilation warnings
* Fixed all NumPy deprecation issues (e.g. `numpy.matrix`)
* Fixed (annotated) circle/ellipse item creation/test
* Fixed all documentation build warnings
* Fixed regressions introduced by PlotPy V1 on top of guiqwt:
  * Global references for the Debian package management
  * Major aspect ratio issues:
    * When resizing the plot widget (images were downsized indefinitely)
    * When auto-scaling the plot widget (images were not displayed entirely)
  * `TrImageItem` rotation algorithm
  * Oblique cross-section test
  * About dialog, version informations
* Ported all [guiqwt](https://pypi.org/project/guiqwt/) bug fixes since the merge
  (i.e. between 2016 and 2023):
  * Added support for Visual Studio 2015 and earlier
  * Speeding-up image alpha channel calculation
  * Optimized colormap icon caching
  * X-axis direction and auto-scale
  * Added load test (with a very large number of plot widgets)
  * Coordinates inversion in `EllipseShape`
  * ValueError with levels histogram
  * Various fixes regarding plot item creation, cross-section features,
    PyQt5 support, DICOM support, TIFF support, etc.
  * Etc.
