# -*- coding: utf-8 -*-
from guidata.dataset import DataSet, TextItem
from qtpy import QtCore as QC

from plotpy.config import _
from plotpy.events import ClickHandler, setup_standard_tool_filter
from plotpy.tools.base import DefaultToolbarID, InteractiveTool


class LabelTool(InteractiveTool):
    """ """

    TITLE = _("Label")
    ICON = "label.png"
    LABEL_STYLE_SECT = "plot"
    LABEL_STYLE_KEY = "label"
    SWITCH_TO_DEFAULT_TOOL = True

    def __init__(
        self,
        manager,
        handle_label_cb=None,
        label_style=None,
        toolbar_id=DefaultToolbarID,
        title=None,
        icon=None,
        tip=None,
        switch_to_default_tool=None,
    ):
        self.handle_label_cb = handle_label_cb
        super().__init__(
            manager,
            toolbar_id,
            title=title,
            icon=icon,
            tip=tip,
            switch_to_default_tool=switch_to_default_tool,
        )
        if label_style is not None:
            self.label_style_sect = label_style[0]
            self.label_style_key = label_style[1]
        else:
            self.label_style_sect = self.LABEL_STYLE_SECT
            self.label_style_key = self.LABEL_STYLE_KEY

    def set_label_style(self, label):
        """

        :param label:
        """
        label.set_style(self.label_style_sect, self.label_style_key)

    def setup_filter(self, baseplot):
        """

        :param baseplot:
        :return:
        """
        filter = baseplot.filter
        start_state = filter.new_state()
        handler = ClickHandler(
            filter, QC.Qt.MouseButton.LeftButton, start_state=start_state
        )
        handler.SIG_CLICK_EVENT.connect(self.add_label_to_plot)
        return setup_standard_tool_filter(filter, start_state)

    def add_label_to_plot(self, filter, event):
        """

        :param filter:
        :param event:
        """
        plot = filter.plot

        # The following import is here to avoid circular imports
        # pylint: disable=import-outside-toplevel
        from plotpy.builder import make

        class TextParam(DataSet):
            text = TextItem("", _("Label"))

        textparam = TextParam(_("Label text"), icon=self.ICON)
        if textparam.edit(plot):
            text = textparam.text.replace("\n", "<br>")

            label = make.label(text, (0.0, 0.0), (10, 10), "TL")
            title = label.labelparam.label
            self.set_label_style(label)
            label.setTitle(self.TITLE)
            x = plot.invTransform(label.xAxis(), event.pos().x())
            y = plot.invTransform(label.yAxis(), event.pos().y())
            label.set_pos(x, y)
            label.setTitle(title)
            label.labelparam.update_param(label)
            plot.add_item(label)
            if self.handle_label_cb is not None:
                self.handle_label_cb(label)
            plot.replot()
            self.SIG_TOOL_JOB_FINISHED.emit()
