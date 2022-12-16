# ==============================================================================
# QuadGrid item
# ==============================================================================
class QuadGridItem(ImageMixin, RawImageItem):
    """
    Construct a QuadGrid image

        * X, Y, Z: A structured grid of quadrilaterals
          each quad is defined by (X[i], Y[i]), (X[i], Y[i+1]),
          (X[i+1], Y[i+1]), (X[i+1], Y[i])
        * param (optional): image parameters (ImageParam instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, IHistDataSource, IVoiImageItemType)

    def __init__(self, X, Y, Z, param=None):
        assert X is not None
        assert Y is not None
        assert Z is not None
        self.X = X
        self.Y = Y
        assert X.shape == Y.shape
        assert Z.shape == X.shape
        self.tr = np.eye(3, dtype=float)
        self.itr = np.eye(3, dtype=float)
        self.points = np.array([[0, 0, 2, 2], [0, 2, 2, 0], [1, 1, 1, 1]], float)
        super(QuadGridItem, self).__init__(Z, param)
        self.set_data(Z)
        self.grid = 1
        self.interpolate = (0, 0.5, 0.5)
        self.param.update_item(self)

        self.set_transform(0, 0, 0)

    # ---- BaseImageItem API ---------------------------------------------------
    def get_default_param(self):
        """Return instance of the default imageparam DataSet"""
        return QuadGridParam(_("Quadrilaterals"))

    def types(self):
        """

        :return:
        """
        return (
            IImageItemType,
            IVoiImageItemType,
            IColormapImageItemType,
            ITrackableItemType,
        )

    def set_data(self, data, X=None, Y=None, lut_range=None):
        """
        Set Image item data

            * data: 2D NumPy array
            * lut_range: LUT range -- tuple (levelmin, levelmax)
        """
        if lut_range is not None:
            _min, _max = lut_range
        else:
            _min, _max = _nanmin(data), _nanmax(data)

        self.data = data
        self.histogram_cache = None
        if X is not None:
            assert Y is not None
            self.X = X
            self.Y = Y

        xmin = self.X.min()
        xmax = self.X.max()
        ymin = self.Y.min()
        ymax = self.Y.max()
        self.points = np.array(
            [[xmin, xmin, xmax, xmax], [ymin, ymax, ymax, ymin], [1, 1, 1, 1]], float
        )
        self.update_bounds()
        self.update_border()
        self.set_lut_range([_min, _max])

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        """
        self._offscreen[...] = np.uint32(0)
        dest = _scale_quads(
            self.X,
            self.Y,
            self.data,
            src_rect,
            self.itr,
            self._offscreen,
            dst_rect,
            self.lut,
            self.interpolate,
            self.grid,
        )
        qrect = QRectF(QPointF(dest[0], dest[1]), QPointF(dest[2], dest[3]))
        painter.drawImage(qrect, self._image, qrect)
        xl, yt, xr, yb = dest
        self._offscreen[yt:yb, xl:xr] = 0

    def notify_new_offscreen(self):
        """ """
        # we always ensure the offscreen is clean before drawing
        self._offscreen[...] = 0


assert_interfaces_valid(QuadGridItem)

# ==============================================================================
# 2-D Histogram
# ==============================================================================
class Histogram2DItem(ImageMixin, BaseImageItem):
    """
    Construct a 2D histogram item

        * X: data (1-D array)
        * Y: data (1-D array)
        * param (optional): style parameters
          (:py:class:`.styles.Histogram2DParam` instance)
    """

    __implements__ = (IBasePlotItem, IBaseImageItem, IHistDataSource, IVoiImageItemType)

    def __init__(self, X, Y, param=None, Z=None):
        if param is None:
            param = ImageParam(_("Image"))
        self._z = Z  # allows set_bins to
        self.tr = np.eye(3, dtype=float)
        self.itr = np.eye(3, dtype=float)
        self.points = np.array([[0, 0, 2, 2], [0, 2, 2, 0], [1, 1, 1, 1]], float)
        super(Histogram2DItem, self).__init__(param=param)

        # Set by parameters
        self.nx_bins = 0
        self.ny_bins = 0
        self.logscale = None

        # internal use
        self._x = None
        self._y = None

        # Histogram parameters
        self.histparam = param
        self.histparam.update_histogram(self)

        self.set_lut_range([0, 10.0])
        self.set_data(X, Y, Z)
        self.setIcon(get_icon("histogram2d.png"))
        self.set_transform(0, 0, 0)

    # ---- Public API -----------------------------------------------------------
    def set_bins(self, NX, NY):
        """Set histogram bins"""
        self.nx_bins = NX
        self.ny_bins = NY
        self.data = np.zeros((self.ny_bins, self.nx_bins), float)
        if self._z is not None:
            self.data_tmp = np.zeros((self.ny_bins, self.nx_bins), float)

    def set_data(self, X, Y, Z=None):
        """Set histogram data"""
        self._x = X
        self._y = Y
        self._z = Z
        xmin = self._x.min()
        xmax = self._x.max()
        ymin = self._y.min()
        ymax = self._y.max()
        self.points = np.array(
            [[xmin, xmin, xmax, xmax], [ymin, ymax, ymax, ymin], [1, 1, 1, 1]], float
        )
        self.compute_bounds()

    # ---- QwtPlotItem API ------------------------------------------------------
    fill_canvas = True

    def draw_image(self, painter, canvasRect, src_rect, dst_rect, xMap, yMap):
        """

        :param painter:
        :param canvasRect:
        :param src_rect:
        :param dst_rect:
        :param xMap:
        :param yMap:
        """
        computation = self.histparam.computation
        i1, j1, i2, j2 = src_rect

        if computation == -1 or self._z is None:
            self.data[:, :] = 0.0
            nmax = histogram2d(
                self._x, self._y, i1, i2, j1, j2, self.itr.A, self.data, self.logscale
            )
        else:
            self.data_tmp[:, :] = 0.0
            if computation in (2, 4):  # sum, avg
                self.data[:, :] = 0.0
            elif computation in (1, 5):  # min, argmin
                val = np.inf
                self.data[:, :] = val
            elif computation in (0, 6):  # max, argmax
                val = -np.inf
                self.data[:, :] = val
            elif computation == 3:
                self.data[:, :] = 1.0
            histogram2d_func(
                self._x,
                self._y,
                self._z,
                i1,
                i2,
                j1,
                j2,
                self.itr.A,
                self.data_tmp,
                self.data,
                computation,
            )
            if computation in (0, 1, 5, 6):
                self.data[self.data == val] = np.nan
            else:
                self.data[self.data_tmp == 0.0] = np.nan
        if self.histparam.auto_lut:
            nmin = _nanmin(self.data)
            nmax = _nanmax(self.data)
            self.set_lut_range([nmin, nmax])
            self.plot().update_colormap_axis(self)
        src_rect = (0, 0, self.nx_bins, self.ny_bins)
        drawfunc = lambda *args: BaseImageItem.draw_image(self, *args)
        if self.fill_canvas:
            x1, y1, x2, y2 = canvasRect.getCoords()
            drawfunc(painter, canvasRect, src_rect, (x1, y1, x2, y2), xMap, yMap)
        else:
            dst_rect = tuple([int(i) for i in dst_rect])
            drawfunc(painter, canvasRect, src_rect, dst_rect, xMap, yMap)

    # ---- IBasePlotItem API ---------------------------------------------------
    def types(self):
        """

        :return:
        """
        return (
            IColormapImageItemType,
            IImageItemType,
            ITrackableItemType,
            IVoiImageItemType,
            IColormapImageItemType,
            ICSImageItemType,
        )

    def update_item_parameters(self):
        """ """
        BaseImageItem.update_item_parameters(self)
        self.histparam.update_param(self)

    def get_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        BaseImageItem.get_item_parameters(self, itemparams)
        itemparams.add("Histogram2DParam", self, self.histparam)

    def set_item_parameters(self, itemparams):
        """

        :param itemparams:
        """
        update_dataset(
            self.histparam, itemparams.get("Histogram2DParam"), visible_only=True
        )
        self.histparam = itemparams.get("Histogram2DParam")
        self.histparam.update_histogram(self)
        BaseImageItem.set_item_parameters(self, itemparams)

    # ---- IBaseImageItem API --------------------------------------------------
    def can_setfullscale(self):
        """

        :return:
        """
        return True

    def can_sethistogram(self):
        """

        :return:
        """
        return True

    def get_histogram(self, nbins):
        """interface de IHistDataSource"""
        if self.data is None:
            return [0], [0, 1]
        _min = _nanmin(self.data)
        _max = _nanmax(self.data)
        if self.data.dtype in (np.float64, np.float32):
            bins = np.unique(
                np.array(np.linspace(_min, _max, nbins + 1), dtype=self.data.dtype)
            )
        else:
            bins = np.arange(_min, _max + 2, dtype=self.data.dtype)
        res2 = np.zeros((bins.size + 1,), np.uint32)
        _histogram(self.data.flatten(), bins, res2)
        # toc("histo2")
        res = res2[1:-1], bins
        return res


assert_interfaces_valid(Histogram2DItem)
