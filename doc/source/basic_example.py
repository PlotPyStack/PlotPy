# -*- coding: utf-8 -*-

# Note: the two following lines are not required
#    if a QApplication has already been created
import plotpy.gui

_app = plotpy.gui.qapplication()

import plotpy.gui.dataset.datatypes as dt
import plotpy.core.dataset.dataitems as di
import plotpy.core.config.config  # load icons


class Processing(dt.DataSetGui):
    """Example"""

    a = di.FloatItem("Parameter #1", default=2.3)
    b = di.IntItem("Parameter #2", min=0, max=10, default=5)
    type = di.ChoiceItem("Processing algorithm", ("type 1", "type 2", "type 3"))


if __name__ == "__main__":
    param = Processing()
    param.edit()
