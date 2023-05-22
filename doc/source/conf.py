# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath("."))

# -- Imports -----------------------------------------------------
# patch some classes inherit from int to avoid sphinx warnings
from qtpy import QtWidgets as QW

# -- Project information -----------------------------------------------------

project = "Plotpy"
copyright = "2018, CEA"
author = "CEA"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = "0"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = "1.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.imgmath",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = [".rst", ".md"]
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``["localtoc.html", "relations.html", "sourcelink.html",
# "searchbox.html"]``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "Plotpydoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    #
    # "papersize": "letterpaper",
    # The font size ("10pt", "11pt" or "12pt").
    #
    # "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    #
    # "preamble": "",
    # Latex figure (float) alignment
    #
    # "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [(master_doc, "Plotpy.tex", "Plotpy Documentation", "CEA", "manual")]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "plotpy", "Plotpy Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
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


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "qwt": ("https://pythonhosted.org/PythonQwt/", None),
    "matplotlib": ("https://matplotlib.org/", None),
}

# Ensure all internal links are valid
nitpicky = True

# Do not emit a warning for methods inherited from Qwt
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
