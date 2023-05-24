.. _examples:

Examples of plotpy
==================

The test launcher
-----------------

A lot of examples are available in the `plotpy.tests` test module ::

    from plotpy.tests.gui import run
    run()

The two lines above execute the `test launcher`:

.. image:: images/screenshots/__init__.png


Curve plotting
--------------

Basic curve plotting
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/plot.py
   :start-after: SHOW


.. image:: images/screenshots/plot.png


.. _tests-computations:

Computations on curves
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/computations.py
   :start-after: SHOW


.. image:: images/screenshots/computations.png


Curve fitting
-------------

.. literalinclude:: ../../tests/gui/fit.py
   :start-after: SHOW


.. image:: images/screenshots/fit.png


Image visualization
-------------------

Image contrast adjustment
~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/contrast.py
   :start-after: SHOW


.. image:: images/screenshots/contrast.png

Image cross-sections
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/cross_section.py
   :start-after: SHOW


.. image:: images/screenshots/cross_section.png

Transformable images
~~~~~~~~~~~~~~~~~~~~

Affine transforms example on 3000x3000 images (real-time transforms):

.. literalinclude:: ../../tests/gui/transform.py
   :start-after: SHOW


.. image:: images/screenshots/transform.png

Image rectangular filter
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/imagefilter.py
   :start-after: SHOW


.. image:: images/screenshots/imagefilter.png


Histograms
----------

2-D histogram
~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/hist2d.py
   :start-after: SHOW


.. image:: images/screenshots/hist2d.png


Other examples
--------------

Dot Array Demo
~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/dotarraydemo.py
   :start-after: SHOW


.. image:: images/screenshots/dotarraydemo.png

Image plot tools
~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/image_plot_tools.py
   :start-after: SHOW


.. image:: images/screenshots/image_plot_tools.png

Real-time Mandelbrot plotting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/mandelbrot.py
   :start-after: SHOW


.. image:: images/screenshots/mandelbrot.png

Simple application
~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/gui/simple_window.py
   :start-after: SHOW


.. image:: images/screenshots/simple_window.png
