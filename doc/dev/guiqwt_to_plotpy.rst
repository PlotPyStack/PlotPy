How to migrate from guiqwt
--------------------------

This section describes the steps to migrate python code using guiqwt to plotpy.

Updating the imports
^^^^^^^^^^^^^^^^^^^^

The following table gives the equivalence between guiqwt and plotpy classes.

For most of them, the change in the module path is the only difference (only
the import statement have to be updated in your client code). For others, the
third column of this table gives more details about the changes that may be
required in your code.

.. csv-table:: Compatibility table
    :file: guiqwt_to_plotpy.csv

Generic PlotWidgets
^^^^^^^^^^^^^^^^^^^

The Curve and Image plot widgets/dialogs/windows classes have been merged
into generic classes capable of handling both plot items types.

As a consequence :

* The ``CurvePlot`` and ``ImagePlot`` classes have been removed.
  If you are using them in your code, you can replace them by the
  :py:class:`.BasePlot` class which takes only one argument for configuration,
  named `options` (a :py:class:`.BasePlotOptions` instance). Choosing between
  curve and image plot is now done by setting the `type` attribute of the
  plot options (that may be set to ``'curve'`` or ``'image'`` for example).
  See also the `Minor changes to the BasePlot class`_ section.

* The ``CurveWidget`` and ``ImageWidget`` classes have been merged into the new
  class :py:class:`.PlotWidget`. If you are using them in your code,
  you can replace them by the :py:class:`.PlotWidget` class, which takes only one
  argument for configuration, named `options` (a :py:class:`.PlotOptions` instance).
  Choosing between curve and image plot is now done by setting the `type` attribute
  of the plot options  (that may be set to ``'curve'`` or ``'image'`` for example).

* The `CurveDialog` and `ImageDialog` classes have been merged into the new class
  :py:class:`.PlotDialog`. If you are using them in your code, you may proceed
  as for the ``CurveWidget`` and ``ImageWidget`` classes.

* The ``CurveWindow`` and ``ImageWindow`` classes have been merged into the new class
  :py:class:`.PlotWindow`. If you are using them in your code, you may proceed
  as for the ``CurveWidget`` and ``ImageWidget`` classes.

.. note::

    Instead of setting the `type` plot option attribute to ``'curve'`` or ``'image'``,
    as stated above, you may consider using the ``'auto'`` value or the
    ``'manual'`` value.

See demo script `tests/features/test_plot_types.py`.

Minor changes to the BasePlot class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some small changes of the :py:class:`.BasePlot` class related
to the `Generic PlotWidgets`_ may require some minor adaptation of your code:

* The :py:meth:`.BasePlot.del_all_items` method now has an
  ``except_grid`` keyword argument defaulting to ``True``. This functionality was
  previously only present in child classes starting from ``CurvePlot``,
  and has been merged into the parent class :py:class:`.BasePlot`.
  As a consequence, if you used the :py:class:`.BasePlot` class
  directly (without using ``CurvePlot`` or other child classes), you may want to
  pass ``except_grid=False`` to your
  :py:meth:`.BasePlot.del_all_items` calls.

* Some arguments were added to the constructor of the :py:class:`.BasePlot` class
  (the arguments of the constructors of the old classes ``CurvePlot`` and
  ``ImagePlot`` have been merged): the new `type` of the plot
  (see `Generic PlotWidgets`_), and the arguments of the ``ImagePlot``
  constructor that the ``CurvePlot`` constructor missed : ``zlabel``, ``zunit``,
  ``yreverse``, ``aspect_ratio``, ``lock_aspect_ratio`` and ``force_colorbar_enabled``.
  As a consequence, if you did not use keywords, but positional-only arguments when
  instantiating a ``CurvePlot`` or ``ImagePlot``, you should adapt the new calls to the
  :py:class:`.BasePlot` constructor to meet the new arguments list.

Renamed update_curve and update_image methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``update_image`` method of the classes `BaseImageParam`, `QuadGridParam`
and their subclasses has been renamed to ``update_item``.

The ``update_curve`` method of the classes `CurveParam`, `ErrorBarParam` and
their subclasses has also been renamed to ``update_item``.

This change allows to treat plot items parameters in a more generic way in client code.

Renamed PlotItems fields
^^^^^^^^^^^^^^^^^^^^^^^^

The ``imageparam`` and ``curveparam`` fields of all plot item classes have been
renamed to ``param``.

This change allows to treat curve and image plot items in a more generic way
in client code.

New features
^^^^^^^^^^^^

The following subsections present new features that may help you to simplify
you code using plotpy.

New method for thresholding image item LUTs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The method :py:meth:`plotpy.items.BaseImageItem.set_lut_threshold` has been
added. It allows to set the percentage of outliers to be clipped from the image
histogram values.

This method is available for all image items:

* :py:class:`.ImageItem`
* :py:class:`.XYImageItem`
* :py:class:`.MaskedImageItem`
* :py:class:`.TrImageItem`


New annotation tools registration methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some new methods were added to class :py:class:`.PlotManager`:

* :py:meth:`.PlotManager.register_curve_annotation_tools`:
  register all curve related annotation tools,
* :py:meth:`.PlotManager.register_image_annotation_tools`:
  register all image related annotation tools,
* :py:meth:`.PlotManager.register_all_annotation_tools`:
  register all annotation tools.

You may use those methods to simplify you code if you were previously registering
annotation tools one by one.

See demo script `tests/items/test_annotations.py`.

New contour features
~~~~~~~~~~~~~~~~~~~~

plotpy integrates now a contour detection algorithm, so that plotpy based
applications depending on matplotlib only for this function can drop this
additional dependency.

See demo script `tests/items/test_contour.py`.

MaskedXYImages
~~~~~~~~~~~~~~

You can now use the :py:class:`.MaskedXYImageItem` to apply masks to XYImageItems
(only ImageItems where previously maskable with the class :py:class:`.MaskedImageItem`.

You can use the convenience methods :py:meth:`.PlotBuilder.maskedxyimage` to
help you build such items.

See demo script `tests/items/test_image_masked_xy.py`.

New options added to plot builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``PlotItemBuilder`` factory class has been renamed to :py:class:`.PlotBuilder`,
because it provides not only methods for creating plot items, but also methods
for creating ready-to-use plots.

New methods for creating ready-to-use plots have been added to the class:

* :py:meth:`.PlotBuilder.widget`
* :py:meth:`.PlotBuilder.dialog`
* :py:meth:`.PlotBuilder.window`

The method :py:meth:`.PlotBuilder.contours` has been added, in order to create
contour curves. It returns a list of :py:class:`plotpy.items.ContourItem` objects.

See demo script `tests/items/test_contour.py`.

The new keyword parameter ``alpha_function`` has been added to the methods
:py:meth:`.PlotBuilder.image`, :py:meth:`.PlotBuilder.xyimage`,
:py:meth:`.PlotBuilder.maskedimage`, :py:meth:`.PlotBuilder.maskedxyimage`,
:py:meth:`.PlotBuilder.trimage`, :py:meth:`.PlotBuilder.rgbimage`, and
:py:meth:`.PlotBuilder.quadgrid`. It allows to specify a function to
compute the alpha channel of the image from the data values. The supported
functions are:

* :py:attr:`plotpy.constants.LUTAlpha.NONE` (default)
* :py:attr:`plotpy.constants.LUTAlpha.CONSTANT`
* :py:attr:`plotpy.constants.LUTAlpha.LINEAR`
* :py:attr:`plotpy.constants.LUTAlpha.SIGMOID`
* :py:attr:`plotpy.constants.LUTAlpha.TANH`
* :py:attr:`plotpy.constants.LUTAlpha.STEP`

.. warning:: The ``alpha_mask`` parameter has been removed from the methods
             :py:meth:`.PlotBuilder.image`, :py:meth:`.PlotBuilder.xyimage`,
             :py:meth:`.PlotBuilder.maskedimage`, :py:meth:`.PlotBuilder.maskedxyimage`,
             :py:meth:`.PlotBuilder.trimage`, :py:meth:`.PlotBuilder.rgbimage`, and
             :py:meth:`.PlotBuilder.quadgrid`. If you were using it, you should
             replace it by the new ``alpha_function`` parameter.

The new keyword parameter ``lut_range`` has been added to the methods
:py:meth:`.PlotBuilder.image`, :py:meth:`.PlotBuilder.xyimage`,
:py:meth:`.PlotBuilder.maskedimage`, :py:meth:`.PlotBuilder.maskedxyimage`,
and :py:meth:`.PlotBuilder.trimage`, so you can now avoid to make calls
to set_lut_range after the PlotItem is built.

See demo script `tests/features/test_builder.py`.

The method :py:meth:`.PlotBuilder.image` now accepts
optional ``x`` and ``y`` keyword arguments, to automatically create a
:py:class:`plotpy.items.XYImageItem` instead of a simple
:py:class:`plotpy.items.ImageItem` if needed.

See demo script `tests/features/test_builder.py`.

The method :py:meth:`.PlotBuilder.curve` now accepts
optional ``dx``, ``dy``, ``errorbarwidth``, ``errorbarcap``, ``errorbarmode``,
`errorbaralpha` keyword arguments, to automatically create a
:py:class:`plotpy.items.ErrorBarCurveItem` instead of a simple
:py:class:`plotpy.items.CurveItem` if needed.

See demo script `tests/features/test_builder.py`.

Transformation (translation, rotate, resize) of ImageItem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most ImageItem can now be selected, translated, rotated and resized.

Auto-scaling and shapes
~~~~~~~~~~~~~~~~~~~~~~~

Auto-scaling takes now into account visible shapes
(subclasses of :py:class:`.PolygonShape`).

See demo script `tests/features/test_autoscale_shapes.py`.
