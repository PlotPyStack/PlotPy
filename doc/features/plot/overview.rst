Overview
--------

Features
^^^^^^^^

The `plot` module provides the following features:

* :py:class:`.PlotManager`: the `plot manager` is an object to
  link `plots`, `panels` and `tools` together for designing highly
  versatile graphical user interfaces

* :py:class:`.PlotWidget`: a ready-to-use widget for curve/image
  displaying with an integrated and preconfigured `plot manager` providing
  the `item list panel` and curve/image-related `tools`

* :py:class:`.PlotDialog`: a ready-to-use dialog box for
  curve/image displaying with an integrated and preconfigured `plot manager`
  providing the `item list panel` and curve/image-related `tools`

* :py:class:`.SyncPlotWindow`: a ready-to-use window for curve/image
  displaying with plot axes synchronization

.. seealso::

    :ref:`items`
        Plot items: curves, images, markers, text, etc.

    :ref:`tools`
        Plot tools: zoom, pan, etc.


Class diagrams
^^^^^^^^^^^^^^

Plot widgets with integrated plot manager:

.. image:: ../../images/plot_widgets.png

Building your own plot manager:

.. image:: ../../images/my_plot_manager.png
