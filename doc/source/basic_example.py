# -*- coding: utf-8 -*-

# Note: the two following lines are not required
#    if a QApplication has already been created
import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt

import plotpy.config  # load icons
import plotpy.widgets

_app = plotpy.widgets.qapplication()


class Processing(dt.DataSet):
    """Example"""

    a = di.FloatItem("Parameter #1", default=2.3)
    b = di.IntItem("Parameter #2", min=0, max=10, default=5)
    type = di.ChoiceItem("Processing algorithm", ("type 1", "type 2", "type 3"))


if __name__ == "__main__":
    param = Processing()
    param.edit()
