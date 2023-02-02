import PIL.Image
from numpy.core.multiarray import ndarray

from plotpy.widgets.variableexplorer.arrayeditor import ArrayEditor
from plotpy.widgets.variableexplorer.dataframeeditor import DataFrameEditor
from plotpy.widgets.variableexplorer.nsview import DataFrame, Series, is_known_type
from plotpy.widgets.variableexplorer.texteditor import TextEditor


def create_dialog(obj, obj_name):
    """Creates the editor dialog and returns a tuple (dialog, func) where func
    is the function to be called with the dialog instance as argument, after
    quitting the dialog box

    The role of this intermediate function is to allow easy monkey-patching.
    (uschmitt suggested this indirection here so that he can monkey patch
    oedit to show eMZed related data)
    """

    conv_func = lambda data: data
    readonly = not is_known_type(obj)
    if isinstance(obj, ndarray):
        dialog = ArrayEditor()
        if not dialog.setup_and_check(obj, title=obj_name, readonly=readonly):
            return
    elif isinstance(obj, PIL.Image.Image):
        dialog = ArrayEditor()
        import numpy as np

        data = np.array(obj)
        if not dialog.setup_and_check(data, title=obj_name, readonly=readonly):
            return
        conv_func = lambda data: PIL.Image.fromarray(data, mode=obj.mode)
    elif isinstance(obj, (DataFrame, Series)):
        dialog = DataFrameEditor()
        if not dialog.setup_and_check(obj):
            return
    elif isinstance(obj, str):
        dialog = TextEditor(obj, title=obj_name, readonly=readonly)
    else:
        from plotpy.widgets.variableexplorer.collectionseditor.collection import (
            CollectionsEditor,
        )

        dialog = CollectionsEditor()
        dialog.setup(obj, title=obj_name, readonly=readonly)

    def end_func(dialog):
        """

        :param dialog:
        :return:
        """
        return conv_func(dialog.get_value())

    return dialog, end_func
