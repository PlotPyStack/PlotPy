class CrossSectionPlot(BasePlot):
    """Cross section plot"""

    CURVE_LABEL = _("Cross section")
    LABEL_TEXT = _("Enable a marker")
    _height = None
    _width = None
    CS_AXIS = None
    Z_AXIS = None
    Z_MAX_MAJOR = 5
    SHADE = 0.2

    def __init__(self, parent=None):
        super(CrossSectionPlot, self).__init__(
            parent=parent, title="", section="cross_section", type=PlotType.CURVE
        )
        self.perimage_mode = True
        self.autoscale_mode = True
        self.autorefresh_mode = True
        self.apply_lut = False
        self.single_source = False
        self.lockscales = True

        self.last_obj = None
        self.known_items = {}
        self._shapes = {}

        self.param = CurveParam(_("Curve"), icon="curve.png")
        self.set_curve_style("cross_section", "curve")

        if self._height is not None:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        elif self._width is not None:
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.label = make.label(self.LABEL_TEXT, "C", (0, 0), "C")
        self.label.set_readonly(True)
        self.add_item(self.label)

        self.setAxisMaxMajor(self.Z_AXIS, self.Z_MAX_MAJOR)
        self.setAxisMaxMinor(self.Z_AXIS, 0)

    def set_curve_style(self, section, option):
        """

        :param section:
        :param option:
        """
        self.param.read_config(CONF, section, option)
        self.param.label = self.CURVE_LABEL

    def connect_plot(self, plot):
        """

        :param plot:
        :return:
        """
        if plot.type == PlotType.CURVE:
            # Connecting only to image plot widgets (allow mixing image and
            # curve widgets for the same plot manager -- e.g. in pyplot)
            return
        plot.SIG_ITEMS_CHANGED.connect(self.items_changed)
        plot.SIG_LUT_CHANGED.connect(self.lut_changed)
        plot.SIG_MASK_CHANGED.connect(lambda item: self.update_plot())
        plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)
        plot.SIG_MARKER_CHANGED.connect(self.marker_changed)
        plot.SIG_ANNOTATION_CHANGED.connect(self.shape_changed)
        plot.SIG_PLOT_LABELS_CHANGED.connect(self.plot_labels_changed)
        plot.SIG_AXIS_DIRECTION_CHANGED.connect(self.axis_dir_changed)
        plot.SIG_PLOT_AXIS_CHANGED.connect(self.plot_axis_changed)
        self.plot_labels_changed(plot)
        for axis_id in plot.AXIS_IDS:
            self.axis_dir_changed(plot, axis_id)
        self.items_changed(plot)

    def register_shape(self, plot, shape, final, refresh=True):
        """

        :param plot:
        :param shape:
        :param final:
        :param refresh:
        :return:
        """
        known_shapes = self._shapes.get(plot, [])
        if shape in known_shapes:
            return
        self._shapes[plot] = known_shapes + [shape]
        self.update_plot(shape, refresh=refresh and self.autorefresh_mode)

    def unregister_shape(self, shape):
        """

        :param shape:
        """
        for plot in self._shapes:
            shapes = self._shapes[plot]
            if shape in shapes:
                shapes.pop(shapes.index(shape))
                if len(shapes) == 0 or shape is self.get_last_obj():
                    for curve in self.get_cross_section_curves():
                        curve.clear_data()
                    self.replot()
                break

    def create_cross_section_item(self):
        """ """
        raise NotImplementedError

    def add_cross_section_item(self, source):
        """

        :param source:
        """
        curve = self.create_cross_section_item()
        curve.set_source_image(source)
        curve.set_readonly(True)
        self.add_item(curve, z=0)
        self.known_items[source] = curve

    def get_cross_section_curves(self):
        """

        :return:
        """
        return list(self.known_items.values())

    def items_changed(self, plot):
        """

        :param plot:
        :return:
        """
        # Del obsolete cross section items
        new_sources = plot.get_items(item_type=ICSImageItemType)
        for source in self.known_items.copy():
            if source not in new_sources:
                curve = self.known_items.pop(source)
                curve.clear_data()  # useful to emit SIG_CS_CURVE_CHANGED
                # (eventually notify other panels that the
                #  cross section curve is now empty)
                self.del_item(curve)

        # Update plot only to show/hide cross section curves according to
        # the associated image item visibility state (hence `refresh=False`)
        self.update_plot(refresh=False)

        self.plot_axis_changed(plot)

        if not new_sources:
            self.replot()
            return

        self.param.shade = self.SHADE / len(new_sources)
        for source in new_sources:
            if source not in self.known_items and source.isVisible():
                if not self.single_source or not self.known_items:
                    self.add_cross_section_item(source=source)

    def active_item_changed(self, plot):
        """Active item has just changed"""
        self.shape_changed(plot.get_active_item())

    def plot_labels_changed(self, plot):
        """Plot labels have changed"""
        raise NotImplementedError

    def axis_dir_changed(self, plot, axis_id):
        """An axis direction has changed"""
        raise NotImplementedError

    def plot_axis_changed(self, plot):
        """Plot was just zoomed/panned"""
        if self.lockscales:
            self.do_autoscale(replot=False, axis_id=self.Z_AXIS)
            vmin, vmax = plot.get_axis_limits(self.CS_AXIS)
            self.set_axis_limits(self.CS_AXIS, vmin, vmax)

    def marker_changed(self, marker):
        """

        :param marker:
        """
        self.update_plot(marker)

    def is_shape_known(self, shape):
        """

        :param shape:
        :return:
        """
        for shapes in list(self._shapes.values()):
            if shape in shapes:
                return True
        else:
            return False

    def shape_changed(self, shape):
        """

        :param shape:
        """
        if self.autorefresh_mode:
            if self.is_shape_known(shape):
                self.update_plot(shape)

    def get_last_obj(self):
        """

        :return:
        """
        if self.last_obj is not None:
            return self.last_obj()

    def update_plot(self, obj=None, refresh=True):
        """
        Update cross section curve(s) associated to object *obj*

        *obj* may be a marker or a rectangular shape
        (see :py:class:`.tools.CrossSectionTool`
        and :py:class:`.tools.AverageCrossSectionTool`)

        If obj is None, update the cross sections of the last active object
        """
        if obj is None:
            obj = self.get_last_obj()
            if obj is None:
                return
        else:
            self.last_obj = weakref.ref(obj)
        if obj.plot() is None:
            self.unregister_shape(obj)
            return
        if self.label.isVisible():
            self.label.hide()
        items = list(self.known_items.items())
        for index, (item, curve) in enumerate(iter(items)):
            if (not self.perimage_mode and index > 0) or not item.isVisible():
                curve.hide()
            else:
                curve.show()
                curve.perimage_mode = self.perimage_mode
                curve.autoscale_mode = self.autoscale_mode
                curve.apply_lut = self.apply_lut
                if refresh:
                    curve.update_item(obj)
        if self.autoscale_mode:
            self.do_autoscale(replot=True)
        elif self.lockscales:
            self.do_autoscale(replot=True, axis_id=self.Z_AXIS)

    def toggle_perimage_mode(self, state):
        """

        :param state:
        """
        self.perimage_mode = state
        self.update_plot()

    def toggle_autoscale(self, state):
        """

        :param state:
        """
        self.autoscale_mode = state
        self.update_plot()

    def toggle_autorefresh(self, state):
        """

        :param state:
        """
        self.autorefresh_mode = state
        if state:
            self.update_plot()

    def toggle_apply_lut(self, state):
        """

        :param state:
        """
        self.apply_lut = state
        self.update_plot()
        if self.apply_lut:
            self.set_axis_title(self.Z_AXIS, LUT_AXIS_TITLE)
            self.set_axis_color(self.Z_AXIS, "red")
        else:
            obj = self.get_last_obj()
            if obj is not None and obj.plot() is not None:
                self.plot_labels_changed(obj.plot())

    def toggle_lockscales(self, state):
        """

        :param state:
        """
        self.lockscales = state
        obj = self.get_last_obj()
        if obj is not None and obj.plot() is not None:
            self.plot_axis_changed(obj.plot())

    def lut_changed(self, plot):
        """

        :param plot:
        """
        if self.apply_lut:
            self.update_plot()


class HorizontalCrossSectionPlot(CrossSectionPlot):
    CS_AXIS = BasePlot.X_BOTTOM
    Z_AXIS = BasePlot.Y_LEFT

    def plot_labels_changed(self, plot):
        """Plot labels have changed"""
        self.set_axis_title("left", plot.get_axis_title("right"))
        self.set_axis_title("bottom", plot.get_axis_title("bottom"))
        self.set_axis_color("left", plot.get_axis_color("right"))
        self.set_axis_color("bottom", plot.get_axis_color("bottom"))

    def axis_dir_changed(self, plot, axis_id):
        """An axis direction has changed"""
        if axis_id == plot.X_BOTTOM:
            self.set_axis_direction("bottom", plot.get_axis_direction("bottom"))
            self.replot()


class VerticalCrossSectionPlot(CrossSectionPlot):
    CS_AXIS = BasePlot.Y_LEFT
    Z_AXIS = BasePlot.X_BOTTOM
    Z_MAX_MAJOR = 3

    def plot_labels_changed(self, plot):
        """Plot labels have changed"""
        self.set_axis_title("bottom", plot.get_axis_title("right"))
        self.set_axis_title("left", plot.get_axis_title("left"))
        self.set_axis_color("bottom", plot.get_axis_color("right"))
        self.set_axis_color("left", plot.get_axis_color("left"))

    def axis_dir_changed(self, plot, axis_id):
        """An axis direction has changed"""
        if axis_id == plot.Y_LEFT:
            self.set_axis_direction("left", plot.get_axis_direction("left"))
            self.replot()


class XCrossSectionPlot(HorizontalCrossSectionPlot):
    """X-axis cross section plot"""

    _height = 130

    def sizeHint(self):
        """

        :return:
        """
        return QSize(self.width(), self._height)

    def create_cross_section_item(self):
        """

        :return:
        """
        return XCrossSectionItem(self.param)


class YCrossSectionPlot(VerticalCrossSectionPlot):
    """Y-axis cross section plot"""

    _width = 140

    def sizeHint(self):
        """

        :return:
        """
        return QSize(self._width, self.height())

    def create_cross_section_item(self):
        """

        :return:
        """
        return YCrossSectionItem(self.param)


# Oblique cross section plot
class ObliqueCrossSectionPlot(HorizontalCrossSectionPlot):
    """Oblique averaged cross section plot"""

    PLOT_TITLE = _("Oblique averaged cross section")
    CURVE_LABEL = _("Oblique averaged cross section")
    LABEL_TEXT = _("Activate the oblique cross section tool")

    def __init__(self, parent=None):
        super(ObliqueCrossSectionPlot, self).__init__(parent)
        self.set_title(self.PLOT_TITLE)
        self.single_source = True

    def create_cross_section_item(self):
        """

        :return:
        """
        return ObliqueCrossSectionItem(self.param)

    def axis_dir_changed(self, plot, axis_id):
        """An axis direction has changed"""
        pass
