Examples of plotpy.core
=======================

Basic example
-------------

Source code : ::

 import plotpy.core.dataset.datatypes as dt
 import plotpy.core.dataset.dataitems as di

 class Processing(dt.DataSet):
     """Example"""
     a = di.FloatItem("Parameter #1", default=2.3)
     b = di.IntItem("Parameter #2", min=0, max=10, default=5)
     type = di.ChoiceItem("Processing algorithm",
                          ("type 1", "type 2", "type 3"))

 param = Processing()
 param.text_edit()

Output :

.. image:: images/basic_example.png

Assigning values to data items or using these values is very easy : ::

 param.a = 5.34
 param.type = "type 3"
 print("a*b =", param.a*param.b)


Other examples
--------------

A lot of examples are available in the `tests` test module ::

    from plotpy.tests.scripts import run
    run()

The two lines above execute the `tests launcher` :

.. image:: images/screenshots/__init__.png

All `plotpy.core` items demo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/scripts/all_items.py
   :start-after: guitest:


.. image:: images/screenshots/all_items.png

All (GUI-related) `plotpy.core` features demo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/scripts/all_features.py
   :start-after: guitest:


.. image:: images/screenshots/all_features.png

Embedding plotpy.core objects in GUI layouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/scripts/editgroupbox.py
   :start-after: guitest:


.. image:: images/screenshots/editgroupbox.png

Data item groups and group selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/scripts/bool_selector.py
   :start-after: guitest:


.. image:: images/screenshots/bool_selector.png

Activable data sets
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/scripts/activable_dataset.py
   :start-after: guitest:


.. image:: images/screenshots/activable_dataset.png

Data set groups
~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/scripts/datasetgroup.py
   :start-after: guitest:


.. image:: images/screenshots/datasetgroup.png
