.. _motivation:

Motivation
==========

What are PlotPy V2 advantages over PlotPy V1?
---------------------------------------------

From a developer point of view, PlotPy V2 is a major overhaul of PlotPy V1:

* Architecture has been redesigned to be more modular and extensible, and more simple.
* Code quality has been improved introducing `ruff` and typing annotations
  all over the codebase

.. note::
    PlotPy V2 is fully typed using Python type annotations.
    This means that you can use your IDE to get autocompletion and type checking
    (e.g. with VSCode, Visual Studio, etc.).
    This is a major improvement when you write code using PlotPy V2:
    you can rely on the type annotations to understand what a function does
    and what it returns, and your IDE can help you a lot with autocompletion
    and type checking.

To sum up, PlotPy V2 is a more modern and more maintainable codebase that will
allow developers to create plotting applications even more easily than before.

From an end-user point of view, PlotPy V2 is also a significant improvement over
PlotPy V1:

* PlotPy V2 is more stable and more robust thanks to the new `pytest`-based
  automated test suite, with a 70% code coverage.

* PlotPy V2 benefits from the backport of many bug fixes and improvements
  that were made in the guiqwt codebase since PlotPy V1 was released (i.e. from
  2016 to 2023).

* PlotPy V2 provides tons of new features (e.g. alpha function for better transparency
  control, refined contour plots, synchronized multiple plots, selection dialog boxes,
  SVG-based shapes, JSON de/serialization of plot items, new simple way to create
  plotting widgets with `PlotBuilder`, etc.)

* PlotPy V2 will be maintained and improved in the future, while PlotPy V1 is not
  maintained anymore. Some significant improvements are already planned for the
  next releases (e.g. enhanced color maps, new plot items, etc.)

What are PlotPy V2 advantages over guiqwt?
------------------------------------------

Except from the backporting of bug fixes and improvements that were made in the
guiqwt codebase since PlotPy V1 was released (i.e. from 2016 to 2023), PlotPy V2
provides the same advantages over guiqwt as PlotPy V1: see previous section.