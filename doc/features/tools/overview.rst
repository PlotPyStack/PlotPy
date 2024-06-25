Overview
--------

A `plot tool` is an object providing various features to a plotting widget
(:py:class:`.BasePlot`):

* Buttons,
* Menus,
* Selection tools,
* Image I/O tools,
* Etc.

Before being used, a tool has to be registered to a plotting widget's manager,
i.e. an instance of the :py:class:`.PlotManager` class (see :ref:`plot`
for more details).

The :py:class:`.BasePlot` widget do not provide any :py:class:`.PlotManager`:
the manager has to be created separately. On the contrary, the ready-to-use widget
:py:class:`.PlotWidget` are higher-level plotting widgets with
integrated manager, tools and panels.

.. seealso::

    :ref:`plot`
        Ready-to-use curve and image plotting widgets and dialog boxes

    :ref:`items`
        Plot items: curves, images, markers, etc.
