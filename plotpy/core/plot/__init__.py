# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

"""
plotpy.core.plot
-----------------------

The `plot` module provides the following features:
    * :py:class:`.plot.PlotManager`: the `plot manager` is an object to
      link `plots`, `panels` and `tools` together for designing highly
      versatile graphical user interfaces
    * :py:class:`.plot.PlotWidget`: a ready-to-use widget for curve/image
      displaying with an integrated and preconfigured `plot manager` providing
      the `item list panel` and curve/image-related `tools`
    * :py:class:`.plot.PlotDialog`: a ready-to-use dialog box for
      curve/image displaying with an integrated and preconfigured `plot manager`
      providing the `item list panel` and curve/image-related `tools`

.. seealso::

    Module :py:mod:`.curve`
        Module providing curve-related plot items and plotting widgets

    Module :py:mod:`.image`
        Module providing image-related plot items and plotting widgets

    Module :py:mod:`.tools`
        Module providing the `plot tools`

    Module :py:mod:`.panels`
        Module providing the `plot panels` IDs

    Module :py:mod:`.baseplot`
        Module providing the `plotpy` plotting widget base class


Class diagrams
~~~~~~~~~~~~~~

Curve-related widgets with integrated plot manager:

.. image:: /images/curve_widgets.png

Image-related widgets with integrated plot manager:

.. image:: /images/image_widgets.png

Building your own plot manager:

.. image:: /images/my_plot_manager.png


Examples
~~~~~~~~

Simple example *without* the `plot manager`:

.. literalinclude:: ../../../tests/gui/filtertest1.py
   :start-after: SHOW

Simple example *with* the `plot manager`:
even if this simple example does not justify the use of the `plot manager`
(this is an unnecessary complication here), it shows how to use it. In more
complex applications, using the `plot manager` allows to design highly versatile
graphical user interfaces.

.. literalinclude:: ../../../tests/gui/filtertest2.py
   :start-after: SHOW

Reference
~~~~~~~~~

.. autoclass:: PlotManager
   :members:
   :inherited-members:
.. autoclass:: BasePlotWidget
   :members:
.. autoclass:: PlotWidget
   :members:
.. autoclass:: PlotWidgetMixin
   :members:
.. autoclass:: PlotDialog
   :members:
.. autoclass:: PlotWindow
   :members:

"""
