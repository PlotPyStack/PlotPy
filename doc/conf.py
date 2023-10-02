# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import plotpy  # noqa: E402

# -- Project information -----------------------------------------------------
project = "PlotPy"
copyright = "2018, CEA"
author = "CEA"
version = ""
version = ".".join(plotpy.__version__.split(".")[:2])
release = plotpy.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_qt_documentation",
]
if "htmlhelp" in sys.argv:
    extensions += ["sphinx.ext.imgmath"]
else:
    extensions += ["sphinx.ext.mathjax"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = []
pygments_style = "sphinx"

if "htmlhelp" in sys.argv:
    html_theme = "classic"
else:
    html_theme = "python_docs_theme"
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
autodoc_default_options = {
    "member-order": "bysource",
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "qwt": ("https://pythonqwt.readthedocs.io/en/latest/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "guidata": ("https://guidata.readthedocs.io/en/latest/", None),
    "guiqwt": ("https://guiqwt.readthedocs.io/en/latest/", None),
    "h5py": ("https://docs.h5py.org/en/stable/", None),
}
nitpicky = True

suppress_warnings = [""]
nitpick_ignore_regex = [("py:attr", r"BasePlot.SIG_.*")]
