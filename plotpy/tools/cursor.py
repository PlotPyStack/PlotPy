# -*- coding: utf-8 -*-

from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.events import QtDragHandler, setup_standard_tool_filter
from plotpy.items import Marker, XRangeSelection
from plotpy.tools.base import SHAPE_Z_OFFSET, DefaultToolbarID, InteractiveTool


class BaseCursorTool(InteractiveTool):
    """ """

    TITLE = None
    ICON = None

    def __init__(
        self,
        manager,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=None,
    ):
        super().__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        self.shape = None

    def create_shape(self):
        """Create and return the cursor/range shape"""
        raise NotImplementedError

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        self.handler = QtDragHandler(
            filter, QC.Qt.MouseButton.LeftButton, start_state=start_state
        )
        self.handler.SIG_MOVE.connect(self.move)
        self.handler.SIG_STOP_NOT_MOVING.connect(self.end_move)
        self.handler.SIG_STOP_MOVING.connect(self.end_move)
        return setup_standard_tool_filter(filter, start_state)

    def move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        plot = filter.plot
        if not self.shape:
            self.shape = self.create_shape()
            self.shape.attach(plot)
            self.shape.setZ(plot.get_max_z() + 1)
            self.shape.move_local_point_to(0, event.pos())
            self.shape.setVisible(True)
        self.shape.move_local_point_to(1, event.pos())
        plot.replot()

    def end_move(self, filter, event):
        """

        :param filter:
        :param event:
        """
        if self.shape is not None:
            assert self.shape.plot() == filter.plot
            filter.plot.add_item_with_z_offset(self.shape, SHAPE_Z_OFFSET)
            self.shape = None
            self.SIG_TOOL_JOB_FINISHED.emit()


class HRangeTool(BaseCursorTool):
    TITLE = _("Horizontal selection")
    ICON = "xrange.png"

    def create_shape(self):
        """

        :return:
        """

        return XRangeSelection(0, 0)


class VCursorTool(BaseCursorTool):
    TITLE = _("Vertical cursor")
    ICON = "vcursor.png"

    def create_shape(self):
        """

        :return:
        """
        marker = Marker()
        marker.set_markerstyle("|")
        return marker


class HCursorTool(BaseCursorTool):
    TITLE = _("Horizontal cursor")
    ICON = "hcursor.png"

    def create_shape(self):
        """

        :return:
        """
        marker = Marker()
        marker.set_markerstyle("-")
        return marker


class XCursorTool(BaseCursorTool):
    TITLE = _("Cross cursor")
    ICON = "xcursor.png"

    def create_shape(self):
        """

        :return:
        """
        marker = Marker()
        marker.set_markerstyle("+")
        return marker
