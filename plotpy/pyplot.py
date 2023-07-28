# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
Interactive plotting widgets
============================

Overview
--------

The `pyplot` module provides an interactive plotting interface similar to
`Matplotlib`'s, i.e. with MATLAB-like syntax.

The :py:mod:`.pyplot` module was designed to be as close as possible
to the :py:mod:`matplotlib.pyplot` module, so that one could easily switch
between these two modules by simply changing the import statement. Basically,
if :mod:`plotpy` does support the plotting commands called in your script, replacing
``import matplotlib.pyplot`` by ``import plotpy.pyplot`` should be enough, as
shown in the following example:

* Simple example using `matplotlib`::

    import matplotlib.pyplot as plt
    import numpy as np
    x = np.linspace(-10, 10)
    plt.plot(x, x**2, 'r+')
    plt.show()

* Switching from `matplotlib` to :mod:`plotpy` is trivial::

    import plotpy.pyplot as plt # only this line has changed!
    import numpy as np
    x = np.linspace(-10, 10)
    plt.plot(x, x**2, 'r+')
    plt.show()

Examples
--------

>>> import numpy as np
>>> import plotpy.pyplot as plt
>>> plt.ion() # switching to interactive mode
>>> x = np.linspace(-5, 5, 1000)
>>> plt.figure(1)
>>> plt.subplot(2, 1, 1)
>>> plt.plot(x, np.sin(x), "r+")
>>> plt.plot(x, np.cos(x), "g-")
>>> plt.errorbar(x, -1+x**2/20+.2*np.random.rand(len(x)), x/20)
>>> plt.xlabel("Axe x")
>>> plt.ylabel("Axe y")
>>> plt.subplot(2, 1, 2)
>>> img = np.fromfunction(lambda x, y: np.sin((x/200.)*(y/200.)**2), (1000, 1000))
>>> plt.xlabel("pixels")
>>> plt.ylabel("pixels")
>>> plt.zlabel("intensity")
>>> plt.gray()
>>> plt.imshow(img)
>>> plt.figure("plotyy")
>>> plt.plotyy(x, np.sin(x), x, np.cos(x))
>>> plt.ylabel("sinus", "cosinus")
>>> plt.show()

Reference
---------

.. autofunction:: interactive
.. autofunction:: ion
.. autofunction:: ioff

.. autofunction:: figure
.. autofunction:: gcf
.. autofunction:: gca
.. autofunction:: show
.. autofunction:: subplot
.. autofunction:: close

.. autofunction:: title
.. autofunction:: xlabel
.. autofunction:: ylabel
.. autofunction:: zlabel

.. autofunction:: yreverse
.. autofunction:: grid
.. autofunction:: legend
.. autofunction:: colormap

.. autofunction:: savefig

.. autofunction:: plot
.. autofunction:: plotyy
.. autofunction:: semilogx
.. autofunction:: semilogy
.. autofunction:: loglog
.. autofunction:: errorbar
.. autofunction:: hist
.. autofunction:: imshow
.. autofunction:: pcolor
"""

# pylint: disable=unused-import
# pylint: disable=wildcard-import
from plotpy.core.plot.interactive import *
