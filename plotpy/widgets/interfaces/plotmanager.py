from plotpy.widgets.plot.base import BasePlot


class InterfacePlotManager(object):
    """A 'controller' that organizes relations between
    plots (BasePlot), panels, tools (GuiTool) and toolbar
    """

    def add_plot(self, plot, plot_id="default"):
        """

        :param plot:
        :param plot_id:
        """
        assert id not in self.plots
        assert isinstance(plot, BasePlot)

    def add_panel(self, panel):
        """

        :param panel:
        """
        assert id not in self.panels

    def add_toolbar(self, toolbar, toolbar_id="default"):
        """

        :param toolbar:
        :param toolbar_id:
        """
        assert id not in self.toolbars

    def get_active_plot(self):
        """The active plot is the plot whose canvas has the focus
        otherwise it's the "default" plot
        """
        pass
