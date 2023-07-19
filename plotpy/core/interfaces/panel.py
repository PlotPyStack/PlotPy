from plotpy.core.panels import PanelWidget


class IPanel:
    """Interface for panels controlled by PlotManager"""

    @staticmethod
    def __inherits__():
        return PanelWidget

    def register_panel(self, manager):
        """Register panel to plot manager"""
        pass

    def configure_panel(self):
        """Configure panel"""
        pass
