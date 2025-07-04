# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

# pylint: disable=C0103

"""
Interactive plot
----------------

The `pyplot` module provides an interactive plotting interface similar to
`Matplotlib`'s, i.e. with MATLAB-like syntax.
"""

import sys

import guidata
import numpy as np
from guidata.configtools import get_icon
from guidata.env import execenv
from guidata.qthelpers import win32_fix_title_bar_background
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy.QtPrintSupport import QPrinter

from plotpy import io
from plotpy._scaler import INTERP_AA, INTERP_LINEAR, INTERP_NEAREST
from plotpy.builder import make
from plotpy.config import _
from plotpy.mathutils.colormap import ALL_COLORMAPS
from plotpy.panels.contrastadjustment import ContrastAdjustment
from plotpy.panels.csection.cswidget import XCrossSection, YCrossSection
from plotpy.panels.itemlist import PlotItemList
from plotpy.plot.base import BasePlot, BasePlotOptions
from plotpy.plot.manager import PlotManager

_qapp = None
_interactive = False
_figures = {}
_current_fig = None
_current_axes = None


def create_qapplication(exec_loop=False):
    """Creating Qt application (only once) and eventually exec Qt main loop"""
    global _qapp  # pylint: disable=global-statement
    if _qapp is None:
        _qapp = guidata.qapplication()
    if exec_loop and not execenv.unattended:
        _qapp.exec()


class Window(QW.QMainWindow):
    """Figure window"""

    def __init__(self, title):
        super().__init__()
        win32_fix_title_bar_background(self)

        self.default_tool = None
        self.plots = []
        self.itemlist = PlotItemList(None)
        self.contrast = ContrastAdjustment(None)
        self.xcsw = XCrossSection(None)
        self.ycsw = YCrossSection(None)

        self.manager = PlotManager(self)
        self.toolbar = QW.QToolBar(_("Tools"), self)
        self.manager.add_toolbar(self.toolbar, "default")
        self.toolbar.setMovable(True)
        self.toolbar.setFloatable(True)
        self.addToolBar(QC.Qt.TopToolBarArea, self.toolbar)

        frame = QW.QFrame(self)
        self.setCentralWidget(frame)
        self.layout = QW.QGridLayout()
        layout = QW.QVBoxLayout(frame)
        frame.setLayout(layout)
        layout.addLayout(self.layout)
        self.frame = frame

        self.setWindowTitle(title)
        self.setWindowIcon(get_icon("plotpy.svg"))

    def closeEvent(self, event):
        """Reimplementing QWidget.closeEvent

        :param event:
        """
        global _figures, _current_fig, _current_axes
        figure_title = str(self.windowTitle())
        if _figures.pop(figure_title) == _current_fig:
            _current_fig = None
            _current_axes = None
        self.itemlist.close()
        self.contrast.close()
        self.xcsw.close()
        self.ycsw.close()
        event.accept()

    def add_plot(self, i, j, plot):
        """Add plot to window

        :param i:
        :param j:
        :param plot:
        """
        i_int = int(i)
        j_int = int(j)
        self.layout.addWidget(plot, i_int, j_int)
        self.manager.add_plot(plot)
        self.plots.append(plot)

    def replot(self):
        """Replot all plots"""
        for plot in self.plots:
            plot.replot()
            item = plot.get_default_item()
            if item is not None:
                plot.set_active_item(item)
                item.unselect()

    def add_panels(self, images=False):
        """Add panels

        :param images:
        """
        self.manager.add_panel(self.itemlist)
        if images:
            for panel in (self.ycsw, self.xcsw, self.contrast):
                panel.hide()
                self.manager.add_panel(panel)

    def register_tools(self, images=False):
        """Register tools

        :param images:
        """
        if images:
            self.manager.register_all_image_tools()
        else:
            self.manager.register_all_curve_tools()

    def display(self):
        """Display window"""
        self.show()
        self.replot()
        self.manager.get_default_tool().activate()
        self.manager.update_tools_status()


class Figure:
    """Object representing a figure"""

    def __init__(self, title):
        self.axes = {}
        self.title = title
        self.win = None

    def get_axes(self, i, j):
        """Get axes

        :param i:
        :param j:
        :return:
        """
        if (i, j) in self.axes:
            return self.axes[(i, j)]

        ax = Axes()
        self.axes[(i, j)] = ax
        return ax

    def build_window(self):
        """Build window"""
        create_qapplication()
        self.win = Window(title=self.title)
        images = False
        for (i, j), ax in list(self.axes.items()):
            ax.setup_window(i, j, self.win)
            if ax.images:
                images = True
        self.win.add_panels(images=images)
        self.win.register_tools(images=images)

    def show(self):
        """Show window"""
        if not self.win:
            self.build_window()
        self.win.display()

    def save(self, fname, format, draft):
        """Save figure

        :param fname:
        :param format:
        :param draft:
        """
        if isinstance(fname, str):
            if format == "pdf":
                try:
                    mode = QPrinter.HighResolution
                except AttributeError:
                    # Some PySide6 / PyQt6 versions do not have this attribute on Linux
                    mode = QPrinter.ScreenResolution
                if draft:
                    mode = QPrinter.ScreenResolution
                printer = QPrinter(mode)
                try:
                    printer.setOutputFormat(QPrinter.PdfFormat)
                except AttributeError:
                    # PyQt6 on Linux
                    printer.setPrinterName("")
                printer.setPageOrientation(QG.QPageLayout.Landscape)
                printer.setOutputFileName(fname)
                printer.setCreator("plotpy.pyplot")
                self.print_(printer)
            else:
                if self.win is None:
                    self.show()
                pixmap = self.win.centralWidget().grab()
                pixmap.save(fname, format.upper())
        else:
            # Buffer
            fd = fname
            assert hasattr(fd, "write"), "object is not file-like as expected"
            if self.win is None:
                self.show()
            pixmap = self.win.centralWidget().grab()
            buff = QC.QBuffer()
            buff.open(QC.QIODevice.ReadWrite)
            pixmap.save(buff, format.upper())
            fd.write(buff.data())
            buff.close()
            fd.seek(0)

    def print_(self, device):
        """Print figure

        :param device:
        """
        if not self.win:
            self.build_window()
        W = device.width()
        H = device.height()

        coords = np.array(list(self.axes.keys()))
        imin = coords[:, 0].min()
        imax = coords[:, 0].max()
        jmin = coords[:, 1].min()
        jmax = coords[:, 1].max()
        w = W / (jmax - jmin + 1)
        h = H / (imax - imin + 1)
        paint = QG.QPainter(device)
        for (i, j), ax in list(self.axes.items()):
            oy = (i - imin) * h
            ox = (j - jmin) * w
            ax.widget.print_(paint, QC.QRect(ox, oy, w, h))


class Axes:
    """Object handling plots, images and axes properties"""

    def __init__(self):
        self.plots = []
        self.images = []
        self.last = None
        self.legend_position = None
        self.grid = False
        self.xlabel = ("", "")
        self.ylabel = ("", "")
        self.xcolor = ("black", "black")  # axis label colors
        self.ycolor = ("black", "black")  # axis label colors
        self.zlabel = None
        self.yreverse = False
        self.colormap = "jet"
        self.xscale = "lin"
        self.yscale = "lin"
        self.xlimits = None
        self.ylimits = None
        self.widget = None
        self.main_widget = None

    def add_legend(self, position):
        """Add legend

        :param position:
        """
        self.legend_position = position

    def set_grid(self, grid):
        """Set grid

        :param grid:
        """
        self.grid = grid

    def set_xlim(self, xmin, xmax):
        """Set x limits

        :param xmin:
        :param xmax:
        """
        self.xlimits = xmin, xmax
        self._update_plotwidget()

    def set_ylim(self, ymin, ymax):
        """Set y limits

        :param ymin:
        :param ymax:
        """
        self.ylimits = ymin, ymax
        self._update_plotwidget()

    def add_plot(self, item):
        """Add plot

        :param item:
        """
        self.plots.append(item)
        self.last = item

    def add_image(self, item):
        """Add image

        :param item:
        """
        self.images.append(item)
        self.last = item

    def setup_window(self, i, j, win):
        """Setup window

        :param i:
        :param j:
        :param win:
        """
        if self.images:
            plot = self.setup_image(i, j, win)
        else:
            plot = self.setup_plot(i, j, win)
        self.widget = plot
        plot.do_autoscale()
        self._update_plotwidget()

    def _update_plotwidget(self):
        """Update plot widget"""
        p = self.main_widget
        if p is None:
            return
        if self.grid:
            p.gridparam.maj_xenabled = True
            p.gridparam.maj_yenabled = True
            p.gridparam.update_grid(p)
        p.set_axis_color("bottom", self.xcolor[0])
        p.set_axis_color("top", self.xcolor[1])
        p.set_axis_color("left", self.ycolor[0])
        p.set_axis_color("right", self.ycolor[1])
        if self.xlimits is not None:
            p.set_axis_limits("bottom", *self.xlimits)
        if self.ylimits is not None:
            p.set_axis_limits("left", *self.ylimits)

    def setup_image(self, i, j, win: Window):
        """Setup image

        :param i:
        :param j:
        :param win:
        :return:
        """
        options = BasePlotOptions(
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            yreverse=self.yreverse,
            type="image",
        )
        p = BasePlot(win, options=options)
        self.main_widget = p
        win.add_plot(i, j, p)
        for item in self.images + self.plots:
            if item in self.images:
                item.set_color_map(self.colormap)
            p.add_item(item)
        if self.legend_position is not None:
            p.add_item(make.legend(self.legend_position))
        return p

    def setup_plot(self, i, j, win):
        """Setup plot

        :param i:
        :param j:
        :param win:
        :return:
        """
        options = BasePlotOptions(xlabel=self.xlabel, ylabel=self.ylabel, type="curve")
        p = BasePlot(win, options=options)
        self.main_widget = p
        win.add_plot(i, j, p)
        for item in self.plots:
            p.add_item(item)
        p.enable_used_axes()
        active_item = p.get_active_item(force=True)
        p.set_scales(self.xscale, self.yscale)
        active_item.unselect()
        if self.legend_position is not None:
            p.add_item(make.legend(self.legend_position))
        return p


def _make_figure_title(N=None):
    """Make figure title"""
    global _figures
    if N is None:
        N = len(_figures) + 1
    if isinstance(N, str):
        return N
    else:
        return f"Figure {N:d}"


def figure(N=None):
    """Create a new figure"""
    global _figures, _current_fig, _current_axes
    title = _make_figure_title(N)
    if title in _figures:
        f = _figures[title]
    else:
        f = Figure(title)
        _figures[title] = f
    _current_fig = f
    _current_axes = None
    return f


def gcf():
    """Get current figure"""
    global _current_fig
    if _current_fig:
        return _current_fig
    else:
        return figure()


def gca():
    """Get current axes"""
    create_qapplication()  # Necessary because of setIcon call during item creation
    global _current_axes
    if not _current_axes:
        axes = gcf().get_axes(1, 1)
        _current_axes = axes
    return _current_axes


def show(mainloop=True):
    """
    Show all figures and enter Qt event loop
    This should be the last line of your script
    """
    global _figures, _interactive, _current_fig
    for fig in list(_figures.values()):
        fig.show()
    if not _interactive:
        if not _current_fig:
            print("Warning: must create a figure before showing it", file=sys.stderr)
        elif mainloop:
            create_qapplication(exec_loop=True)


def _show_if_interactive():
    """Show all figures if interactive mode is on"""
    global _interactive
    if _interactive:
        show()


def subplot(n, m, k):
    """
    Create a subplot command

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        figure(1)
        subplot(2, 1, 1)
        plot(x, np.sin(x), "r+")
        subplot(2, 1, 2)
        plot(x, np.cos(x), "g-")
        show()
    """
    global _current_axes
    lig = (k - 1) // m
    col = (k - 1) % m
    fig = gcf()
    axe = fig.get_axes(lig, col)
    _current_axes = axe
    return axe


def plot(*args, **kwargs):
    """
    Plot curves

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        plot(x, np.sin(x), "r+")
        plot(x, np.cos(x), "g-")
        show()
    """
    axe = gca()
    curves = make.mcurve(*args, **kwargs)
    if not isinstance(curves, list):
        curves = [curves]
    for curve in curves:
        axe.add_plot(curve)
    _show_if_interactive()
    return curves


def plotyy(x1, y1, x2, y2):
    """
    Plot curves with two different y axes

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        plotyy(x, np.sin(x), x, np.cos(x))
        ylabel("sinus", "cosinus")
        show()
    """
    axe = gca()
    curve1 = make.mcurve(x1, y1, yaxis="left")
    curve2 = make.mcurve(x2, y2, yaxis="right")
    axe.ycolor = (curve1.param.line.color, curve2.param.line.color)
    axe.add_plot(curve1)
    axe.add_plot(curve2)
    _show_if_interactive()
    return [curve1, curve2]


def hist(data, bins=None, logscale=None, title=None, color=None):
    """
    Plot 1-D histogram

    Example::

        from numpy.random import normal
        data = normal(0, 1, (2000, ))
        hist(data)
        show()
    """
    axe = gca()
    curve = make.histogram(
        data, bins=bins, logscale=logscale, title=title, color=color, yaxis="left"
    )
    axe.add_plot(curve)
    _show_if_interactive()
    return [curve]


def semilogx(*args, **kwargs):
    """
    Plot curves with logarithmic x-axis scale

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        semilogx(x, np.sin(12*x), "g-")
        show()
    """
    axe = gca()
    axe.xscale = "log"
    curve = make.mcurve(*args, **kwargs)
    axe.add_plot(curve)
    _show_if_interactive()
    return [curve]


def semilogy(*args, **kwargs):
    """
    Plot curves with logarithmic y-axis scale

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        semilogy(x, np.sin(12*x), "g-")
        show()
    """
    axe = gca()
    axe.yscale = "log"
    curve = make.mcurve(*args, **kwargs)
    axe.add_plot(curve)
    _show_if_interactive()
    return [curve]


def loglog(*args, **kwargs):
    """
    Plot curves with logarithmic x-axis and y-axis scales

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        loglog(x, np.sin(12*x), "g-")
        show()
    """
    axe = gca()
    axe.xscale = "log"
    axe.yscale = "log"
    curve = make.mcurve(*args, **kwargs)
    axe.add_plot(curve)
    _show_if_interactive()
    return [curve]


def errorbar(*args, **kwargs):
    """
    Plot curves with error bars

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        errorbar(x, -1+x**2/20+.2*np.random.rand(len(x)), x/20)
        show()
    """
    axe = gca()
    curve = make.merror(*args, **kwargs)
    axe.add_plot(curve)
    _show_if_interactive()
    return [curve]


def imread(fname, to_grayscale=False):
    """Read data from *fname*"""
    return io.imread(fname, to_grayscale=to_grayscale)


def imshow(data, interpolation=None, mask=None):
    """
    Display the image in *data* to current axes
    interpolation: 'nearest', 'linear' (default), 'antialiasing'

    Example::

        import numpy as np
        x = np.linspace(-5, 5, 1000)
        img = np.fromfunction(lambda x, y: np.sin((x/200.)*(y/200.)**2), (1000, 1000))
        gray()
        imshow(img)
        show()
    """
    axe = gca()

    if isinstance(data, np.ma.MaskedArray) and mask is None:
        mask = data.mask
        data = data.data
    if mask is None:
        img = make.image(data)
    else:
        img = make.maskedimage(data, mask, show_mask=True)
    if interpolation is not None:
        interp_dict = {
            "nearest": INTERP_NEAREST,
            "linear": INTERP_LINEAR,
            "antialiasing": INTERP_AA,
        }
        assert interpolation in interp_dict, "invalid interpolation option"
        img.set_interpolation(interp_dict[interpolation], size=5)
    axe.add_image(img)
    axe.yreverse = True
    _show_if_interactive()
    return [img]


def pcolor(*args):
    """
    Create a pseudocolor plot of a 2-D array

    Example::

        import numpy as np
        r = np.linspace(1., 16, 100)
        th = np.linspace(0., np.pi, 100)
        R, TH = np.meshgrid(r, th)
        X = R*np.cos(TH)
        Y = R*np.sin(TH)
        Z = 4*TH+R
        pcolor(X, Y, Z)
        show()
    """
    axe = gca()
    img = make.pcolor(*args)
    axe.add_image(img)
    axe.yreverse = len(args) == 1
    _show_if_interactive()
    return [img]


def interactive(state):
    """Toggle interactive mode"""
    global _interactive
    _interactive = state


def ion():
    """Turn interactive mode on"""
    interactive(True)


def ioff():
    """Turn interactive mode off"""
    interactive(False)


# TODO: The following functions (title, xlabel, ...) should update an already
#      shown figure to be compatible with interactive mode -- for now it just
#      works if these functions are called before showing the figure
def title(text):
    """Set current figure title"""
    global _figures
    fig = gcf()
    _figures.pop(fig.title)
    fig.title = text
    _figures[text] = fig


def xlabel(bottom="", top=""):
    """Set current x-axis label"""
    assert isinstance(bottom, str) and isinstance(top, str)
    axe = gca()
    axe.xlabel = (bottom, top)


def ylabel(left="", right=""):
    """Set current y-axis label"""
    assert isinstance(left, str) and isinstance(right, str)
    axe = gca()
    axe.ylabel = (left, right)


def zlabel(label):
    """Set current z-axis label"""
    assert isinstance(label, str)
    axe = gca()
    axe.zlabel = label


def yreverse(reverse):
    """
    Set y-axis direction of increasing values

    reverse = False (default)
        y-axis values increase from bottom to top

    reverse = True
        y-axis values increase from top to bottom
    """
    assert isinstance(reverse, bool)
    axe = gca()
    axe.yreverse = reverse


def grid(act):
    """Toggle grid visibility"""
    axe = gca()
    axe.set_grid(act)


def legend(pos="TR"):
    """Add legend to current axes (pos='TR', 'TL', 'BR', ...)"""
    axe = gca()
    axe.add_legend(pos)


def colormap(name):
    """Set color map to *name*"""
    axe = gca()
    axe.colormap = name


def _add_colormaps(glbs):
    """Add colormap functions to *glbs*"""
    for cmap_name in ALL_COLORMAPS.keys():
        glbs[cmap_name] = lambda name=cmap_name: colormap(name)
        glbs[cmap_name].__doc__ = "Set color map to '%s'" % cmap_name


_add_colormaps(globals())


def close(N=None, all=False):
    """Close figure"""
    global _figures, _current_fig, _current_axes
    if all:
        _figures = {}
        _current_fig = None
        _current_axes = None
        return
    if N is None:
        fig = gcf()
    else:
        fig = figure(N)
    fig.close()


def savefig(fname, format=None):
    """
    Save figure

    Currently supports QImageWriter formats only
    (see https://doc.qt.io/qt-5/qimagewriter.html#supportedImageFormats)
    """
    if not isinstance(fname, str) and format is None:
        # Buffer/fd
        format = "png"
    if format is None:
        format = fname.rsplit(".", 1)[-1].lower()
        fmts = [fmt.data().decode() for fmt in QG.QImageWriter.supportedImageFormats()]
        assert format in fmts, _(
            "Function 'savefig' currently supports the following formats:\n%s"
        ) % ", ".join(fmts)
    else:
        format = format.lower()
    fig = gcf()
    fig.save(fname, format)
