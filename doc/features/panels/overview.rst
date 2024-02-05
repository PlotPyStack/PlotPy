Overview
--------

A `plot panel` is a graphical user interface element that interacts with a
`plot` object, `plot items` and `plot tools`.

Panels are objects inheriting from the :py:class:`.PanelWidget` class.

.. seealso::

    :ref:`plot`
        Ready-to-use curve and image plotting widgets and dialog boxes

    :ref:`items`
        Plot items: curves, images, markers, etc.

    :ref:`tools`
        Plot tools: zoom, pan, etc.


The built-in panels are:

* :py:data:`plotpy.constants.ID_ITEMLIST`: `item list` panel
* :py:data:`plotpy.constants.ID_CONTRAST`: `contrast adjustment` panel
* :py:data:`plotpy.constants.ID_XCS`: `X-axis cross section` panel
* :py:data:`plotpy.constants.ID_YCS`: `Y-axis cross section` panel
* :py:data:`plotpy.constants.ID_OCS`: `oblique cross section` panel
* :py:data:`plotpy.constants.ID_LCS`: `line cross section` panel
