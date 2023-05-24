# -*- coding: utf-8 -*-

import guidata
import guidata.dataset.dataitems as gdi
import guidata.dataset.datatypes as gdt

import plotpy.config  # load icons


class Processing(gdt.DataSet):
    """Example"""

    a = gdi.FloatItem("Parameter #1", default=2.3)
    b = gdi.IntItem("Parameter #2", min=0, max=10, default=5)
    type = gdi.ChoiceItem("Processing algorithm", ("type 1", "type 2", "type 3"))


if __name__ == "__main__":
    # The following line is not required if a QApplication has already been created
    _app = guidata.qapplication()

    param = Processing()
    param.edit()
