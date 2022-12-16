# -*- coding: utf-8 -*-
import warnings

from guidata.configtools import get_font
from qtpy import QtCore as QC
from qtpy import QtGui as QG

from plotpy.config import CONF, _
from plotpy.widgets.variableexplorer.nsview import (
    display_to_value,
    get_color_name,
    get_human_readable_type,
    get_object_attrs,
    get_size,
    get_type_string,
    sort_against,
    value_to_display,
)

LARGE_NROWS = 100
ROWS_TO_LOAD = 50


class ProxyObject(object):
    """Dictionary proxy to an unknown object."""

    def __init__(self, obj):
        """Constructor."""
        self.__obj__ = obj

    def __len__(self):
        """Get len according to detected attributes."""
        return len(get_object_attrs(self.__obj__))

    def __getitem__(self, key):
        """Get the attribute corresponding to the given key."""
        # Catch NotImplementedError to fix #6284 in pandas MultiIndex
        # due to NA checking not being supported on a multiindex.
        # Catch AttributeError to fix #5642 in certain special classes like xml
        # when this method is called on certain attributes.
        # Catch TypeError to prevent fatal Python crash to desktop after
        # modifying certain pandas objects. Fix issue #6727 .
        # Catch ValueError to allow viewing and editing of pandas offsets.
        # Fix issue #6728 .
        try:
            attribute_toreturn = getattr(self.__obj__, key)
        except (NotImplementedError, AttributeError, TypeError, ValueError):
            attribute_toreturn = None
        return attribute_toreturn

    def __setitem__(self, key, value):
        """Set attribute corresponding to key with value."""
        # Catch AttributeError to gracefully handle inability to set an
        # attribute due to it not being writeable or set-table.
        # Fix issue #6728 . Also, catch NotImplementedError for safety.
        try:
            setattr(self.__obj__, key, value)
        except (TypeError, AttributeError, NotImplementedError):
            pass
        except Exception as e:
            if "cannot set values for" not in str(e):
                raise


class ReadOnlyCollectionsModel(QC.QAbstractTableModel):
    """CollectionsEditor Read-Only Table Model"""

    sig_setting_data = QC.Signal()

    def __init__(
        self, parent, data, title="", names=False, minmax=False, dataframe_format=None
    ):
        QC.QAbstractTableModel.__init__(self, parent)
        if data is None:
            data = {}
        self.names = names
        self.minmax = minmax
        self.dataframe_format = dataframe_format
        self.header0 = None
        self._data = None
        self.total_rows = None
        self.showndata = None
        self.keys = None
        self.title = str(title)  # in case title is not a string
        if self.title:
            self.title = self.title + " - "
        self.sizes = []
        self.types = []
        self.set_data(data)

    def get_data(self):
        """Return model data"""
        return self._data

    def set_data(self, data, coll_filter=None):
        """Set model data"""
        self._data = data
        data_type = get_type_string(data)

        if coll_filter is not None and isinstance(data, (tuple, list, dict)):
            data = coll_filter(data)
        self.showndata = data

        self.header0 = _("Index")
        if self.names:
            self.header0 = _("Name")
        if isinstance(data, tuple):
            self.keys = list(range(len(data)))
            self.title += _("Tuple")
        elif isinstance(data, list):
            self.keys = list(range(len(data)))
            self.title += _("List")
        elif isinstance(data, dict):
            self.keys = list(data.keys())
            self.title += _("Dictionary")
            if not self.names:
                self.header0 = _("Key")
        else:
            self.keys = get_object_attrs(data)
            self._data = data = self.showndata = ProxyObject(data)
            if not self.names:
                self.header0 = _("Attribute")

        if not isinstance(self._data, ProxyObject):
            self.title += " (" + str(len(self.keys)) + " " + _("elements") + ")"
        else:
            self.title += data_type

        self.total_rows = len(self.keys)
        if self.total_rows > LARGE_NROWS:
            self.rows_loaded = ROWS_TO_LOAD
        else:
            self.rows_loaded = self.total_rows
        self.sig_setting_data.emit()
        self.set_size_and_type()
        self.reset()

    def set_size_and_type(self, start=None, stop=None):
        """

        :param start:
        :param stop:
        """
        data = self._data

        if start is None and stop is None:
            start = 0
            stop = self.rows_loaded
            fetch_more = False
        else:
            fetch_more = True

        # Ignore pandas warnings that certain attributes are deprecated
        # and will be removed, since they will only be accessed if they exist.
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(
                    r"^\w+\.\w+ is deprecated and "
                    "will be removed in a future version"
                ),
            )

            sizes = [get_size(data[self.keys[index]]) for index in range(start, stop)]
            types = [
                get_human_readable_type(data[self.keys[index]])
                for index in range(start, stop)
            ]

        if fetch_more:
            self.sizes = self.sizes + sizes
            self.types = self.types + types
        else:
            self.sizes = sizes
            self.types = types

    def sort(self, column, order=QC.Qt.AscendingOrder):
        """Overriding sort method"""
        reverse = order == QC.Qt.DescendingOrder
        if column == 0:
            self.sizes = sort_against(self.sizes, self.keys, reverse)
            self.types = sort_against(self.types, self.keys, reverse)
            try:
                self.keys.sort(reverse=reverse)
            except:
                pass
        elif column == 1:
            self.keys[: self.rows_loaded] = sort_against(self.keys, self.types, reverse)
            self.sizes = sort_against(self.sizes, self.types, reverse)
            try:
                self.types.sort(reverse=reverse)
            except:
                pass
        elif column == 2:
            self.keys[: self.rows_loaded] = sort_against(self.keys, self.sizes, reverse)
            self.types = sort_against(self.types, self.sizes, reverse)
            try:
                self.sizes.sort(reverse=reverse)
            except:
                pass
        elif column == 3:
            values = [self._data[key] for key in self.keys]
            self.keys = sort_against(self.keys, values, reverse)
            self.sizes = sort_against(self.sizes, values, reverse)
            self.types = sort_against(self.types, values, reverse)
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, qindex=QC.QModelIndex()):
        """Array column number"""
        return 4

    def rowCount(self, index=QC.QModelIndex()):
        """Array row number"""
        if self.total_rows <= self.rows_loaded:
            return self.total_rows
        else:
            return self.rows_loaded

    def canFetchMore(self, index=QC.QModelIndex()):
        """

        :param index:
        :return:
        """
        if self.total_rows > self.rows_loaded:
            return True
        else:
            return False

    def fetchMore(self, index=QC.QModelIndex()):
        """

        :param index:
        """
        reminder = self.total_rows - self.rows_loaded
        items_to_fetch = min(reminder, ROWS_TO_LOAD)
        self.set_size_and_type(self.rows_loaded, self.rows_loaded + items_to_fetch)
        self.beginInsertRows(
            QC.QModelIndex(), self.rows_loaded, self.rows_loaded + items_to_fetch - 1
        )
        self.rows_loaded += items_to_fetch
        self.endInsertRows()

    def get_index_from_key(self, key):
        """

        :param key:
        :return:
        """
        try:
            return self.createIndex(self.keys.index(key), 0)
        except (RuntimeError, ValueError):
            return QC.QModelIndex()

    def get_key(self, index):
        """Return current key"""
        return self.keys[index.row()]

    def get_value(self, index):
        """Return current value"""
        if index.column() == 0:
            return self.keys[index.row()]
        elif index.column() == 1:
            return self.types[index.row()]
        elif index.column() == 2:
            return self.sizes[index.row()]
        else:
            return self._data[self.keys[index.row()]]

    def get_bgcolor(self, index):
        """Background color depending on value"""
        if index.column() == 0:
            color = QG.QColor(QC.Qt.lightGray)
            color.setAlphaF(0.05)
        elif index.column() < 3:
            color = QG.QColor(QC.Qt.lightGray)
            color.setAlphaF(0.2)
        else:
            color = QG.QColor(QC.Qt.lightGray)
            color.setAlphaF(0.3)
        return color

    def data(self, index, role=QC.Qt.DisplayRole):
        """Cell content"""
        if not index.isValid():
            return None
        value = self.get_value(index)
        if index.column() == 3:
            display = value_to_display(value, minmax=self.minmax)
        else:
            display = str(value)
        if role == QC.Qt.DisplayRole:
            return display
        elif role == QC.Qt.EditRole:
            return value_to_display(value)
        elif role == QC.Qt.TextAlignmentRole:
            if index.column() == 3:
                if len(display.splitlines()) < 3:
                    return int(QC.Qt.AlignLeft | QC.Qt.AlignVCenter)
                else:
                    return int(QC.Qt.AlignLeft | QC.Qt.AlignTop)
            else:
                return int(QC.Qt.AlignLeft | QC.Qt.AlignVCenter)
        elif role == QC.Qt.BackgroundColorRole:
            return self.get_bgcolor(index)
        elif role == QC.Qt.FontRole:
            return get_font(CONF, "dicteditor", "font")
        return None

    def headerData(self, section, orientation, role=QC.Qt.DisplayRole):
        """Overriding method headerData"""
        if role != QC.Qt.DisplayRole:
            return None
        i_column = int(section)
        if orientation == QC.Qt.Horizontal:
            headers = (self.header0, _("Type"), _("Size"), _("Value"))
            return headers[i_column]
        else:
            return None

    def flags(self, index):
        """Overriding method flags"""
        # This method was implemented in CollectionsModel only, but to enable
        # tuple exploration (even without editing), this method was moved here
        if not index.isValid():
            return QC.Qt.ItemIsEnabled
        return QC.Qt.ItemFlags(
            QC.QAbstractTableModel.flags(self, index) | QC.Qt.ItemIsEditable
        )

    def reset(self):
        """ """
        self.beginResetModel()
        self.endResetModel()


class CollectionsModel(ReadOnlyCollectionsModel):
    """Collections Table Model"""

    def set_value(self, index, value):
        """Set value"""
        self._data[self.keys[index.row()]] = value
        self.showndata[self.keys[index.row()]] = value
        self.sizes[index.row()] = get_size(value)
        self.types[index.row()] = get_human_readable_type(value)
        self.sig_setting_data.emit()

    def get_bgcolor(self, index):
        """Background color depending on value"""
        value = self.get_value(index)
        if index.column() < 3:
            color = ReadOnlyCollectionsModel.get_bgcolor(self, index)
        else:
            color_name = get_color_name(value)
            color = QG.QColor(color_name)
            color.setAlphaF(0.2)
        return color

    def setData(self, index, value, role=QC.Qt.EditRole):
        """Cell content change"""
        if not index.isValid():
            return False
        if index.column() < 3:
            return False
        value = display_to_value(value, self.get_value(index), ignore_errors=True)
        self.set_value(index, value)
        self.dataChanged.emit(index, index)
        return True
