# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
spyder.widgets.variableexplorer
===============================

Variable Explorer related widgets
"""
from plotpy.widgets.variableexplorer.arrayeditor import (
    ArrayDelegate,
    ArrayEditor,
    ArrayEditorWidget,
    ArrayModel,
    ArrayView,
    get_idx_rect,
    is_float,
    is_number,
)
from plotpy.widgets.variableexplorer.collectionseditor import (
    BaseTableView,
    CollectionsDelegate,
    CollectionsEditor,
    CollectionsEditorTableView,
    CollectionsEditorWidget,
    CollectionsModel,
    DictEditor,
    ProxyObject,
    ReadOnlyCollectionsModel,
    fix_reference_name,
)
from plotpy.widgets.variableexplorer.dataframeeditor import (
    DataFrameEditor,
    DataFrameModel,
    DataFrameView,
    FrozenTableView,
    bool_false_check,
    global_max,
)
from plotpy.widgets.variableexplorer.importwizard import (
    ContentsWidget,
    ImportWizard,
    PreviewTable,
    PreviewTableModel,
    PreviewWidget,
    datestr_to_datetime,
    get_color,
    try_to_eval,
    try_to_parse,
)
from plotpy.widgets.variableexplorer.nsview import (
    address,
    collections_display,
    datestr_to_datetime,
    default_display,
    display_to_value,
    get_color_name,
    get_human_readable_type,
    get_numpy_dtype,
    get_object_attrs,
    get_remote_data,
    get_size,
    get_supported_types,
    get_type_string,
    globalsfilter,
    is_editable_type,
    is_known_type,
    is_supported,
    make_remote_view,
    sort_against,
    str_to_timedelta,
    try_to_eval,
    unsorted_unique,
    value_to_display,
)
from plotpy.widgets.variableexplorer.objecteditor import create_dialog, keeper, oedit
from plotpy.widgets.variableexplorer.texteditor import TextEditor
