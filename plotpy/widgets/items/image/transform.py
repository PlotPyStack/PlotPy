# ==============================================================================
# Image with a custom linear transform
# ==============================================================================
class TrImageItem(TransformImageMixin, RawImageItem):
    """
    Construct a transformable image item

        * data: 2D NumPy array
        * param (optional): image parameters
          (:py:class:`.styles.TrImageParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, IExportROIImageItemType)

    _trx = 0.5
    _try = 0.5
    _can_select = True
    _can_resize = True
    _can_rotate = True
    _can_move = True
    ROTATION_POINT_DIAMETER = 10  # in pixels

    def __init__(self, data=None, param=None):
        self.tr = np.eye(3, dtype=float)
        self.itr = np.eye(3, dtype=float)
        self.points = np.array([[0, 0, 2, 2], [0, 2, 2, 0], [1, 1, 1, 1]], float)
        self.locked = False
        self.rotation_point = None
        self.rotation_point_move_with_shape = None
        super(TrImageItem, self).__init__(data, param)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self):
        """Return instance of the default imageparam DataSet"""
        return TrImageParam(_("Image"))

    # ---- Public API ----------------------------------------------------------

    def set_crop(self, left, top, right, bottom):
        """

        :param left:
        :param top:
        :param right:
        :param bottom:
        """
        self.param.set_crop(left, top, right, bottom)

    def get_crop(self):
        """

        :return:
        """
        return self.param.get_crop()

    def get_crop_coordinates(self):
        """Return crop rectangle coordinates"""
        tpos = np.array(np.dot(self.itr, self.points))
        xmin, ymin, _ = tpos.min(axis=1).flatten()
        xmax, ymax, _ = tpos.max(axis=1).flatten()
        left, top, right, bottom = self.param.get_crop()
        return (xmin + left, ymin + top, xmax - right, ymax - bottom)

    def compute_bounds(self):
        """ """
        x0, y0, x1, y1 = self.get_crop_coordinates()
        self.bounds = QRectF(QPointF(x0, y0), QPointF(x1, y1))
        self.update_border()

    def set_rotation_point(self, x, y, rotation_point_move_with_shape=True):
        self.rotation_point_move_with_shape = rotation_point_move_with_shape
        self.rotation_point = colvector(x, y)

    def set_rotation_point_to_center(self):
        handles = self.itr * self.points
        center = handles.sum(axis=1) / 4
        self.set_rotation_point(
            center[0], center[1], rotation_point_move_with_shape=True
        )

    def set_locked(self, state):
        self.locked = state

    def is_locked(self):
        return self.locked

    # --- RawImageItem API -----------------------------------------------------
    def set_data(self, data, lut_range=None):
        """

        :param data:
        :param lut_range:
        """
        RawImageItem.set_data(self, data, lut_range)
        ni, nj = self.data.shape
        self.points = np.array([[0, 0, nj, nj], [0, ni, ni, 0], [1, 1, 1, 1]], float)
        self.compute_bounds()

    # --- BaseImageItem API ----------------------------------------------------
    def get_filter(self, filterobj, filterparam):
        """Provides a filter object over this image's content"""
        raise NotImplementedError
        # TODO: Implement TrImageFilterItem

    #        return TrImageFilterItem(self, filterobj, filterparam)

    def get_pixel_coordinates(self, xplot, yplot):
        """Return (image) pixel coordinates (from plot coordinates)"""
        v = self.tr * colvector(xplot, yplot)
        xpixel, ypixel, _ = v[:, 0]
        return xpixel, ypixel

    def get_plot_coordinates(self, xpixel, ypixel):
        """Return plot coordinates (from image pixel coordinates)"""
        v0 = self.itr * colvector(xpixel, ypixel)
        xplot, yplot, _ = v0[:, 0].A.ravel()
        return xplot, yplot

    def get_x_values(self, i0, i1):
        """

        :param i0:
        :param i1:
        :return:
        """
        v0 = self.itr * colvector(i0, 0)
        x0, _y0, _ = v0[:, 0].A.ravel()
        v1 = self.itr * colvector(i1, 0)
        x1, _y1, _ = v1[:, 0].A.ravel()
        return np.linspace(x0, x1, i1 - i0)

    def get_y_values(self, j0, j1):
        """

        :param j0:
        :param j1:
        :return:
        """
        v0 = self.itr * colvector(0, j0)
        _x0, y0, _ = v0[:, 0].A.ravel()
        v1 = self.itr * colvector(0, j1)
        _x1, y1, _ = v1[:, 0].A.ravel()
        return np.linspace(y0, y1, j1 - j0)

    def get_r_values(self, i0, i1, j0, j1, flag_circle=False):
        v0 = self.itr * colvector(i0, j0)
        x0, y0, _ = v0[:, 0].A.ravel()
        v1 = self.itr * colvector(i1, j1)
        x1, y1, _ = v1[:, 0].A.ravel()
        if flag_circle:
            r = abs(y1 - y0)
        else:
            r = np.sqrt((y1 - y0) ** 2 + (x1 - x0) ** 2)
        return np.linspace(0, r, abs(j1 - j0))

    def get_closest_coordinates(self, x, y):
        """Return closest image pixel coordinates"""
        xi, yi = self.get_closest_indexes(x, y)
        v = self.itr * colvector(xi, yi)
        x, y, _ = v[:, 0].A.ravel()
        return x, y

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        :return:
        """
        W = canvasRect.width()
        H = canvasRect.height()
        if W <= 1 or H <= 1:
            return

        x0, y0, x1, y1 = src_rect
        cx = canvasRect.left()
        cy = canvasRect.top()
        sx = (x1 - x0) / (W - 1)
        sy = (y1 - y0) / (H - 1)
        # tr1 = tr(x0,y0)*scale(sx,sy)*tr(-cx,-cy)
        tr = np.matrix([[sx, 0, x0 - cx * sx], [0, sy, y0 - cy * sy], [0, 0, 1]], float)
        mat = self.tr * tr

        dst_rect = tuple([int(i) for i in dst_rect])
        dest = _scale_tr(
            self.data, mat, self._offscreen, dst_rect, self.lut, self.interpolate
        )
        qrect = QRectF(QPointF(dest[0], dest[1]), QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)
        # -- rotation circle
        if self.can_rotate():
            if self.rotation_point is None:
                self.set_rotation_point_to_center()
            brush = QBrush(QColor("magenta"))
            pen = QPen(QColor("magenta"))
            pen.setBrush(brush)
            painter.setBrush(brush)
            center = QPointF(
                *axes_to_canvas(self, self.rotation_point[0], self.rotation_point[1])
            )
            painter.drawEllipse(
                center,
                self.ROTATION_POINT_DIAMETER / 2.0,
                self.ROTATION_POINT_DIAMETER / 2.0,
            )

    def export_roi(
        self,
        src_rect,
        dst_rect,
        dst_image,
        apply_lut=False,
        apply_interpolation=False,
        original_resolution=False,
        force_interp_mode=None,
        force_interp_size=None,
    ):
        """Export Region Of Interest to array"""
        if apply_lut:
            a, b, _bg, _cmap = self.lut
        else:
            a, b = 1.0, 0.0

        xs0, ys0, xs1, ys1 = src_rect
        xd0, yd0, xd1, yd1 = dst_rect

        if original_resolution:
            _t1, _t2, _t3, xscale, yscale, _t4, _t5 = self.get_transform()
        else:
            xscale, yscale = (
                (xs1 - xs0) / float(xd1 - xd0),
                (ys1 - ys0) / float(yd1 - yd0),
            )

        mat = self.tr * (translate(xs0, ys0) * scale(xscale, yscale))

        x0, y0, x1, y1 = self.get_crop_coordinates()
        xd0 = max([xd0, xd0 + int((x0 - xs0) / xscale)])
        yd0 = max([yd0, yd0 + int((y0 - ys0) / xscale)])
        xd1 = min([xd1, xd1 + int((x1 - xs1) / xscale)])
        yd1 = min([yd1, yd1 + int((y1 - ys1) / xscale)])
        dst_rect = xd0, yd0, xd1, yd1

        if apply_interpolation:
            if force_interp_mode is not None:
                if force_interp_mode in (INTERP_NEAREST, INTERP_LINEAR):
                    interp = (force_interp_mode,)
                else:  # INTERP_AA
                    aa = np.ones(
                        (force_interp_size, force_interp_size), self.data.dtype
                    )
                    interp = (force_interp_mode, aa)
            else:  # don't force interpolation, keep current image interpolation
                interp = self.interpolate
        else:  # don't apply interpolation --> INTERP_NEAREST
            interp = (INTERP_NEAREST,)
        _scale_tr(self.data, mat, dst_image, dst_rect, (a, b, None), interp)


assert_interfaces_valid(TrImageItem)
