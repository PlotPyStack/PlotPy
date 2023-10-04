class IPanel:
    """Interface for panels controlled by PlotManager"""

    @staticmethod
    def __inherits__():
        # Avoid circular import
        # pylint: disable=import-outside-toplevel
        from plotpy.panels import PanelWidget

        return PanelWidget

    def register_panel(self, manager):
        """Register panel to plot manager"""
        pass

    def configure_panel(self):
        """Configure panel"""
        pass
