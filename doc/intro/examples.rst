.. _examples:

Examples
========

The test launcher
-----------------

A lot of examples are available in the `plotpy.tests` test module ::

    from plotpy.tests import run
    run()

The two lines above execute the `test launcher`:

.. image:: ../images/screenshots/__init__.png


Curve plotting
--------------

Basic curve plotting
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/items/test_curve.py
   :start-after: guitest:


.. image:: ../images/screenshots/plot.png


.. _tests-computations:

Computations on curves
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/features/test_computations.py
   :start-after: guitest:


.. image:: ../images/screenshots/computations.png


Curve fitting
-------------

.. literalinclude:: ../../plotpy/tests/features/test_fit.py
   :start-after: guitest:


.. image:: ../images/screenshots/fit.png


Image visualization
-------------------

Image contrast adjustment
~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/features/test_contrast.py
   :start-after: guitest:


.. image:: ../images/screenshots/contrast.png

Image cross-sections
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/tools/test_cross_section.py
   :start-after: guitest:


.. image:: ../images/screenshots/cross_section.png

Transformable images
~~~~~~~~~~~~~~~~~~~~

Affine transforms example on 3000x3000 images (real-time transforms):

.. literalinclude:: ../../plotpy/tests/items/test_transform.py
   :start-after: guitest:


.. image:: ../images/screenshots/transform.png

Image rectangular filter
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/features/test_imagefilter.py
   :start-after: guitest:


.. image:: ../images/screenshots/imagefilter.png


Histograms
----------

2-D histogram
~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/items/test_hist2d.py
   :start-after: guitest:


.. image:: ../images/screenshots/hist2d.png


Other examples
--------------

Dot Array Demo
~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/widgets/test_dotarraydemo.py
   :start-after: guitest:


.. image:: ../images/screenshots/dotarraydemo.png

Image plot tools
~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/tools/test_image_plot_tools.py
   :start-after: guitest:


.. image:: ../images/screenshots/image_plot_tools.png

Real-time Mandelbrot plotting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/items/test_mandelbrot.py
   :start-after: guitest:


.. image:: ../images/screenshots/mandelbrot.png

Simple application
~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../plotpy/tests/widgets/test_simple_window.py
   :start-after: guitest:


.. image:: ../images/screenshots/simple_window.png
