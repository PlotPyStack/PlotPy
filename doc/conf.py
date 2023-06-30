# -*- coding: utf-8 -*-

from qtpy import QtWidgets as QW

import plotpy

# -- Project information -----------------------------------------------------
project = "Plotpy"
copyright = "2018, CEA"
author = "CEA"
version = ""
version = ".".join(plotpy.__version__.split(".")[:2])
release = plotpy.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.imgmath",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = []
pygments_style = "sphinx"
html_theme = "classic"
html_title = "%s %s Manual" % (project, version)
html_short_title = "%s Manual" % project
html_logo = "images/plotpy-vertical.png"
html_favicon = "_static/favicon.ico"
html_static_path = ["_static"]
htmlhelp_basename = "plotpy"
latex_documents = [(master_doc, "Plotpy.tex", "Plotpy Documentation", "CEA", "manual")]
man_pages = [(master_doc, "plotpy", "Plotpy Documentation", [author], 1)]
texinfo_documents = [
    (
        master_doc,
        "Plotpy",
        "Plotpy Documentation",
        author,
        "Plotpy",
        "One line description of project.",
        "Miscellaneous",
    )
]

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "qwt": ("https://pythonqwt.readthedocs.io/en/latest/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}
nitpicky = True
nitpick_ignore = [
    ("py:class", "QBrush"),
    ("py:class", "QColor"),
    ("py:class", "QFont"),
    ("py:class", "QPaintDevice"),
    ("py:class", "QPainter"),
    ("py:class", "QPen"),
    ("py:class", "QPoint"),
    ("py:class", "QPointF"),
    ("py:class", "QPolygonF"),
    ("py:class", "QPrinter"),
    ("py:class", "QRectF"),
    ("py:class", "QSize"),
    ("py:class", "QSizeF"),
    ("py:class", "QSvgGenerator"),
    ("py:class", "QWidget"),
    ("py:class", "Qt.Alignment"),
    ("py:class", "Qt.Orientation"),
    ("py:class", "Qt.PenStyle"),
    ("py:class", "QwtPlot.LegendPosition"),
    ("py:class", "fload"),
    ("py:class", "qwt.legend.QwtAbstractLegend"),
    ("py:class", "qwt.scale_map.QwtScaleMap"),
    ("py:class", "qwt.scale_widget.QwtScaleWigdet"),
    ("py:data", "QwtPlot.legendDataChanged"),
    ("py:meth", "QwtPlot.autoRefresh"),
    ("py:meth", "QwtPlot.getCanvasMarginsHint"),
    ("py:meth", "QwtPlot.legendChanged"),
    ("py:meth", "QwtPlot.updateCanvasMargins"),
    ("py:meth", "QwtPlot.updateLegend"),
    ("py:meth", "QwtPlotDict.itemList"),
    ("py:meth", "QwtPlotItem.LegendInterest"),
    ("py:meth", "QwtPlotItem.boundingRect"),
    ("py:meth", "QwtPlotItem.getCanvasMarginHint"),
    ("py:meth", "QwtPlotItem.getCanvasMarginsHint"),
    ("py:meth", "QwtPlotItem.legendData"),
    ("py:meth", "QwtPlotItem.updateCanvasMargin"),
    ("py:meth", "QwtPlotItem.updateCanvasMargins"),
    ("py:meth", "QwtPlotItem.updateLegend"),
    ("py:meth", "brush"),
    ("py:meth", "getCanvasMarginHint"),
    ("py:meth", "pen"),
    ("py:meth", "setLabelRotation"),
]


def to_bytes(*args, **kwargs):
    return int.to_bytes(*args, **kwargs)


to_bytes.__doc__ = int.to_bytes.__doc__.replace("`sys.byteorder'", "`sys.byteorder`")


def from_bytes(*args, **kwargs):
    return int.from_bytes(*args, **kwargs)


to_bytes.__doc__ = int.to_bytes.__doc__.replace("`sys.byteorder'", "`sys.byteorder`")

for cls in (
    QW.QWidget.RenderFlag,
    QW.QWidget.PaintDeviceMetric,
    QW.QFrame.Shadow,
    QW.QFrame.Shape,
    QW.QFrame.StyleMask,
    QW.QDialog.DialogCode,
):
    cls.to_bytes = to_bytes
    cls.from_bytes = from_bytes
