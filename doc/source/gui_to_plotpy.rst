Migrating from guidata and guiqwt to plotpy
===========================================

This section describes the steps to migrate python code using guidata and/or guiqwt to plotpy.

Updating the imports
-----------------------

The following table gives the equivalence between guidata/guiqwt classes and plotpy new classes.

For most classes, the change in the module path is the only difference (only the import statement
have to be updated in your client code). For others, the third column of this table gives more
detail about the needed changes.

.. csv-table:: Compatibility table
    :file: gui_to_plotpy.csv


DataSetGui vs DataSet
---------------------

Since plotpy is usable in non-GUI (script) mode only, the `DataSet` class has been stripped from its
GUI part, that is the `edit()` and `view()` methods which create GUI forms to edit or view the
`DataSet`.

In existing code, the `DataSet` class can be safely replaced by the equivalent class `DataSetGui`.
A new option is to use the `DataSet` (non-GUI) class for non-GUI scripts only.


Generic PlotWidgets
-------------------

The Curve and Image plot widgets/dialogs/windows classes have been merged into generic classes
capable of handling both plot items types.

As a consequence :

    * the `CurvePlot` and `ImagePlot` classes have been removed. If you are using them in your
      code, you can replace them by the :py:class:`.BasePlot` class, and pass to its
      constructor the new keyword `type` with the value :py:attr:`.PlotType.CURVE` or
      :py:attr:`.PlotType.IMAGE` respectively to get the equivalent specialized plot
      component. See also the `Minor changes to the BasePlot class`_ section.
    * the `CurveWidget` and `ImageWidget` classes have been merged into the new class
      :py:class:`.PlotWidget`. If you are using them in your code, you can replace them by the
      :py:class:`.PlotWidget` class, and pass to its constructor an `options` dict with
      the value :py:attr:`.PlotType.CURVE` or :py:attr:`.PlotType.IMAGE` for key `type`. See also
      the `Changes to the PlotWidget class`_ section.
    * the `CurveDialog` and `ImageDialog` classes have been merged into the new class
      :py:class:`.PlotDialog`. If you are using them in your code, you can replace them by the
      :py:class:`.PlotDialog` class, and pass to its constructor an `options` dict with
      the value :py:attr:`.PlotType.CURVE` or :py:attr:`.PlotType.IMAGE` for key `type`.
    * the `CurveWindow` and `ImageWindow` classes have been merged into the new class
      :py:class:`.PlotWindow`. If you are using them in your code, you can replace them by the
      :py:class:`.PlotWindow` class, and pass to its constructor an `options` dict with
      the value :py:attr:`.PlotType.CURVE` or :py:attr:`.PlotType.IMAGE` for key `type`.


.. note::

    Instead of using the `type` keyword with :py:attr:`.PlotType.CURVE` or
    :py:attr:`.PlotType.IMAGE` as stated above, you may consider using the
    :py:attr:`.PlotType.AUTO` or :py:attr:`.PlotType.MANUAL` values if they fit your needs.

See demo script `tests/gui/plot_types.py`.

Minor changes to the BasePlot class
-----------------------------------

Some small changes of the :py:class:`.BasePlot` class related to the `Generic PlotWidgets`_ may
require some minor adaptation of your code :

    * the :py:meth:`.BasePlot.del_all_items` method now has an `except_grid` keyword argument
      defaulting to `True`. This functionality was previously only present in child classes starting
      from `CurvePlot`, and has been merged into the parent class :py:class:`.BasePlot`.
      As a consequence, if you used the :py:class:`.BasePlot` class directly (without using
      `CurvePlot` or other child classes), you may want to pass `except_grid=False` to your
      :py:meth:`.BasePlot.del_all_items` calls.
    * Some arguments were added to the constructor of the :py:class:`.BasePlot` class (the arguments
      of the constructors of the old classes `CurvePlot` and `ImagePlot` have been merged) : the new
      `type` of the plot (see `Generic PlotWidgets`_), and the arguments of the `ImagePlot`
      constructor that the `CurvePlot` constructor missed : `zlabel`, `zunit`, `yreverse`,
      `aspect_ratio`, `lock_aspect_ratio` and `force_colorbar_enabled`.
      As a consequence, if you did not use keywords, but positional-only arguments when
      instantiating a `CurvePlot` or `ImagePlot`, you should adapt the new calls to the
      :py:class:`.BasePlot` constructor to meet the new arguments list.

Changes to the PlotWidget class
-------------------------------------

The architecture of the new :py:class:`.PlotWidget` class (previously `CurveWidget` and
`ImageWidget`) has been changed to be consistent with the :py:class:`.PlotDialog` and
:py:class:`.PlotWindow` classes : they now all inherit directly from the
:py:class:`.PlotWidgetMixin` class.

As a consequence, the many constructor arguments of the :py:class:`.PlotWidget` class have been
replaced by an `options` dictionary. You may have to change your calls accordingly if you used the
old classes `CurveWidget` or `ImageWidget` and replaced them by the :py:class:`.PlotWidget` class.


Renamed update_curve and update_image methods
---------------------------------------------

The `update_image` method of the classes `BaseImageParam`, `QuadGridParam` and their subclasses has
been renamed to `update_item`.

The `update_curve` method of the classes `CurveParam`, `ErrorBarParam` and their subclasses has also
been renamed to `update_item`.

This change allows to treat plot items parameters in a more generic way in client code.

Renamed PlotItems fields
------------------------

The `imageparam` and `curveparam` fields of all plot item classes have been renamed to `param`.

This change allows to treat curve and image plot items in a more generic way in client code.

New features
-------------

The following subsections present new features that may help you to simplify you code using plotpy.

New annotation tools registration methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some new methods were added to classes :py:class:`.PlotWidget`, :py:class:`.PlotDialog` and
:py:class:`.PlotWindow`:

    * :py:meth:`.PlotManager.register_curve_annotation_tools`: register all curve related annotation
      tools,
    * :py:meth:`.PlotManager.register_image_annotation_tools`: register all image related annotation
      tools,
    * :py:meth:`.PlotManager.register_all_annotation_tools`: register all annotation tools.

You may use those methods to simplify you code if you were previously registering annotation tools
one by one.

See demo script `test/gui/annotations.py`.

Integrated spyder components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The spyder interactive python console used by some applications using guiData and/or guiQwt and
by the :ref:`sift example <sift-page>`, as well as some other spyder components (for example the
arrayeditor module) have been integrated directly to the plotpy package.

If your code has spyder as a dependency, you may be able to remove it, and import used classes
from plotpy.console instead of spyder.

For example, you can replace :

.. code-block:: python

    from spyder.widgets.internalshell import InternalShell

by :

.. code-block:: python

    from plotpy.console.widgets.internalshell import InternalShell

New contour function
~~~~~~~~~~~~~~~~~~~~~~~~

plotpy integrates now a contour detection algorithm, so that plotpy based applications depending on
matplotlib only for this function can drop this additional dependency.

See demo script `tests/gui/contour.py`.

MaskedXYImages
~~~~~~~~~~~~~~~~~~~~~~~~

You can now use the :py:class:`.MaskedXYImageItem` to apply masks to XYImageItems (only ImageItems
where previously maskable with the class :py:class:`.MaskedImageItem`.

You can use the convenience methods :py:meth:`.PlotItemBuilder.maskedxyimage` to help you build such
items.

See demo script `tests/gui/image_masked_xy.py`.

New options added to the PlotItemBuilder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The new keyword parameter `lut_range` has been added to the following helper methods :
:py:meth:`.PlotItemBuilder.image`, :py:meth:`.PlotItemBuilder.xyimage`,
:py:meth:`.PlotItemBuilder.maskedimage`, :py:meth:`.PlotItemBuilder.maskedxyimage`,
:py:meth:`.PlotItemBuilder.trimage`, so you can now avoid to make calls to set_lut_range after the
PlotItem is built.

See demo script `tests/gui/builder.py`.

The method :py:meth:`.PlotItemBuilder.image` now accepts optional `x` and `y` keyword arguments, to
automatically create an :py:class:`.XYImageItem` instead of a simple :py:class:`.ImageItem` if
needed.

See demo script `tests/gui/builder.py`.

The method :py:meth:`.PlotItemBuilder.curve` now accepts optional `dx`, `dy`, `errorbarwidth`,
`errorbarcap`, `errorbarmode`, `errorbaralpha` keyword arguments, to automatically create an
:py:class:`.ErrorBarCurveItem` instead of a simple :py:class:`.CurveItem` if needed.

See demo script `tests/gui/builder.py`.

Transformation (translation, rotate, resize) of ImageItem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most ImageItem can now be selected, translated, rotated and resized.
Subclass can inherit from :py:class:`.TransformImageMixin` to simplify the transformation.

Auto-scaling and shapes
~~~~~~~~~~~~~~~~~~~~~~~

Auto-scaling takes now into account visible shapes (subclasses of :py:class:`.PolygonShape`).

See demo script `tests/gui/autoscale_schapes.py`.
