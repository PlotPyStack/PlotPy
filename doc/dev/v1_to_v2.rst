How to migrate from plotpy V1
-----------------------------

This section describes the steps to migrate python code using plotpy V1 to plotpy V2.

Updating the imports
^^^^^^^^^^^^^^^^^^^^

The following table gives the equivalence between plotpy V1 and plotpy V2 classes.

For most of them, the change in the module path is the only difference (only
the import statement have to be updated in your client code). For others, the
third column of this table gives more details about the changes that may be
required in your code.

.. csv-table:: Compatibility table
    :file: v1_to_v2.csv

New options added to item builder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The method :py:meth:`.PlotItemBuilder.contours` has been added, in order to create
contour curves. It returns a list of :py:class:`plotpy.core.items.ContourShape` objects.

See demo script `tests/gui/test_contour.py`.

The new keyword parameter ``alpha_function`` has been added to the methods
:py:meth:`.PlotItemBuilder.image`, :py:meth:`.PlotItemBuilder.xyimage`,
:py:meth:`.PlotItemBuilder.maskedimage`, :py:meth:`.PlotItemBuilder.maskedxyimage`,
:py:meth:`.PlotItemBuilder.trimage`, :py:meth:`.PlotItemBuilder.rgbimage`, and
:py:meth:`.PlotItemBuilder.quadgrid`. It allows to specify a function to
compute the alpha channel of the image from the data values. The supported
functions are:

* :py:attr:`plotpy.core.builder.LUTAlpha.NONE` (default)
* :py:attr:`plotpy.core.builder.LUTAlpha.CONSTANT`
* :py:attr:`plotpy.core.builder.LUTAlpha.LINEAR`
* :py:attr:`plotpy.core.builder.LUTAlpha.SIGMOID`
* :py:attr:`plotpy.core.builder.LUTAlpha.TANH`

.. warning:: The ``alpha_mask`` parameter has been removed from the methods
             :py:meth:`.PlotItemBuilder.image`, :py:meth:`.PlotItemBuilder.xyimage`,
             :py:meth:`.PlotItemBuilder.maskedimage`, :py:meth:`.PlotItemBuilder.maskedxyimage`,
             :py:meth:`.PlotItemBuilder.trimage`, :py:meth:`.PlotItemBuilder.rgbimage`, and
             :py:meth:`.PlotItemBuilder.quadgrid`. If you were using it, you should
             replace it by the new ``alpha_function`` parameter.
