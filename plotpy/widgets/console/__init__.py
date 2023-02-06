"""
MIT License
===========

Copyright (c) 2009- Spyder Project Contributors and others (see AUTHORS.txt)

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
# Console
from plotpy.widgets.console.arraybuilder import (
    NumpyArrayDialog,
    NumpyArrayInline,
    NumpyArrayTable,
)
from plotpy.widgets.console.calltip import CallTipWidget
from plotpy.widgets.console.dochelpers import (
    getargs,
    getargsfromdoc,
    getargsfromtext,
    getargspecfromtext,
    getargtxt,
    getdoc,
    getobj,
    getobjdir,
    getsignaturefromtext,
    getsource,
    isdefined,
)
from plotpy.widgets.console.editortools import PythonCFM
from plotpy.widgets.console.helperwidgets import HelperToolButton
from plotpy.widgets.console.interpreter import Interpreter

# Shell
from plotpy.widgets.console.shell import (
    InternalShell,
    PythonShellWidget,
    ShellBaseWidget,
    SysOutput,
    WidgetProxy,
    WidgetProxyData,
    create_action,
)
from plotpy.widgets.console.syntaxhighlighters import (
    COLOR_SCHEME_KEYS,
    COLOR_SCHEME_NAMES,
    BaseSH,
    OutlineExplorerData,
    PythonSH,
    TextSH,
    any,
    get_color_scheme,
    make_python_patterns,
)
